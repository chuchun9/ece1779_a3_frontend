from flask import Flask
from flask_awscognito import AWSCognitoAuthentication
from flask_jwt_extended import (
    JWTManager,
    set_access_cookies,
    get_jwt_identity,
)
from jwt.algorithms import RSAAlgorithm
import requests
import json


def get_cognito_public_keys(region, pool_id):
    url = f"https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/jwks.json"
    resp = requests.get(url)
    return json.dumps(json.loads(resp.text)["keys"][1])


webapp = Flask(__name__)

webapp.config['AWS_DEFAULT_REGION'] = 'us-east-1'
webapp.config['AWS_COGNITO_DOMAIN'] = 'https://ece1779.auth.us-east-1.amazoncognito.com'
webapp.config['AWS_COGNITO_USER_POOL_ID'] = 'us-east-1_vZDoM58z5'
webapp.config['AWS_COGNITO_USER_POOL_CLIENT_ID'] = '77v7ofpsqe8idt2m406517n8br'
webapp.config['AWS_COGNITO_REDIRECT_URL'] = 'http://localhost:3000/loggedin'
webapp.config['AWS_COGNITO_USER_POOL_CLIENT_SECRET'] = None
webapp.config['SECRET_KEY'] = 'secret key'
webapp.config['JWT_COOKIE_CSRF_PROTECT'] = False
webapp.config['JWT_ALGORITHM'] = 'RS256'
webapp.config['JWT_IDENTITY_CLAIM'] = 'sub'
webapp.config['JWT_COOKIE_SECURE '] = True
webapp.config['JWT_TOKEN_LOCATION'] = ["cookies"]
webapp.config["JWT_PUBLIC_KEY"] = RSAAlgorithm.from_jwk(get_cognito_public_keys(
    webapp.config['AWS_DEFAULT_REGION'],
    webapp.config['AWS_COGNITO_USER_POOL_ID']
))

global aws_auth

aws_auth = AWSCognitoAuthentication(webapp)

jwt = JWTManager(webapp)

from app import main

