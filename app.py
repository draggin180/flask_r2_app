from flask import Flask
import os

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

if __name__ == "__main__":
    app.run(debug=True)
