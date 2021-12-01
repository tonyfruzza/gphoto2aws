from __future__ import print_function

import logging
import os
import time
import subprocess
import sys
import uuid
import boto3
import gphoto2 as gp

AWS_REGION='us-west-2'
RESOURCE_STACK_NAME='photo-infra'
sqs = boto3.client('sqs', region_name=AWS_REGION)
photo_bucket = None
queue_url = None
WAIT_TIME_BETWEEN_PICS=5


def get_outputs(stackname):
    global AWS_REGION
    global queue_url
    global photo_bucket
    cloudformation = boto3.client('cloudformation', region_name=AWS_REGION)
    outputs = cloudformation.describe_stacks(StackName=stackname)['Stacks'][0]['Outputs']
    for output in outputs:
        if output['OutputKey'] == 'S3Bucket':
            photo_bucket = output['OutputValue']
        if output['OutputKey'] == 'Queue':
            queue_url = output['OutputValue']

def upload_pic(local_file, bucket):
    new_img_name = str(uuid.uuid1()) + '.jpg'
    print("Uploading image to s3://%s/%s" % (bucket, new_img_name))
    s3_client = boto3.client('s3')
    s3_client.upload_file(
        local_file,
        bucket,
        new_img_name
    )

def take_pic():
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    callback_obj = gp.check_result(gp.use_python_logging())
    camera = gp.Camera()
    camera.init()
    print('Capturing image')
    file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
    print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))
    target = os.path.join('/tmp', file_path.name)
    print('Copying image to', target)
    camera_file = camera.file_get(
        file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
    camera_file.save(target)
    # subprocess.call(['xdg-open', target])
    camera.exit()
    return target

get_outputs(RESOURCE_STACK_NAME)
while True:
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=20
    )

    print(response)
    if 'Messages' in response and len(response['Messages']) > 0:
        print("Message found!")
        print(response['Messages'][0])
        try:
            upload_pic(take_pic(), photo_bucket)
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=response['Messages'][0]['ReceiptHandle']
            )
            time.sleep(WAIT_TIME_BETWEEN_PICS)
        except Exception as e:
            print(e)
