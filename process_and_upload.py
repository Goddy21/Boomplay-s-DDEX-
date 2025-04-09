import os
from data_handler import read_excel, validate_image_size, move_to_batch_folder
from xml_generator import create_ddex_xml
from data_handler import validate_ddex_xml, check_audio_bitrate
from ftp_uploader import upload_to_ftp
from config import EXCEL_FILE, BATCH_FOLDER, LOG_FILE, SCHEMA_FILE, LOCAL_DIR

def process_and_upload():
    df = read_excel(EXCEL_FILE)
    files_to_upload = []

    for _, row in df.iterrows():
        print(f"📝 Processing track: {row['track_titles']} (ISRC: {row['isrc_code']}, UPC: {row['upc_code']})")
        upc_code = row['upc_code']
        resource_folder = os.path.join(BATCH_FOLDER, upc_code)
        os.makedirs(resource_folder, exist_ok=True)
        image_filename = None

        for ext, folder in [('mp3', 'AUDIO'), ('wav', 'WAV'), ('flac', 'AUDIO'), ('jpg', 'IMAGES')]:
            search_folder = os.path.join(LOCAL_DIR, folder)
            matching_files = [f for f in os.listdir(search_folder) if
                              row['track_titles'].lower().replace(' ', '_') in f.lower() and f.endswith(ext)]

            if matching_files:
                file_path = os.path.join(search_folder, matching_files[0])
                if ext == 'jpg' and not validate_image_size(file_path):
                    continue
                
                # Check audio bitrate for audio files
                if ext in ['mp3', 'wav', 'flac']:
                    if not check_audio_bitrate(file_path):
                        with open(LOG_FILE, 'a') as log:
                            log.write(f"Low bitrate: {row['track_titles']}.{ext}\n")
                        continue  # Skip this file if bitrate is too low
                
                new_path = move_to_batch_folder(file_path, upc_code, BATCH_FOLDER)
                if new_path:
                    files_to_upload.append((new_path, upc_code))
                    if ext == 'jpg':
                        image_filename = os.path.basename(new_path)
            else:
                with open(LOG_FILE, 'a') as log:
                    log.write(f"Missing file: {row['track_titles']}.{ext}\n")

        xml_file = create_ddex_xml(row, image_filename)
        if validate_ddex_xml(xml_file, SCHEMA_FILE):
            files_to_upload.append((xml_file, upc_code))
        else:
            with open(LOG_FILE, 'a') as log:
                log.write(f"Invalid XML: {os.path.basename(xml_file)}\n")

    print("📝 Files ready for upload:")
    for file, _ in files_to_upload:
        print(file)

    confirm = input("❓ Proceed with upload? (y/n): ")
    if confirm.lower() == 'y':
        for file, upc_code in files_to_upload:
            upload_to_ftp(file, upc_code)
