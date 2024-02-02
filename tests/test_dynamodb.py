#  Copyright 2023 Amazon.com and its affiliates; all rights reserved.
#  This file is Amazon Web Services Content and may not be duplicated or distributed without permission.

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from langchain_core.messages import (
    BaseMessage,
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../dingtalk_app"))
from dingtalk_app.chatbot.dynamodb import DynamoDBChatMessageHistory


@pytest.mark.parametrize(
    "table_name",
    ["Ting-DingTalk-with-Bedrock_conversation_table"],
)
@pytest.mark.parametrize(
    "conversation_id",
    ["3c08003f-a2fd-11ee-8abb-8e1df9f23b"],
)
@pytest.mark.parametrize(
    "limited_item_count",
    [2],
)
def test_dynamodb(table_name, conversation_id, limited_item_count):
    logger = MagicMock()

    ddb_history = DynamoDBChatMessageHistory(
        table_name=table_name,
        session_id=conversation_id,
        limited_item_count=limited_item_count,
    )

    limited_messages = ddb_history.messages
    all_messages = ddb_history.all_messages

    ddb_history.clear()

    message: BaseMessage = BaseMessage(content="Hello?", type="human")
    ddb_history.add_message(message)
