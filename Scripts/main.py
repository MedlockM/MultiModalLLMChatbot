import openai
from link_scrapper import *
from summarizer import Summarizer

video_filepath = r"C:\Users\marc.medlock\Downloads/VID-20231030-WA0007.mp4"

media = convert_video_to_mp3(video_filepath)

summarizer = Summarizer(openai.api_key, 'medium', 'gpt-3.5-turbo-16k', 'en', 'en')

media_transcript = summarizer.transcript(media.contenu_actuel)

media_summarize = summarizer.summarize(media_transcript.contenu_actuel)

with open(r'C:\Users\marc.medlock\OneDrive - Accenture\Desktop\Listener-Summarizer\Transcripts/video_mp4_sumup.txt', "w",
          encoding="utf-8") as txt:
    txt.write(media_summarize.contenu_actuel)

url = 'https://www.youtube.com/watch?v=4BibQ69MD8c'

summarizer = Summarizer('medium', 'gpt-4-1106-preview', 'en', 'en')

media_transcript = youtube2media(url, summarizer.output_language)

media_summarized = summarizer.summarize(media_transcript.contenu_actuel)

with open(r'C:\Users\marc.medlock\OneDrive - Accenture\Desktop\Listener-Summarizer\Transcripts/devops_transcript.txt', "w",
          encoding="utf-8") as txt:
    txt.write(media_summarized.contenu_actuel)
