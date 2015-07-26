'''
Code largely taken from:
http://runnable.com/UiPcaBXaxGNYAAAL/how-to-upload-a-file-to-the-server-in-flask-for-python
'''
import os
from uuid import uuid4

from flask import Flask, render_template, request, redirect, url_for
from flask.helpers import send_from_directory
from werkzeug.utils import secure_filename

from Logger import logger
from controller import Controller
import string_constants


logger.info("Starting server")
app = Flask(__name__)
controlr = Controller()

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation


@app.route("/")
def index():
    return render_template(string_constants.file_homepage)


@app.errorhandler(500)
def internal_server_error(e):
    logger.error(e)

    return render_template(string_constants.file_errorpage), 500

# Route that will process the file upload


@app.route("/upload", methods=['POST'])
def upload():

    file = request.files['file']

    if controlr.supportsFile(file.filename):
        # Make the filename safe, remove unsupported chars
        #safe_filename = secure_filename(file.filename)

        # save filename as guid, helps parallel sessions and accessing info for
        # error analysis
        extension = file.filename.rsplit(".", 1)[1]
        safe_filename = str(uuid4())+"."+extension
        server_file_path = os.path.join(
            string_constants.folder_upload, safe_filename)

        # Move the file form the temp folder to the upload folder
        file.save(server_file_path)

        expanded_acronyms = controlr.processFile(safe_filename)

        output_file_path = os.path.join(
            string_constants.folder_output, controlr.getOutputFilename(safe_filename))
        controlr.writeOutputToFile(expanded_acronyms, output_file_path)

        return redirect(url_for('output_file', filename=controlr.getOutputFilename(safe_filename)))

# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(string_constants.folder_upload, filename)


@app.route("/output/<filename>")
def output_file(filename):
    logger.info(string_constants.folder_output + filename)

    return send_from_directory(string_constants.folder_output, filename)


def main():
    app.run(debug=False, host='0.0.0.0', port=80)
    logger.info("Server is ready")
if __name__ == "__main__":
    main()
