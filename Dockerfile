FROM python:3.7-alpine

WORKDIR /app

COPY src ./

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "/app/asn-to-ip.py"]
