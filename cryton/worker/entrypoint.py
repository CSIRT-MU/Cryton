try:
    from cryton.worker.cli import cli
except ImportError:
    print("Unable to start `cryton-worker`. Make sure cryton[worker] extras are installed.")
    exit(1)
