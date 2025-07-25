from flask import Flask, request, jsonify, render_template
import os
import boto3

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

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400

    client = boto3.client(
        's3',
        endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
        aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY")
    )

    bucket = os.getenv("R2_BUCKET_NAME")
    client.upload_fileobj(file, bucket, file.filename)

    return jsonify({"message": f"Uploaded {file.filename} to R2."}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
