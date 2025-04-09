# config.py
import os
import time
from dotenv import load_dotenv

load_dotenv()

FTP_SERVER = os.getenv('FTP_SERVER')
FTP_USERNAME = os.getenv('FTP_USERNAME')
FTP_PASSWORD = os.getenv('FTP_PASSWORD')
LOCAL_DIR = os.getenv('LOCAL_DIR')
SCHEMA_FILE = "http://ddex.net/xml/ern/383/release-notification.xsd"
EXCEL_FILE = os.path.join(LOCAL_DIR, 'choir.xlsx')
BATCH_NUMBER = time.strftime('%Y%m%d')
BATCH_FOLDER = os.path.join(LOCAL_DIR, f"BATCH_{BATCH_NUMBER}")
os.makedirs(BATCH_FOLDER, exist_ok=True)
LOG_FILE = os.path.join(LOCAL_DIR, f"upload_log_{BATCH_NUMBER}.txt")

DDEX_ERN_NAMESPACE = 'http://ddex.net/xml/ern/383'
DDEX_AVS_NAMESPACE = "http://ddex.net/xml/avs/avs"
XSI_NAMESPACE = 'http://www.w3.org/2001/XMLSchema-instance'
