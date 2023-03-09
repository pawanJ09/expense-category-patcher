#!/bin/bash

# AWS Version check
aws_version=$(aws --version)
echo "$aws_version"

# AWS CLI v2 command
aws lambda invoke --function-name expense-category-patcher \
--invocation-type RequestResponse --payload file://events/test-agw-event.json \
--cli-binary-format raw-in-base64-out /tmp/lambda-response.txt
error_message=$(grep "\"statusCode\": 500" /tmp/lambda-response.txt)
echo "$error_message"

# Exit if error received from Lambda invocation
if [ -z "$error_message" ]
then
  echo "Success returned from Lambda"
  exit 0
else
  echo "Error returned from Lambda"
  exit 1
fi