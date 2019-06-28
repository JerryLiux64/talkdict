import os
import csv
from playsound import playsound
from gtts import gTTS
from flask import Flask, flash, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename

CWD = os.path.dirname(os.path.abspath(__file__))
DICT_UPLOAD_FOLDER = os.path.abspath(os.path.join(CWD, 'data'))
AUDIO_UPLOAD_FOLDER = os.path.abspath(os.path.join(DICT_UPLOAD_FOLDER, 'word_audio'))
ALLOWED_EXETENSIONS = set(['csv'])

if not os.path.isdir(DICT_UPLOAD_FOLDER):
    os.makedirs(DICT_UPLOAD_FOLDER, exist_ok=True)

if not os.path.isdir(AUDIO_UPLOAD_FOLDER):
    os.makedirs(AUDIO_UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['DICT_UPLOAD_FOLDER'] = DICT_UPLOAD_FOLDER
app.config['AUDIO_UPLOAD_FOLDER'] = AUDIO_UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXETENSIONS

def get_table_text(filename):
    with open(f'./data/{filename}', 'r', encoding = 'utf8') as f:
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
    filepath = os.path.abspath(os.path.join(app.config['AUDIO_UPLOAD_FOLDER'], f'{word}.mp3'))
    if not os.path.isfile(filepath):
        tts = gTTS(word)
        tts.save(filepath)
    playsound(filepath)
                
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        #check if the post request has the file part
        app.logger.debug(request)
        app.logger.debug(request.files)
        error = None
        if 'file' not in request.files:
            error = 'No file part'

        file = request.files['file']
        #if user does not select file, browser also submit an empty part without filename
        if file.filename == '':
            app.logger.debug("No selected file")
            error = 'No selected file'

        if file:
            if allowed_file(file.filename):
                app.logger.debug(f'{file.filename} is allowed')
                filename = secure_filename(file.filename)
                app.logger.debug(filename)
                file.save(os.path.join(app.config['DICT_UPLOAD_FOLDER'], filename))
                return redirect(url_for('show_table', filename = filename))
                # return '', 204
            else:
                error = 'File not allowed.'
        
        flash(error)
    return render_template('upload.html')

@app.route('/table/<filename>')
def show_table(filename):
    text = get_table_text(filename)
    return render_template('talkdict.html', filename = filename, text = text)

@app.route('/tts', methods=['GET','POST'])
def text_to_speech():
    if request.method == 'POST':
        word = request.form.get('word', type=str)
    if request.method == 'GET':
        word = request.args.get('word', type=str)
    app.logger.debug(word)
    get_text_audio(word)
    return '', 204

from flask import send_from_directory
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['DICT_UPLOAD_FOLDER'], filename)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)