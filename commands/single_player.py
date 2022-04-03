import click
import requests


def hello():
    client = requests.Session()

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    }

    response = client.get("http://localhost:5500/login", headers=headers, verify=False)
    click.echo(response)
    response = client.post(
        "http://localhost:5500/login",
        json={"email": "admin@proquiz.io", "password": "p@ssworth"},
        headers=headers,
        verify=False,
    )
    # import pdb;pdb.set_trace()
    click.echo(response)


if __name__ == "__main__":
    hello()
