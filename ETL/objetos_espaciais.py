from os import getenv, makedirs
import requests
from io import BytesIO
import zipfile
import pandas as pd

DATA_GOV_URL = "https://www.gov.br/aeb/pt-br/acesso-a-informacao/dados-abertos/dados/objetos_espaciais_brasileiros_csv_2025.zip"
LOCAL_DATA_PATH = "../data/Objetos Espaciais Brasileiros CSV 2025"
ONLINE_DOWNLOAD = False
ADLS_ACCOUNT = getenv('ADLS_ACCOUNT')

reading_settings = {
    'sep': ';',
    'encoding': 'utf-8'
}
tables = [
    'base', 'entidade', 'funcesp', 'funcgen', 'geral',
    'metadados', 'orbita', 'satelite', 'satfab',
    'satfuncesp', 'satpropri', 'status', 'vcge', 'veiculo'
]

def get_storage(layer, filename):
    if ADLS_ACCOUNT:
        return f"abfss://{layer}@{ADLS_ACCOUNT}.dfs.core.windows.net/objetos_espaciais/{filename}"
    else:
        makedirs(f"{LOCAL_DATA_PATH}/processed/{layer}", exist_ok=True)
        return f"{LOCAL_DATA_PATH}/processed/{layer}/{filename}"

dfs = {}
if ONLINE_DOWNLOAD:
    response = requests.get(DATA_GOV_URL, timeout=60)
    response.raise_for_status()
    with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
        for table in tables:
            with zip_ref.open(f'Objetos Espaciais Brasileiros CSV 2025/{table}.csv') as csvfile:
                dfs[table] = pd.read_csv(csvfile, **reading_settings)
else:
    for table in tables:
        dfs[table] = pd.read_csv(f'{LOCAL_DATA_PATH}/{table}.csv', **reading_settings)

# Saving data to bronze layer in Data Lake
for table in tables:
    dfs[table].to_parquet(
        get_storage("bronze", f"{table}.parquet"),
        index=False
    )

# Data cleaning based on metadata
for meta in dfs["metadados"].itertuples(index=False):
    table = meta.Tabela
    col = meta.Coluna
    dtype = meta.Tipo

    if col not in dfs[table].columns:
        continue

    if dtype == 'varchar':
        dfs[table][col] = dfs[table][col].astype("string").str.strip()
    elif dtype == 'date':
        dfs[table][col] = pd.to_datetime(dfs[table][col], format='%d/%m/%Y', errors='coerce').dt.date
    elif dtype == 'int2':
        dfs[table][col] = dfs[table][col].str.replace(',', '.').astype(float)
    else:
        print(f"[WARN] Tipo não tratado: {dtype} em {table}.{col}")

# Saving cleaned data to silver layer in Data Lake
for table, df in dfs.items():
    df.to_parquet(
        get_storage("silver", f"{table}.parquet"),
        index=False
    )

# Creating fact table
fato_satelite = dfs["satelite"][[
    "codigo", "nssdc", "nome", "massainicial", "lancamento", "fimop",
    "base", "entidade", "funcgen", "orbita", "status", "vcge", "veiculo"
]].copy()
fato_satelite.columns = [
    "satelite_id", "nssdc", "satelite_nome", "massa_inicial", "data_lancamento",
    "data_fim_operacao", "base_id", "entidade_id", "funcao_geral_id",
    "orbita_id", "status_id", "vcge_id", "veiculo_id"
]
fato_satelite.to_parquet(
    get_storage("gold", "fato_satelite.parquet"),
    index=False
)

# Creating dimension tables
dim_base = dfs["base"][[ "codigo", "nome" ]].copy()
dim_base.columns = [ "base_id", "base_nome" ]

dim_entidade = dfs["entidade"][[ "codigo", "nome", "pais" ]].copy()
dim_entidade.columns = [ "entidade_id", "entidade_nome", "entidade_pais" ]

dim_funcao_esp = dfs["funcesp"][[ "codigo", "descricao" ]].copy()
dim_funcao_esp.columns = [ "funcao_esp_id", "funcao_esp_descricao" ]

dim_funcao_geral = dfs["funcgen"][["codigo", "descricao"]].copy()
dim_funcao_geral.columns = ["funcao_geral_id", "funcao_geral_descricao"]

dim_orbita = dfs["orbita"][[ "sigla", "descricao" ]].copy()
dim_orbita.columns = [ "orbita_id", "orbita_descricao" ]

dim_status = dfs["status"][[ "codigo", "descricao" ]].copy()
dim_status.columns = [ "status_id", "status_descricao" ]

dim_vcge = dfs["vcge"][[ "codigo", "termo" ]].copy()
dim_vcge.columns = [ "vcge_id", "vcge_termo" ]

dim_veiculo = dfs["veiculo"][[ "codigo", "nome" ]].copy()
dim_veiculo.columns = [ "veiculo_id", "veiculo_nome" ]

dims = [
    (dim_base, "base"),
    (dim_entidade, "entidade"),
    (dim_funcao_esp, "funcao_esp"),
    (dim_funcao_geral, "funcao_geral"),
    (dim_orbita, "orbita"),
    (dim_status, "status"),
    (dim_vcge, "vcge"),
    (dim_veiculo, "veiculo")
]
## Validating uniqueness and integrity of keys
for dim, name in dims:
    assert dim[f"{name}_id"].is_unique
    assert (
        name == "funcao_esp" or
        fato_satelite[ fato_satelite[f"{name}_id"].notnull() ][f"{name}_id"].isin(dim[f"{name}_id"]).all()
    )
    dim.to_parquet(
        get_storage("gold", f"dim_{name}.parquet"),
        index=False
    )

# creating bridge tables
bridge_satelite_proprietario = dfs["satpropri"][[ "satelite", "entidade" ]].copy()
bridge_satelite_proprietario.columns = [ "satelite_id", "entidade_id" ]

bridge_satelite_funcao_esp = dfs["satfuncesp"][[ "satelite", "funcesp" ]].copy()
bridge_satelite_funcao_esp.columns = [ "satelite_id", "funcao_esp_id" ]

bridge_satelite_fabricante = dfs["satfab"][[ "satelite", "entidade" ]].copy()
bridge_satelite_fabricante.columns = [ "satelite_id", "entidade_id" ]

bridges = {
    "bridge_satelite_proprietario": {
        "bridge": bridge_satelite_proprietario,
        "connections": [
            (fato_satelite, "satelite_id"),
            (dim_entidade, "entidade_id")
        ]
    },
    "bridge_satelite_funcao_esp": {
        "bridge": bridge_satelite_funcao_esp,
        "connections": [
            (fato_satelite, "satelite_id"),
            (dim_funcao_esp, "funcao_esp_id")
        ]
    },
    "bridge_satelite_fabricante": {
        "bridge": bridge_satelite_fabricante,
        "connections": [
            (fato_satelite, "satelite_id"),
            (dim_entidade, "entidade_id")
        ]
    }
}

## validating uniqueness and integrity in bridge tables
for name, bridge in bridges.items():
    assert not bridge["bridge"].duplicated().any(), f"Duplicate entries found in bridge table {name}"

    for df, attr in bridge["connections"]:
        assert bridge["bridge"][attr].isin(df[attr]).all(), f"Integrity check failed for {attr} in bridge table {name}"

    bridge["bridge"].to_parquet(
        get_storage("gold", f"{name}.parquet"),
        index=False
    )
