from flask import Flask, request, jsonify, session, send_file
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Used for session management

# S3 Configuration
bucketname = os.getenv('BUCKET_NAME', 'upload')
minio_endpoint = os.getenv('MINIO_ENDPOINT', 'http://minio:9000')
access_key = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
secret_key = os.getenv('MINIO_SECRET_KEY', 'minioadmin')

s3 = boto3.client(
    's3',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url=minio_endpoint,
    region_name='us-east-1'
)

# Ensure the bucket exists
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

# In-memory database for users (for demonstration purposes only)
users = {
    "testuser": "password123"
}

# Route 1: Login microservice
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username in users and users[username] == password:
        session['username'] = username
        return jsonify({"message": "Login successful!"}), 200
    else:
        return jsonify({"message": "Invalid username or password."}), 401

# Route 2: Upload files for user microservice
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'username' not in session:
        return jsonify({"message": "Please login first."}), 401

    if 'file' not in request.files:
        return jsonify({"message": "No file part in the request."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No file selected."}), 400

    if file and file.filename.endswith('.txt'):
        username = session['username']
        s3_key = f"{username}/{file.filename}"

        try:
            s3.upload_fileobj(file, bucketname, s3_key)
            return jsonify({"message": "File uploaded successfully."}), 200
        except NoCredentialsError:
            return jsonify({"error": "Credentials not available"}), 403
        except ClientError as e:
            return jsonify({"error": e.response['Error']['Message']}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"message": "Only .txt files are allowed."}), 400

# Route 3: Display text files for logged-in users only
@app.route('/files', methods=['GET'])
def list_files():
    if 'username' not in session:
        return jsonify({"message": "Please login first."}), 401

    username = session['username']
    prefix = f"{username}/"

    try:
        response = s3.list_objects_v2(Bucket=bucketname, Prefix=prefix)
        files = [obj['Key'].split('/')[-1] for obj in response.get('Contents', [])]
        return jsonify({"files": files}), 200
    except ClientError as e:
        return jsonify({"error": e.response['Error']['Message']}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to download a specific file
@app.route('/files/<filename>', methods=['GET'])
def download_file(filename):
    if 'username' not in session:
        return jsonify({"message": "Please login first."}), 401

    username = session['username']
    s3_key = f"{username}/{filename}"

    try:
        file_obj = s3.get_object(Bucket=bucketname, Key=s3_key)
        return send_file(
            file_obj['Body'],
            attachment_filename=filename,
            as_attachment=True
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "NoSuchKey":
            return jsonify({"message": "File not found."}), 404
        return jsonify({"error": e.response['Error']['Message']}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
