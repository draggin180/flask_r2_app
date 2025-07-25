
from flask import Flask, jsonify, request, Response
import boto3
import os
from botocore.exceptions import BotoCoreError, ClientError

app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Hello from your R2 Flask app on Render!"

@app.route("/status")
def status():
    return {
        "R2_ACCESS_KEY_ID": os.getenv("R2_ACCESS_KEY_ID", "Not Set"),
        "R2_BUCKET_NAME": os.getenv("R2_BUCKET_NAME", "Not Set"),
        "env": os.getenv("FLASK_ENV", "Not Set")
    }

def get_r2_client():
    return boto3.client(
        's3',
        endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
        aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY")
    )

@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "No file provided"}), 400

        client = get_r2_client()
        bucket = os.getenv("R2_BUCKET_NAME")
        client.upload_fileobj(file, bucket, file.filename)

        return jsonify({"message": f"Uploaded {file.filename} to R2."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/list", methods=["GET"])
def list_files():
    try:
        client = get_r2_client()
        bucket = os.getenv("R2_BUCKET_NAME")
        response = client.list_objects_v2(Bucket=bucket)

        files = [obj["Key"] for obj in response.get("Contents", [])]
        return jsonify({"files": files}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

