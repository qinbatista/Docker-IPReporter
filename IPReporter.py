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
        self.__target_server_v4 = server_domain_name
        self.__target_server_v6 = server_domain_name
        self.__file_path = "/ipreporter.txt"

        # https://domains.google.com/checkip banned by Chinese GFW
        self._get_ipv4_website = "https://checkip.amazonaws.com"
        self._get_ipv6_website = "https://api6.ipify.org"
        self._can_connect = 0
        self.__log(f"google_username={google_username},google_password={google_password},client_domain_name={client_domain_name}, server_domain_name={server_domain_name}")
        self.__log(f"this_docker_ipv4={self.__get_current_ipv4()},this_docker_ipv6={self.__get_current_ipv6()}")

    def _ping_server_thread(self):
        thread_refresh = threading.Thread(target=self.__ping_server, name="t1", args=())
        thread_refresh.start()

    def __ping_server(self):
        while True:
            try:
                # Ping the target server
                process = subprocess.Popen(f"ping -c 1 {self.__target_server_v4}", stdout=subprocess.PIPE, universal_newlines=True, shell=True)
                process.wait()

                # Check the result of the ping command
                if process.returncode == 0:
                    self._can_connect = 1# can reach the server
                else:
                    self._can_connect = 0# cannot reach the server
                self.__log(f"[{datetime.now().strftime('^%Y-%m-%d %H:%M:%S')}][ping_server][ping -c 1 {self.__target_server_v4}]{self._can_connect}")

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
                this_docker_ipv4 = self.__get_current_ipv4()
                this_docker_ipv6 = self.__get_current_ipv6()
                udpClient.sendto((f"{gethostbyname(self.__target_server_v4)},{str(self._can_connect)},{self.__google_username}:{self.__google_password},{self._my_domain},v4").encode(encoding="utf-8"), (self.__target_server_v4, 7171))
                # udpClient.sendto((f"{gethostbyname(self.__target_server_v4)},{str(self._can_connect)},{self.__google_username}:{self.__google_password},{self._my_domain},v6").encode(encoding="utf-8"), (self.__target_server_v6, 7171))
                self.__log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][update_this_server]Updated to server={gethostbyname(self.__target_server_v4)}, {self.__target_server_v4}: reachable={self._can_connect} message: {this_docker_ipv4},{str(self._can_connect)},{self.__google_username}:{self.__google_password},{self._my_domain}")
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


    def __get_current_ipv6(self):
        try:
            response = requests.get(self._get_ipv6_website, timeout=5)
            response.raise_for_status()  # Raises an HTTPError for bad HTTP responses
            return response.text.strip()
        except requests.exceptions.HTTPError as errh:
            self.__log(f"[get_host_ipv6] HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            self.__log(f"[get_host_ipv6] Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            self.__log(f"[get_host_ipv6] Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            self.__log(f"[get_host_ipv6] Request Exception: {err}")
        return None

    def __get_current_ipv4(self):
        try:
            response = requests.get(self._get_ipv4_website,timeout=5)
            response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
            return response.text.strip()
        except requests.exceptions.HTTPError as errh:
            self.__log(f"[get_host_ip] HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            self.__log(f"[get_host_ip] Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            self.__log(f"[get_host_ip] Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            self.__log(f"[get_host_ip] Request Exception: {err}")
        return ""


if __name__ == '__main__':
    google_username = os.environ["GOOGLE_USERNAME"]
    google_password = os.environ["GOOGLE_PASSWORD"]
    client_domain_name = os.environ["CLIENT_DOMAIN_NAME"]
    server_domain_name = os.environ["SERVER_DOMAIN_NAME"]

    ss = DDNSClient(google_username, google_password, client_domain_name, server_domain_name)
    ss._ping_server_thread()
    ss._update_this_server_thread()
