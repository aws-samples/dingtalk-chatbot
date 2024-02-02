#  Copyright 2023 Amazon.com and its affiliates; all rights reserved.
#  This file is Amazon Web Services Content and may not be duplicated or distributed without permission.

from aws_cdk import (
    Duration,
    Stack,
)

try:
    from aws_cdk import core as cdk
except ImportError:
    import aws_cdk as cdk

from constructs import Construct
from .vpc_component import VPC
from .ecs_component import ECSService
from .ddb_stack import DDB
from .bedrock_log import BedrockLog


class AppStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, config_map: dict, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = VPC(self, construct_id)
        ddb = DDB(self, construct_id)
        ECSService(
            self, construct_id, vpc.get_vpc(), ddb.get_conversation_table(), config_map
        )

        enable_bedrock_log = config_map.get("enable_bedrock_log", False)
        if enable_bedrock_log:
            BedrockLog(self, construct_id)
