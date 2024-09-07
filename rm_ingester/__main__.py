#!/usr/bin/env python3
import click


@click.command()
@click.argument("url")
def main(url):
    pass


if __name__ == "__main__":
    main()
