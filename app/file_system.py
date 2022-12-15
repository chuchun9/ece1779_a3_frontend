import logging
import boto3
import botocore
import os


class FileSystem:
    @classmethod
    def __init__(self, bucket_name):
        self.s3 = boto3.resource('s3')
        self.bucket = self.s3.Bucket(bucket_name)
        self.bucket_name = bucket_name

        logging.info("Connecting to S3 bucket")
        try:
            self.s3.meta.client.head_bucket(Bucket=bucket_name)
        except botocore.exceptions.ClientError as e:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logging.error(e)
                raise Exception("Could not connect to bucket {}".format(bucket_name))

        logging.info("Successfully connected to S3 bucket")
        # self.bucket.Acl().put(ACL='public-read')

    def upload_image(self, file_name, object_name=None):
        s3_client = boto3.client('s3')

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)

        try:
            s3_client.upload_file(file_name, self.bucket_name, object_name)
        except botocore.exceptions.ClientError as e:
            logging.error(e)
            return False
        return True

    def upload_inmem_image(self, inmemfile, filename, type):
        s3_client = boto3.client('s3')

        try:
            s3_client.upload_fileobj(inmemfile, self.bucket_name, filename, ExtraArgs={'ContentType': type})
        except botocore.exceptions.ClientError as e:
            logging.error(e)
            return False
        return True

    def download_image(self, file_name, object_name=None):
        s3 = boto3.client('s3')
        try:
            s3.download_file(self.bucket_name, object_name, file_name)
        except botocore.exceptions.ClientError as e:
            logging.error(e)
            return False
        return True
