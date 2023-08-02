from math import fabs
import os
import time
import requests
import threading
import subprocess
from socket import *
from datetime import datetime
import platform


class DDNSClient:
    def __init__(self, google_username, google_password, client_domain_name, server_domain_name):
        self.__google_username = google_username
        self.__google_password = google_password
        self._my_domain = client_domain_name
        self.__target_server = server_domain_name
        self.__file_path = "/root/logs.txt"
        print(f"google_username={google_username},google_password={google_password},client_domain_name={client_domain_name}, server_domain_name={server_domain_name}")
        print(f"this_docker_ipv4={self.__get_host_ip()},this_docker_ipv6={self.__get_current_ipv6()}")
        if platform.system() == 'Darwin':
            self.__file_path = "/Users/qin/Desktop/logs.txt"

        # https://domains.google.com/checkip banned by Chinese GFW
        self._get_ip_website = "https://checkip.amazonaws.com"
        self._can_connect = 0
        self.__ip = ""
        print(self.__get_current_ipv6())

    def _ping_server_thread(self):
        thread_refresh = threading.Thread(target=self.__ping_server, name="t1", args=())
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
        thread_refresh = threading.Thread(target=self.__update_this_server, name="t1", args=())
        thread_refresh.start()

    def __update_this_server(self):
        udpClient = socket(AF_INET, SOCK_DGRAM)
        while True:
            try:
                self.__log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][update_this_server]IP: {self.__target_server}")
                self.__log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][update_this_server]IP: {(self.__target_server)}")
                this_docker_ipv4 = self.__get_host_ip()
                this_docker_ipv6 = self.__get_current_ipv6()
                # print(f"this_docker_ipv4={this_docker_ipv4},this_docker_ipv6={this_docker_ipv6}")
                udpClient.sendto((f"{gethostbyname(self.__target_server)},{str(self._can_connect)},{self.__google_username}:{self.__google_password},{self._my_domain}").encode(encoding="utf-8"), (self.__target_server, 7171))
                self.__log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][update_this_server]Updated to server={gethostbyname(self.__target_server)}, {self.__target_server}: reachable={self._can_connect} message: {this_docker_ipv4},{str(self._can_connect)},{self.__google_username}:{self.__google_password},{self._my_domain}")
                time.sleep(60)
            except Exception as e:
                time.sleep(60)
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

    def __get_current_ipv6(self):
        """Get the current external IPv6 address or return None if no connection to the IPify service is possible"""
        try:
            return requests.get("https://api6.ipify.org", timeout=5).text
        except requests.exceptions.ConnectionError as ex:
            return None


if __name__ == '__main__':
    google_username = os.environ["GOOGLE_USERNAME"]
    google_password = os.environ["GOOGLE_PASSWORD"]
    client_domain_name = os.environ["CLIENT_DOMAIN_NAME"]
    server_domain_name = os.environ["SERVER_DOMAIN_NAME"]

    ss = DDNSClient(google_username, google_password, client_domain_name, server_domain_name)
    ss._ping_server_thread()
    ss._update_this_server_thread()
