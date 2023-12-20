import os

import whisper
from media_class import Media
from moviepy.editor import VideoFileClip

def transcript(mp3_filepath, input_language='fr', transcripter_model_ref='base'):
    model = whisper.load_model(transcripter_model_ref, download_root="../model/")
    response = model.transcribe(
        audio=mp3_filepath,
        language=input_language,  # Adjust the language code as needed
        fp16=False
    )
    return Media("audio", response['text'], 'raw_text')

def convert_video_to_mp3(video_filepath):
    cd = os.getcwd()[:-8]
    mp3_dir = cd+'/tempMP3/'
    video_clip = VideoFileClip(video_filepath)
    audio_clip = video_clip.audio
    mp3_output_filepath = os.path.join(mp3_dir, os.path.splitext(os.path.basename(video_filepath))[0] + ".mp3")
    print("mp3 output filepath", mp3_output_filepath)
    audio_clip.write_audiofile(mp3_output_filepath)
    return Media("video", mp3_output_filepath, "audio")

if __name__ == '__main__':
    convert_video_to_mp3(r'C:\Users\marc.medlock\OneDrive - Accenture\Desktop\Listener-Summarizer\uploads\video_40secs_test.mp4')