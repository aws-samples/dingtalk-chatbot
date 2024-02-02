#  Copyright 2023 Amazon.com and its affiliates; all rights reserved.
#  This file is Amazon Web Services Content and may not be duplicated or distributed without permission.

from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_logs as logs,
    aws_iam as iam,
    aws_secretsmanager as sm,
    aws_dynamodb,
)
import os

try:
    from aws_cdk import core as cdk
except ImportError:
    import aws_cdk as cdk


class ECSService(Construct):
    def __init__(
        self,
        scope,
        construct_id,
        vpc: ec2.Vpc,
        ddb_table: aws_dynamodb.Table,
        config_map: dict,
    ) -> None:
        super().__init__(scope, "ECSService")
        self.config_map = config_map
        self._create_ecs(construct_id, vpc, ddb_table)

    def _create_ecs(self, construct_id, vpc, ddb_table):
        secret = sm.Secret.from_secret_name_v2(
            self,
            "DINGTALK_SETTING",
            self.config_map["dingtalk_app_credential_secret_name"],
        )

        cluster = ecs.Cluster(self, "ECSCluster", vpc=vpc, container_insights=True)

        fargate_task_definition = ecs.FargateTaskDefinition(self, "ECSTaskDef")

        fargate_task_definition.add_container(
            "ECSContainer",
            image=ecs.ContainerImage.from_asset("./dingtalk_app"),
            memory_limit_mib=512,
            cpu=256,
            docker_labels={"docker_name": construct_id},
            logging=ecs.LogDriver.aws_logs(
                stream_prefix="dingtalk_app", log_retention=logs.RetentionDays.ONE_WEEK
            ),
            # health_check=ecs.HealthCheck(
            #     command=["CMD-SHELL", "curl -f http://localhost/ || exit 1"],
            #     # the properties below are optional
            #     interval=cdk.Duration.minutes(5),
            #     retries=10,
            #     start_period=cdk.Duration.minutes(5),
            #     timeout=cdk.Duration.minutes(1),
            # ),
            environment={
                "DB_Secret": "",
                "DINGTALK_SETTING": self.config_map[
                    "dingtalk_app_credential_secret_name"
                ],
                "DINGTALK_SETTING_REGION": os.environ.get("CDK_DEPLOY_REGION", os.environ["CDK_DEFAULT_REGION"]),
                "DDB_TABLE_NAME": ddb_table.table_name,
                "BEDROCK_MODEL_ID": self.config_map["bedrock_model_id"],
                "INPUT_HISTORY_CONVERSATION_COUNT": self.config_map[
                    "input_history_conversation_count"
                ],
            },
        )

        service = ecs.FargateService(
            self,
            "FargateService",
            cluster=cluster,
            task_definition=fargate_task_definition,
            capacity_provider_strategies=[
                ecs.CapacityProviderStrategy(capacity_provider="FARGATE", weight=1)
            ],
            desired_count=1,
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True),
        )

        service.task_definition.add_to_task_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                resources=[
                    f"arn:{cdk.Aws.PARTITION}:bedrock:{cdk.Aws.REGION}::foundation-model/*",
                    f"arn:{cdk.Aws.PARTITION}:bedrock:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:guardrail/*",
                ],
            )
        )

        # Add DDB Table CRUD access.
        service.task_definition.add_to_task_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:Scan",
                    "dynamodb:Query",
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:BatchWriteItem",
                    "dynamodb:BatchGetItem",
                    "dynamodb:DescribeTable",
                    "dynamodb:List*",
                ],
                resources=[ddb_table.table_arn],
            )
        )

        secret.grant_read(service.task_definition.task_role)
