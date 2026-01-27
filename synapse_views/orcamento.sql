USE dw;
GO

CREATE OR ALTER VIEW vw_orcamento AS
SELECT CAST(REPLACE(data.filepath(1), 'Ano=', '') AS INT) AS Ano, *
FROM OPENROWSET(BULK 'https://aebdatalake0.dfs.core.windows.net/gold/orcamento/Ano=*/', FORMAT = 'PARQUET') AS data;

-- DROP VIEW vw_orcamento;