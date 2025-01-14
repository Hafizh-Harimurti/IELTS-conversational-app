import threading
import io
import boto3
from botocore import UNSIGNED
from botocore.client import Config as AWSConfig

from utils import rname

class FileUploader:
    def __init__(self, bucket_name='static-contents-smartjen'):
        self.s3_client = boto3.client('s3', config=AWSConfig(signature_version=UNSIGNED))
        self.bucket_name = bucket_name

    def upload_fileobj(self, fileobj, status_callback):
        """
        Uploads an in-memory file object to S3 in a separate thread and updates the UI via a structured callback.
        :param fileobj: In-memory file object (e.g., BytesIO) to upload
        :param status_callback: Function to return status updates to the UI
        """
        def upload_thread():
            try:
                # Notify that the upload is starting
                status_callback({"is_uploading": True, "upload_success": False, "file_url": ""})

                # Generate a unique key for the file in the S3 bucket
                key_name = f"audio/heyjenAudio/{rname()}.wav"

                # Reset the file pointer to the beginning before uploading
                fileobj.seek(0)

                # Perform the actual upload
                self.s3_client.upload_fileobj(
                    fileobj,
                    self.bucket_name,
                    key_name,
                    ExtraArgs={"ContentType": "audio/wav"}
                )

                # Construct the file URL
                file_url = f"https://{self.bucket_name}.s3.amazonaws.com/{key_name}"

                # Notify that the upload completed successfully
                status_callback({"is_uploading": False, "upload_success": True, "file_url": file_url})
                print(f"File uploaded to S3 bucket {self.bucket_name} accessible on {file_url}.")
            except Exception as e:
                print(f"Failed to upload file: {e}")
                status_callback({"is_uploading": False, "upload_success": False, "file_url": ""})

        # Start the upload in a separate thread
        thread = threading.Thread(target=upload_thread)
        thread.start()
