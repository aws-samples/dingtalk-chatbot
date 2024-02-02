#  Copyright 2023 Amazon.com and its affiliates; all rights reserved.
#  This file is Amazon Web Services Content and may not be duplicated or distributed without permission.

from dingtalk_app.chatbot.bedrock_chatbot import Chatbot
import pytest


@pytest.mark.parametrize(
    "model_id",
    [
        "anthropic.claude-v2:1",
        # "meta.llama2-13b-chat-v1",
    ],
)
@pytest.mark.parametrize(
    "prompt",
    [
        "write me something about harry potter",
    ],
)
def test_ask_stream(model_id, prompt):
    try:
        chatbot = Chatbot(model_id)

        result = ""
        for chunk in chatbot.ask_stream(prompt):
            result += chunk

        print(f"{model_id} result: {result}")
    except Exception as e:
        raise pytest.fail("DID RAISE {0}".format(e))


@pytest.mark.parametrize(
    "model_id",
    [
        "meta.llama2-13b-chat-v1",
    ],
)
@pytest.mark.parametrize(
    "prompt",
    [
        "write me something about harry potter",
    ],
)
def test_ask_stream_not_supported_model(model_id, prompt):
    with pytest.raises(
        Exception, match="model_id meta.llama2-13b-chat-v1 is not supported"
    ) as exec_info:
        chatbot = Chatbot(model_id)

        result = ""
        for chunk in chatbot.ask_stream(prompt):
            result += chunk


@pytest.mark.parametrize(
    "model_id",
    [
        # "meta.llama2-13b-chat-v1",
        "anthropic.claude-v2:1",
    ],
)
def test_ask_stream_token_exception(model_id):
    with pytest.raises(
        Exception,
        # match="This model's maximum context length is 4096 tokens. Please reduce the length of the prompt",
        match="Member must have length less than or equal to 25000000",
    ) as exec_info:
        chatbot = Chatbot(model_id)

        chatbot.ask_stream("hello" * 10000000)

    print(exec_info)
