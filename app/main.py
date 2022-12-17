from flask import render_template, redirect, url_for, request, g, jsonify, make_response
from app import webapp, aws_auth, fs
import base64
from flask_jwt_extended import (
    set_access_cookies,
    verify_jwt_in_request,
    get_jwt_identity,
)
import boto3
import logging
import io
import requests
from aws_endpoints_credentials import table_name
import json

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

@webapp.route("/main", methods=["GET"])
def main():
    ret = verify_jwt_in_request(optional=True)
    if get_jwt_identity():
        username = ret[1]['username']
        return render_template("main.html", username=username)
    else:
        return redirect(aws_auth.get_sign_in_url())

@webapp.route('/filter', methods=["POST"])
def filter():
    ret = verify_jwt_in_request(optional=True)
    if get_jwt_identity():
        username = ret[1]['username']
        image = request.files['file']
        image_type = image.headers.get('Content-Type').split("/")[-1]
        selected_filter = request.form.get('filter')

        is_image = True
        if image.filename.split('.')[-1].lower() not in webapp.config['INPUT_FILE_TYPE']:
            logging.error("Uploaded file is not of image types")
            is_image = False

        if len(image.filename) == 0 or (not is_image):
            return jsonify("Input Error"), 400
        image_io = io.BytesIO()
        image.save(image_io)
        image_base64 = base64.b64encode(image_io.getvalue())
        data = {
            'filterNum': selected_filter,
            'image': image_base64.decode('utf-8'),
            'imageType': image_type
        }
        json_data = json.dumps(data)
        obj = json.loads(json_data)

        response = requests.post(webapp.config['BACKEND_URL'] + '/Filter', json=obj)
        if response.status_code != 200:
            return jsonify("Filter Image Error"), 400

        newbase64 = response.json()['img']
        dataurl = "data:{};base64,{}".format(image.headers.get('Content-Type'), newbase64)
        return jsonify(dataurl), 200
    else:
        return redirect(aws_auth.get_sign_in_url())

@webapp.route('/upload', methods=["POST"])
def upload():
    ret = verify_jwt_in_request(optional=True)
    if get_jwt_identity():
        username = ret[1]['username']
        dynamodb = boto3.resource('dynamodb')

        table = dynamodb.Table(table_name)

        base64_string = request.form.get('dataurl')
        image_name = request.form.get('imageName')
        image_type = request.form.get('imageType')
        filter_num = request.form.get('filterNum')
        image_name = username + "__" + str(filter_num) + "__" + image_name
        base64_string = base64_string.split("data:image/png;base64,")[-1]
        imgdata = base64.b64decode(str(base64_string))
        inmem = io.BytesIO(imgdata)
        inmem.seek(0)

        result = fs.upload_inmem_image(inmem, image_name, image_type)
        if result:
            response = table.put_item(
                Item={
                    'username': username,
                    'imageName': image_name,
                    'filterNum': filter_num
                }
            )
            print(response)
            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                return jsonify("Database Failure"), 400

            return jsonify("Uploading Image Success"), 200
        else:
            return jsonify("Uploading Image Error"), 400
    else:
        return redirect(aws_auth.get_sign_in_url())

