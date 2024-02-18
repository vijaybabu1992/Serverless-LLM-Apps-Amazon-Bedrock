# Lesson 5: Event-driven generation
# Import all needed packages
import boto3, os

from helpers.Lambda_Helper import Lambda_Helper
from helpers.S3_Helper import S3_Helper

lambda_helper = Lambda_Helper()
s3_helper = S3_Helper()

bucket_name_text = os.environ['LEARNERS3BUCKETNAMETEXT']
bucket_name_audio = os.environ['LEARNERS3BUCKETNAMEAUDIO']

### Deploy your lambda function
%%writefile lambda_function.py

#############################################################
#
# This Lambda function is written to a file by the notebook 
# It does not run in the notebook!
#
#############################################################

import json
import boto3
import uuid
import os

s3_client = boto3.client('s3')
transcribe_client = boto3.client('transcribe', region_name='us-west-2')

def lambda_handler(event, context):
    # Extract the bucket name and key from the incoming event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # One of a few different checks to ensure we don't end up in a recursive loop.
    if key != "dialog.mp3": 
        print("This demo only works with dialog.mp3.")
        return

    try:
        
        job_name = 'transcription-job-' + str(uuid.uuid4()) # Needs to be a unique name

        response = transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': f's3://{bucket}/{key}'},
            MediaFormat='mp3',
            LanguageCode='en-US',
            OutputBucketName= os.environ['S3BUCKETNAMETEXT'],  # specify the output bucket
            OutputKey=f'{job_name}-transcript.json',
            Settings={
                'ShowSpeakerLabels': True,
                'MaxSpeakerLabels': 2
            }
        )
        
    except Exception as e:
        print(f"Error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error occurred: {e}")
        }

    return {
        'statusCode': 200,
        'body': json.dumps(f"Submitted transcription job for {key} from bucket {bucket}.")
    }

lambda_helper.lambda_environ_variables = {'S3BUCKETNAMETEXT' : bucket_name_text}
lambda_helper.deploy_function(["lambda_function.py"], function_name="LambdaFunctionTranscribe")

lambda_helper.filter_rules_suffix = "mp3"
lambda_helper.add_lambda_trigger(bucket_name_audio, function_name="LambdaFunctionTranscribe")

s3_helper.upload_file(bucket_name_audio, 'dialog.mp3')

s3_helper.list_objects(bucket_name_audio)

#### Restart kernel if needed.
"""
- If you run the code fairly quickly from start to finish, it's possible that the following code cell `s3_helper.list_objects(bucket_name_text)` will give a "Not Found" error.  
- If waiting a few seconds (10 seconds) and re-running this cell does not resolve the error, then you can restart the kernel of the jupyter notebook.
- Go to menu->Kernel->Restart Kernel.
- Then run the code cells from the start of the notebook, waiting 2 seconds or so for each code cell to finish executing."""

s3_helper.list_objects(bucket_name_text)

#### Re-run "download" code cell as needed
- It may take a few seconds for the results to be generated.
- If you see a `Not Found` error, please wait a few seconds and then try running the `s3_helper.download_object` again.

s3_helper.download_object(bucket_name_text, 'results.txt')

from helpers.Display_Helper import Display_Helper
display_helper = Display_Helper()
display_helper.text_file('results.txt')

# Extra resources
https://community.aws/code/generative-ai
https://community.aws/generative-ai