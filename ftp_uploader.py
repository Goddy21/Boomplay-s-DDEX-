# ftp_uploader.py
from ftplib import FTP
import os
import time
from config import FTP_SERVER, FTP_USERNAME, FTP_PASSWORD, BATCH_NUMBER

def ensure_ftp_directory(ftp, directory):
    try:
        ftp.cwd(directory)
    except Exception:
        try:
            ftp.mkd(directory)
            ftp.cwd(directory)
        except Exception as e:
            print(f"❌ Failed to create FTP directory {directory}: {e}")

def upload_to_ftp(file_path, upc_code, max_retries=3):
    attempt = 0
    while attempt < max_retries:
        try:
            with FTP(FTP_SERVER) as ftp:
                ftp.login(FTP_USERNAME, FTP_PASSWORD)
                batch_dir = f"/BATCH_{BATCH_NUMBER}"
                upc_dir = f"{batch_dir}/{upc_code}"

                ensure_ftp_directory(ftp, batch_dir)
                ensure_ftp_directory(ftp, upc_dir)

                filename = os.path.basename(file_path)
                if filename in ftp.nlst():
                    print(f"🔄 Skipping duplicate: {file_path}")
                    return

                with open(file_path, 'rb') as file:
                    ftp.storbinary(f"STOR {filename}", file)
                print(f"✅ Uploaded: {file_path}")
                return
        except Exception as e:
            print(f"❌ FTP upload failed for {file_path} (Attempt {attempt + 1}/{max_retries}): {e}")
            attempt += 1
            time.sleep(5)

    print(f"🚨 Permanent failure: Could not upload {file_path}")
