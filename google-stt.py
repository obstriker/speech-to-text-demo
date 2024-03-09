import typer
import os
from google.cloud import speech
from google.cloud import storage
from pydub import AudioSegment
from bidi.algorithm import get_display

g_blob_path = "demo/audio-files/"
g_bucket_name = "demo-speechless"

class SpeechToTextProcessor:
    def __init__(self):
        # Consider using environment variables for credentials
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account_google.json"

        self.client = speech.SpeechClient()
        
    def convert_mp3_to_flac(self, mp3_file_path, flac_file_path):
        """Converts an MP3 file to FLAC format."""
        audio_file = AudioSegment.from_mp3(mp3_file_path)
        audio_file.export(flac_file_path, format="flac")

    def upload_blob(self, bucket_name, source_file_name, destination_blob_name):
        """Uploads a file to the Cloud Storage bucket."""
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        print(f"File {source_file_name} uploaded to {destination_blob_name}.")

    def generate_text(self, input_file=None, gs_uri=None):
        """Generates text transcript from audio."""
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
            audio_channel_count=2,  # Specify audio channel count explicitly
            language_code="he-IL",
        )
        if gs_uri:
            audio = speech.RecognitionAudio(uri=gs_uri)
        elif input_file:
            with open(input_file, "rb") as audio_file:
                content = audio_file.read()
                audio = speech.RecognitionAudio(content=content)
        else:
            return
        response = self.client.long_running_recognize(config=config, audio=audio)
        return response

app = typer.Typer()

@app.command()
def transcribe(
    input_file: str = typer.Option(
        ..., help="Path to the local MP3 file for transcription."
    ),
    bucket_name: str = typer.Option(
        g_bucket_name, help="Name of the Google Cloud Storage bucket for uploaded FLAC file."
    ),
    blob_path: str = typer.Option(
        g_blob_path, help="Destination path of the uploaded FLAC file within the bucket."
    ),
):
    """Transcribes audio from an MP3 file and returns the text."""
    processor = SpeechToTextProcessor()

    # Convert MP3 to FLAC and upload to Cloud Storage
    # Check with checksum if the media is present, if it does dont upload it again
    flac_file = f"{os.path.basename(input_file)[:-4]}.flac"  # Generate FLAC filename from MP3
    processor.convert_mp3_to_flac(input_file, flac_file)
    processor.upload_blob(bucket_name, flac_file, blob_path + flac_file)

    # Generate text transcript from uploaded FLAC
    gs_uri = f"gs://{bucket_name}/{blob_path}{flac_file}"
    text_response = processor.generate_text(gs_uri=gs_uri).result()

    for chunk in text_response.results:
        print(get_display(chunk.alternatives[0].transcript))
    # Process text_response as needed (e.g., print results)
    # ...

    # print time took to process the audio
    # Add support for mp4
    # Conversion from mp4 doesnt work

if __name__ == "__main__":
    app()