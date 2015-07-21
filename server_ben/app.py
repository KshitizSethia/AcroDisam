'''
Code largely taken from:
http://runnable.com/UiPcaBXaxGNYAAAL/how-to-upload-a-file-to-the-server-in-flask-for-python
'''


import os
import acronymvark
# We'll render HTML templates and access data sent by POST
# using the request object from flask. Redirect and url_for
# will be used to redirect the user once the upload is done
# and send_from_directory will help us to send/show on the
# browser the file that the user just uploaded
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

# Initialize the Flask application
app = Flask(__name__)

#script_dir = os.path.dirname(__file__)
# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['OUTPUT_FOLDER'] = 'output/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Redirect the user to the output_file route, which
        # will basicaly show on the browser the outputed file
        process_file(filename)
        return redirect(url_for('output_file',
                                filename=filename[:-4]+'.txt'))

## This takes a file, creates output file
#def process_file(filename):
#    result = acronymvark.expand_acronyms(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#    out = open(os.path.join(app.config['OUTPUT_FOLDER'], filename[:-4]+'.txt'), 'w')
#    result = sorted(result, key = lambda x:x[0])
#    for row in result:
#        out.write(row+'\n')
#    out.close()

# This takes a file, creates output file
def process_file(filename):
    result = acronymvark.expand_acronyms(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    if filename[-4:]=='.pdf':
        filename = filename[:-4]+'.txt'
    out = open(os.path.join(app.config['OUTPUT_FOLDER'], filename), 'w')
    result = sorted(result, key = lambda x:x[0])
    for row in result:
        out.write(row+'\n')
    if not result:
        out.write("No acronyms (between 3 and 8 letters long) were found")
    out.close()

# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/output/<filename>')
def output_file(filename):
    print app.config['OUTPUT_FOLDER'], filename
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0', port=85)
