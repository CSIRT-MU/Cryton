# TODO: Merge entrypoints into a single cli? cryton hive instead of cryton-hive; imports will be in each method
#  Could be done after a bit more testing and in the click-typer transition

try:
    from cryton.hive.cli import cli
except ImportError as ex:
    print("Unable to start `cryton-hive`. Make sure cryton[hive] extras are installed.")
    print(f"Original error: {ex}")
    exit(1)

if __name__ == "__main__":
    cli()
