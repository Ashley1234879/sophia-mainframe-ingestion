""" Configuration file for  Sophia EMR setup """
import os
from pathlib import Path

# region
REGION = 'ap-southeast-2'
# EMR cluster name
EMR_CLUSTER_NAME = 'sophia_emr_test'

EMR_VERSION = 'emr-5.30.0'

# Instances
EC2_INSTANCE_TYPE = 'm5.xlarge'
SOPHIA_KEY_PAIR = 'prj-sophia-atlas'
SUB_NET_ID = 'subnet-03c5dd5e6fc20b837'
EMR_CLUSTER_PROFILE = 'sophia-iam-emr-airflow-datasvcsdev-EMRClusterInstanceProfile-1OLDLZVHA2WIQ'
EMR_SERVICE_ROLE = 'sophia-iam-emr-airflow-datasvcsdev-EMRDefaultRole-OIZW6GY2113U'

# LOGGING #
SHARED_LOG_FILE_NAME = "logs/shared_emr.log"
SHARED_LOGGING_PARAMETERS = {"log_file_name": SHARED_LOG_FILE_NAME, "file_mode": "a",
                             "max_bytes": 5 * 1024 * 1024, "backup_count": 10}

APP_PATH = Path(os.environ["PYTHONPATH"])

CONNECTION_ID = 'livy'


# Jenkins
JENKINS_URL = 'https://jenkins.kaccess.net'
JENKINS_USERNAME ='akumarks'
LIVY_SESSION_URL = 'http://emr-prod.sophia.int.ap-southeast-2.datasvcsprod.a-sharedinfra.net:8998/sessions'
JENKINS_BUILD_PATH_START = 'projects/prj-sophia/sophia-emr-cluster/prod'
JENKINS_BUILD_PATH_STOP = 'projects/prj-sophia/sophia-emr-cluster/prod-stop'
CLUSTER_NAME = 'SophiaEMRCluster'
LIVY_HOST = 'http://emr-prod.sophia.int.ap-southeast-2.datasvcsprod.a-sharedinfra.net'
LIVY_PORT = 8998

# Snowflake

SF_DB_ACCOUNT = 'kmartau.ap-southeast-2.privatelink'
SF_DB_USER='sophia_airflow'
SF_DB_ROLE='KSF_AIRFLOW'
SF_DB_WAREHOUSE='KSF_AIRFLOW_WH'
SF_DB_DATABASE='KSFDA'
SF_DB_SCHEMA='MR2'
SF_DB_PASSWORD='r8fqmjn6'
