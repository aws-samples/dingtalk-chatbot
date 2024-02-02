#  Copyright 2023 Amazon.com and its affiliates; all rights reserved.
#  This file is Amazon Web Services Content and may not be duplicated or distributed without permission.

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../dingtalk_app"))

import pytest
from unittest.mock import patch, MagicMock

from dingtalk_stream import CallbackMessage, ChatbotMessage, AckMessage, TextContent
from dingtalk_app.app import CardBotHandler, WELCOME_MESSAGE


# Mock for the callback message
@pytest.fixture
def callback_message():
    callback = MagicMock(spec=CallbackMessage)

    callback.data = {
        "msgtype": "text",
        "text": {"content": "hi"},
        "senderNick": "test_staff",
        "conversationId": "test_conversation",
    }
    callback.headers = {
        "app_id": "test_app",
        "connection_id": "test_connection",
        "content_type": "application/json",
        "message_id": "test_message_id",
        "time": 1703741384512,
        "topic": "/v1.0/im/bot/messages/get",
        "extensions": {},
    }
    return callback


@pytest.mark.parametrize(
    "model_id",
    ["anthropic.claude-v1"],
)
# Test process method help command
@patch("chatbot.bedrock_chatbot.Chatbot")
def test_process_help_command(mock_chatbot, callback_message, model_id):
    logger = MagicMock()
    handler = CardBotHandler(logger, model_id)
    callback_message.data["text"] = {"content": "help"}

    # Use the mock for the reply_text method
    with patch.object(handler, "reply_text") as mock_reply_text:
        status, message = handler.process(callback_message)

    # Assert the function returns the correct status and message
    assert status == AckMessage.STATUS_OK
    assert message == "OK"


@pytest.mark.parametrize(
    "model_id",
    ["anthropic.claude-v1"],
)
@patch("chatbot.bedrock_chatbot.Chatbot")
def test_process_reset_command(mock_chatbot, callback_message, model_id):
    logger = MagicMock()
    handler = CardBotHandler(logger, model_id)
    callback_message.data["text"] = {"content": "reset"}

    # Patch the reply_text method
    with patch.object(handler, "reply_text") as mock_reply_text:
        status, message = handler.process(callback_message)

    # Assert the process function returns the correct status and message
    assert status == AckMessage.STATUS_OK
    assert message == "OK"


# More tests can be written for other parts of the CardBotHandler class and other functions.
