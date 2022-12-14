from flask import Flask
from flask_awscognito import AWSCognitoAuthentication
from flask_jwt_extended import (
    JWTManager
)
from jwt.algorithms import RSAAlgorithm
import requests
import json
from aws_endpoints_credentials import s3_bucket_name as original_s3_bucket_name
from .file_system import FileSystem


def get_cognito_public_keys(region, pool_id):
    url = f"https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/jwks.json"
    resp = requests.get(url)
    return json.dumps(json.loads(resp.text)["keys"][1])


webapp = Flask(__name__)

webapp.config['AWS_DEFAULT_REGION'] = 'us-east-1'
webapp.config['AWS_COGNITO_DOMAIN'] = 'https://ece1779.auth.us-east-1.amazoncognito.com'
webapp.config['AWS_COGNITO_USER_POOL_ID'] = 'us-east-1_vZDoM58z5'
webapp.config['AWS_COGNITO_USER_POOL_CLIENT_ID'] = '77v7ofpsqe8idt2m406517n8br'
webapp.config['AWS_COGNITO_REDIRECT_URL'] = 'https://9j392u7dc6.execute-api.us-east-1.amazonaws.com/dev/loggedin'
# webapp.config['AWS_COGNITO_REDIRECT_URL'] = 'http://localhost:3000/loggedin'
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
webapp.config['INPUT_FILE_TYPE'] = set(["rgb", "gif", "pbm", "pgm", "ppm",
                                  "tiff", "rast", "xbm", "jpeg", "jpg",
                                  "bmp", "png", "webp", "exr"])

webapp.config['BACKEND_URL'] = "https://tt6u4o6zcj.execute-api.us-east-1.amazonaws.com/test/Filter"

global aws_auth

aws_auth = AWSCognitoAuthentication(webapp)

jwt = JWTManager(webapp)

global fs
fs = FileSystem(original_s3_bucket_name)

from app import main
from app import gallery

