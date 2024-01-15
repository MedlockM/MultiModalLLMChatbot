import os
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
from media_class import Media
from youtube_transcript_api._errors import TranscriptsDisabled
import os
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import spotipy
import requests
import urllib.parse
from spotipy.oauth2 import SpotifyClientCredentials
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
from moviepy.editor import VideoFileClip

# Function to convert a video to an MP3 file

def youtube2media(url, requested_language):
    """
    Convert a YouTube video into a Media object with a transcript or audio.

    Args:
        url (str): The URL of the YouTube video.
        requested_language (str): The desired language for the transcript or translation.

    Returns:
        Media: A Media object containing either the transcript or audio file.
    """

    def concatenate_text_from_dicts(data):
        """
        Concatenate text from a list of dictionaries.

        Args:
            data (list): List of dictionaries containing 'text' key.

        Returns:
            str: Concatenated text.
        """
        concatenated_text = ""

        for item in data:
            concatenated_text += item['text'] + " "

        return concatenated_text.strip()

    # Find the video ID in the YouTube URL
    index = url.find("watch?v=")
    video_id = url[index + len("watch?v="):]

    # List available transcripts for the video
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        print('----- some transcripts available -------\n', transcript_list )
        print('and translations :', [available_trsl['language_code'] for transcript in transcript_list for available_trsl in
              transcript.translation_languages])
        # Check if a transcript is available in the requested language
        transcript_in_language = [transcript for transcript in transcript_list if
                                  transcript.language_code == requested_language]
        if len(transcript_in_language) > 0:
            print('------- transcript available in requested language -------')
            transcript = transcript_in_language[0].fetch()
            transcript_text_formatted = concatenate_text_from_dicts(transcript)
            print(transcript_text_formatted)
            return Media('video', transcript_text_formatted, 'raw_text')

        # Check if a translation is available in the requested language
        print([available_trsl['language_code'] for transcript in transcript_list for available_trsl in
              transcript.translation_languages])
        if requested_language in [available_trsl['language_code'] for transcript in transcript_list for available_trsl in
                                  transcript.translation_languages]:
            print('----- no transcript available in requested language but translation available ------')
            transcript_list_filtered = [transcript for transcript in transcript_list if requested_language in
                                        [trsl['language_code'] for trsl in transcript.translation_languages]]
            transcript = transcript_list_filtered[0]
            print(transcript.is_translatable)
            translated_transcript = transcript.translate(requested_language).fetch()
            print(translated_transcript)
            trsl_transcript_text_formatted = concatenate_text_from_dicts(translated_transcript)
            print(trsl_transcript_text_formatted)
            return Media('video', trsl_transcript_text_formatted, 'raw_text')
        else:
            print('no transcript neither translation available in requested language, translating with language model...')
            print(transcript_list)
            # TODO: Translate the script using a language model

    except TranscriptsDisabled:
        print('no transcript available, mp3 downloading...')
        # Create output folder if it doesn't exist
        os.makedirs('../tempMP3', exist_ok=True)

        # Initialize a YouTube object
        yt = YouTube(url)

        # Select the highest quality audio stream
        audio_stream = yt.streams.filter(only_audio=True).first()

        # Download the audio stream as MP3
        audio_stream.download(output_path='../tempMP3', filename=yt.title + '.mp3')

        return Media('video', yt.title + '.mp3', 'audio')

class CustomWebElement:

    def __init__(self, web_attribute_type, web_attribute_value, action_type, action_value):
        self.web_attribute_type = web_attribute_type
        self.web_attribute_value = web_attribute_value
        self.action_type = action_type
        self.action_value = action_value

    def do_action_on_elem(self, web_element):
        print(f'trying {self.action_type} with {self.action_value}')
        if self.action_type == 'click':
            web_element.click()
        elif self.action_type == 'fill':
            web_element.send_keys(self.action_value)

class SpotifyWebAutomation:

    def __init__(self, url, client_id, client_secret):
        self.driver = webdriver.Chrome()
        self.url = url
        self.driver.get(url)
        self.client_id = client_id
        self.client_secret = client_secret

    def find_element_by_attribute_value(self, custom_element):
        # Initialize a WebDriver (in this case, using Chrome)

        # Construct an XPath expression to find elements with the specified attribute
        xpath = f"//*[contains(@{custom_element.web_attribute_type}, '{custom_element.web_attribute_value}')]"
        elements = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath)))

        return elements

    def find_transcript(self):

        element1 = CustomWebElement('data-testid', 'login-button', 'click', '1')
        element2 = CustomWebElement('id', 'login-username', 'fill', self.client_id)
        element3 = CustomWebElement('id', 'login-password', 'fill', self.client_secret)
        element4 = CustomWebElement('class', 'Type__TypeElement-sc-goli3j-0 cOJqPq sc-jSUZER sc-gKPRtg hJfyeq hgatVV', 'click', '1')
        element5 = CustomWebElement('id', 'onetrust-reject-all-handler', 'click', '1')
        element6 = CustomWebElement('class', 'Link-sc-1g2blu2-0 VkYMJ QiHXpFb4dLZNOFe5gpp3', 'click', '1')
        element7 = CustomWebElement('class', 'NavBar__NavBarPage-sc-1guraqe-0 ejVULV', 'Return', '1')

        elements = [element1, element2, element3, element4, element5, element6, element7]

        for custom_elem in elements:
            # TODO verify captcha presence
            print(f'trying to find elem with attr {custom_elem.web_attribute_type} and value {custom_elem.web_attribute_value}')
            elem = self.find_element_by_attribute_value(custom_elem)
            print(f'elem found')
            try:
                custom_elem.do_action_on_elem(elem)
            except ElementClickInterceptedException:
                print('need to scroll down to show element')
                self.driver.execute_script("arguments[0].scrollIntoView();", elem)
                custom_elem.do_action_on_elem(elem)

        # Get all the sub-elements containing text within the big element
        sub_elements = elem.find_elements(By.XPATH, ".//span[@data-encore-id='type']")

        # Loop through the sub-elements and extract their text
        text_content = [sub_element.text for sub_element in sub_elements]

        result_string = ' '.join(text_content)

        return Media('audio', result_string, 'raw_text')

    def download_as_mp3(self):
        # TODO: from a spotify url to a mp3 filename
        return

if __name__ == '__main__':
    print(youtube2media('https://www.youtube.com/watch?v=-lXvFrHxIK8', 'fr'))
    # video_test_path = '../videos/video1.mp4'
    # print(convert_video_to_mp3(video_test_path).contenu_actuel)
    # from dotenv import load_dotenv
    #
    # load_dotenv()
    # client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    # client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
    # url = "https://open.spotify.com/episode/6pmbVygCb3EA7orGr5rwkC?si=xqpsZ_2rTAKTUs3Y1GcvUA&nd=1"
    #
    # spot = SpotifyWebAutomation(url, client_id, client_secret)
    # print(spot.find_transcript().contenu_actuel)