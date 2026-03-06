from flask import Flask, request, jsonify

app = Flask(__name__)

saved_state = False

@app.route("/state")
def state():
    global saved_state

    state = request.args.get("state")

    if state == "true":
        if saved_state:
            return jsonify({"result": 1})
        else:
            saved_state = True
            return jsonify({"result": 0})

    return jsonify({"result": 0})


if __name__ == "__main__":
    app.run(debug=True)
