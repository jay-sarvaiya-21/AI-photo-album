import json
import urllib.parse
import boto3
import logging
import os
import datetime
import requests

def lambda_handler(event, context):
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    s3 = boto3.client('s3')
    region_name = "us-east-1"
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("!!!!!!",event)
    # logger("$$$$$",event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print("Bucket is",bucket)
    print("Key is",key)

    ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
    SECRET_KEY = os.environ.get(' AWS_SECRET_ACCESS_KEY')
    metadata_label, metadata_confidence = [], []
    client = boto3.client('rekognition',
                          aws_access_key_id=ACCESS_KEY,
                          aws_secret_access_key=SECRET_KEY,
                          region_name=region_name)
    print("before response######")
    response = client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': key}})
    print("Response is",response)

    for label in response['Labels']:
        metadata_label.append(label['Name'])
        #metadata_confidence.append(format(label['Confidence'], '.2f'))
    
    # data = dict(zip(metadata_label, metadata_confidence))
    
    tresponse = s3.head_object(Bucket=bucket, Key=key) 
    if "x-amz-meta-tags" in tresponse["ResponseMetadata"]["HTTPHeaders"]:
        tags = tresponse["ResponseMetadata"]["HTTPHeaders"]["x-amz-meta-tags"]
        metadata_label.extend(tags.split(","))
        metadata_label=[x.lower() for x in metadata_label]
        metadata_label= list(set(metadata_label))
   
    openSearchEndpoint = 'https://search-photos-h2ytin4xmemmfg6w3jit4ocqs4.us-east-1.es.amazonaws.com/photo-index/_doc/' 
    esauth = ('****', '****')
    format = {'objectKey':key,'bucket':bucket,'createdTimestamp':timestamp,'labels':metadata_label}
    headers = {"Content-Type": "application/json"}
    r = requests.post(openSearchEndpoint,auth=esauth,data=json.dumps(format).encode("utf-8"), headers=headers)
    print("r is ",r)
    print("metadata labels is",metadata_label)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    
    # logger.info(r)
    # logger.info(metadata_label)
    