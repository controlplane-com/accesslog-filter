import gzip
import uuid
import boto3
import io
import os
import misc


(DEST_BUCKET, DEST_PATH) = misc.get_bucket_and_key(os.getenv('DEST_URI'))

(_, SOURCE_PREFIX) = misc.get_bucket_and_key(os.getenv('SOURCE_URI'))

s3 = boto3.client('s3')


def handler(event, context):
    # task = {
    #     "s3SchemaVersion": "1.0",
    #     "configurationId": "tf-s3-lambda-20220727112810026100000001",
    #     "bucket": {
    #         "name": "julian-log-router-test",
    #         "ownerIdentity": {
    #         "principalId": "A2VWZB4X1D3ETR"
    #         },
    #         "arn": "arn:aws:s3:::julian-log-router-test"
    #     },
    #     "object": {
    #         "key": "cpln-test/Agenda.txt",
    #         "size": 219,
    #         "eTag": "62319a931cce6616040afd74d1b75bc3",
    #         "sequencer": "0062E12E2890FDF3A7"
    #     }
    # }
    task = event['Records'][0]['s3']

    response = s3.get_object(
        Bucket=task['bucket']['name'], Key=task['object']['key'])

    dest_key = misc.compute_key(
        SOURCE_PREFIX, DEST_PATH, task['object']['key'])

    filtered_data = io.BytesIO()

    gz = gzip.GzipFile(fileobj=response['Body'])
    misc.retain_accesslogs(filtered_data, gz)

    if filtered_data.tell() != 0:
        fname = '/tmp/'+str(uuid.uuid4())
        with gzip.open(fname, 'wb') as f:
            f.write(filtered_data.getvalue())

        with open(fname, 'rb') as f:
            s3.put_object(Bucket=DEST_BUCKET, Key=dest_key,
                          Body=f, ContentEncoding='gzip')
    else:
        print(f"file {task['object']['key']} does not contain access logs")
