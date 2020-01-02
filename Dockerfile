FROM python:3.7-alpine

RUN pip install Flask

COPY files/asn-to-ip.py /

WORKDIR /

ENTRYPOINT ["python", "asn-to-ip.py"]
