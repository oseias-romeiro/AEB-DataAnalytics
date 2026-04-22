import pandas as pd
from os import makedirs
from pathlib import Path

BASE_PATH = Path("../../data/Objetos Espaciais Brasileiros CSV 2025/processed/gold")
OUTPUT_PATH = Path("../../data/kaggle")
makedirs(OUTPUT_PATH, exist_ok=True)

## Carregando tabelas
fato = pd.read_parquet(BASE_PATH / "fato_satelite.parquet")

dim_base = pd.read_parquet(BASE_PATH / "dim_base.parquet")
dim_entidade = pd.read_parquet(BASE_PATH / "dim_entidade.parquet")
dim_funcao_geral = pd.read_parquet(BASE_PATH / "dim_funcao_geral.parquet")
dim_funcao_esp = pd.read_parquet(BASE_PATH / "dim_funcao_esp.parquet")
dim_orbita = pd.read_parquet(BASE_PATH / "dim_orbita.parquet")
dim_status = pd.read_parquet(BASE_PATH / "dim_status.parquet")
dim_veiculo = pd.read_parquet(BASE_PATH / "dim_veiculo.parquet")

bridge_proprietario = pd.read_parquet(BASE_PATH / "bridge_satelite_proprietario.parquet")
bridge_fabricante = pd.read_parquet(BASE_PATH / "bridge_satelite_fabricante.parquet")
bridge_funcao_esp = pd.read_parquet(BASE_PATH / "bridge_satelite_funcao_esp.parquet")

# Dimensões simples
df = (
    fato
    .merge(dim_base, on="base_id", how="left")
    .merge(dim_funcao_geral, on="funcao_geral_id", how="left")
    .merge(dim_orbita, on="orbita_id", how="left")
    .merge(dim_status, on="status_id", how="left")
    .merge(dim_veiculo, on="veiculo_id", how="left")
)

bridge_proprietario.rename(columns={"entidade_id": "proprietario_id"}, inplace=True)

## Proprietário
df = (
    df
    .merge(bridge_proprietario, on="satelite_id", how="left")
    .merge(
        dim_entidade
        .rename(columns={
            "entidade_id": "proprietario_id",
            "entidade_nome": "proprietario_nome",
            "entidade_pais": "proprietario_pais"
        }),
        on="proprietario_id",
        how="left"
    )
)

## Fabricante
df = (
    df
    .merge(
        bridge_fabricante
        .rename(columns={"entidade_id": "fabricante_id"}),
        on="satelite_id",
        how="left"
    )
    .merge(
        dim_entidade
        .rename(columns={
            "entidade_id": "fabricante_id",
            "entidade_nome": "fabricante_nome",
            "entidade_pais": "fabricante_pais"
        }),
        on="fabricante_id",
        how="left"
    )
)

df = df.merge(bridge_funcao_esp, on="satelite_id", how="left") \
    .merge(dim_funcao_esp, on="funcao_esp_id", how="left")


flatten = df[[
    "satelite_id", "nssdc", "satelite_nome", "massa_inicial",
    "data_lancamento", "data_fim_operacao",

    "base_nome", "veiculo_nome",

    "orbita_descricao", "status_descricao",

    "funcao_geral_descricao", "funcao_esp_descricao",

    "proprietario_nome", "proprietario_pais",

    "fabricante_nome", "fabricante_pais",
]].copy()

flatten.to_csv(
    OUTPUT_PATH / "brazilian_space_objects_analytics.csv",
    index=False
)
