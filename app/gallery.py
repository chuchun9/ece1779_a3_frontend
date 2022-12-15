from flask import render_template, redirect, url_for, request, g, jsonify, make_response
from app import webapp, aws_auth
from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt_identity,
)
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@webapp.route('/gallery',methods=['GET'])
def gallery():
    ret = verify_jwt_in_request(optional=True)
    if get_jwt_identity():
        username = ret[1]['username']
        return render_template("gallery.html", username=username)
    else:
        return redirect(aws_auth.get_sign_in_url())

