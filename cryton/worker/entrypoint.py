try:
    from cryton.worker.cli import cli
except ImportError as ex:
    print("Unable to start `cryton-worker`. Make sure cryton[worker] extras are installed.")
    print(f"Original error: {ex}")
    exit(1)


if __name__ == "__main__":
    cli()
