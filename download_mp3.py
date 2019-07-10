import os
from flask import Blueprint, g, request, current_app, send_file

bp = Blueprint('download', __name__, url_prefix='/download')

@bp.route('')
def download():
    if request.method == 'GET':
        audio = request.args.get('audio', type=str)
    current_app.logger.debug(audio)
    filepath = os.path.abspath(os.path.join(current_app.config['AUDIO_UPLOAD_FOLDER'], audio))
    if not os.path.isfile(filepath):
        return "", 404

    return send_file(filepath, mimetype='audio/mpeg', as_attachment=True)