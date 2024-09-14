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
    redis_host = os.getenv("REDIS_HOST")
    runner_url = os.getenv("RUNNER_URL")
    redis_client = redis.Redis(host=redis_host)

    listings_gen = scraping.iter_listings(url)

    def send_to_runner(profile: data.Profile):
        profile_data = dataclasses.asdict(profile)
        payload = json.dumps(profile_data)
        requests.post(runner_url, payload)

    ingested = adapters.RedisSetStore(redis_client, namespace="ingested-rm")

    service.ingest_listings(listings_gen,
                            ingest_callback=send_to_runner,
                            ingested=ingested)


if __name__ == "__main__":
    main()
