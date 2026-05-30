"""Cloudflare R2 (S3-compatible) storage."""
USE_R2 = True

AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME", "")
AWS_S3_ENDPOINT_URL = env.str("AWS_S3_ENDPOINT_URL", "")
AWS_S3_REGION_NAME = env.str("AWS_S3_REGION_NAME", "auto")
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = 3600

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/"
