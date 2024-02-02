#  Copyright 2023 Amazon.com and its affiliates; all rights reserved.
#  This file is Amazon Web Services Content and may not be duplicated or distributed without permission.

import json

import boto3

from botocore.exceptions import ClientError


def load_dingtalk_app_setting(secret_name: str, region_name: str) -> tuple:
    """
    load Dingtalk app secret and Key from secret manager

    # If you need more information about configurations
    # or implementing the sample code, visit the AWS docs:
    # https://aws.amazon.com/developer/language/python/
    :param secret_name: secret name in secrets manager
    :param region_name: secret manager region name

    :return: (AppKey, AppSecret)
    """
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        # For a list of exceptions thrown
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response["SecretString"]

    json_secret = json.loads(secret)

    return json_secret["AppKey"], json_secret["AppSecret"]
