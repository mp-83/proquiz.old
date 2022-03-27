import json

import click


@click.command()
def hello():
    with open("/package/codechallenge/commands/test.yaml", "r") as yaml_file:
        content = json.loads(yaml_file.read())

    click.echo(content)


if __name__ == "__main__":
    hello()
