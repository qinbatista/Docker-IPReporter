FROM python:3-slim

ADD * /
RUN apt-get update
RUN apt-get -y install iputils-ping
RUN pip3 install -r requirements.txt

WORKDIR /root
CMD ["python3", "/PingList.py"]
