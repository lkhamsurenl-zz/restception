from flask import Flask, request
from flask.ext.restful import Api as FlaskRestfulAPI, Resource, reqparse, abort
from werkzeug.datastructures import FileStorage
from werkzeug import secure_filename

from cStringIO import StringIO
import json, os
import sys
import subprocess

UPLOAD_FOLDER = '/Users/lkhamsurenl/Development/restception/images'

## config
ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']
FILE_CONTENT_TYPES = { # these will be used to set the content type of S3 object. It is binary by default.
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png'
}

## app initilization
app = Flask(__name__)
app.config.from_object(__name__)

## extensions
api = FlaskRestfulAPI(app)


class FileStorageArgument(reqparse.Argument):
    """This argument class for flask-restful will be used in
    all cases where file uploads need to be handled."""
    
    def convert(self, value, op):
        if self.type is FileStorage:  # only in the case of files
            # this is done as self.type(value) makes the name attribute of the
            # FileStorage object same as argument name and value is a FileStorage
            # object itself anyways
            return value

        # called so that this argument class will also be useful in
        # cases when argument type is not a file.
        super(FileStorageArgument, self).convert(*args, **kwargs)

class UploadImage(Resource):

    put_parser = reqparse.RequestParser(argument_class=FileStorageArgument)
    put_parser.add_argument("image", required=True, type=FileStorage, location='files')

    def get(self):
    	args = self.put_parser.parse_args()
        image = args["image"]

    	return json.dumps({'hello': 'world'})

    def post(self):
        args = self.put_parser.parse_args()
        image = args["image"]

        filename = secure_filename(image.filename)
        fullpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        mode = 'a' if os.path.exists(fullpath) else 'w'
        with open(fullpath, mode) as f:
            image.save(fullpath)

        # Run the algorithm here to classify the image.
        output = []
        labels = subprocess.check_output([sys.executable, "classify_image.py", \
            "--image_file", fullpath])
        labels = labels.split('\n')
        for label in labels:
            label = label.split("=")
            if len(label) == 2: # It is a valid text: score pair.
                output.append({'name': label[0], 'score': label[1]})

        return json.dumps(output)


api.add_resource(UploadImage, '/upload')


if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', debug=True)
