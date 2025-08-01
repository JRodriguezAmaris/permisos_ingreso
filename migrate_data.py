import pandas as pd
import oracledb
from sqlalchemy import create_engine

oracle_config = {
    "username": "dashboard",
    "password": "#D4shb04rd",
    "host": "10.80.123.15",
    "port": "1521",
    "service_name": "CTGINST",
}

oracle_config_ptm = {
    "username": "calidadrc",
    "password": "Telefonica1",
    "host": "10.89.216.252",
    "port": "1521",
    "service_name": "ORCLDB_SVC",
}

oracledb.init_oracle_client(lib_dir="C:\\Program Files\\Oracle\\instantclient_23_6")

# Query deptos
query_deptos = """WITH
    DESC_DEP AS (
    SELECT DP.LOCATION AS COD_DEPARTAMENTO,DP.DESCRIPTION AS DESCRIPTION_DP, DP.COD_DANE AS COD_DANE_DP, --N1
    M.LOCATION AS COD_MUNICIPIO, M.DESCRIPTION AS DESCRIPTION_MUNI, M.CODIGO_DANE AS COD_DANE_MUNI, M.AMBITO AS AMBITO --N2
    FROM MAXIMO.SIPI_DEPTO DP
    INNER JOIN MAXIMO.SIPI_MUNICIPIO M
    ON DP.LOCATION=M.DEPARTAMENTO
    ),
    DEP AS (
    SELECT LOCATION, ANCESTOR FROM MAXIMO.LOCANCESTOR WHERE ANCESTOR LIKE 'D%'
    ),
    MUN AS (
    SELECT LOCATION, ANCESTOR FROM MAXIMO.LOCANCESTOR WHERE ANCESTOR LIKE 'M%'
    )
    SELECT
        ROW_NUMBER() OVER (ORDER BY cod_dane) AS id,
        cod_dane,
        name
    FROM (
        SELECT
            SUBSTR(DEP.ANCESTOR, 2) AS cod_dane,
            DESC_DEP.DESCRIPTION_DP AS name
        FROM
            MAXIMO.LOCATIONS L
        INNER JOIN DEP ON L.LOCATION = DEP.LOCATION
        INNER JOIN MUN ON L.LOCATION = MUN.LOCATION
        INNER JOIN DESC_DEP ON DEP.ANCESTOR=DESC_DEP.COD_DEPARTAMENTO AND MUN.ANCESTOR=DESC_DEP.COD_MUNICIPIO
        WHERE
            L.CLASSSTRUCTUREID = '3087'
            AND L.STATUS='OPERATING'
        GROUP BY
            SUBSTR(DEP.ANCESTOR, 2),
            DESC_DEP.DESCRIPTION_DP
    )
"""

query_mpios = """WITH
    DESC_DEP AS (
    SELECT DP.LOCATION AS COD_DEPARTAMENTO,DP.DESCRIPTION AS DESCRIPTION_DP, DP.COD_DANE AS COD_DANE_DP,
    M.LOCATION AS COD_MUNICIPIO, M.DESCRIPTION AS DESCRIPTION_MUNI, M.CODIGO_DANE AS COD_DANE_MUNI, M.AMBITO AS AMBITO
    FROM MAXIMO.SIPI_DEPTO DP
    INNER JOIN MAXIMO.SIPI_MUNICIPIO M
    ON DP.LOCATION=M.DEPARTAMENTO
    ),
    DEP AS (
    SELECT LOCATION, ANCESTOR FROM MAXIMO.LOCANCESTOR WHERE ANCESTOR LIKE 'D%'
    ),
    MUN AS (
    SELECT LOCATION, ANCESTOR FROM MAXIMO.LOCANCESTOR WHERE ANCESTOR LIKE 'M%'
    )
    SELECT
        ROW_NUMBER() OVER (ORDER BY cod_dane) AS id,
    	departament_id,
        cod_dane,
        name
    FROM (
        SELECT
        	SUBSTR(DEP.ANCESTOR, 2) AS departament_id,
            SUBSTR(MUN.ANCESTOR, 2) AS cod_dane,
            DESC_DEP.DESCRIPTION_MUNI AS name
        FROM
            MAXIMO.LOCATIONS L
        INNER JOIN DEP ON L.LOCATION = DEP.LOCATION
        INNER JOIN MUN ON L.LOCATION = MUN.LOCATION
        INNER JOIN DESC_DEP ON 
            DEP.ANCESTOR = DESC_DEP.COD_DEPARTAMENTO 
            AND MUN.ANCESTOR = DESC_DEP.COD_MUNICIPIO
        WHERE
            L.CLASSSTRUCTUREID = '3087'
            AND L.STATUS = 'OPERATING'
        GROUP BY SUBSTR(DEP.ANCESTOR, 2),
            SUBSTR(MUN.ANCESTOR, 2),
            DESC_DEP.DESCRIPTION_MUNI
        ORDER BY
            SUBSTR(DEP.ANCESTOR, 2),
            SUBSTR(MUN.ANCESTOR, 2)
    )
"""

