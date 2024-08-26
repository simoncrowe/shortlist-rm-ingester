#!/usr/bin/env python3
import click
import scraping


@click.command()
@click.argument("url")
def main(url):

    for listing in scraping.iter_new_listings(url, lambda _: True):
        pass


if __name__ == "__main__":
    main()
