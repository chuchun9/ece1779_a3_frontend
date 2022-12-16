from flask import render_template, redirect, url_for, request, g, jsonify, make_response
from app import webapp, aws_auth, fs
from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt_identity,
)
import logging
import boto3
from boto3.dynamodb.conditions import Key, Attr
import random
from aws_endpoints_credentials import table_name, s3_bucket_name
import urllib.parse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@webapp.route('/gallery',methods=['GET'])
def gallery():
    ret = verify_jwt_in_request(optional=True)
    if get_jwt_identity():
        username = ret[1]['username']
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)

        ## should be -1
        filter_num = 0
        response = table.query(
            KeyConditionExpression=Key('username').eq(username),
            FilterExpression=Attr('filterNum').eq(str(filter_num))
        )
        items = response['Items']
        if len(items) > 10:
            items = random.sample(items, 10)

        for item in items:
            url = f'''https://{s3_bucket_name}.s3.amazonaws.com/{urllib.parse.quote(item['imageName'], safe="~()*!.'")}'''
            item['url'] = url
        return render_template("gallery.html", username=username, items=items, len=len(items))
    else:
        return redirect(aws_auth.get_sign_in_url())

