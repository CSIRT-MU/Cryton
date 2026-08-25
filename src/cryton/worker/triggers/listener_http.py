from click import echo
import bottle
from wsgiref.simple_server import make_server, WSGIRequestHandler
from threading import Thread
from queue import PriorityQueue
from uuid import uuid1

from cryton.worker.utility import constants as co
from cryton.worker.triggers import Listener


class MyWSGIRefServer(bottle.ServerAdapter):
    """
    WSGIRef server wrapper.
    """

    server = None

    def run(self, handler) -> None:
        """
        Start the server.
        :param handler: Handler
        :return: None
        """
        if self.quiet:

            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw):
                    pass

            self.options["handler_class"] = QuietHandler
        self.server = make_server(self.host, self.port, handler, **self.options)
        self.server.serve_forever()

    def stop(self) -> None:
        """
        Stop the server.
        :return: None
        """
        self.server.shutdown()
        self.server.server_close()


class HTTPListener(Listener):
    def __init__(self, main_queue: PriorityQueue, port: int, host: str = "0.0.0.0"):
        """
        Class for HTTPListeners (wrapper for Bottle).
        :param main_queue: Worker's queue for internal request processing
        :param port: Listener port
        :param host: Listener ip address
        """
        super().__init__(main_queue)
        self._identifiers = {co.LISTENER_HOST: host, co.LISTENER_PORT: port}
        self._app = bottle.Bottle()
        self._stopped = True
        self.server: MyWSGIRefServer | None = None
        self._logger = self._logger.bind(identifiers=self._identifiers)

    def add_trigger(self, details: dict) -> str:
        """
        Add trigger to Listener and restart it.
        :param details: Trigger options
            Example:
            {
                "host": str,
                "port": int,
                "reply_to": str,
                "routes": [
                    {
                        "path": str,
                        "method": str,
                        "parameters": [
                            {"name": str, "value": str},
                        ]
                    }
                ]
            }
        :return: ID of the new trigger
        """
        self._logger.debug("adding trigger to http listener", details=details)
        trigger_id = str(uuid1())
        details.update({co.TRIGGER_ID: trigger_id})

        with self._triggers_lock:
            self._triggers.append(details)
            self._restart()
        return trigger_id

    def remove_trigger(self, trigger: dict) -> None:
        """
        Remove trigger from Listener and restart it.
        :param trigger: Desired trigger
        :return: None
        """
        self._logger.debug("removing trigger from HTTP listener", trigger_id=trigger.get(co.TRIGGER_ID))
        with self._triggers_lock:
            self._triggers.remove(trigger)
            self._restart()

    def _restart(self) -> None:
        """
        Stop the App, reload triggers and start the App again.
        :return: None
        """
        self._logger.debug("restarting http listener")
        if self.any_trigger_exists():  # If there are no active triggers, only call stop.
            if not self._stopped:
                self.stop()
                self._app = bottle.Bottle()  # Discard old Bottle instance if adding more triggers.

            for trigger in self._triggers:  # Feed routes to the App again after discarding.
                for route in trigger.get("routes"):
                    self._app.route(route.get("path"), method=route.get("method"), callback=self._handle_request)
            self.start()

        else:
            if not self._stopped:
                self.stop()

    def _handle_request(self) -> None:
        """
        Handle HTTPListener request (call) (check path, method and parameters).
        :return: None
        """
        path = bottle.request.path
        self._logger.debug("handling http listener request", path=path)

        with self._triggers_lock:
            for trigger in self._triggers:
                for route in trigger.get("routes"):  # For each route check path, method and parameters.
                    if route.get("path") == path and route.get("method") == bottle.request.method:
                        request_parameters = self._check_parameters(route.get("parameters"))
                        if request_parameters is not None:
                            message_body = {
                                co.EVENT_T: co.EVENT_TRIGGER_STAGE,
                                co.EVENT_V: {
                                    co.TRIGGER_ID: trigger.get(co.TRIGGER_ID),
                                    co.TRIGGER_PARAMETERS: request_parameters,
                                },
                            }
                            self._notify(trigger.get(co.REPLY_TO), message_body)

    def _check_parameters(self, parameters: list) -> dict | None:
        """
        Check if requested parameters are correct.
        :param parameters: Parameters to check
        :return: Request's parameters if they match given parameters
        """
        self._logger.debug("checking parameters", parameters=parameters)
        if bottle.request.method == "GET":
            request_parameters = bottle.request.query
            for param in parameters:
                if str(request_parameters.get(param.get("name"))) != str(param.get("value")):  # Bad value.
                    return None

        elif bottle.request.method == "POST":
            request_parameters = bottle.request.forms
            for param in parameters:
                if str(request_parameters.get(param.get("name"))) != str(param.get("value")):  # Bad value.
                    return None

        else:
            return None

        request_parameters_dict = {}  # Create dictionary from bottle.FormsDict, otherwise json.dumps would fail
        for key, value in request_parameters.items():
            request_parameters_dict.update({key: value})
        return request_parameters_dict

    def compare_identifiers(self, identifiers: dict) -> bool:
        """
        Check if specified identifiers match with Listener's.
        :param identifiers: Data containing identifiers
        :return: True if identifiers match Listener's
        """
        if self._identifiers[co.LISTENER_HOST] == identifiers.get(co.LISTENER_HOST) and self._identifiers[
            co.LISTENER_PORT
        ] == identifiers.get(co.LISTENER_PORT):
            return True
        return False

    def start(self) -> None:
        """
        Start the Listener.
        :return: None
        """
        if self._stopped:
            echo(f"Starting HTTP listener. Identifiers: {self._identifiers}")
            self._logger.debug("starting http listener")
            Thread(target=self._run).start()
            self._stopped = False

    def _run(self) -> None:
        """
        Create WSGIRef server and run the Bottle application.
        :return: None
        """
        self.server = MyWSGIRefServer(
            host=self._identifiers[co.LISTENER_HOST], port=self._identifiers[co.LISTENER_PORT]
        )
        self._app.run(
            **{
                co.LISTENER_HOST: self._identifiers[co.LISTENER_HOST],
                co.LISTENER_PORT: self._identifiers[co.LISTENER_PORT],
                "quiet": True,
                "server": self.server,
            }
        )

    def stop(self) -> None:
        """
        Stop the Listener.
        :return: None
        """
        if not self._stopped:
            echo(f"Stopping HTTP listener. Identifiers: {self._identifiers}")
            self._logger.debug("stopping http listener")
            self._app.close()
            self._stopped = True
            self.server.stop()
