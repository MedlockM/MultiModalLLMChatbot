import whisper
import numpy as np
from pydub import AudioSegment
from pydub import AudioSegment

# Set the path to the FFmpeg executable
AudioSegment.converter = r"C:\Users\marc.medlock\OneDrive - Accenture\Desktop\Listener-Summarizer\Scripts\ffmpeg.exe"
# Input .opus file
input_file = r"C:\Users\marc.medlock\OneDrive - Accenture\Desktop\Listener-Summarizer\opus_files\flex_audio_22012024.ogg"

# Output file format (e.g., "mp3", "wav", "ogg", etc.)
output_filename = "flex_audio_22012024.mp3"

# Load the .opus file
audio = AudioSegment.from_file(input_file, format="ogg")

# Convert and save the audio in the desired format
output_filepath = r"C:\Users\marc.medlock\OneDrive - Accenture\Desktop\Listener-Summarizer\tempMP3/" + output_filename
audio.export(output_filepath, format="mp3")

# print(f"File converted and saved as {output_filename}")
# # Load the Whisper model
# model = whisper.load_model("medium", download_root="../model/")
# input_format = '.mp3'
# output_format = '.txt'
# abs_path = r'/tempMP3/'
#
# responses = []
# for input_filename in ['flex_audio_22012024.ogg']:
#
#
#     response = model.transcribe(
#         audio=abs_path+input_filename+input_format,
#         language="en",  # Adjust the language code as needed
#         fp16=False
#     )
#     responses.append(response['text'])
#
# result_text = '\n \n'.join(responses)
#
# with open(r"C:\Users\marc.medlock\OneDrive - Accenture\Desktop\Listener-Summarizer\Transcripts/" + "alex_transcript_22012024" + output_format, "w",
#           encoding="utf-8") as txt:
#     txt.write(result_text)

