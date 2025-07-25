from flask import Flask, request, jsonify, send_file
import boto3
import os
from botocore.exceptions import BotoCoreError, ClientError
from io import BytesIO
import werkzeug

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
    try:
        return boto3.client(
            's3',
            endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
            aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY")
        )
    except Exception as e:
        raise RuntimeError(f"Failed to create R2 client: {str(e)}")

@app.route("/upload", methods=["POST"])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Missing file field"}), 400

        file = request.files['file']

        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        # Secure the filename
        filename = werkzeug.utils.secure_filename(file.filename)

        # Limit size to 10MB (adjust if needed)
        if file.content_length and file.content_length > 10 * 1024 * 1024:
            return jsonify({"error": "File too large. Max 10MB"}), 400

        client = get_r2_client()
        bucket = os.getenv("R2_BUCKET_NAME")

        client.upload_fileobj(file, bucket, filename)

        return jsonify({"message": f"Uploaded {filename} to R2."}), 200

    except (BotoCoreError, ClientError) as e:
        return jsonify({"error": f"AWS error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/list", methods=["GET"])
def list_files():
    try:
        client = get_r2_client()
        bucket = os.getenv("R2_BUCKET_NAME")
        response = client.list_objects_v2(Bucket=bucket)

        files = [obj["Key"] for obj in response.get("Contents", [])]
        return jsonify({"files": files}), 200

    except (BotoCoreError, ClientError) as e:
        return jsonify({"error": f"AWS error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/download", methods=["GET"])
def download():
    try:
        filename = request.args.get("filename")
        if not filename:
            return jsonify({"error": "Missing 'filename' parameter"}), 400

        client = get_r2_client()
        bucket = os.getenv("R2_BUCKET_NAME")

        file_obj = BytesIO()
        client.download_fileobj(bucket, filename, file_obj)
        file_obj.seek(0)

        return send_file(file_obj, as_attachment=True, download_name=filename)

    except client.exceptions.NoSuchKey:
        return jsonify({"error": f"File '{filename}' not found"}), 404
    except (BotoCoreError, ClientError) as e:
        return jsonify({"error": f"AWS error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
