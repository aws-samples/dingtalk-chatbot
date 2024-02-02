# Dingtalk Chatbot Integration with Amazon Bedrock

## Description

DingTalk is a versatile communication and collaboration platform developed by Alibaba Group. It offers a wide range of features including instant messaging, video conferencing, task management, and more, making it a popular choice for businesses and teams to streamline their communication and
enhance productivity.

Amazon Bedrock is a fully managed service that offers a choice of high-performing foundation models (FMs) from leading AI companies like AI21 Labs, Anthropic, Cohere, Meta, Stability AI, and Amazon via a single API, along with a broad set of capabilities you need to build generative AI applications
with security, privacy, and responsible AI. Using Amazon Bedrock, you can easily experiment with and evaluate top FMs for your use case, privately customize them with your data using techniques such as fine-tuning and Retrieval Augmented Generation (RAG), and build agents that execute tasks using
your enterprise systems and data sources.

Integrating DingTalk with Amazon Bedrock enables businesses and teams to leverage the advanced language capabilities of Bedrock within the DingTalk ecosystem, enhancing communication, collaboration, and productivity by incorporating natural language processing and AI-driven interactions into
DingTalk's features.

## Deployment
1. Please follow docs/dingtalk-application.md create a DingTalk application.
2. Create a secret key in AWS Secrets Manager with below plaintext, and replace your own value for these two keys:
    `{"AppKey":"your-client-id","AppSecret":"your-client-secret"}`
2. Open an AWS Cloud9 environment, please select m5.large as the instance type.
3. Open Cloud9 IDE, run `git clone https://github.com/aws-samples/dingtalk-bedrock-chatbot.git` 
4. Open dingtalk-bedrock-chatbot/params-config.json, modify value of dingtalk_app_credential_secret_name to the key name you created in step 1.
5. ```Deploy with AWS CDK
    cd dingtalk-bedrock-chatbot
    python3 -m venv env
    source env/bin/activate
    pip3 install -r  requirements.txt
    cdk bootstrap
    cdk deploy
   ``` 
6. Test chatbot in your Dingtalk APP.

## Legal

During the launch of this prototype, you will install software (and dependencies) on the Amazon ECS instances launched in your account via stack creation. The software packages and/or sources you will install will be from the Amazon Linux distribution, as well as from third party sites. Below is the
list of such third party software, the source link, and the license link for each software. Please review and decide your comfort with installing these before continuing.

| Name                | Version | License                 |
|---------------------|---------|-------------------------|
| anthropic           | 0.8.0   | MIT License             |
| aws-cdk-lib         | 2.111.0 | Apache-2.0              |
| boto3               | 1.34.4  | Apache Software License |
| botocore            | 1.34.4  | Apache Software License |
| dingtalk-stream     | 0.15.2  | MIT License             |
| langchain           | 0.0.351 | MIT License             |
| langchain-community | 0.0.4   | MIT License             |
| langchain-core      | 0.1.1   | MIT License             |



## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
