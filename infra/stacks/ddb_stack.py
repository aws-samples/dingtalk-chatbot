#  Copyright 2023 Amazon.com and its affiliates; all rights reserved.
#  This file is Amazon Web Services Content and may not be duplicated or distributed without permission.

from constructs import Construct
from aws_cdk import (
    aws_dynamodb,
)


try:
    from aws_cdk import core as cdk
except ImportError:
    import aws_cdk as cdk


class DDB(Construct):
    def __init__(self, scope, construct_id) -> None:
        super().__init__(scope, f"{construct_id}DDBTable")

        # conversation table
        self.conversation_table = aws_dynamodb.Table(
            self,
            "conversation_table",
            table_name=f"{construct_id}_conversation_table",
            partition_key=aws_dynamodb.Attribute(
                name="SessionId", type=aws_dynamodb.AttributeType.STRING
            ),
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=aws_dynamodb.TableEncryption.AWS_MANAGED,
            stream=aws_dynamodb.StreamViewType.NEW_IMAGE,
            point_in_time_recovery=True,
        )

    def get_conversation_table(self):
        return self.conversation_table
