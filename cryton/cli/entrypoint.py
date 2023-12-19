try:
    from cryton.cli.cli import cli
except ImportError as ex:
    print("Unable to start `cryton-cli`. Make sure cryton[cli] extras are installed.")
    exit(1)
