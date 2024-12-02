from gunicorn.app.base import BaseApplication
from multiprocessing import Process


class GunicornApplication(BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        self._process: Process | None = None
        super().__init__()

    def init(self, parser, opts, args):
        pass

    def load_config(self):
        config = {key: value for key, value in self.options.items() if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

    def start(self):
        self._process = Process(target=self.run)
        self._process.start()

    def stop(self):
        self._process.terminate()
        self._process.join()