query_branches = """
        SELECT
            ROW_NUMBER() OVER (ORDER BY LOCATION) AS id, LOCATION AS code, DESCRIPTION AS name, DIRECCION_PROYECTO_TOP AS address,
            CASE WHEN PROPIETARIO_TORRE LIKE '%TELEFONICA%' OR PROPIETARIO_TORRE LIKE '%COLOMBIA TELECOM%' OR PROPIETARIO_TORRE IS NULL THEN 'technical' ELSE 'external' END type, SUBSTR(COD_MUNICIPIO, 2) AS cod_mun, 0 AS is_j10 
        FROM CALIDADRC.MAPPER_LOCATIONS_ATTR_VIEW 
        WHERE STATUS = 'OPERATING' AND CLASSSTRUCTUREID = '3087' 
        ORDER BY LOCATION
"""

sqlite_db_path = "test.db"


dsn = oracledb.makedsn(
    oracle_config["host"],
    oracle_config["port"],
    service_name=oracle_config["service_name"]
)

oracle_conn = oracledb.connect(
    user=oracle_config["username"],
    password=oracle_config["password"],
    dsn=dsn
)



dsn = oracledb.makedsn(
    oracle_config_ptm["host"],
    oracle_config_ptm["port"],
    service_name=oracle_config_ptm["service_name"]
)

oracle_conn_ptm = oracledb.connect(
    user=oracle_config_ptm["username"],
    password=oracle_config_ptm["password"],
    dsn=dsn
)

try:
    df_deptos = pd.read_sql(query_deptos, con=oracle_conn)
    df_mpios = pd.read_sql(query_mpios, con=oracle_conn)

    df_mpios = df_mpios.merge(df_deptos, left_on="DEPARTAMENT_ID", right_on="COD_DANE", how="left")[['ID_x', 'ID_y', 'COD_DANE_x', 'NAME_x',]]

    df_mpios.rename(columns={
                "ID_x": "ID",
                "ID_y": "DEPARTMENT_ID",
                "COD_DANE_x": "COD_DANE",
                "NAME_x": "NAME",
            }, inplace=True)

    print(df_mpios)
    sqlite_engine = create_engine(f"sqlite:///{sqlite_db_path}")
    #df_deptos.to_sql("departments", sqlite_engine, if_exists="replace", index=False)
    #df_mpios.to_sql("municipalities", sqlite_engine, if_exists="replace", index=False)

    df_branches = pd.read_sql(query_branches, con=oracle_conn_ptm)
    df_branches = df_branches.merge(
        df_mpios, left_on="COD_MUN", right_on="COD_DANE", how="left", suffixes=('', '_muni'))
    df_branches = df_branches[['ID', 'CODE', 'NAME', 'ADDRESS', 'TYPE', 'IS_J10', 'DEPARTMENT_ID', 'ID_muni']]
    df_branches.rename(columns={
        "ID_muni": "MUNICIPALITY_ID",
    }, inplace=True)

    #df_branches.to_sql("branches", sqlite_engine, if_exists="replace", index=False)
    print(df_branches)
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    oracle_conn.close()
    oracle_conn_ptm.close()
