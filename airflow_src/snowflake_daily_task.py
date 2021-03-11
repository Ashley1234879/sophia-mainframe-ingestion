import config
from snowflake_conn import DBManager
SNOWFLAKE_CONNECTOR = DBManager('snowflake')
import sys

def execute_snowflake_task(domainName, tableName):
    try:
        fileName = '/projects/app/etl_scripts/'+domainName.upper()+'/'+tableName.upper()+'/'+tableName.upper()+'_AIRFLOW.sql'
        with open(fileName, 'r') as fd:
            queries = fd.read().split(';')
            SNOWFLAKE_CONNECTOR.execute_query("use role ksf_dba;")
            SNOWFLAKE_CONNECTOR.execute_query("use warehouse ksf_airflow_wh;")
            for query in queries:
                if query.strip():
                    response = SNOWFLAKE_CONNECTOR.execute_query(query)
                    print("Snowflake response: ")
                    print(str(response.fetchone()).replace("\\n",""))

    except Exception as e:
        print(str(e))
        raise

if __name__ == '__main__':
    execute_snowflake_task(sys.argv[1], sys.argv[2])
