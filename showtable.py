import os
import csv
from flask import Blueprint, g, request, render_template, current_app
from gtts import gTTS

bp = Blueprint('table', __name__, url_prefix='/table')

def get_table_text(filename):
    # f'./data/{filename}'
    current_app.logger.debug(current_app.config['DICT_UPLOAD_FOLDER'])
    filepath = os.path.abspath(os.path.join(current_app.config['DICT_UPLOAD_FOLDER'], filename))
    with open(filepath, 'r', encoding = 'utf8') as f:
        csv_reader = csv.reader(f, delimiter=',')
        line = 0
        text = ""
        text += '<table>'
        for row in csv_reader:
            text += '<tr>'
            for cell in row:
                text += f'<td onclick="sayword(this)">{cell}</td>'
            text += '</tr>'
        text += '</table>'
    return text

def get_text_audio(word):
    filepath = os.path.abspath(os.path.join(current_app.config['AUDIO_UPLOAD_FOLDER'], f'{word}.mp3'))
    if not os.path.isfile(filepath):
        tts = gTTS(word)
        tts.save(filepath)
    # playsound(filepath)
    return filepath

@bp.route('/<filename>')
def show_table(filename):
    text = get_table_text(filename)
    return render_template('talkdict/talkdict.html', filename = filename, text = text)

@bp.route('/tts', methods=['GET','POST'])
def text_to_speech():
    if request.method == 'POST':
        word = request.form.get('word', type=str)
    if request.method == 'GET':
        word = request.args.get('word', type=str)
    current_app.logger.debug(word)
    filepath = get_text_audio(word)
    return f"/download?audio={word}.mp3"
    # return "", 204


