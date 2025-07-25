import os
from flask import Flask, request, jsonify
import boto3
from dotenv import load_dotenv
import uuid

load_dotenv()

app = Flask(__name__)

s3 = boto3.client(
    "s3",
    endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
    aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    region_name="auto"
)

BUCKET = os.environ["R2_BUCKET_NAME"]

@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    key = f"{uuid.uuid4()}_{file.filename}"
    s3.upload_fileobj(file, BUCKET, key)
    return jsonify({"message": "File uploaded", "key": key}), 200

@app.route("/download/<key>", methods=["GET"])
def download(key):
    try:
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET, 'Key': key},
            ExpiresIn=3600
        )
        return jsonify({"download_url": url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
