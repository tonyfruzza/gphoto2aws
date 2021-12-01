#!/bin/sh
REGION=us-west-2
aws --region $REGION cloudformation deploy \
--stack-name photo-infra \
--template-file photo-infra.yaml
