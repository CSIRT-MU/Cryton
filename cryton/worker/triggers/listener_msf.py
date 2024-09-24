from click import echo
from threading import Thread
from queue import PriorityQueue
from typing import Optional

from cryton.worker.utility import logger, constants as co, exceptions
from cryton.worker.triggers import Listener
from cryton.modules.metasploit.module import Module


class MSFListener(Listener):
    def __init__(self, main_queue: PriorityQueue):
        """
        Class for MSFListeners.
        :param main_queue: Worker's queue for internal request processing
        """
        super().__init__(main_queue)
        self._identifiers: dict = {}
        self._stopped = True
        self._trigger_id = None
        self._module: Optional[Module] = None

    def add_trigger(self, details: dict) -> str:
        """
        Add trigger to Listener and start the Listener.
        :param details: Trigger details
            Example:
            {
                "reply_to": str,
                "identifiers": {
                    'type': 'shell',
                    'tunnel_local': '192.168.56.10:555',
                    'tunnel_peer': '192.168.56.1:48584',
                    'via_exploit': 'exploit/multi/handler',
                    'via_payload': 'payload/python/shell_reverse_tcp',
                    'desc': 'Command shell',
                    'info': '',
                    'workspace': 'false',
                    'session_host': '192.168.56.1',
                    'session_port': 48584,
                    'target_host': '',
                    'username': 'vagrant',
                    'uuid': 'o3mnfksh',
                    'exploit_uuid': 'vkzl8sib',
                    'routes': '',
                    'arch': 'python'
                }
            }
        :return: ID of the new trigger
        """
        logger.logger.debug("Adding trigger to MSFListener.", session_identifiers=self._identifiers)
        if self.any_trigger_exists():
            raise exceptions.TooManyTriggers(str(self))

        self._trigger_id = str(self._generate_id())
        details.update({co.TRIGGER_ID: self._trigger_id})
        with self._triggers_lock:
            self._triggers.append(details)
            if not self._identifiers:
                self._identifiers = details
                self._module = Module(details)
            try:
                self.start()
            except (ConnectionError, RuntimeError, TypeError) as ex:
                self.remove_trigger(details)
                raise ex
        return self._trigger_id

    def remove_trigger(self, trigger: dict) -> None:
        """
        Remove trigger from Listener and optionally stop the Listener.
        :param trigger: Desired trigger
        :return: None
        """
        logger.logger.debug(
            "Removing trigger from MSFListener.", trigger_id=self._trigger_id, session_identifiers=self._identifiers
        )
        with self._triggers_lock:
            self._triggers.remove(trigger)
            if not self.any_trigger_exists():
                self.stop()

    def _start(self) -> None:
        """
        Execute Metasploit module and wait for it to finish.
        :return: None
        """
        result = self._module.execute()
        message_body = {
            co.EVENT_T: co.EVENT_TRIGGER_STAGE,
            co.EVENT_V: {
                co.TRIGGER_ID: self._trigger_id,
                co.TRIGGER_PARAMETERS: result.serialized_output,
            },
        }
        self._notify(self._triggers[0].get(co.REPLY_TO), message_body)

    def compare_identifiers(self, identifiers: dict) -> bool:
        """
        Check if specified identifiers match with Listener's.
        :param identifiers: Trigger identifiers
        :return: True if supplied session identifiers match with those on Listener
        """
        return False

    def start(self) -> None:
        """
        Start the Listener.
        :return: None
        """
        if not self._stopped:
            return

        self._module.check_requirements()
        echo(f"Starting MSFListener. trigger_id: {self._trigger_id}, session_identifiers: {self._identifiers}")
        logger.logger.debug("Starting MSFListener.", trigger_id=self._trigger_id, session_identifiers=self._identifiers)
        self._stopped = False
        Thread(target=self._start).start()

    def stop(self) -> None:
        """
        Stop the Listener.
        :return: None
        """
        if self._stopped:
            return

        echo(f"Stopping MSFListener. trigger_id: {self._trigger_id}")
        logger.logger.debug("Stopping MSFListener.", trigger_id=self._trigger_id, session_identifiers=self._identifiers)
        self._stopped = True
