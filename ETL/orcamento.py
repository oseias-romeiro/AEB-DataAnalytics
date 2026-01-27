from os import getenv
import requests
from io import BytesIO
import zipfile
import pandas as pd

DATA_GOV_URL = "https://www.gov.br/aeb/pt-br/acesso-a-informacao/dados-abertos/dados/orcamento-aeb-2022-a-maio-2025-csv.zip"
LOCAL_DATA_PATH = "../data/orcamento-aeb-2022-a-maio-2025-csv"
ONLINE_DOWNLOAD = False
ADLS_ACCOUNT = getenv('ADLS_ACCOUNT')

def get_storage(layer):
    if ADLS_ACCOUNT:
        return f"abfss://{layer}@{ADLS_ACCOUNT}.dfs.core.windows.net/orcamento"
    else:
        return f"{LOCAL_DATA_PATH}/processed/{layer}/"

# Downloading and extracting the CSV file from the ZIP archive
if ONLINE_DOWNLOAD:
    response = requests.get(DATA_GOV_URL, timeout=60)
    response.raise_for_status()
    with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
        with zip_ref.open(zip_ref.namelist()[0]) as csvfile:
            df = pd.read_csv(csvfile, sep=";", encoding="utf-8")
else:
    df = pd.read_csv(f'{LOCAL_DATA_PATH}/CSV ORÇAMENTO AEB - 2022 A MAIO 2025.csv', sep=";", encoding="utf-8")

# Dropping rows with missing values
df.dropna(inplace=True)

# Saving data partitioned by year to bronze layer in Data Lake
df.to_parquet(
    get_storage("bronze"),
    index=False,
    partition_cols=["Ano"]
)

# Converting data types
for col in ['Dotação Atual', 'Empenhado', 'Liquidado', 'Pago']:
    df[col] = df[col].str.replace('.', '', regex=False)
    df[col] = df[col].str.replace(',', '.', regex=False)
    df[col] = df[col].astype('float32')

df["Ano"] = df["Ano"].astype('int16')

# cleaning columns
df["Unidade Orçamentária"] = df["Unidade Orçamentária"].str[:5]

# Saving data partitioned by year to silver layer in Data Lake
df.to_parquet(
    get_storage("silver"),
    index=False,
    partition_cols=["Ano"]
)

# Splitting 'Programa' and 'Ação' columns into code and description
df["Programa (Cod)"] = df["Programa"].str[:4].astype('int16')
df["Programa"] = df["Programa"].str[7:]

df["Ação (Cod)"] = df["Ação"].str[:4]
df["Ação"] = df["Ação"].str[7:]

# Reordering columns
df = df[['Ano', 'Unidade Orçamentária', 'Programa',
    'Programa (Cod)', 'Ação', 'Ação (Cod)', 'Dotação Atual',
    'Empenhado', 'Liquidado', 'Pago'
]]

# Saving data partitioned by year to gold layer in Data Lake
df.to_parquet(
    get_storage("gold"),
    index=False,
    partition_cols=["Ano"]
)
