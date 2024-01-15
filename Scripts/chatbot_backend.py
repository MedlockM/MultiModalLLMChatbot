from flask import Flask, request, jsonify, render_template, session
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
import openai
import re
from link_scrapper import youtube2media
from utils import convert_video_to_mp3, transcript
from media_class import Media

# Configuration pour le téléchargement de fichiers
working_directory = os.getcwd()[:-8]
UPLOAD_FOLDER = working_directory + '/uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'mp4'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load your OpenAI API key from an environment variable or secret management service
load_dotenv()
openai.api_key = os.environ.get('OPENAI_KEY')
app.secret_key = os.environ.get('APP_SECRET_KEY')
default_input_language = os.environ.get('DEFAULT_INPUT_LANGUAGE')


@app.route('/')
def home():
    session['history'] = []  # Initialize the conversation history
    return render_template('index.html')

def add_history(message):
    session['history'].append(message)
    session.modified = True  # Assurez-vous d'ajouter cette ligne après avoir changé la session
@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json.get('input', '')
    if 'history' not in session:
        session['history'] = []
    add_history(f"User: {user_input}")

    # Vérifier si l'entrée est un lien YouTube.
    youtube_link_match = re.search(r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/watch\?v=([a-zA-Z0-9_-]+)', user_input)
    if youtube_link_match:
        youtube_url = youtube_link_match.group(0)
        # Appeler la fonction pour obtenir le transcript de la vidéo
        try:
            media_response = youtube2media(youtube_url, 'fr')  # or your preferred language
            if media_response.type_actuel == 'raw_text':
                chatbot_response = media_response.contenu_actuel
            else:
                chatbot_response = "I'm sorry, I cannot extract the text from this video."
        except Exception as e:
            chatbot_response = f"Error obtaining video transcript: {e}"
        add_history(f"User : {chatbot_response}")
        return jsonify({'response': chatbot_response})

    # Si ce n'est pas un lien YouTube, procéder normalement pour obtenir une réponse de GPT.
    # Maintenir l'historique pour le modèle GPT
    chat_history = " ".join(session['history'])
    try:
        print(chat_history)
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=chat_history,
            max_tokens=150
        )
        chatbot_response = response.choices[0].text.strip()
        add_history(f"System: {chatbot_response}")

    except Exception as e:
        chatbot_response = str(e)

    return jsonify({'response': chatbot_response})


# Function to check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_extension(filename):
    return filename[-3:]

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'response': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'response': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        # if get_file_extension(filename) == 'mp4':
        #     audio_media = convert_video_to_mp3(filepath)
        # else:
        audio_media = Media('audio', filepath, 'audio')
        print(audio_media.contenu_actuel)
        text_media = transcript(mp3_filepath=audio_media.contenu_actuel)
        add_history(f"User : {text_media.contenu_actuel}")
        return jsonify({'response': text_media.contenu_actuel}), 200
    else:
        return jsonify({'response': 'File type not allowed'}), 400

# @app.route('/set_language', methods=['POST'])
# def set_language():
#     global default_input_language
#     data = request.get_json()
#     language = data.get('language', default_input_language)
#     default_input_language = language
#     # Vous pouvez choisir de retourner la nouvelle valeur de la langue par défaut au client
#     return jsonify({'default_input_language': default_input_language})

if __name__ == '__main__':
    app.run(debug=True)
    languages_dict = {'English': 'en', 'French': 'fr', 'Spanish': 'es', 'German': 'de', 'Italian': 'it', 'Portuguese': 'pt'}
    languages_list = list(languages_dict.keys())

