from openai import OpenAI

api_key = os.environ.get("OPENAI_API_KEY")
api_key = "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"


client = OpenAI(api_key=api_key)

audio_file= open("ira_short.mp3", "rb")
transcription = client.audio.transcriptions.create(
  model="whisper-1", 
  file=audio_file,
  response_format="srt"
)
print(transcription.text)