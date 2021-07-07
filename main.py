#!/usr/bin/env python

import boto3
import botocore
import core.perf
import functools
import lib.s3
import logging
import sys
import time

from argparse import ArgumentParser
from datetime import datetime, timedelta
from timeloop import Timeloop
from typing import Any, Dict, List


tl = Timeloop()

logger = logging.getLogger(__name__)


@tl.job(interval=timedelta(minutes=5))
@core.perf.timer
def s3_encryption_audit(region_name: str = "us-west-2"):
    """Checks encryption configuration on s3 buckets."""
    s3_client = lib.s3.get_s3_client()
    for bucket_name in lib.s3.get_s3_bucket_names(s3_client):
        bucket_region = lib.s3.get_bucket_region(s3_client, bucket_name)
        s3_rg_client = lib.s3.get_s3_client(region_name=bucket_region)
        bucket_encryption = lib.s3.get_bucket_encryption(
            s3_client=s3_rg_client, bucket_name=bucket_name
        )
        if bucket_encryption:
            logger.debug(f"{bucket_name} encrypted with {bucket_encryption}")
        else:
            logger.info(f"{bucket_name} is not encrypted!")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--log-level",
        default=logging.INFO,
        type=lambda x: getattr(logging, x.upper()),
        help="Configure the logging level.",
    )
    parser.add_argument(
        "--perf-log-level",
        default=logging.INFO,
        type=lambda x: getattr(logging, x.upper()),
        help="Configure core.perf logging level.",
    )
    parser.add_argument(
        "--log-to-file",
        type=str,
        help="Configure where logger outputs",
    )
    args = parser.parse_args()

    kwargs = {
        "format": "[%(asctime)s] [%(levelname)s] %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    }
    if args.log_to_file:
        print(f"logging to {args.log_to_file}")
        kwargs["filename"] = args.log_to_file
    logging.basicConfig(**kwargs)

    logger.setLevel(args.log_level)

    logging.getLogger("core.perf").setLevel(args.perf_log_level)

    tl.start(block=True)
