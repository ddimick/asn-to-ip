FROM python:3.7-alpine

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY asn-to-ip.py ./

EXPOSE 5000

ENTRYPOINT ["python", "/app/asn-to-ip.py"]
