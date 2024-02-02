#  Copyright 2023 Amazon.com and its affiliates; all rights reserved.
#  This file is Amazon Web Services Content and may not be duplicated or distributed without permission.

import json

import aws_cdk as cdk

from infra.stacks.main_stack import AppStack
from cdk_nag import AwsSolutionsChecks, NagSuppressions


def read_config():
    """read configuration in config.json"""
    with open("params-config.json", "r", encoding="utf-8") as json_file:
        config = json.load(json_file)
    return config


config_map = read_config()


app = cdk.App()
stack = AppStack(
    app,
    config_map["construct_id"],
    config_map
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.
    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.
    # env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
)
cdk.Aspects.of(app).add(AwsSolutionsChecks())

NagSuppressions.add_stack_suppressions(
    stack,
    [
        {
            "id": "AwsSolutions-VPC7",
            "reason": "vpc does not need a flow log in this app, please check project report",
        },
        {
            "id": "AwsSolutions-S1",
            "reason": "The bucket is for access log already",
        },
        {"id": "AwsSolutions-IAM5", "reason": "action or resource has been limited"},
        {
            "id": "AwsSolutions-ECS2",
            "reason": "need to pass some parameters to the task",
        },
    ],
)
app.synth()
