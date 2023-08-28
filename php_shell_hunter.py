#!/usr/bin/env python3
# Author: Clarence Subia
# Date: 06/11/2023
# Usage: python3 php_shell_hunter.py --remote 192.168.1.100 --directory /var/www/html

import requests
import argparse
import paramiko

import sys
import json
import time
import subprocess
from datetime import datetime

# Define Colors to beautify print() outputs
G = "\033[92m"  # green
Y = "\033[93m"  # yellow
B = "\033[94m"  # blue
R = "\033[91m"  # red
W = "\033[0m"   # white

TIME_NOW = datetime.now().strftime("%H:%M:%S")

def parse_args():
    parser = argparse.ArgumentParser(description="Hunt PHP webshells on a specific directory.")
    parser.add_argument("-d", "--directory", metavar="", required=True, help="Target directory to find webshells.")
    parser.add_argument("-r", "--remote-host", metavar="", required=False, help="Target remote host.")
    parser.add_argument("-i", "--interval", metavar="", required=False, help="Time interval for file checking.", default=5, type=int)
    return parser.parse_args()


def server_connect(host):
    # If you prefer username and password, remove private_key* lines then add username and password parameters
    # under client.connect()
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        private_key_path = "/root/.ssh/id_rsa"
        private_key = paramiko.RSAKey.from_private_key_file(private_key_path)
        client.connect(hostname=host, username="clarence", pkey=private_key)
        return client
    except BlockingIOError as err:
        print(f"{R}An error occured:{W} {err}")
        sys.exit(1)
    

def local_shell_hunt(directory, interval=5):
    # Executes command in local machine
    # finds any .php file under the directory that contains any php functions defined below and was created or spawned in less than 24 hours.    
    # A directory checker is put in place. Exits out when said directory is not found
    command = f"find {directory} -type f -name '*.php' -mtime -1 | xargs egrep -rl \"(mail|fsocketopen|pfsocketopen|exec|system|passthru|eval|base64_decode) *\\(\""
    directory_stat = subprocess.run([f"ls -l {directory}"], shell=True, capture_output=True, text=True).returncode
    if directory_stat != 0:
        print(f"{R}[X] Error in checking directory {directory}.{W}")
        sys.exit(directory_stat)
        
    found_shells = []
    while True:
        start_interval = 0
        time.sleep(start_interval)
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        response = result.stdout
        if result.returncode == 0:
            file = response.split()[0].removesuffix(":")
            if file not in found_shells:
                found_shells.append(file)
                send_slack(file=file)
        start_interval = interval
                
                
def remote_shell_hunt(directory, client, interval : int):
    # Executes command in remote machine through paramiko
    # finds any .php file under the directory that contains any php functions defined below and was created or spawned in less than 24 hours.
    # A directory checker is put in place. Exits out when said directory is not found
    command = f"find {directory} -type f -name '*.php' -mtime -1 2>/dev/null | xargs egrep -rl \"(mail|fsocketopen|pfsocketopen|exec|system|passthru|eval|base64_decode) *\\(\""
    stdin, stdout, stderr = client.exec_command(f"ls -l {directory}")
    directory_stat = stdout.channel.recv_exit_status()
    if directory_stat != 0:
        print(f"{R}[X] Error in checking directory {directory}.{W}")
        sys.exit(directory_stat)
    
    found_shells = []
    while True:
        start_interval = 0
        time.sleep(start_interval)
        stdin, stdout, stderr = client.exec_command(command)
        return_code = stdout.channel.recv_exit_status()
        if return_code == 0:
            files = [file.strip() for file in stdout.readlines()]
            for file in files:
                if file not in found_shells:
                    found_shells.append(file)
                    send_slack(file=file)
        start_interval = interval

                
    
def send_slack(file):
    # Sends message to slack channel whenever the script finds a php shell
    url = "https://hooks.slack.com/services/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" # Replace with your Slack webhook URL
    payload = {
        "channel": "#threat-hunting-training", # Replace with your channel 
        "username": "web-shell-hunter", # Replace with the bot username you want to use
        "text": f"[!] PHP shell found on *{file}*. Time: *{TIME_NOW}*",
        "icon_emoji": ":crossed_swords:"
    }

    data = {"payload": json.dumps(payload)}
    response = requests.post(url, data=data)
    if response.ok:
        print(f"Message sent to {G}#threat-hunting-traning{W} channel @ {TIME_NOW}")


def main():
    args = parse_args()
    directory = args.directory
    remote_host = args.remote_host
    interval = args.interval
    
    if remote_host:
        print(f"{G}Started PHP shell hunt on Host {remote_host}:{directory}{W} at {TIME_NOW}")
        client = server_connect(host=remote_host)
        remote_shell_hunt(directory=directory, client=client, interval=interval)
    else:
        print(f"{G}Started PHP shell hunt on Host localhost:{directory}{W} at {TIME_NOW}")
        local_shell_hunt(directory=directory, interval=interval)
    
    
    
if __name__ == "__main__": 
    try:
        main()
    except KeyboardInterrupt:
        print(f"{Y}Exiting...{W}")
        sys.exit()