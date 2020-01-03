FROM python:3.7-alpine

WORKDIR /app

COPY src/requirements.txt ./

RUN pip install -r requirements.txt

COPY src/asn-to-ip.py ./

ENTRYPOINT ["python", "/app/asn-to-ip.py"]
