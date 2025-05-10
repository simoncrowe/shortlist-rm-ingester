#!/usr/bin/env python3
import dataclasses
import json
import sys

import click
import redis
import requests
import structlog

import adapters
import data
import scraping
import service

RECORDED_PROFILES_KEY = "recorded-profiles-rm"
INGESTED_KEY = "rm-ingested"
RECORDED_KEY = "rm-recorded"

logger = structlog.getLogger(__name__)
structlog.configure(processors=[structlog.processors.JSONRenderer()])


@click.group()
@click.option("--redis-host", type=str, default="127.0.0.1")
@click.option("--redis-pass", type=str, default=None)
@click.pass_context
def cli(ctx: click.Context, redis_host, redis_pass):
    redis_client = redis.Redis(host=redis_host, password=redis_pass)
    ctx.obj["redis_client"] = redis_client


@cli.command()
@click.argument("results_url")
@click.argument("runner_url")
@click.pass_context
def ingest(ctx: click.Context, results_url: str, runner_url: str):
    redis_client = ctx.obj["redis_client"]

    def send_to_runner(profile: data.Profile):
        profile_data = dataclasses.asdict(profile)
        payload = json.dumps(profile_data)
        resp = requests.post(runner_url, payload)
        resp.raise_for_status()
        logger.info("Profile ingested.", profile_data=profile_data)

    ingested = adapters.RedisSetStore(redis_client, namespace=INGESTED_KEY)

    listings_gen = scraping.iter_listings(results_url)

    service.ingest_listings(listings_gen,
                            ingest_callback=send_to_runner,
                            ingested=ingested)


@cli.command()
@click.argument("results_url")
@click.option("-n", "--number-of-profiles", type=int, default=24)
@click.option("-k", "--db-key", type=str, default=RECORDED_PROFILES_KEY)
@click.pass_context
def record(ctx: click.Context, results_url: str,
           number_of_profiles: int, db_key: str):

    redis_client = ctx.obj["redis_client"]
    redis_client.delete(db_key)
    redis_client.delete(RECORDED_KEY)

    saved_count = 0

    def save_to_redis(profile: data.Profile):
        nonlocal saved_count
        profile_data = dataclasses.asdict(profile)
        redis_client.lpush(db_key, json.dumps(profile_data))

        saved_count += 1
        logger.info("Profile persisted.",
                    profiles_count=saved_count,
                    profile_url=profile.metadata.url,
                    redis_key=db_key)

        if saved_count == number_of_profiles:
            sys.exit(0)

    ingested = adapters.RedisSetStore(redis_client, namespace=RECORDED_KEY)

    listings_gen = scraping.iter_listings(results_url)

    service.ingest_listings(listings_gen,
                            ingest_callback=save_to_redis,
                            ingested=ingested)


@cli.command()
@click.argument("runner_url")
@click.option("-k", "--db-key", type=str, default=RECORDED_PROFILES_KEY)
@click.pass_context
def replay(ctx: click.Context, runner_url: str, db_key: str):
    redis_client = ctx.obj["redis_client"]

    for profile_data in redis_client.lrange(db_key, 0, -1):
        resp = requests.post(runner_url, profile_data)
        resp.raise_for_status()
        logger.info("Profile ingested.",
                    profile_data=profile_data,
                    redis_key=db_key)


if __name__ == "__main__":
    cli(obj={})
