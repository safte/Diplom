from flask import Flask, request, jsonify, abort, make_response, Response
import logging
from logging.handlers import RotatingFileHandler
import boto3
import os

app = Flask(__name__)

s3 = boto3.resource('s3')

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}


@app.route('/', methods=['POST', 'GET', 'DELETE'])
def process_picture():
    """ Upload, download and delete profile picture from remote storage """

    # Upload picture to remote storage
    if request.method == 'POST':
        if bucket_exists(s3.Bucket(os.environ['BUCKET'])):
            files = request.files.getlist('file')
            if len(files) > 0:
                for file in files:
                    fname = file.filename

                    if allowed_file(fname):
                        s3.Bucket(os.environ['BUCKET']).put_object(Key=fname,
                                                                   Body=file)
                    else:
                        return jsonify(status='Unsupported file extension')

                return jsonify(status='Uploaded')
            return jsonify(status='No username entered')
        else:
            bad_response('The bucket does not exist', 404)

    # Download picture from remote storage
    if request.method == 'GET':
        if bucket_exists(s3.Bucket(os.environ['BUCKET'])):
            name = request.form.get('name')

            if name is not None:
                for object in s3.Bucket(os.environ['BUCKET']).objects.all():
                    if object.key.startswith(name):
                        s3_object = s3.Object(os.environ['BUCKET'], object.key)

                        return Response(s3_object.get()['Body'].read())
        else:
            bad_response('The bucket does not exist', 404)

    # Delete picture from remote storage
    if request.method == 'DELETE':
        if bucket_exists(s3.Bucket(os.environ['BUCKET'])):
            name = request.form.get('name')

            if name is not None:
                for object in s3.Bucket(os.environ['BUCKET']).objects.all():
                    if object.key.startswith(name):
                        s3.Object(os.environ['BUCKET'], object.key).delete()

                        return jsonify(status=object.key + ' deleted')

                return jsonify(status='No such user')
            return jsonify(status='No username entered')
        else:
            bad_response('The bucket does not exist', 404)

    return make_response('200')


@app.route('/delete-all-pictures', methods=['DELETE'])
def delete_pictures():
    """ Delete all profile pictures from remote storage """

    if bucket_exists(s3.Bucket(os.environ['BUCKET'])):
        s3.Bucket(os.environ['BUCKET']).objects.delete()

        return jsonify(status='Pictures deleted')
    else:
        bad_response('The bucket does not exist', 404)


@app.errorhandler(Exception)
def exception_handler(error):
    """ Any Errors """

    app.logger.error(error)

    return jsonify(error='Something wrong')


def bucket_exists(bucket: str):
    """ Check if S3 Bucket exists """

    if bucket.creation_date is None:
        return False
    else:
        return True


def bad_response(message: str, code: int):
    """ Handle errors """

    app.logger.error(message)

    abort(make_response(jsonify(error=message), code))


def allowed_file(filename: str):
    """ Check if file extension is supported """

    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    handler = RotatingFileHandler('/var/log/pp.log', mode='a')

    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)

    app.logger.addHandler(handler)

    app.run(host='0.0.0.0')
