from math import fabs
import os
import time
import requests
import threading
import subprocess
from socket import *
from datetime import datetime
import platform


class PingList:
    def __init__(self):
        self.__target_server_domain_name_list = ["timov4.qinyupeng.com"]
        self.__file_path = "/root/logs.txt"
        if platform.system() == 'Darwin':
            self.__file_path = "/Users/qin/Desktop/logs.txt"
        # https://domains.google.com/checkip banned by Chinese GFW
        self._get_ip_website = "https://checkip.amazonaws.com"
        self._can_connect = 0
        self.__ip = ""
        print(f"this_docker_ipv4={self.__get_current_ipv4()},this_docker_ipv6={self.__get_current_ipv6()}")

    def __ping4_server(self, target_domain_name):
        while True:
            try:
                # Ping the target server
                process = subprocess.Popen(f"ping -c 1 {target_domain_name}", stdout=subprocess.PIPE, universal_newlines=True, shell=True)
                process.wait()

                # Check the result of the ping command
                if process.returncode == 0:
                    self._can_connect = 1
                    self.__log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][ping_server][ping -c 1 {target_domain_name}]{self._can_connect}")
                else:
                    self._can_connect = 0
                    self.__log(f"[{datetime.now().strftime('^%Y-%m-%d %H:%M:%S')}][ping_server][ping -c 1 {target_domain_name}]{self._can_connect}")

                return self._can_connect
            except Exception as e:
                self.__log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][ping_server]Error:{str(e)}")

    def _update_this_server_thread(self):
        thread_refresh = threading.Thread(target=self.__update_this_server, name="t1", args=())
        thread_refresh.start()

    def __update_this_server(self):
        udpClient = socket(AF_INET, SOCK_DGRAM)
        while True:
            for target_domain in self.__target_server_domain_name_list:
                try:
                    can_connect = self.__ping4_server(target_domain)
                    self.__log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][update_this_server]IP: {target_domain}")
                    self.__log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][update_this_server]IP: {(target_domain)}")
                    self.__target_server_ipv4 = gethostbyname(target_domain)
                    self.__target_server_ipv6 = gethostbyname(target_domain)#fake ipv6
                    this_docker_ipv4 = self.__get_current_ipv4()
                    this_docker_ipv6 = self.__get_current_ipv6()
                    # print(f"this_docker_ipv4={this_docker_ipv4},this_docker_ipv6={this_docker_ipv6}")
                    udpClient.sendto((f"{self.__target_server_ipv4},{str(can_connect)}").encode(encoding="utf-8"), (self.__target_server_ipv4, 7171))
                    self.__log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][update_this_server]Updated to {self.__target_server_ipv4}, message: {this_docker_ipv4},{str(self._can_connect)}")
                    # udpClient.sendto((f"{self.__target_server_ipv6},{str(self._can_connect)}").encode(encoding="utf-8"), (self.__target_server_ipv6, 7171))
                    # self.__log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][update_this_server]Updated to {self.__target_server_ipv6}, message: {this_docker_ipv6},{str(self._can_connect)}")
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

    def __get_current_ipv4(self):
        self.__ip = ""
        try:
            self.__ip = requests.get(self._get_ip_website).text.strip()
        except Exception as e:
            self.__log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][get_host_ip]Error: {str(e)}")
        return self.__ip

    def __get_current_ipv6(self):
        try:
            return requests.get("https://api6.ipify.org", timeout=5).text
        except requests.exceptions.ConnectionError as ex:
            return None


if __name__ == '__main__':
    ss = PingList()
    # ss._ping_server_thread()
    ss._update_this_server_thread()
