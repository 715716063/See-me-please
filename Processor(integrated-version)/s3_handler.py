# s3_handler.py

import boto3

class S3Handler:
    """Class for handling S3 operations."""
    def __init__(self, config):
        self.config = config
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            region_name=config.region_name
        )
        self.bucket_name = config.bucket_name

    def list_files(self):
        """List all files in the S3 bucket."""
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            if 'Contents' in response:
                return [file['Key'] for file in response['Contents']]
            return []
        except Exception as e:
            raise Exception(f"Failed to list files from S3: {str(e)}")

    def download_file(self, file_key, destination_path):
        """Download a file from S3."""
        try:
            self.s3_client.download_file(self.bucket_name, file_key, destination_path)
        except Exception as e:
            raise Exception(f"Failed to download file from S3: {str(e)}")
