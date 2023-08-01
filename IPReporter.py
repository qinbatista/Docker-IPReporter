from math import fabs
import os
import time
import requests
import base64
import threading
import uuid
import subprocess
from socket import *
from datetime import datetime
import sys


class DDNSClient:
    def __init__(self, google_username, google_password, client_domain_name, server_domain_name):
        # configuration for different reporter from google domain
        self.__google_username = google_username
        self.__google_password = google_password
        self._my_domain = "client.example.com"

        # system variables
        # https://domains.google.com/checkip banned by Chinese GFW
        self.__file_path = "/root/logs.txt"
        # self.__file_path = "/Users/qin/Desktop/logs.txt"
        self.__target_server = "server.example.com"
        self._get_ip_website = "https://checkip.amazonaws.com"
        self._can_connect = 0
        self.__ip = ""

    def _ping_server_thread(self):
        thread_refresh = threading.Thread(
            target=self.__ping_server, name="t1", args=())
        thread_refresh.start()

    def __ping_server(self):
        while True:
            try:
                # Ping the target server
                process = subprocess.Popen(f"ping -c 1 {self.__target_server}", stdout=subprocess.PIPE, universal_newlines=True, shell=True)
                process.wait()

                # Check the result of the ping command
                if process.returncode == 0:
                    self._can_connect = 1
                    self.__log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][ping_server][ping -c 1 {self.__target_server}]{self._can_connect}")
                else:
                    self._can_connect = 0
                    self.__log(f"[{datetime.now().strftime('^%Y-%m-%d %H:%M:%S')}][ping_server][ping -c 1 {self.__target_server}]{self._can_connect}")

                # Wait for 1 minute before pinging again
                time.sleep(60)
            except Exception as e:
                self.__log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][ping_server]Error:{str(e)}")

    def _update_this_server_thread(self):
        thread_refresh = threading.Thread(
            target=self.__update_this_server, name="t1", args=())
        thread_refresh.start()

    def __update_this_server(self):
        udpClient = socket(AF_INET, SOCK_DGRAM)
        while True:
            try:
                this_docker_ip = self.__get_host_ip()
                udpClient.sendto((f"{gethostbyname(self.__target_server)},{str(self._can_connect)},{self.__google_username}:{self.__google_password},{self._my_domain}").encode(
                    encoding="utf-8"), (self.__target_server, 7171))
                self.__log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][update_this_server]Updated to server={gethostbyname(self.__target_server)}, {self.__target_server}: reachable={self._can_connect} message: {this_docker_ip},{str(self._can_connect)},{self.__google_username}:{self.__google_password},{self._my_domain}")
                time.sleep(60)
            except Exception as e:
                self.__log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][update_this_server]Error: {str(e)}")

    def __log(self, result):
        with open(self.__file_path, "a+") as f:
            f.write(result+"\n")
        if os.path.getsize(self.__file_path) > 1024*128:
            with open(self.__file_path, "r") as f:
                content = f.readlines()
                os.remove(self.__file_path)

    def __get_host_ip(self):
        self.__ip = ""
        try:
            self.__ip = requests.get(self._get_ip_website).text.strip()
        except Exception as e:
            self.__log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][get_host_ip]Error: {str(e)}")
        return self.__ip


if __name__ == '__main__':
    if len(sys.argv) >= 4:
        google_username = sys.argv[0]
        google_password = sys.argv[1]
        client_domain_name = sys.argv[2]
        server_domain_name = sys.argv[3]

    ss = DDNSClient(google_username, google_password, client_domain_name, server_domain_name)
    ss._ping_server_thread()
    ss._update_this_server_thread()
