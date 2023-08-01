FROM python:3-slim



ARG google_username
ARG google_password
ARG client_domain_name
ARG server_domain_name


ADD * /
RUN apt-get update
RUN apt-get -y install iputils-ping
RUN pip3 install -r requirements.txt

WORKDIR /root
CMD ["python3","/IPReporter.py",google_username,google_password,client_domain_name,server_domain_name]
