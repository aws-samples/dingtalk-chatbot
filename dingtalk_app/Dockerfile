#  Copyright 2023 Amazon.com and its affiliates; all rights reserved.
#  This file is Amazon Web Services Content and may not be duplicated or distributed without permission.


FROM public.ecr.aws/amazonlinux/amazonlinux:2023

ARG APP_HOME=/app


#install python 3.11
RUN cd ~/
RUN yum install gcc openssl-devel bzip2-devel libffi-devel zlib-devel wget tar gzip -y && yum clean all
RUN wget https://www.python.org/ftp/python/3.11.7/Python-3.11.7.tgz
RUN tar xzf Python-3.11.7.tgz
RUN cd Python-3.11.7 && ./configure --enable-optimizations && make install

RUN yum install python3-pip -y && yum clean all
RUN python3.11 -m pip install --upgrade pip

WORKDIR $APP_HOME

ENV LANG=en_US.UTF-8
ENV TZ=:/etc/localtime

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN echo $(pip list)

RUN echo $(python3.11 -v)

COPY app.py app.py
COPY chatbot chatbot

# EXPOSE 8501

ENTRYPOINT ["python3.11", "app.py"]

