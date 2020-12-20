import boto3
import configparser
import psycopg2
from sql_queries import table_queries

s3 = boto3.client('s3')
sns = boto3.client('sns')

create_sql = table_queries[0]
copy_sql = table_queries[1]


def create_table(cur, conn):
    """
    Create database table if it does not exist
    Include jsonb field
    """
    print('running query: ' + create_sql)
    cur.execute(str(create_sql))
    conn.commit()

def publish_sns(message):
    """
    Create SNS topic if it doesn't exist
    Publish message to SNS topic
    """
    topic = sns.create_topic(Name='message-from-lambda')
    topic_arn = topic['TopicArn']
    sns.publish(Message=message, TopicArn=topic_arn) 

def lambda_handler(event, context):
    """
    Main lambda function method
    Imports JSON file from S3 bucket into PostgreSQL database on RDS
    """
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    print('Importing file {} from S3 to PostgreSQL.'.format(key))

    config = configparser.ConfigParser()
    config.read('database.cfg')

    # Get file from S3
    local_path = '/tmp/' + key.split('/')[-1]
    s3.download_file(bucket_name, key, local_path)

    # Connect to RDS
    conn = psycopg2.connect("host={} dbname={} user={} password={}".format(*config['RDS'].values()))
    cur = conn.cursor()

    # Create table if necessary
    create_table(cur, conn)

    # Open file for copy and load into table
    f = open(local_path, "r")
    cur.copy_expert(copy_sql, f)
    conn.commit()
    conn.close()

    # Send notification
    msg = 'Imported {} to PostgreSQL on RDS.'.format(key)
    publish_sns(msg)

    