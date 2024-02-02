#  Copyright 2023 Amazon.com and its affiliates; all rights reserved.
#  This file is Amazon Web Services Content and may not be duplicated or distributed without permission.

import pytest
import os
import json
from dingtalk_app.chatbot.settings import load_dingtalk_app_setting


def read_config():
    # current_dir = os.getcwd()  # 获取当前工作目录
    # parent_dir = os.path.dirname(current_dir)  # 获取当前目录的上一级目录
    #
    # print(parent_dir)
    """read configuration in config.json"""
    with open("params-config.json", "r", encoding="utf-8") as json_file:
        config = json.load(json_file)
    return config


config_map = read_config()


@pytest.mark.parametrize(
    "secret_name",
    ["dingtalk_app_credential"],
)
@pytest.mark.parametrize(
    "region_name",
    ["us-west-2"],
)
def test_get_dingtalk_settings(secret_name, region_name):
    app_key, app_secret = load_dingtalk_app_setting(
        config_map["dingtalk_app_credential_secret_name"], region_name
    )

    # assert app_key.startswith("dingxct5ui")
    # assert app_secret.startswith("3u_e7gBNrg")
