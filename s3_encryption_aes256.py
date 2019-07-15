#Encrypt all your existing buckets and its objects with aes256. 
#Install boto3 using: pip3 install boto3 
#configure AWS credentials using aws configure
# remove safe_buckets after testing and change the for loop as for bucket in buckets.
# run as python3 s3_encryption_aes256.py
# Future modifications: Give the count of how many buckets are encrypted and how many are already encrypted.

import sys
import boto3
from botocore.exceptions import ClientError

# obv input needed
session = boto3.Session(profile_name='default')
s3_client = session.client('s3')
s3_resource = session.resource('s3')

# Get all buckets
buckets = [s3_resource.Bucket(bucket['Name']) for bucket in s3_client.list_buckets()['Buckets']]

# TEST line for quickly testing buckets
safe_buckets = buckets[-4:]

# Loop through all buckets
for bucket in safe_buckets:
    print (bucket.name)
    try:
        #print (s3_client.get_bucket_encryption(Bucket=bucket.name))
        encrypted_bucket = len(s3_client.get_bucket_encryption(Bucket=bucket.name)['ServerSideEncryptionConfiguration']['Rules']) > 0
        if encrypted_bucket:
            print (bucket.name + ' - Encrypted')
    except ClientError as e:
        if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
            add_encryption_response = s3_client.put_bucket_encryption(
                Bucket=bucket.name,
                ServerSideEncryptionConfiguration={
                    'Rules': [
                        {
                            'ApplyServerSideEncryptionByDefault': {
                                'SSEAlgorithm': 'AES256'
                            }
                        }
                    ]
                }
            )
            # print (add_encryption_response)
            print (bucket.name + " - Bucket now encrypted")
        # else:
        # print ("Unexpected error: %s" % e)
for bucket in safe_buckets:
    for obj in bucket.objects.all():
        t_obj = s3_resource.Object(obj.bucket_name, obj.key)
        print (obj.key + ' - ' + str(t_obj.server_side_encryption))
        if not t_obj.server_side_encryption:
            bucket.copy(
                {
                    'Bucket': obj.bucket_name,
                    'Key': obj.key
                },
                obj.key
            )
            print (bucket.name + ' - ' + obj.key + ' - Object now encypted')

print ('All objects in all buckets are encrypted! Well done!')
