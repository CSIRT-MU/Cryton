try:
    from cryton.cli.cli import cli
except ImportError as ex:
    print("Unable to start `cryton-cli`. Make sure cryton[cli] extras are installed.")
    print(f"Original error: {ex}")
    exit(1)

if __name__ == "__main__":
    cli()
