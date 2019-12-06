# An Amazon CloudWatch rule that triggers Lambda and lambda sends alarm notifications to Slack.
import boto3
import json
import logging
import os
import requests
import json
from urllib.request import Request, urlopen, URLError, HTTPError
import requests
requests.packages.urllib3.disable_warnings()

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

HOOK_URL = "https://hooks.slack.com/services/T4TTS87RP/BQVGS418T/ZkdXEByWMOZFCT1AMNSFAFA"
SLACK_CHANNEL = "deleteme"

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    with open('/Users/draobala/Bala/Commands/Releases/DEV1/event.json') as json_file:
        event = json.load(json_file)
    print(event)
    try:
        # get the JSON and parse as per your requirements.
        alarm_name=event['detail']['containers'][0]['lastStatus']
        # stopCode=event['detail']['stopCode']
        stoppedReason=event['detail']['stoppedReason']
        stoppedAt=event['detail']['stoppedAt']
        taskArn=(event['resources'][0]).replace('arn:aws:ecs:us-west-2:924422562222:task/',"")
        exitCode=event['detail']['containers'][0]["exitCode"]
        serviceName=event['detail']['containers'][0]['name']
        image=(event['detail']['containers'][0]['image']).replace('924422562222.dkr.ecr.us-west-2.amazonaws.com/',"")
        clusterArn=(event['detail']['clusterArn']).replace('arn:aws:ecs:us-west-2:924422562222:cluster/',"")
        slack_message = {
            'channel': SLACK_CHANNEL,
            'username': serviceName,
            'icon_emoji': ':boom:',
            # 'text': " *Status:* %s. \n*Cluster:* %s \n*Exitcode:* %s \n*Image:* %s  \n*Stopped Reason:* %s.\n*StoppedAt:* %s .\n*TaskID:* %s ." % ( alarm_name, clusterArn, exitCode, image,  stoppedReason, stoppedAt,   taskArn)
            'text': "*ServiceName:* %s \n*Status:* %s. \n*Cluster:* %s \n*Exitcode:* %s \n*Image:* %s  \n*Stopped Reason:* %s.\n*StoppedAt:* %s .\n*TaskID:* %s ." % ( serviceName, alarm_name, clusterArn, exitCode, image,  stoppedReason, stoppedAt,   taskArn)

        }
    except:
        slack_message = {
            'channel': SLACK_CHANNEL,
            'username': 'AWS',
            'icon_emoji': ':fire:',
            'text': "serviceName %s is now  %s: %s Exit Code: %s" % (serviceName, alarm_name, stoppedReason, exitCode)
        }
    req = Request(HOOK_URL, json.dumps(slack_message).encode('utf-8'))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message['channel'])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)


lambda_handler("file://Users/draobala/Bala/Commands/Releases/DEV1/event.json","context")
