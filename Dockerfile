FROM python:3.7-alpine

RUN apk --no-cache add \
    shadow \
    supervisor \
    curl

ENV PORT=5000 \
    IP=0.0.0.0

EXPOSE ${PORT}

HEALTHCHECK --interval=30s \
            --timeout=30s \
            --start-period=5s \
            --retries=3 \
            CMD curl -f http://${IP}:${PORT}/ || exit 1

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache -r requirements.txt

COPY asn-to-ip.py ./

ARG USER=docker
ARG USER_UID=1000
ARG USER_GID=1000

RUN groupadd --gid ${USER_GID} ${USER} \
 && useradd --system --uid ${USER_UID} --gid ${USER_GID} -M -d / -s /sbin/nologin ${USER}

RUN echo -e "[supervisord]\n\
user=root\n\
nodaemon=true\n\
logfile=/var/log/supervisord.log\n\
pidfile=/var/run/supervisord.pid\n\
childlogdir=/var/log/\n\
logfile_maxbytes=50MB\n\
logfile_backups=10\n\
loglevel=error\n\
\n\
[program:asn-to-ip]\n\
user=${USER}\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\
command=python /app/asn-to-ip.py --daemon --ip %(ENV_IP)s --port %(ENV_PORT)s"\
> /etc/supervisord.conf

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]