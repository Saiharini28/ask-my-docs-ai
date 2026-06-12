from flask import Flask, request, jsonify
from flask_cors import CORS
from rag import ask_question, process_pdf
import os

app = Flask(__name__)
CORS(app)

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    query = data.get("message")

    if not query:
        return jsonify({
            "error": "No message provided"
        }), 400

    answer = ask_question(query)

    return jsonify({
        "answer": answer
    })

@app.route("/upload", methods=["POST"])
def upload_pdf():

    if "file" not in request.files:
        return jsonify({
            "error": "No file uploaded"
        }), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "error": "No file selected"
        }), 400

    upload_folder = "../uploads"

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    file_path = os.path.join(
        upload_folder,
        file.filename
    )

    file.save(file_path)

    process_pdf(file_path)

    return jsonify({
        "message": "PDF uploaded and processed successfully"
    })

if __name__ == "__main__":
    app.run(debug=True)