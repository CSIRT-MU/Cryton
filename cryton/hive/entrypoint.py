try:
    from cryton.hive.cli import cli
except ImportError:
    print("Unable to start `cryton-hive`. Make sure cryton[hive] extras are installed.")
    exit(1)
