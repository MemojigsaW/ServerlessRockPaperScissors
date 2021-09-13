from app import webapp
from flask import render_template, request, jsonify
from util import awsapis as aws
import base64
import io
import PIL.Image as Image
from app.IndexPage import login_required


@webapp.route("/video", methods=['GET'])
#@login_required
def loadVideoPage():
    return render_template('VideoPage.html')

@webapp.route("/video-old", methods=['GET'])
def loadVideoPage2():
    return render_template('VideoPage1.html')


@webapp.route("/api/process_screenshot", methods=['POST'])
def process_screenshot():
    key = "image" #the key to be saved in s3. user can assumed to be accessed from session

    # string is base64 encoded image
    Image64 = request.form['Image64']

    # reconstruct from base64
    imgByteFile = base64.b64decode(Image64)
    image = Image.open(io.BytesIO(imgByteFile))

    _format = "png"
    # a file interface, is it cleared after use?
    buffer = io.BytesIO()
    image.save(buffer, "png")
    buffer.seek(0)  # rewind pointer back to start

    result = aws.uploadFile(buffer, key, _format)
    if (result):
        response = jsonify({
            'result': 'success',
            's3path': key+"."+_format
        })
    else:
        response = jsonify({
            'result': 'fail'
        })
    buffer.close()
    return response
