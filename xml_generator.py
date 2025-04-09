from lxml import etree
import time
import random
import os
from config import DDEX_ERN_NAMESPACE, DDEX_AVS_NAMESPACE, XSI_NAMESPACE, BATCH_FOLDER, LOG_FILE
from data_handler import format_duration

def generate_grid():
    return f"A1{random.randint(10000000, 99999999)}V"

def create_ddex_xml(row, image_filename):
    resource_folder = os.path.join(BATCH_FOLDER, row['upc_code'])
    os.makedirs(resource_folder, exist_ok=True)

    ernm = "{http://ddex.net/xml/ern/383}"
    avs = "{http://ddex.net/xml/avs/avs}"
    xsi = "{http://www.w3.org/2001/XMLSchema-instance}"

    NewReleaseMessage = etree.Element(f"{ernm}NewReleaseMessage",
                                        attrib={
                                            "LanguageAndScriptCode": "en",
                                            "ReleaseProfileVersionId": "ClassicalAudioAlbum",
                                            f"{xsi}schemaLocation": "http://ddex.net/xml/ern/383 http://ddex.net/xml/ern/383/release-notification.xsd",
                                            "MessageSchemaVersionId": "ern/383"
                                        },
                                        nsmap={
                                            "ernm": DDEX_ERN_NAMESPACE,
                                            "avs": DDEX_AVS_NAMESPACE,
                                            "xsi": XSI_NAMESPACE
                                        })

    MessageHeader = etree.SubElement(NewReleaseMessage, "MessageHeader")
    etree.SubElement(MessageHeader, "MessageThreadId").text = f"{random.randint(100000, 999999)}-{random.randint(1000, 9999)}"
    etree.SubElement(MessageHeader, "MessageId").text = f"{random.randint(100000, 999999)}-{random.randint(1000, 9999)}"

    MessageSender = etree.SubElement(MessageHeader, "MessageSender")
    etree.SubElement(MessageSender, "PartyId").text = "PA-DPIDA-2025040901-M"
    PartyName = etree.SubElement(MessageSender, "PartyName")
    etree.SubElement(PartyName, "FullName").text = "Mkononi Limited"

    MessageRecipient = etree.SubElement(MessageHeader, "MessageRecipient")
    etree.SubElement(MessageRecipient, "PartyId").text = "PA-DPIDA-2025021301-D"
    PartyName = etree.SubElement(MessageRecipient, "PartyName")
    etree.SubElement(PartyName, "FullName").text = "Boomplay"

    etree.SubElement(MessageHeader, "MessageCreatedDateTime").text = time.strftime('%Y-%m-%dT%H:%M:%SZ')
    etree.SubElement(MessageHeader, "MessageControlType").text = "LiveMessage"

    ResourceList = etree.SubElement(NewReleaseMessage, "ResourceList")
    SoundRecording = etree.SubElement(ResourceList, "SoundRecording")
    etree.SubElement(SoundRecording, "SoundRecordingType").text = "MusicalWorkSoundRecording"
    SoundRecordingId = etree.SubElement(SoundRecording, "SoundRecordingId")
    etree.SubElement(SoundRecordingId, "ISRC").text = str(row['isrc_code'])

    resource_reference = f"A{random.randint(1000, 9999)}"
    etree.SubElement(SoundRecording, "ResourceReference").text = resource_reference

    ReferenceTitle = etree.SubElement(SoundRecording, "ReferenceTitle")
    etree.SubElement(ReferenceTitle, "TitleText").text = str(row['track_titles'])
    etree.SubElement(SoundRecording, "Duration").text = format_duration(row['duration'])

    # RightsAgreementId - Adding a dummy one for now
    RightsAgreementId = etree.SubElement(SoundRecording, "RightsAgreementId")
    etree.SubElement(RightsAgreementId, "ProprietaryId", attrib={"Namespace": "Boomplay"}).text = f"{random.randint(100000, 999999)}"

    # Adding SoundRecordingDetailsByTerritory
    SoundRecordingDetailsByTerritory = etree.SubElement(SoundRecording, "SoundRecordingDetailsByTerritory")
    etree.SubElement(SoundRecordingDetailsByTerritory, "TerritoryCode").text = "Worldwide"
    Title = etree.SubElement(SoundRecordingDetailsByTerritory, "Title")
    etree.SubElement(Title, "TitleText").text = str(row['track_titles'])
    DisplayArtist = etree.SubElement(SoundRecordingDetailsByTerritory, "DisplayArtist")
    PartyName = etree.SubElement(DisplayArtist, "PartyName")
    etree.SubElement(PartyName, "FullName").text = str(row['primary_artists'])
    etree.SubElement(DisplayArtist, "ArtistRole").text = "MainArtist"

    # Adding Composer
    if 'composer' in row:
        for composer in row.get('composer', '').split(';'):
            if composer:
                Contributor = etree.SubElement(SoundRecordingDetailsByTerritory, "Contributor")
                PartyName = etree.SubElement(Contributor, "PartyName")
                etree.SubElement(PartyName, "FullName").text = composer.strip()
                etree.SubElement(Contributor, "ContributorRole").text = "Composer"

    # Adding Producer
    if 'producer' in row:
        for producer in row.get('producer', '').split(';'):
            if producer:
                Contributor = etree.SubElement(SoundRecordingDetailsByTerritory, "Contributor")
                PartyName = etree.SubElement(Contributor, "PartyName")
                etree.SubElement(PartyName, "FullName").text = producer.strip()
                etree.SubElement(Contributor, "ContributorRole").text = "Producer"

    PLine = etree.SubElement(SoundRecordingDetailsByTerritory, "PLine")
    etree.SubElement(PLine, "Year").text = "2024"
    etree.SubElement(PLine, "PLineCompany").text = "Mkononi Limited"
    etree.SubElement(PLine, "PLineText").text = "℗ 2024 Mkononi Limited"
    etree.SubElement(SoundRecordingDetailsByTerritory, "ParentalWarningType").text = "NotExplicit"

    ReleaseList = etree.SubElement(NewReleaseMessage, "ReleaseList")
    Release = etree.SubElement(ReleaseList, "Release", attrib={"IsMainRelease": "true"})
    ReleaseId = etree.SubElement(Release, "ReleaseId")
    etree.SubElement(ReleaseId, "ICPN").text = str(row['upc_code'])
    etree.SubElement(Release, "ReleaseReference").text = "ReleaseRef1"

    ReferenceTitle = etree.SubElement(Release, "ReferenceTitle")
    etree.SubElement(ReferenceTitle, "TitleText").text = str(row['track_titles'])
    ReleaseResourceReferenceList = etree.SubElement(Release, "ReleaseResourceReferenceList")
    etree.SubElement(ReleaseResourceReferenceList, "ReleaseResourceReference").text = resource_reference

    ReleaseDetailsByTerritory = etree.SubElement(Release, "ReleaseDetailsByTerritory")
    etree.SubElement(ReleaseDetailsByTerritory, "TerritoryCode").text = "Worldwide"
    etree.SubElement(ReleaseDetailsByTerritory, "DisplayArtistName").text = str(row['primary_artists'])
    etree.SubElement(ReleaseDetailsByTerritory, "LabelName").text = "Mkononi Limited"
    Title = etree.SubElement(ReleaseDetailsByTerritory, "Title")
    etree.SubElement(Title, "TitleText").text = str(row['track_titles'])
    DisplayArtist = etree.SubElement(ReleaseDetailsByTerritory, "DisplayArtist")
    PartyName = etree.SubElement(DisplayArtist, "PartyName")
    etree.SubElement(PartyName, "FullName").text = str(row['primary_artists'])
    etree.SubElement(DisplayArtist, "ArtistRole").text = "MainArtist"
    etree.SubElement(ReleaseDetailsByTerritory, "IsMultiArtistCompilation").text = "false"
    etree.SubElement(ReleaseDetailsByTerritory, "ReleaseType").text = "Album"
    etree.SubElement(ReleaseDetailsByTerritory, "ParentalWarningType").text = str(row.get('parental_advisory', 'NotExplicit'))
    Genre = etree.SubElement(ReleaseDetailsByTerritory, "Genre")
    etree.SubElement(Genre, "GenreText").text = str(row.get('genre', 'Gospel'))
    if 'genre_code' in row:
        etree.SubElement(Genre, "GenreCode").text = str(row['genre_code'])

    etree.SubElement(ReleaseDetailsByTerritory, "ReleaseDate").text = time.strftime('%Y-%m-%d')

    etree.SubElement(Release, "Duration").text = format_duration(row['duration'])
    PLine = etree.SubElement(Release, "PLine")
    etree.SubElement(PLine, "Year").text = str(row.get('published_year', '2024'))
    etree.SubElement(PLine, "PLineCompany").text = "Mkononi Limited"
    etree.SubElement(PLine, "PLineText").text = f"℗ {row.get('published_year', '2024')} Mkononi Limited"
    CLine = etree.SubElement(Release, "CLine")
    etree.SubElement(CLine, "Year").text = str(row.get('copyright_year', '2024'))
    etree.SubElement(CLine, "CLineCompany").text = "Mkononi Limited"
    etree.SubElement(CLine, "CLineText").text = f"© {row.get('copyright_year', '2024')} Mkononi Limited"
    etree.SubElement(Release, "GlobalOriginalReleaseDate").text = time.strftime('%Y-%m-%d')

    tree = etree.ElementTree(NewReleaseMessage)
    xml_filename = os.path.join(resource_folder, f"{row['upc_code']}_{row['track_titles'].replace(' ', '_')}_{time.strftime('%Y%m%d')}.xml")
    tree.write(xml_filename, encoding='utf-8', xml_declaration=True, pretty_print=True)

    return xml_filename
 


