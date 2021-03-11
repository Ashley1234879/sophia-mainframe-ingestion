import time
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.operators.sensors import S3KeySensor
from airflow.operators.python_operator import BranchPythonOperator
import os
import logging
import pendulum

from alerts import send_failure_notification

# Boto3
import boto3, json, requests
from collections import OrderedDict

# smtp
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText as text
from email.utils import COMMASPACE
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

local_tz = pendulum.timezone("Australia/Sydney")

# Setup logger
# Todo is info okay??
logger = logging.getLogger()
logger.setLevel(logging.INFO)

proxy = 'http://proxy.int.sharedsvc.a-sharedinfra.net:8080/'
os.environ['http_proxy'] = proxy
os.environ['https_proxy'] = proxy
os.environ['HTTPS_PROXY'] = proxy
os.environ['HTTPS_PROXY'] = proxy

# SMTP server configuration
PORT = 25
SMTP_SERVER = "appsmtpgw.core.kmtltd.net.au"

# Todo Need to change hard-coded path
# Dev
s3_bucket_name = 'kmartau-dataanalytics-markdown-test'
s3_tracker_file = 'location/input_large.txt'
s3_bucket_key = 's3://' + s3_bucket_name + '/' + s3_tracker_file

# QA
s3_bucket_name = 'kmartau-kdw-loadfiles-prod'
s3_tracker_file = 'redshift_upload/snowflakedfincriment/tracker_file/tracker_file_df_udt_skuprojstatic_'


def get_tracker_file_name():
    # curent date
    date = pendulum.now(local_tz).strftime("%Y%m%d")
    date_formatted = date + ('000') + (".") + ("parquet")

    s3_tracker_file_name = s3_tracker_file + date_formatted

    s3_bucket_key = 's3://' + s3_bucket_name + '/' + s3_tracker_file_name

    logger.info("looking for file in bucket location: " + s3_bucket_key)

    return s3_bucket_key


def get_tracker_file_prefix_name():
    # curent date
    date = pendulum.now(local_tz).strftime("%Y%m%d")
    date_formatted = date + ('000') + (".") + ("parquet")

    s3_tracker_file_name = s3_tracker_file + date_formatted

    logger.info("looking for file : " + s3_tracker_file_name)

    return s3_tracker_file_name


def send_mail_alerts_failure():
    msg = MIMEMultipart()

    subject = "ETL Pipeline [mr2.schema Daily load] status - Red"

    message = "Hi Team,"
    message+= "\n"
    message+= "\n"
    message+=" File is not available due to delay in upstream sytem, so tables of mr2 schema[df_udt_skuprojstatic] are still not loaded into snowflake."
    message+=" Sophia team will look into it."
    message+= "\n"
    message+= "\n"
    message+= "Thanks,"
    message+= "\n"
    message+= "Data Platform Team"

    msg['From'] = "sophiasnowflakemonitoring@kas-services.com"
    msg['To'] = "KASSDataPlatform-BLR@kmart.com.au,Siddharth.Dixit@kas-services.com,Somsubhra.Sikdar@kas-services.com,KASBLRINVENTORYTEAM@kas-services.com"
    msg['Subject']=subject

    part1 = MIMEText(message, "plain")
    msg.attach(part1)
    server = smtplib.SMTP(SMTP_SERVER)
    server.sendmail(msg['From'], msg['To'], msg.as_string())


def send_success_mail_alerts(context):
    msg = MIMEMultipart()

    subject = "ETL Pipeline [mr2.schema Daily load] status - Green"

    message = "Hi Team,"
    message += "\n"
    message += "\n"
    message += "  Tables of mr2 schema[df_udt_skuprojstatic] successfully loaded into Snowflake"
    message += "\n"
    message += "\n"
    message += "Thanks,"
    message += "\n"
    message += "Data Platform Team"

    msg['From'] = "ronnit.cpeter@kas-services.com"
    msg['To'] = "ronnit.cpeter@kas-services.com"
    msg['Subject'] = subject

    part1 = MIMEText(message, "plain")
    msg.attach(part1)
    server = smtplib.SMTP(SMTP_SERVER)
    server.sendmail(msg['From'], msg['To'], msg.as_string())


def check_tracker_file(**kwargs):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(s3_bucket_name)
    objs = list(bucket.objects.filter(Prefix=get_tracker_file_prefix_name()))
    if (len(objs) > 0):
        return 't2_file_present'
    else:
        send_mail_alerts_failure()
        return 't2_poke_tracker_file'


def t2_file_present(**kwargs):
    logger.info("Tracker file is there, so loading the data")


def trigger_mr2_etl(**kwargs):
    logger.info(os.getcwd(), "Current directory")
    logger.info(os.environ)


def task_cleanup(**kwargs):
    logger.info("Task load is done")


