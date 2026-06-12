from flask import Flask, request, jsonify
from rag import ask_question

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)