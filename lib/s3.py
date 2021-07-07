import boto3
import botocore
import core.perf
import functools
import logging


from typing import List, Optional


logger = logging.getLogger(__name__)


@core.perf.timer
@core.perf.cache()
def get_s3_client(**kwargs) -> "botocore.client.S3":
    """Returns s3 client using default profile provided by environment."""
    return boto3.client("s3", **kwargs)


@core.perf.timer
def get_s3_bucket_names(s3_client: "botocore.client.S3") -> List[str]:
    """Returns names of all buckets owned by sender of request."""
    return [bucket["Name"] for bucket in s3_client.list_buckets()["Buckets"]]


@core.perf.timer
@core.perf.cache(max_age_seconds=3600)
def get_bucket_region(s3_client: "botocore.client.S3", bucket_name: str) -> str:
    """Returns the region a bucket resides in.

    NOTE: If null, the bucket is created in S3's default region (us-east-1)
    """
    region = s3_client.get_bucket_location(Bucket=bucket_name)["LocationConstraint"]
    if region is None:
        region = "us-east-1"
    return region


@core.perf.timer
def get_bucket_encryption(
    s3_client: "botocore.client.S3", bucket_name: str
) -> Optional[str]:
    """Returns the bucket's ssealgorithm if encryption enabled; otherwise none.

    NOTE: If bucket does not have encryption configuration,
    GetBucketEncryption returns ServerSideEncryptionConfigurationNotFoundError
    """
    try:
        response = s3_client.get_bucket_encryption(Bucket=bucket_name)
        encryption_conf = response["ServerSideEncryptionConfiguration"]
        encryption_algorithm = encryption_conf["Rules"][0][
            "ApplyServerSideEncryptionByDefault"
        ]["SSEAlgorithm"]
    except botocore.exceptions.ClientError as e:
        encryption_algorithm = None
        if (
            e.response["Error"]["Code"]
            != "ServerSideEncryptionConfigurationNotFoundError"
        ):
            # If we receive an unexpected response, let's log it and
            # assume the bucket is unencrypted to be looked into later.
            # we prefer not to raise and stop the program since it is
            # important to continue our audit for remaining buckets.
            logger.exception(e)
    return encryption_algorithm
