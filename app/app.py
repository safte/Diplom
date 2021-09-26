from flask import Flask, request, jsonify, abort, make_response
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


@app.route('/', methods=['POST', 'GET'])
def upload_picture():
    """ Upload profile picture to remote storage """

    if 'name' not in request.form:
        app.logger.error('Username field is empty')

        abort(make_response(jsonify(error='Username field is empty'), 404))

    username = request.form['name']

    if request.method == 'POST':
        if 'file' not in request.files:
            app.logger.error('File is not uploaded')

            abort(make_response(jsonify(error='File is not uploaded'), 404))

        file = request.files['file']
        fname = request.files['file'].filename

        if allowed_file(fname):
            s3.Bucket(os.environ['BUCKET_NAME']).put_object(Key=username +
                                                            extension(fname),
                                                            Body=file)

            return jsonify(file=username + extension(fname), status=200)
        else:
            app.logger.error('Unsupported extension')

            abort(make_response(jsonify(error='Unsupported extension'), 404))

    if request.method == 'GET':

        for bucket_obj in s3.Bucket(os.environ['BUCKET_NAME']).objects.all():
            if bucket_obj.key.startswith(username):
                s3_object = s3.Object(os.environ['BUCKET_NAME'],
                                      bucket_obj.key)
                s3_object.download_file(UPLOAD_FOLDER + bucket_obj.key)

        return jsonify(file=bucket_obj.key, status=200)


@app.route('/upload-multiple-files', methods=['POST'])
def upload_pictures():
    """ Upload profile pictures to remote storage """

    files = request.files.getlist("file")
    for file in files:
        if allowed_file(file.filename):
            s3.Bucket(os.environ['BUCKET_NAME']).put_object(Key=file.filename,
                                                            Body=file)
        else:
            app.logger.error('Unsupported file extension')

            abort(make_response(jsonify(error='Unsupported extension'), 404))

    return jsonify(type(files), status=200)


@app.route('/delete', methods=['POST'])
def delete_pictures():
    """ Delete profile pictures from remote storage """

    if 'name' not in request.form:
        s3.Bucket(os.environ['BUCKET_NAME']).objects.delete()

    else:
        username = request.form['name']
        for bucket_obj in s3.Bucket(os.environ['BUCKET_NAME']).objects.all():
            if bucket_obj.key.startswith(username):
                s3.Object(os.environ['BUCKET_NAME'], bucket_obj.key).delete()

    return jsonify(status='Pictures deleted')


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
