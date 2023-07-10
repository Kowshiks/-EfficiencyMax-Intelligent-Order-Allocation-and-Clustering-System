FROM python:3.8

WORKDIR /test-ui 

COPY . /test-ui

RUN pip install -r requirements.txt

EXPOSE 5000

CMD python ./app_main.py


