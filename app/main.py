from flask import render_template, redirect, url_for, request, g, jsonify, make_response
from app import webapp, aws_auth
from flask_jwt_extended import (
    set_access_cookies,
    verify_jwt_in_request,
    get_jwt_identity,
)

@webapp.route('/sign_in')
def sign_in():
    return redirect(aws_auth.get_sign_in_url())

@webapp.route('/',methods=['GET'])
def home():
    return render_template("index.html")

@webapp.route("/loggedin", methods=["GET"])
def logged_in():
    access_token = aws_auth.get_access_token(request.args)
    resp = make_response(redirect(url_for("main")))
    set_access_cookies(resp, access_token, max_age=30 * 60)
    return resp

@webapp.route("/main", methods=["GET"])
def main():
    print(verify_jwt_in_request(optional=True))
    if get_jwt_identity():
        return render_template("main.html")
    else:
        return redirect(aws_auth.get_sign_in_url())
