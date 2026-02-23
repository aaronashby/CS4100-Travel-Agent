from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Enabling CORS so the React frontend can make requests to this backend
CORS(app)

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello from the Flask backend!"})

@app.route('/api/plan', methods=['POST'])
def plan_trip():
    pass

if __name__ == "__main__":
    app.run(debug=True, port=5000)
