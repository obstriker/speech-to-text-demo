import typer
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

app = typer.Typer()


@app.command(help="Transcribe an audio file using OpenAI's Whisper model.")
def transcribe(audio_file: str):
    """Transcribes the specified audio file and prints the text content."""

    with open(audio_file, "rb") as f:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="srt"
        )

    print(transcription.text)


if __name__ == "__main__":
    app()