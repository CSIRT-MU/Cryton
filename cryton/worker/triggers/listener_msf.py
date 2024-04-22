from click import echo
import time
from copy import deepcopy
from threading import Thread
from queue import PriorityQueue

from cryton.worker.utility import logger, util, constants as co, exceptions
from cryton.worker.triggers import Listener


class MSFListener(Listener):
    def __init__(self, main_queue: PriorityQueue, identifiers: dict):
        """
        Class for MSFListeners.
        :param main_queue: Worker's queue for internal request processing
        :param identifiers: Trigger(session) identifiers
        """
        super().__init__(main_queue)
        self._identifiers = identifiers
        self.msf = util.Metasploit()
        self._stopped = True
        self._trigger_id = None

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
                if via_exploit := details.get(co.EXPLOIT):
                    self._identifiers["via_exploit"] = via_exploit
                    if via_payload := details.get(co.PAYLOAD):
                        self._identifiers["via_payload"] = via_payload
                elif auxiliary := details.get(co.AUXILIARY):
                    self._identifiers["via_exploit"] = auxiliary
            try:
                self.start()
            except (KeyError, ValueError, TypeError, exceptions.MsfModuleNotFound) as err:
                self.remove_trigger(details)
                raise err
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

    def _check_for_session(self) -> None:
        """
        Check regularly for created session and if is found send it.
        :return: None
        """
        logger.logger.debug(
            "MSFListener is looking for MSF session with matching parameters", session_identifiers=self._identifiers
        )
        while not self._stopped and self.msf.is_connected():
            active_sessions = self.msf.get_sessions(**self._identifiers)
            if active_sessions:
                message_body = {
                    co.EVENT_T: co.EVENT_TRIGGER_STAGE,
                    co.EVENT_V: {co.TRIGGER_ID: self._trigger_id, co.TRIGGER_PARAMETERS: active_sessions[-1]},
                }
                time.sleep(3)  # MSF limitation. If we use the session immediately, it may not give output.
                self._notify(self._triggers[0].get(co.REPLY_TO), message_body)
                break
            time.sleep(5)

    def compare_identifiers(self, identifiers: dict) -> bool:
        """
        Check if specified identifiers match with Listener's.
        :param identifiers: Trigger identifiers
        :return: True if supplied session identifiers match with those on Listener
        """
        if identifiers.get(co.IDENTIFIERS) == self._identifiers:
            return True
        return False

    def start(self) -> None:
        """
        Start the Listener.
        :return: None
        """
        if self._stopped:
            if not self.msf.is_connected():
                raise exceptions.MsfConnectionError
            echo(f"Starting MSFListener. trigger_id: {self._trigger_id}, session_identifiers: {self._identifiers}")
            logger.logger.debug(
                "Starting MSFListener.", trigger_id=self._trigger_id, session_identifiers=self._identifiers
            )
            details = deepcopy(self._triggers[0])
            if co.EXPLOIT in details:
                self.msf.execute_exploit(
                    details.pop(co.EXPLOIT),
                    details.pop(co.PAYLOAD, None),
                    details.pop(co.EXPLOIT_ARGUMENTS, None),
                    details.pop(co.PAYLOAD_ARGUMENTS, None),
                )
            elif co.AUXILIARY in details:
                self.msf.execute_auxiliary(details.pop(co.AUXILIARY), details.pop(co.AUXILIARY_ARGUMENTS, None))

            self._stopped = False
            t = Thread(target=self._check_for_session)
            t.start()

    def stop(self) -> None:
        """
        Stop the Listener.
        :return: None
        """
        if not self._stopped:
            echo(f"Stopping MSFListener. trigger_id: {self._trigger_id}")
            logger.logger.debug(
                "Stopping MSFListener.", trigger_id=self._trigger_id, session_identifiers=self._identifiers
            )
            self._stopped = True
