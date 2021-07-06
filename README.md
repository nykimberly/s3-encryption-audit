## s3 encryption audit sample script
- docker build -t s3-encryption-audit .
- docker run -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY s3-encryption-audit