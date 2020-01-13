FROM python:3.7-alpine

WORKDIR /app

COPY requirements.txt ./
COPY asn-to-ip.py ./

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "/app/asn-to-ip.py"]
