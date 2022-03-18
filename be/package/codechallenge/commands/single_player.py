import click


@click.command()
def hello():
    click.echo("test")


if __name__ == "__main__":
    hello()
