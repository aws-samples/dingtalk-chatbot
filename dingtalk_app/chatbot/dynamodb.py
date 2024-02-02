#  Copyright 2023 Amazon.com and its affiliates; all rights reserved.
#  This file is Amazon Web Services Content and may not be duplicated or distributed without permission.

import logging
from typing import TYPE_CHECKING, Dict, List, Optional

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import (
    BaseMessage,
    message_to_dict,
    messages_from_dict,
    messages_to_dict,
)
from boto3.session import Session
import time

# if TYPE_CHECKING:
#     from boto3.session import Session

logger = logging.getLogger(__name__)


class DynamoDBChatMessageHistory(BaseChatMessageHistory):
    """Chat message history that stores history in AWS DynamoDB.

    This class expects that a DynamoDB table exists with name `table_name`

    Args:
        table_name: name of the DynamoDB table
        session_id: arbitrary key that is used to store the messages
            of a single chat session.
        endpoint_url: URL of the AWS endpoint to connect to. This argument
            is optional and useful for test purposes, like using Localstack.
            If you plan to use AWS cloud service, you normally don't have to
            worry about setting the endpoint_url.
        primary_key_name: name of the primary key of the DynamoDB table. This argument
            is optional, defaulting to "SessionId".
        key: an optional dictionary with a custom primary and secondary key.
            This argument is optional, but useful when using composite dynamodb keys, or
            isolating records based off of application details such as a user id.
            This may also contain global and local secondary index keys.
        kms_key_id: an optional AWS KMS Key ID, AWS KMS Key ARN, or AWS KMS Alias for
            client-side encryption
    """

    def __init__(
        self,
        table_name: str,
        session_id: str,
        endpoint_url: Optional[str] = None,
        primary_key_name: str = "SessionId",
        limited_item_count: Optional[int] = 10,
        key: Optional[Dict[str, str]] = None,
        boto3_session: Optional[Session] = None,
        kms_key_id: Optional[str] = None,
    ):
        if boto3_session:
            client = boto3_session.resource("dynamodb", endpoint_url=endpoint_url)
        else:
            try:
                import boto3
            except ImportError as e:
                raise ImportError(
                    "Unable to import boto3, please install with `pip install boto3`."
                ) from e
            if endpoint_url:
                client = boto3.resource("dynamodb", endpoint_url=endpoint_url)
            else:
                client = boto3.resource("dynamodb")
        self.table = client.Table(table_name)
        self.session_id = session_id
        self.key: Dict = key or {primary_key_name: session_id}
        self.primary_key_name = primary_key_name
        self.limited_item_count = limited_item_count

        if kms_key_id:
            try:
                from dynamodb_encryption_sdk.encrypted.table import EncryptedTable
                from dynamodb_encryption_sdk.identifiers import CryptoAction
                from dynamodb_encryption_sdk.material_providers.aws_kms import (
                    AwsKmsCryptographicMaterialsProvider,
                )
                from dynamodb_encryption_sdk.structures import AttributeActions
            except ImportError as e:
                raise ImportError(
                    "Unable to import dynamodb_encryption_sdk, please install with "
                    "`pip install dynamodb-encryption-sdk`."
                ) from e

            actions = AttributeActions(
                default_action=CryptoAction.DO_NOTHING,
                attribute_actions={"History": CryptoAction.ENCRYPT_AND_SIGN},
            )
            aws_kms_cmp = AwsKmsCryptographicMaterialsProvider(key_id=kms_key_id)
            self.table = EncryptedTable(
                table=self.table,
                materials_provider=aws_kms_cmp,
                attribute_actions=actions,
                auto_refresh_table_indexes=False,
            )

    @property
    def messages(self) -> List[BaseMessage]:  # type: ignore
        """Retrieve the messages from DynamoDB"""
        try:
            from botocore.exceptions import ClientError
        except ImportError as e:
            raise ImportError(
                "Unable to import botocore, please install with `pip install botocore`."
            ) from e

        response = None
        try:
            response = self.table.get_item(Key=self.key)
        except ClientError as error:
            if error.response["Error"]["Code"] == "ResourceNotFoundException":
                logger.warning("No record found with session id: %s", self.session_id)
            else:
                logger.error(error)

        if response and "Item" in response:
            items = response["Item"]["History"][-1 * self.limited_item_count :]
        else:
            items = []

        messages = messages_from_dict(items)
        return messages

    @property
    def all_messages(self) -> List[BaseMessage]:  # type: ignore
        """Retrieve the messages from DynamoDB"""
        try:
            from botocore.exceptions import ClientError
        except ImportError as e:
            raise ImportError(
                "Unable to import botocore, please install with `pip install botocore`."
            ) from e

        response = None
        try:
            response = self.table.get_item(Key=self.key)
        except ClientError as error:
            if error.response["Error"]["Code"] == "ResourceNotFoundException":
                logger.warning("No record found with session id: %s", self.session_id)
            else:
                logger.error(error)

        if response and "Item" in response:
            items = response["Item"]["History"]
        else:
            items = []

        messages = messages_from_dict(items)
        return messages

    def add_message(self, message: BaseMessage) -> None:
        """Append the message to the record in DynamoDB"""
        try:
            from botocore.exceptions import ClientError
        except ImportError as e:
            raise ImportError(
                "Unable to import botocore, please install with `pip install botocore`."
            ) from e

        messages = messages_to_dict(self.all_messages)
        _message = message_to_dict(message)
        messages.append(_message)

        try:
            self.table.put_item(Item={**self.key, "History": messages})
        except ClientError as err:
            logger.error(err)

    def clear(self) -> None:
        """Clear session memory from DynamoDB"""
        try:
            from botocore.exceptions import ClientError
        except ImportError as e:
            raise ImportError(
                "Unable to import botocore, please install with `pip install botocore`."
            ) from e

        try:
            # Backup the conversation
            response = self.table.get_item(Key=self.key)
            current_timestamp = str(int(time.time() * 1000))
            backup_session_id = self.session_id + "#" + current_timestamp
            if response and "Item" in response:
                response["Item"]["SessionId"] = backup_session_id
                self.table.put_item(Item=response["Item"])

            # Delete current conversation
            self.table.delete_item(Key=self.key)
        except ClientError as err:
            logger.error(err)
