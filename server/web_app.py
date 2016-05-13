'''
Code largely taken from:
http://runnable.com/UiPcaBXaxGNYAAAL/how-to-upload-a-file-to-the-server-in-flask-for-python
'''
import os
from uuid import uuid4

from flask import Flask, render_template, request, redirect, url_for
from flask.helpers import send_from_directory

from AcronymExtractors.AcronymExtractor_v1 import AcronymExtractor_v1
from DataCreators import ArticleDB, AcronymDB
from Logger import common_logger
from TextExtractors.Extract_PdfMiner import Extract_PdfMiner
from AcronymDisambiguator import AcronymDisambiguator
import string_constants
from AcronymExpanders import AcronymExpanderEnum
from sklearn.externals import joblib
from string_constants import file_vectorizer


common_logger.info("Starting server")
app = Flask(__name__)


common_logger.info("Initializing AcronymDisambiguator")
articleDB = ArticleDB.load()
acronymDB = AcronymDB.load()
disambiguator = AcronymDisambiguator(text_extractor=Extract_PdfMiner(),
                      acronym_extractor=AcronymExtractor_v1(),
                      expanders=[AcronymExpanderEnum.fromText_v2,
                                 AcronymExpanderEnum.Tfidf_multiclass],
                      articleDB=articleDB,
                      acronymDB=acronymDB,
                      vectorizer=joblib.load(file_vectorizer))


# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation


@app.route("/")
def index():
    return render_template(string_constants.file_homepage)


@app.errorhandler(500)
def internal_server_error(e):
    common_logger.error(e)

    return render_template(string_constants.file_errorpage), 500

# Route that will process the file upload


@app.route("/upload", methods=['POST'])
def upload():

    uploaded_file = request.files["file"]

    if disambiguator.supportsFile(uploaded_file.filename):
        # Make the filename safe, remove unsupported chars
        #safe_filename = secure_filename(uploaded_file.filename)

        # save filename as guid, helps parallel sessions and accessing info for
        # error analysis
        extension = uploaded_file.filename.rsplit(".", 1)[1]
        safe_filename = str(uuid4()) + "." + extension
        server_file_path = os.path.join(
            string_constants.folder_upload, safe_filename)

        # Move the uploaded_file form the temp folder to the upload folder
        uploaded_file.save(server_file_path)

        text = disambiguator.extractText(safe_filename)
        expanded_acronyms = disambiguator.processText(text)

        output_file_path = os.path.join(
            string_constants.folder_output, disambiguator.getOutputFilename(safe_filename))
        disambiguator.writeOutputToFile(expanded_acronyms, output_file_path)

        return redirect(url_for('output_file', filename=disambiguator.getOutputFilename(safe_filename)))

# This route is expecting a parameter containing the name
# of a uploaded_file. Then it will locate that uploaded_file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(string_constants.folder_upload, filename)


@app.route("/output/<filename>")
def output_file(filename):
    common_logger.info(string_constants.folder_output + filename)

    return send_from_directory(string_constants.folder_output, filename)


def main():
    app.run(debug=False, host='0.0.0.0', port=80)
    common_logger.info("Server is ready")
if __name__ == "__main__":
    main()
