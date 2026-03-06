from flask import Flask, jsonify, make_response
import random

app = Flask(__name__)

@app.route("/random")
def random_number():
    number = random.randint(1, 1000)

    response = make_response(jsonify({
        "number": number
    }))

    response.headers["Cache-Control"] = "public, max-age=10"

    return response


if __name__ == "__main__":
    app.run(debug=True)
