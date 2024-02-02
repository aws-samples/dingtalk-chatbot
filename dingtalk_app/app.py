#  Copyright 2023 Amazon.com and its affiliates; all rights reserved.
#  This file is Amazon Web Services Content and may not be duplicated or distributed without permission.

import os
import logging
import time
import dingtalk_stream

from dingtalk_stream import AckMessage

from copy import deepcopy

from chatbot.templates import INTERACTIVE_CARD_JSON_SAMPLE
from chatbot.settings import load_dingtalk_app_setting
from chatbot.bedrock_chatbot import Chatbot
from chatbot.dynamodb import DynamoDBChatMessageHistory
from langchain.memory import ConversationBufferMemory
from datetime import datetime

# 影响调用钉钉开放平台接口频率，越小调用频率越高，建议设置大一点
STREAM_SIZE = 50
BUSY_MESSAGE = "Only one message at a time"
WELCOME_MESSAGE = """我是某某聊天机器人:
==========================
♻️ 重置 👉 重置带上下文聊天
❓ 帮助 👉 显示帮助信息
==========================
🚜 例：@我发送 空 或 帮助 将返回此帮助信息
"""


def setup_logger():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("dingtalk_bedrock")
    return logger


class CardBotHandler(dingtalk_stream.AsyncChatbotHandler):
    """
    接收回调消息。
    回复一个卡片，然后更新卡片的文本和图片。
    """

    def __init__(self, logger: logging.Logger, model_id):
        max_workers = os.cpu_count()
        super(CardBotHandler, self).__init__(max_workers=max_workers)
        self.logger = logger

        # Initialize chatbot
        self.chatbot = Chatbot(model_id=model_id)

    def bedrock_reply_stream(self, input_text, incoming_message, conversation_id):
        card = deepcopy(INTERACTIVE_CARD_JSON_SAMPLE)
        card["contents"][0]["id"] = f"text_{int(time.time() * 100)}"
        card_biz_id = None
        is_first_reply = True

        message_history = DynamoDBChatMessageHistory(
            table_name=os.environ.get("DDB_TABLE_NAME", "chatbot_conversation_table"),
            session_id=conversation_id,
            # Each conversation has 2 items in DDB table.
            limited_item_count=int(
                os.environ.get("INPUT_HISTORY_CONVERSATION_COUNT", "10")
            )
            * 2,
        )
        memory = ConversationBufferMemory(
            memory_key="history", chat_memory=message_history, return_messages=True
        )

        for i, query in enumerate(
            self.chatbot.ask_stream(
                input_text,
                role=incoming_message.sender_staff_id,
                convo_id=incoming_message.conversation_id,
                conversation_history=memory,
            )
        ):
            card["contents"][0]["text"] += query
            if i % STREAM_SIZE == 0:
                # 先回复一个文本卡片
                if is_first_reply:
                    card_biz_id = self.reply_card(
                        card,
                        incoming_message,
                        False,
                    )
                    is_first_reply = False
                self.update_card(
                    card_biz_id,
                    card,
                )

        if is_first_reply:
            card_biz_id = self.reply_card(
                card,
                incoming_message,
                False,
            )
        elif i % STREAM_SIZE != 0:
            self.update_card(
                card_biz_id,
                card,
            )

    def process(self, callback: dingtalk_stream.CallbackMessage):
        """
        多线程场景，process函数不要用 async 修饰
        :param message:
        :return:
        """

        incoming_message = dingtalk_stream.ChatbotMessage.from_dict(callback.data)
        input_text = incoming_message.text.content.strip()
        conversation_id = incoming_message.conversation_id.strip()

        self.logger.info(callback.headers)
        self.logger.info(callback.data)

        if input_text in ["", "帮助", "help"]:
            self.reply_text(
                WELCOME_MESSAGE,
                incoming_message,
            )
            return AckMessage.STATUS_OK, "OK"
        elif input_text in ["重置", "reset"]:
            message_history = DynamoDBChatMessageHistory(
                table_name=os.environ.get(
                    "DDB_TABLE_NAME", "chatbot_conversation_table"
                ),
                session_id=conversation_id,
            )
            message_history.clear()
            self.logger.info(f"message_history for {conversation_id} cleared.")
            self.reply_text(
                "会话已重置",
                incoming_message,
            )
            return AckMessage.STATUS_OK, "OK"

        try:
            self.bedrock_reply_stream(input_text, incoming_message, conversation_id)
        except Exception as e:
            self.logger.error(e)
            self.reply_text(
                "上下文过多,请输入'重置'清理后再尝试",
                incoming_message,
            )
            return AckMessage.STATUS_OK, "OK"

# Main Function
def main():
    logger = setup_logger()

    dingtalk_settings = os.environ.get("DINGTALK_SETTING", "dingtalk_app_credential")

    dingtalk_settings_region = os.environ.get("DINGTALK_SETTING_REGION", "us-west-2")

    bedrock_model_id = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-v1")

    logger.info(dingtalk_settings + "," + dingtalk_settings_region)

    app_key, app_secret = load_dingtalk_app_setting(
        dingtalk_settings, dingtalk_settings_region
    )

    credential = dingtalk_stream.Credential(app_key, app_secret)
    client = dingtalk_stream.DingTalkStreamClient(credential)

    client.register_callback_handler(
        dingtalk_stream.chatbot.ChatbotMessage.TOPIC,
        CardBotHandler(logger, bedrock_model_id),
    )
    client.start_forever()


# Run Application
if __name__ == "__main__":
    main()
