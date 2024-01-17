FROM python:3-slim

ARG google_username
ARG google_password
ARG client_domain_name
ARG server_domain_name

ENV GOOGLE_USERNAME="$google_username"
ENV GOOGLE_PASSWORD="$google_password"
ENV CLIENT_DOMAIN_NAME="$client_domain_name"
ENV SERVER_DOMAIN_NAME="$server_domain_name"

ADD * /
RUN apt-get update
RUN apt-get -y install iputils-ping
RUN pip3 install -r requirements.txt

CMD ["python3", "/IPReporter.py", "$GOOGLE_USERNAME", "$GOOGLE_PASSWORD", "$CLIENT_DOMAIN_NAME", "$SERVER_DOMAIN_NAME"]