def send_success_notification(context):
    details = OrderedDict()

    details['Alert Name'] = "`" + 'Sophia Airflow: ' + str(context.get('dag', '')) + 'Success' + "`"
    details['Description'] = "`" + str(context['dag'].description) + "`"
    details['Job Owner'] = "`" + str(context['dag'].owner) + "`"
    details['Alert Details'] = "`" + str(context.get('dag_run', 'Check Airflow logs for more details')) + "`"
    details['Job ID'] = "`" + context.get('run_id', 'Check Airflow logs for more details') + "`"
    details['Job Run Time'] = "`" + str(context.get('execution_date', '-')) + "`"
    details['Job Next Run Time'] = "`" + str(context.get('next_execution_date', '-')) + "`"
    details['Job Success Message'] = "`" + str('Data loading done successfully!!!!') + '`'
    cloudwatch_event = boto3.client('events', region_name='ap-southeast-2')

    logger.info(json.dumps(details))
    cloudwatch_event.put_events(
        Entries=[{'Source': 'Sophia Airflow', 'DetailType': details['Alert Name'], 'Detail': json.dumps(details)}, ])
    send_slack_alert(details)


def get_formatted_message(message):
    message_string = ":redsiren: <!channel> :ambulance: \n "
    for each in message:
        message_string += each + ': ' + str(message[each]) + '\n'
    # message_string += ":this-is-fine: For more info login to <https://kmartau.pagerduty.com/incidents?status=triggered|PagerDuty> \n"
    logger.info(message_string)
    return message_string


def send_slack_alert(details):
    webhook_url = "https://hooks.slack.com/services/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"
    logger.info('sending slack request')
    # details = {'slack': 'test'}
    status = requests.post(webhook_url, data=json.dumps(
        {"text": get_formatted_message(details)}))  # , headers={'Content-Type': 'application/json'})
    logger.info(status.text)

# Default Arguments
DEFAULT_ARGS = {
    'owner': 'Sophia',
    'depends_on_past': False,
    'description': 'Inventory ETL Pipeline',
    'start_date': datetime(2021, 2, 12, tzinfo=local_tz),
    'email': ['ronnit.cpeter@kas-services.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),

    'on_failure_callback': send_failure_notification,

    # Is it working for each task?
    # 'on_success_callback': send_success_notification
}

DAG_ID = DAG('inv-mr2-etl-pipeline-daily-incremental-load-prod', catchup=False, default_args=DEFAULT_ARGS,
             schedule_interval='00 11 * * *')  # Scheduled at 5:50 every day
# USING CRON 00 11 * * * Australia/Sydney

# trigger
t1 = PythonOperator(
    namespace='sophia-airflow',
    task_id='trigger_mr2_etl',
    python_callable=trigger_mr2_etl,
    provide_context=True,
    dag=DAG_ID,
)

# Branching whether tracker file avail or not?
t2_check_tracker_file = BranchPythonOperator(
    task_id='t2_check_tracker_file',
    python_callable=check_tracker_file,
    do_xcom_push=False,
    dag=DAG_ID
)
# Tracker file not available?
# Todo set the interval rightly
t2_poke_tracker_file = S3KeySensor(
    namespace='sophia-airflow',
    task_id='t2_poke_tracker_file',
    poke_interval=600,
    timeout=3600,
    soft_fail=False,
    bucket_key=get_tracker_file_name(),
    bucket_name=None,
    on_failure_callback=send_failure_notification,
    dag=DAG_ID)

# Tracker file Available?
t2_file_present = PythonOperator(
    namespace='sophia-airflow',
    task_id='t2_file_present',
    python_callable=t2_file_present,
    provide_context=True,
    dag=DAG_ID)

# MR2
    #product_country_profile
t3 = KubernetesPodOperator(namespace='sophia-airflow',
    image="847029211010.dkr.ecr.ap-southeast-2.amazonaws.com/sophia/sophia-inventory-etl",
    cmds=["python","snowflake_daily_task.py"],
    arguments=["MR2", 'DF_UDT_SKUPROJSTATIC'],
    name="task-inventory-etl-df-udt-skuprojstatic",
    is_delete_operator_pod=True,
    task_id="task-inventory-etl-df-udt-skuprojstatic",
    image_pull_policy='Always',
    get_logs=True,
    trigger_rule='none_failed_or_skipped',
    dag=DAG_ID)


# slack notification
'''t4 = PythonOperator(
    namespace='sophia-airflow',
    task_id='task-cleanup-success-alert',
    python_callable=task_cleanup,
    provide_context=True,
    on_success_callback=send_success_notification,
    dag=DAG_ID)

# Mail alert
t5 = PythonOperator(
    namespace='sophia-airflow',
    task_id='pipeline-completed-mail-alert',
    python_callable=task_cleanup,
    provide_context=True,
    on_success_callback=send_success_mail_alerts,
    dag=DAG_ID)
'''
t1 >> t2_check_tracker_file >> [t2_poke_tracker_file, t2_file_present] >> t3

logger.info("Done!!")