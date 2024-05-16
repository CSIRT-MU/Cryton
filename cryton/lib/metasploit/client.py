from snek_sploit import *

from cryton.worker.config.settings import SETTINGS


class MetasploitClientUpdated(MetasploitClient):
    def __init__(
        self,
        username: str = SETTINGS.metasploit.username,
        password: str = SETTINGS.metasploit.password,
        host: str = SETTINGS.metasploit.host,
        port: int = SETTINGS.metasploit.port,
        ssl: bool = SETTINGS.metasploit.ssl,
        *args,
        **kwargs,
    ):
        super().__init__(username, password, host, port, ssl=ssl, disable_https_warnings=True, *args, **kwargs)
