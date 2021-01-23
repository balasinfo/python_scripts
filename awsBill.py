import boto3
from datetime import date, timedelta

#import boto3
import json
import logging
import os

from base64 import b64decode
from urllib2 import Request, urlopen, URLError, HTTPError


client = boto3.client('ce')

day_before_yesterday = (date.today() - timedelta(days=2)).strftime('%Y-%m-%d')
yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
today = (date.today()).strftime('%Y-%m-%d')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


SLACK_CHANNEL="status-ms-devops"
HOOK_URL = "https://hooks.slack.com/services/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"

day_before_yesterday_spending = client.get_cost_and_usage(
    TimePeriod={
        'Start': day_before_yesterday,
        'End': yesterday
    },
    Granularity='DAILY',
    Metrics=[
        'AmortizedCost',
    ]
)

yesterday_spending = client.get_cost_and_usage(
    TimePeriod={
        'Start': yesterday,
        'End': today
    },
    Granularity='DAILY',
    Metrics=[
        'AmortizedCost',
    ]
)

#print((day_before_yesterday_spending['ResultsByTime'])[0])
#print((day_before_yesterday_spending['ResultsByTime'])[0]['Total']['AmortizedCost']['Amount'])

print("AWS Spending for "+day_before_yesterday+" is : $"+(day_before_yesterday_spending['ResultsByTime'])[0]['Total']['AmortizedCost']['Amount'])
print("AWS Spending for "+yesterday+" is : $"+(yesterday_spending['ResultsByTime'])[0]['Total']['AmortizedCost']['Amount'])


slack_message = {
    'channel': SLACK_CHANNEL,
    "username": "AWS Billing Alerter",
    "icon_emoji": ":bill:",
    "attachments": [
        {
            "fallback": "*Aws Billing alert - %s* " % ((yesterday_spending['ResultsByTime'])[0]['Total']['AmortizedCost']['Amount']),
            "pretext": "*AWS Billing Alert*",
            "fields": [
                {
                    "title": "AWS Bill for - "+day_before_yesterday,
                    "value": "$"+(day_before_yesterday_spending['ResultsByTime'])[0]['Total']['AmortizedCost']['Amount'],
                    "short": "false"
                },
                {
                    "title": "AWS Bill for yesterday - "+yesterday,
                    "value": "$"+(yesterday_spending['ResultsByTime'])[0]['Total']['AmortizedCost']['Amount'],
                    "short": "false",
                }
            ],
            "color": "#439FE0"
        }
    ]
}
req = Request(HOOK_URL, json.dumps(slack_message))
try:
    response = urlopen(req)
    response.read()
    #logger.info("Message posted to %s", slack_message['channel'])
except HTTPError as e:
    print("Error")
    #logger.error("Request failed: %d %s", e.code, e.reason)
except URLError as e:
    print("Error")
    #logger.error("Server connection failed: %s", e.reason)
