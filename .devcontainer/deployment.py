import logging
import os
import time

import paramiko

logging.basicConfig(level=logging.INFO)

USERNAME = os.getenv('SSH_USERNAME')
PASSWORD = os.getenv('SSH_PASSWORD')
SERVER_ADDRESS = os.getenv('SERVER_ADDRESS')
PATH = os.getenv('PRODUCTION_PROJECT_PATH')

if not all([USERNAME, PASSWORD, PATH, SERVER_ADDRESS]):
    raise Exception('Script is improperly configured')

ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(SERVER_ADDRESS, username=USERNAME, password=PASSWORD, allow_agent=False)

logging.info(ssh_client)
logging.info('Running deployment command')
command = f'cd {PATH} && git pull && supervisorctl restart bot homesite'
stdin, stdout, stderr = ssh_client.exec_command(command)
time.sleep(10)
logging.info(''.join(stdout.readlines()))
