import os

from flask import Blueprint, flash, g, request, render_template, redirect, url_for, current_app

from werkzeug.utils import secure_filename

from talkdict.auth import login_required

bp = Blueprint('upload', __name__, url_prefix='/upload')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXETENSIONS']

@bp.route('/', methods=['GET', 'POST'])
@login_required
def upload_file():
    current_app.logger.debug('In upload/upload_file')
    if request.method == 'POST':
        #check if the post request has the file part
        current_app.logger.debug(request)
        current_app.logger.debug(request.files)
        error = None
        if 'file' not in request.files:
            error = 'No file part'

        file = request.files['file']
        #if user does not select file, browser also submit an empty part without filename
        if file.filename == '':
            current_app.logger.debug("No selected file")
            error = 'No selected file'

        if file:
            if allowed_file(file.filename):
                current_app.logger.debug(f'{file.filename} is allowed')
                filename = secure_filename(file.filename)
                current_app.logger.debug(filename)
                current_app.logger.info( g.user['username'])
                userfolder = os.path.abspath(os.path.join(current_app.config['DICT_UPLOAD_FOLDER'], g.user['username']))
                try:
                    if not os.path.isdir(userfolder):
                        os.makedirs(userfolder)
                        current_app.logger.info(f'Create new folder for {g.user['username']} at {userfolder}.')
                except OSError:
                    error = '[OSError] Can not create user directory.'
                 

                file.save(os.path.abspath(os.path.join(userfolder, filename)))
                return redirect(url_for('table.show_table', filename = filename))
            else:
                error = 'File not allowed.'
        
        flash(error)
    return render_template('upload/upload.html')

from flask import send_from_directory
@bp.route('/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['DICT_UPLOAD_FOLDER'], filename)
