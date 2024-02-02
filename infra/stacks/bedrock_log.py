#  Copyright 2023 Amazon.com and its affiliates; all rights reserved.
#  This file is Amazon Web Services Content and may not be duplicated or distributed without permission.

import re

from constructs import Construct
from aws_cdk import aws_s3 as s3, aws_logs as logs, aws_iam as iam, RemovalPolicy

try:
    from aws_cdk import core as cdk
except ImportError:
    import aws_cdk as cdk


def filter_string(input_string):
    # This regular expression pattern matches any character that is NOT a lowercase letter or a dash.
    pattern = "[^a-z-]"

    # Replace all characters that do not match the pattern with an empty string.
    filtered_string = re.sub(pattern, "", input_string)

    return filtered_string


class BedrockLog(Construct):
    """
    This class will create the Bedrock related log resources.

    It will create the following resources:
        - AWS IAM role
        - AWS S3 bucket for logging: "amazon-bedrock-log-[ACCOUNT_ID]-[REGION]"
        - AWS cloudwatch log group： /aws/bedrock


    As of December 27, 2023, there are no available documents providing instructions on how to configure logging for individual applications. Consequently, the following instructions pertain to the setup of logging for all bedrock logs. Prior to proceeding, please ensure that you have not already configured logging.


    For more information on the setup, please refer to the documentation:
    https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html

    """

    def __init__(self, scope, construct_id: str) -> None:
        super().__init__(scope, f"BedrockLog")

        bucket = self._create_log_bucket()

        cdk.CfnOutput(
            self,
            "BucketOutput",
            value=bucket.bucket_name,
            description="Bedrock Log Bucket",
        )

        log_group = self._create_log_group()

        cdk.CfnOutput(
            self,
            "LogGroupOutput",
            value=log_group.log_group_name,
            description="Bedrock Log Group",
        )

        self.role = self._create_iam_role(log_group.log_group_name)

        cdk.CfnOutput(
            self,
            "RoleArnOutput",
            value=self.role.role_arn,
            description="Bedrock Log Role ARN",
        )

    def _create_iam_role(self, log_group_name):
        policy_document = iam.PolicyDocument(
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["logs:CreateLogStream", "logs:PutLogEvents"],
                    resources=[
                        f"arn:aws:logs:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:log-group:{log_group_name}:log-stream:aws/bedrock/modelinvocations"
                    ],
                )
            ]
        )

        role = iam.Role(
            self,
            "Role",
            assumed_by=iam.ServicePrincipal(
                "bedrock.amazonaws.com",
                conditions={
                    "StringEquals": {"aws:SourceAccount": cdk.Aws.ACCOUNT_ID},
                    "ArnLike": {
                        "aws:SourceArn": f"arn:aws:bedrock:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:*"
                    },
                },
            ),
            inline_policies={"bedrock-log-policy": policy_document},
        )
        return role

    def _create_log_group(self):
        log_group = logs.LogGroup(
            self,
            "LogGroup",
            log_group_name=f"/aws/bedrock",
            retention=logs.RetentionDays.ONE_WEEK,  # Set retention (optional)
            removal_policy=RemovalPolicy.DESTROY,
        )

        return log_group

    def _create_log_bucket(self):
        log_bucket = s3.Bucket(
            self,
            "Bucket",
            removal_policy=RemovalPolicy.DESTROY,
            encryption=s3.BucketEncryption.S3_MANAGED,
            bucket_name=f"amazon-bedrock-log-{cdk.Aws.ACCOUNT_ID}-{cdk.Aws.REGION}",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            auto_delete_objects=True,
            lifecycle_rules=[s3.LifecycleRule(expiration=cdk.Duration.days(7))],
        )

        log_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="AllowSSLRequestsOnly",
                effect=iam.Effect.DENY,
                actions=["s3:*"],
                conditions={"Bool": {"aws:SecureTransport": "false"}},
                principals=[iam.AnyPrincipal()],
                resources=[
                    log_bucket.arn_for_objects("*"),
                    log_bucket.bucket_arn,
                ],
            )
        )

        log_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="bedrock_only",
                effect=iam.Effect.ALLOW,
                actions=["s3:PutObject"],
                principals=[iam.ServicePrincipal("bedrock.amazonaws.com")],
                conditions={
                    "StringEquals": {"aws:SourceAccount": cdk.Aws.ACCOUNT_ID},
                    "ArnLike": {
                        "aws:SourceArn": f"arn:aws:bedrock:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:*"
                    },
                },
                resources=[
                    log_bucket.arn_for_objects(
                        f"AWSLogs/{cdk.Aws.ACCOUNT_ID}/BedrockModelInvocationLogs/*"
                    ),
                ],
            )
        )

        return log_bucket
