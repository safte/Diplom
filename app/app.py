from flask import Flask, request, render_template
from werkzeug.exceptions import HTTPException
import logging
from logging.handlers import RotatingFileHandler
import boto3
import os


app = Flask(__name__)

s3 = boto3.resource('s3')

UPLOAD_FOLDER = 'profile_pictures/'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def upload():
    """ Upload the main page """

    return render_template('index.html')


@app.route('/username')
def username():
    """ Upload the page to get profile picture """

    return render_template('username.html')


@app.route('/upload', methods=['POST'])
def upload_picture():
    """ Upload profile picture to remote storage """

    file = request.files['uploadedPicture']
    username = request.form['username']

    if not file:
        app.logger.error('File is not uploaded')

        return 'File is not uploaded', 404

    if not username:
        app.logger.error('Username field is empty')

        return 'Username field is empty', 404

    name = file.filename

    if allowed_file(name):
        s3.Bucket(os.environ['BUCKET_NAME']).put_object(Key=username +
                                                        extension(name),
                                                        Body=file)

        return render_template('username.html')
    else:
        app.logger.error('Unsupported file extension')

        return 'Unsupported file extension', 404


@app.route('/username', methods=['POST'])
def get_picture():
    """ Get profile picture from remote storage by username """

    username = request.form['username']

    if username:
        for bucket_obj in s3.Bucket(os.environ['BUCKET_NAME']).objects.all():
            if bucket_obj.key.startswith(username):
                s3_object = s3.Object(os.environ['BUCKET_NAME'],
                                      bucket_obj.key)
                s3_object.download_file(UPLOAD_FOLDER + bucket_obj.key)

        return render_template('index.html')
    else:

        return 'Username field is empty', 404


@app.route('/upload-multiple-files', methods=['POST'])
def upload_pictures():
    """ Upload profile pictures to remote storage """

    files = request.files.getlist("uploadedPictures")
    for file in files:
        if allowed_file(file.filename):
            s3.Bucket(os.environ['BUCKET_NAME']).put_object(Key=file.filename,
                                                            Body=file)
        else:
            app.logger.error('Unsupported file extension')

            return 'Unsupported file extension', 404

    return render_template('username.html')


@app.route('/delete', methods=['POST'])
def delete_pictures():
    """ Delete profile pictures from remote storage """

    s3.Bucket(os.environ['BUCKET_NAME']).objects.delete()

    return render_template('index.html')


@app.errorhandler(404)
def not_found_error(error):
    """ Error 404 """

    app.logger.error(error)

    return error


@app.errorhandler(500)
def internal_error(error):
    """ Error 500 """

    app.logger.error(error)

    return error


@app.errorhandler(Exception)
def exception_handler(error):
    """ All Errors """

    if isinstance(error, HTTPException):
        app.logger.error(error)

        return error

    app.logger.error('Something wrong')

    return 'Something wrong'


def allowed_file(filename: str) -> str:
    """ Check if file extension is supported """

    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def extension(filename: str) -> str:
    """ Get extension of uploaded file """

    extension = '.' + filename.rsplit('.')[-1]

    return extension


if __name__ == '__main__':
    handler = RotatingFileHandler('error.log', mode='a')

    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)

    app.logger.addHandler(handler)

    app.run(debug=True, host='0.0.0.0')  #
