import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import logging

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class S3FileDownloader:
    def __init__(self, bucket_name, s3_prefix, aws_access_key, aws_secret_key, region):
        """
        Initialize the S3FileDownloader with S3 configurations.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_prefix (str): The S3 prefix to search under.
            aws_access_key (str): AWS Access Key.
            aws_secret_key (str): AWS Secret Key.
            region (str): AWS Region.
        """
        self.bucket_name = bucket_name
        self.s3_prefix = s3_prefix.rstrip('/')  # Ensure no trailing slash
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )

        # Path to the downloads folder inside the current working directory
        self.download_path = os.path.join(os.getcwd(), "downloads", "narayana")
        os.makedirs(self.download_path, exist_ok=True)


    def list_files(self):
        """
        List all files under the specified S3 prefix.

        Returns:
            list: A list of S3 keys (file paths).
        """
        logger.info(f"Listing files in S3 bucket '{self.bucket_name}' under prefix '{self.s3_prefix}'")
        try:
            files = []
            paginator = self.s3_client.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=self.s3_prefix):
                for obj in page.get("Contents", []):
                    files.append(obj["Key"])
            logger.info(f"Found {len(files)} files in S3 path '{self.s3_prefix}'")
            return files
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return []

    def download_raw_quiz_files(self):
        """
        Search for and download all 'raw_quiz.tex' files from the S3 path,
        maintaining the folder structure locally under the Downloads folder.
        """
        try:
            files = self.list_files()
            raw_quiz_files = [file for file in files if file.endswith("raw_quiz.tex")]

            if not raw_quiz_files:
                logger.info("No 'raw_quiz.tex' files found.")
                return

            for s3_key in raw_quiz_files:
                # Relative path by removing the prefix
                relative_path = os.path.relpath(s3_key, self.s3_prefix)

                # Local path to save the file
                local_file_path = os.path.join(self.download_path, relative_path)

                # Ensure the local directory exists
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

                # Download file
                self.s3_client.download_file(self.bucket_name, s3_key, local_file_path)
                logger.info(f"Downloaded: {s3_key} to {local_file_path}")

        except NoCredentialsError:
            logger.error("AWS credentials not found.")
        except PartialCredentialsError:
            logger.error("Incomplete AWS credentials.")
        except Exception as e:
            logger.error(f"Error downloading 'raw_quiz.tex' files: {str(e)}")


# Example Usage
if __name__ == "__main__":
    # S3 configuration
    S3_BUCKET_NAME = "s3-learn-eon-prod"
    S3_PREFIX = "efd03438-f326-4b3e-a418-6d32dac068a7/"  # Base S3 path to search
    AWS_ACCESS_KEY = os.getenv("PROD_AWS_ACCESS_KEY_ID")
    AWS_SECRET_KEY = os.getenv("PROD_AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")

    # Initialize downloader
    downloader = S3FileDownloader(
        bucket_name=S3_BUCKET_NAME,
        s3_prefix=S3_PREFIX,
        aws_access_key=AWS_ACCESS_KEY,
        aws_secret_key=AWS_SECRET_KEY,
        region=AWS_REGION
    )

    # Download all raw_quiz.tex files
    downloader.download_raw_quiz_files()
