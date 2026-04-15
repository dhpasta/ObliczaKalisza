import pymysql

import boto3
import json
from botocore.exceptions import ClientError

def connect_params(self):
    secret_name = "rds_pwd"
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

    return pymysql.connect(
        host = rds_credentials["db_hostname"],
        user = rds_credentials["db_username"],
        password = rds_credentials["db_password"],
        port = rds_credentials["db_port"],
        db = rds_credentials["db_name"]
    )


