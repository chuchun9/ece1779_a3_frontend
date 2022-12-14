from flask import render_template, redirect, url_for, request, g, jsonify, make_response
from app import webapp, aws_auth
from werkzeug.utils import secure_filename
from flask_jwt_extended import (
    set_access_cookies,
    verify_jwt_in_request,
    get_jwt_identity,
)

import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@webapp.route('/sign_in')
def sign_in():
    return redirect(aws_auth.get_sign_in_url())

@webapp.route('/',methods=['GET'])
def home():
    return redirect(url_for("main"))

@webapp.route("/loggedin", methods=["GET"])
def logged_in():
    access_token = aws_auth.get_access_token(request.args)
    resp = make_response(redirect(url_for("main")))
    set_access_cookies(resp, access_token, max_age=30 * 60)
    return resp

@webapp.route('/',methods=['GET'])
@webapp.route("/main", methods=["GET"])
def main():
    ret = verify_jwt_in_request(optional=True)
    if get_jwt_identity():
        username = ret[1]['username']
        return render_template("main.html", username=username)
    else:
        return redirect(aws_auth.get_sign_in_url())

@webapp.route("/show-image", methods=["POST"])
def show_image():
    logging.info("entered show_image function")
    logging.info(f"upload folder: {webapp.config['UPLOAD_FOLDER']}")
    image = request.files['file']
    logger.info("image obtained")

    is_image = True
    if image.filename.split('.')[-1].lower() not in webapp.config['INPUT_FILE_TYPE']:
        logging.error("Uploaded file is not of image types")
        is_image = False

    if len(image.filename) == 0 or (not is_image):
        return render_template("main.html", state=2, message="Input Error")

    logger.info("image file verified")

    filename = secure_filename(image.filename)
    temp_save_file_path = os.path.join(webapp.config['UPLOAD_FOLDER'], filename)
    logging.info(f"temp file path: {temp_save_file_path}")
    image.save(temp_save_file_path)
    logger.info("image saved")

    return render_template("main.html", show=True, user_image = temp_save_file_path, filename=filename)


@webapp.route('/display/<filename>')
def display_image(filename):
    logging.info("entered display_image function")
    return redirect(url_for("static", filename=filename), code=301)


