#!/bin/bash
awslocal s3 mb s3://tropmed-files-local
awslocal sqs create-queue --queue-name tropmed-tasks-local
awslocal sqs create-queue --queue-name tropmed-notifications-local
awslocal sns create-topic --name tropmed-notifications-local
awslocal secretsmanager create-secret --name tropmed/db-uri --secret-string "mongodb://mongodb:27017/tropmed"
awslocal secretsmanager create-secret --name tropmed/jwt-secret --secret-string "dev-secret-change-in-prod"
echo "LocalStack resources initialized."
