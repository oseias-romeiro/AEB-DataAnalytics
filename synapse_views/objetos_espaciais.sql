USE dw;
GO

-- Fact view
CREATE OR ALTER VIEW vw_fato_satelite AS
SELECT * FROM OPENROWSET(BULK 'https://aebdatalake0.dfs.core.windows.net/gold/objetos_espaciais/fato_satelite.parquet', FORMAT = 'PARQUET') AS f;
GO

-- Dimensions views
CREATE OR ALTER VIEW vw_dim_base AS
SELECT * FROM OPENROWSET(BULK 'https://aebdatalake0.dfs.core.windows.net/gold/objetos_espaciais/dim_base.parquet', FORMAT = 'PARQUET') AS f;
GO

CREATE OR ALTER VIEW vw_dim_entidade AS
SELECT * FROM OPENROWSET(BULK 'https://aebdatalake0.dfs.core.windows.net/gold/objetos_espaciais/dim_entidade.parquet', FORMAT = 'PARQUET') AS f;
GO

CREATE OR ALTER VIEW vw_dim_funcao_esp AS
SELECT * FROM OPENROWSET(BULK 'https://aebdatalake0.dfs.core.windows.net/gold/objetos_espaciais/dim_funcao_esp.parquet', FORMAT = 'PARQUET') AS f;
GO

CREATE OR ALTER VIEW vw_dim_funcao_geral AS
SELECT * FROM OPENROWSET(BULK 'https://aebdatalake0.dfs.core.windows.net/gold/objetos_espaciais/dim_funcao_geral.parquet', FORMAT = 'PARQUET') AS f;
GO

CREATE OR ALTER VIEW vw_dim_orbita AS
SELECT * FROM OPENROWSET(BULK 'https://aebdatalake0.dfs.core.windows.net/gold/objetos_espaciais/dim_orbita.parquet', FORMAT = 'PARQUET') AS f;
GO

CREATE OR ALTER VIEW vw_dim_status AS
SELECT * FROM OPENROWSET(BULK 'https://aebdatalake0.dfs.core.windows.net/gold/objetos_espaciais/dim_status.parquet', FORMAT = 'PARQUET') AS f;
GO

CREATE OR ALTER VIEW vw_dim_vcge AS
SELECT * FROM OPENROWSET(BULK 'https://aebdatalake0.dfs.core.windows.net/gold/objetos_espaciais/dim_vcge.parquet', FORMAT = 'PARQUET') AS f;
GO

CREATE OR ALTER VIEW vw_dim_veiculo AS
SELECT * FROM OPENROWSET(BULK 'https://aebdatalake0.dfs.core.windows.net/gold/objetos_espaciais/dim_veiculo.parquet', FORMAT = 'PARQUET') AS f;
GO

-- Bridge views
CREATE OR ALTER VIEW vw_bridge_satelite_fabricante AS
SELECT * FROM OPENROWSET(BULK 'https://aebdatalake0.dfs.core.windows.net/gold/objetos_espaciais/bridge_satelite_fabricante.parquet', FORMAT = 'PARQUET') AS f;
GO

CREATE OR ALTER VIEW vw_bridge_satelite_funcao_esp AS
SELECT * FROM OPENROWSET(BULK 'https://aebdatalake0.dfs.core.windows.net/gold/objetos_espaciais/bridge_satelite_funcao_esp.parquet', FORMAT = 'PARQUET') AS f;
GO

CREATE OR ALTER VIEW vw_bridge_satelite_proprietario AS
SELECT * FROM OPENROWSET(BULK 'https://aebdatalake0.dfs.core.windows.net/gold/objetos_espaciais/bridge_satelite_proprietario.parquet', FORMAT = 'PARQUET') AS f;
GO

-- Drops
-- DROP VIEW vw_fato_satelite;
-- DROP VIEW vw_dim_base;
-- DROP VIEW vw_dim_entidade;
-- DROP VIEW vw_dim_funcao_esp;
-- DROP VIEW vw_dim_funcao_geral;
-- DROP VIEW vw_dim_orbita;
-- DROP VIEW vw_dim_status;
-- DROP VIEW vw_dim_vcge;
-- DROP VIEW vw_dim_veiculo;
-- DROP VIEW vw_bridge_satelite_fabricante;
-- DROP VIEW vw_bridge_satelite_funcao_esp;
-- DROP VIEW vw_bridge_satelite_proprietario;