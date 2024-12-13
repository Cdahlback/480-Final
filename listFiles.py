from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

app = Flask(__name__)

#Allow the user to enter URL, bucket name, access key, and secret key
bucketname = input("Enter the name of the bucket: ")
access_key = input("Enter your access key: ")
secret_key = input("Enter your secret key: ")

# Create a client with the MinIO server playground, its access key and secret key.
s3 = boto3.client(
    's3',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url='http://localhost:9000',
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
@app.route('/files', methods=['GET'])
@token_required
def list_files():
    try:
        # List all files in the S3 bucket
        response = s3.list_objects_v2(Bucket=bucketname)
        if 'Contents' in response:
            files = [obj['Key'] for obj in response['Contents']]
            return jsonify({"files": files}), 200
        else:
            return jsonify({"message": "No files found"}), 200
    except NoCredentialsError:
        return jsonify({"error": "Credentials not available"}), 403
    except ClientError as e:
        return jsonify({"error": e.response['Error']['Message']}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)