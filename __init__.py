import os

from flask import Flask, redirect, url_for

def create_app(test_config=None):
    CWD = os.path.dirname(os.path.abspath(__file__))
    DICT_UPLOAD_FOLDER = os.path.abspath(os.path.join(CWD, 'data'))
    AUDIO_UPLOAD_FOLDER = os.path.abspath(os.path.join(DICT_UPLOAD_FOLDER, 'word_audio'))
    ALLOWED_EXETENSIONS = set(['csv'])
        
    if not os.path.isdir(DICT_UPLOAD_FOLDER):
        os.makedirs(DICT_UPLOAD_FOLDER, exist_ok=True)

    if not os.path.isdir(AUDIO_UPLOAD_FOLDER):
        os.makedirs(AUDIO_UPLOAD_FOLDER, exist_ok=True)

    app = Flask(__name__, instance_relative_config=True)
    app.config['ALLOWED_EXETENSIONS'] = ALLOWED_EXETENSIONS
    app.config['DICT_UPLOAD_FOLDER'] = DICT_UPLOAD_FOLDER
    app.config['AUDIO_UPLOAD_FOLDER'] = AUDIO_UPLOAD_FOLDER
    app.config['SECRET_KEY'] = os.urandom(55)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config.from_mapping(
        SECRET_KEY= os.urandom(32),
        DATABASE=os.path.join(app.instance_path, 'talkdict.sqlite'),
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import auth
    app.register_blueprint(auth.bp)

    from . import upload
    app.register_blueprint(upload.bp)

    from . import showtable
    app.register_blueprint(showtable.bp)

    from . import download_mp3
    app.register_blueprint(download_mp3.bp)
    # Unlike the auth blueprint, the blog blueprint does not have a url_prefix. So the index view will be at '/'
    # app.add_url_rule() associates the endpoint name 'index' with the / url so that url_for('index') or url_for('blog.index') will both work, generating the same / URL either way.
    # app.add_url_rule('/', endpoint='upload_file')
    @app.route('/')
    def index():
        return redirect(url_for('upload.upload_file'))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)