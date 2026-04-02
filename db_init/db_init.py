import pymysql

import boto3
import json
from botocore.exceptions import ClientError

secret_name = "rds-pwd"
region_name = "eu-west-1"

# Create a Secrets Manager client
session = boto3.session.Session()
client = session.client(
    service_name='secretsmanager',
    region_name=region_name
)

try:
    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )
except ClientError as e:
    # For a list of exceptions thrown, see
    # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    raise e

secret = get_secret_value_response['SecretString']
rds_credentials = json.loads(secret)


# Establish a connection to the MySQL server
conn = pymysql.connect(
    host = rds_credentials["db_hostname"],
    user = rds_credentials["db_username"],
    password = rds_credentials["db_password"],
    port = rds_credentials["db_port"]
)

# Create a cursor to execute queries
cursor = conn.cursor()

# Open and read the SQL file
with open('data.sql', 'r') as file:
    sql_queries = file.read()

# Split the SQL file content into individual queries
queries = sql_queries.split(';')

# Iterate over the queries and execute them
for query in queries:
    try:
        if query.strip() != '':
            cursor.execute(query)
            conn.commit()
            print("Query executed successfully!")
    except Exception as e:
        print("Error executing query:", str(e))

# Close the cursor and the database connection
cursor.close()
conn.close()
