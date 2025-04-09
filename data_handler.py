# data_handler.py
import pandas as pd
from PIL import Image
import os
import shutil
import urllib.request
from lxml import etree
import wave


def read_excel(file_path):
    df = pd.read_excel(file_path, engine='openpyxl')
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')

    def clean_duration(value):
        value = str(value)
        parts = value.split(':')
        if len(parts) == 3:
            return f"{parts[1]}:{parts[2]}"
        return value

    df.fillna({
        'primary_artists': 'UNKNOWN_ARTIST',
        'label': 'UNKNOWN_LABEL',
        'isrc_code': 'UNKNOWN_ISRC',
        'upc_code': 'UNKNOWN_UPC',
        'track_titles': 'UNKNOWN_TRACK',
        'parental_advisory': 'NoAdviceAvailable',
        'duration': 'PT0M0S'
    }, inplace=True)

    df['upc_code'] = df['upc_code'].astype(str)
    df['isrc_code'] = df['isrc_code'].astype(str)
    df['duration'] = df['duration'].fillna('0:00').astype(str)
    return df

def validate_image_size(image_path):
    with Image.open(image_path) as img:
        if img.width < 800 or img.height < 800:
            print(f"⚠️ Image {image_path} is too small ({img.width}x{img.height}). Skipping upload.")
            return False
        return True

def format_duration(duration):
    try:
        print(f"🔍 Original duration input: {duration}")

        parts = duration.split(':')

        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            corrected_minutes = hours
            corrected_seconds = minutes
            print(f"📌 Corrected values -> Minutes: {corrected_minutes}, Seconds: {corrected_seconds}")
            formatted_duration = f"PT{corrected_minutes}M{corrected_seconds}S"

        elif len(parts) == 2:
            minutes, seconds = map(int, parts)
            formatted_duration = f"PT{minutes}M{seconds}S"

        else:
            formatted_duration = 'PT0M0S'

        print(f"✅ Final formatted duration: {formatted_duration}")
        return formatted_duration

    except Exception as e:
        print(f"❌ Error formatting duration: {e}")
        return 'PT0M0S'

def validate_ddex_xml(xml_file, schema_file):
    try:
        if schema_file.startswith('http://') or schema_file.startswith('https://'):
            try:
                with urllib.request.urlopen(schema_file) as f:
                    schema_doc = etree.parse(f)
            except Exception as e:
                print(f"❌ Error opening URL: {schema_file}")
                print(e)
                return False
        else:
            schema_file = os.path.abspath(schema_file)
            try:
                schema_doc = etree.parse(schema_file)
            except etree.XMLSyntaxError as e:
                print(f"❌ Invalid XML schema file: {schema_file}")
                print(e)
                return False
            except Exception as e:
                print(f"❌ Error creating schema: {e}")
                print(e)
                return False

        schema = etree.XMLSchema(schema_doc)
        xml_doc = etree.parse(xml_file)

        if schema.validate(xml_doc):
            print(f"✅ XML Validation Passed: {xml_file}")
            return True
        else:
            print(f"❌ XML Validation Failed: {xml_file}")
            print(schema.error_log)
            return False

    except Exception as e:
        print(f"🚨 XML validation error: {e}")
        return False
    
def move_to_batch_folder(file_path, upc_code, BATCH_FOLDER):
    resource_folder = os.path.join(BATCH_FOLDER, upc_code)
    os.makedirs(resource_folder, exist_ok=True)

    if os.path.exists(file_path):
        dest_path = os.path.join(resource_folder, os.path.basename(file_path))
        shutil.copy2(file_path, dest_path)
        return dest_path
    return None

def get_audio_bitrate(file_path):
    """
    Gets the bitrate of an audio file without using FFmpeg.

    Args:
        file_path (str): The path to the audio file.

    Returns:
        int: The bitrate of the audio file in kbps, or None if it cannot be determined.
    """
    try:
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == '.wav':
            with wave.open(file_path, 'rb') as wf:
                frame_rate = wf.getframerate()
                num_channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                bitrate = (frame_rate * num_channels * sample_width * 8) / 1000.0  # kbps
                return int(bitrate)
        elif file_ext == '.aiff' or file_ext == '.aifc' or file_ext == '.mp3' or file_ext == '.flac':
            try:
                import mutagen
                audio = mutagen.File(file_path)
                if audio and hasattr(audio, 'info') and hasattr(audio.info, 'bitrate'):
                    return int(audio.info.bitrate / 1000)  # kbps
                else:
                    return None
            except ImportError:
                print("Mutagen library is required to determine MP3/FLAC/AIFF bitrate.")
                return None
        else:
            print(f"Unsupported file format: {file_ext}")
            return None
    except Exception as e:
        print(f"Error getting bitrate: {e}")
        return None

def check_audio_bitrate(file_path):
    """
    Checks if the bitrate of an audio file is at least 320 kbps.

    Args:
        file_path (str): The path to the audio file.

    Returns:
        bool: True if the bitrate is at least 320 kbps, False otherwise.
    """
    bitrate = get_audio_bitrate(file_path)
    if bitrate is not None:
        if bitrate >= 320:
            print(f"Audio bitrate is {bitrate} kbps - OK")
            return True
        else:
            print(f"Audio bitrate is {bitrate} kbps - FAIL (below 320 kbps)")
            return False
    else:
        return False