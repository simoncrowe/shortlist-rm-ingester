#!/usr/bin/env python3
import dataclasses
import json
import os

import click
import redis
import requests

import adapters
import data
import scraping
import service


@click.command()
@click.argument("url")
def main(url):
    runner_url = os.getenv("RUNNER_URL")

    def _send_to_runner(profile: data.Profile):
        profile_data = dataclasses.asdict(profile)
        payload = json.dumps(profile_data)
        resp = requests.post(runner_url, payload)
        resp.raise_for_status()

    redis_host = os.getenv("REDIS_HOST")
    redis_pass = os.getenv("REDIS_PASS")

    redis_client = redis.Redis(host=redis_host, password=redis_pass)
    ingested = adapters.RedisSetStore(redis_client, namespace="ingested-rm")

    listings_gen = scraping.iter_listings(url)

    service.ingest_listings(listings_gen,
                            ingest_callback=_send_to_runner,
                            ingested=ingested)


if __name__ == "__main__":
    main()
