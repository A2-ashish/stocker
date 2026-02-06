import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-prod'
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.environ.get('AWS_REGION') or 'us-east-1'
    DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME') or 'StockerData'
    SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
