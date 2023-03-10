FROM python:slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

RUN mkdir /secure-connect && mkdir /bundles

CMD [ "python3", "app.py"]