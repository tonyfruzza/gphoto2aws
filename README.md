# Sample Image Capture w/AWS S3/SQS

gphoto2 lib with python module that triggers an image capture when a SQS message is sent. The image is uploaded to an AWS S3 bucket.


## Setup

Your system should already have gphoto2 lib installed and plug your supported camera into your USB port.

Ensure you have python `pipenv` installed on your machine and run `make init`. This will install the modules python modules necessary to run `capture.py`

Deploy the `aws-infra/` folder using the supplied `./deploy.sh` which makes use of awscli. You'll need to have your AWS credentials to launch the cloudformation template that creates the S3 bucket and SQS queue.

## Run

Use `make run` to start up the `capture.py` processes which will run in a forever loop polling for messages to be sent to the SQS queue. When any message is received it will attempt to trigger your camera to take a picture and upload it to the S3 bucket.
