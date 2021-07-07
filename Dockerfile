FROM python:3

COPY main.py /
COPY core/ core/
COPY lib/ lib/

RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir \
    boto3==1.17.105 \
    timeloop==1.0.2 \
    expiringdict==1.2.1 \
    && pip3 check

CMD [ "python3", "./main.py", "--log-level=debug", "--perf-log-level=debug" ]