import typer
from openai import OpenAI
from dotenv import load_dotenv
import os
from moviepy.editor import AudioFileClip
import math  # for ceiling function

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

app = typer.Typer()

def chunk_audio(audio_file, chunk_size_mb):
    """Chunks an audio file into smaller files based on the specified size in MB.

    Args:
        audio_file: Path to the audio file.
        chunk_size_mb: Size of each chunk in Megabytes.

    Returns:
        List of chunk filenames.
    """

    audio = AudioFileClip(audio_file)
    duration = audio.duration
    file_size = os.path.getsize(audio.filename)

    # Calculate total chunks (considering potential remainder)
    total_chunks = math.ceil(file_size / (chunk_size_mb * 1024 * 1024))

    chunks = []
    start = 0
    for chunk_number in range(total_chunks):
        # Calculate chunk duration based on fraction of total duration
        chunk_duration = duration * (chunk_size_mb * 1024 * 1024) / file_size

        # Adjust end for last chunk to avoid exceeding audio duration
        end = min(start + chunk_duration, duration)
        chunk = audio.subclip(start, end)
        chunk_filename = f"{audio_file.split('.')[0]}_chunk_{start}.mp3"
        chunk.write_audiofile(chunk_filename)
        chunks.append(chunk_filename)
        start = end

    return chunks


def transcribe_chunks(chunks):
    """Transcribes each audio chunk using OpenAI's Whisper model.

    Args:
        chunks: List of chunk filenames.

    Returns:
        List of chunk transcripts.
    """

    transcriptions = []
    for chunk in chunks:
        with open(chunk, "rb") as f:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="srt",
            )
        transcriptions.append(transcription.text)
    return transcriptions


@app.command(help="Transcribe a chunked audio file using OpenAI's Whisper model.")
def transcribe(audio_file: str, chunk_size_mb: float = 25):
    """Transcribes the specified audio file in chunks and combines the transcripts.

    Args:
        audio_file: Path to the audio file.
        chunk_size_mb: Size of each chunk in Megabytes (default: 25).
    """

    chunks = chunk_audio(audio_file, chunk_size_mb)
    transcriptions = transcribe_chunks(chunks)

    # Combine and print transcripts
    combined_transcript = "\n".join(transcriptions)
    print(combined_transcript)

    # Clean up temporary chunks (optional)
    for chunk in chunks:
        os.remove(chunk)


if __name__ == "__main__":
    app()
