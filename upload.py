from flask import Flask, request, jsonify, send_file
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os

app = Flask(__name__)

# Specify the URL, bucket name, access key, and secret key
bucketname = os.getenv('BUCKET_NAME', 'upload')
minio_endpoint = os.getenv('MINIO_ENDPOINT', 'http://minio:9000')
access_key = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
secret_key = os.getenv('MINIO_SECRET_KEY', 'minioadmin')

# Create a client with the MinIO server playground, its access key and secret key.
s3 = boto3.client(
    's3',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url=minio_endpoint,
    region_name='us-east-1'
)

# Make a bucket if it doesn't exist
try:
    s3.head_bucket(Bucket=bucketname)
    print("Bucket", bucketname, "already exists")
except ClientError as e:
    error_code = int(e.response['Error']['Code'])
    if error_code == 404:
        s3.create_bucket(Bucket=bucketname)
        print("Created bucket", bucketname)
    elif error_code == 403:
        print("Forbidden: You don't have permission to access this bucket.")
    else:
        print("Error:", e)

@app.route('/upload', methods=['POST'])
def upload():
    # Check if your request has a file
    if 'file' not in request.files:
        return jsonify({"No file is in the request"}), 400
    
    file = request.files['file']

    # Check if the file has a name
    if file.filename == '':
        return jsonify({"No file selected"}), 400

    try:
        # upload the file to the s3 bucket
        s3.upload_fileobj(file, bucketname, file.filename)
        return jsonify({"File uploaded successfully"}), 200
    except NoCredentialsError:
        return jsonify({"error": "Credentials not available"}), 403
    except ClientError as e:
        return jsonify({"error": e.response['Error']['Message']}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    # View all of the files you have uploaded
    files = s3.list_objects(Bucket=bucketname)
    for file in files['Contents']:
        print(obj.bucket_name, obj.object_name, obj.last_modified, obj.etag, obj.size, obj.content_type)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)