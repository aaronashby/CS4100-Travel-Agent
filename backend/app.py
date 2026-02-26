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
    data = request.json
    destination = data.get('destination', 'Unknown Location')
    
    # Placeholder for actual travel planning logic
    print(f"Received trip plan request for: {destination}")
    print(f"Full details: {data}")
    
    return jsonify({
        "status": "success",
        "message": f"Successfully received trip plan for {destination}!",
        "received_data": data
    })

if __name__ == "__main__":
    app.run(debug=True, port=5001)
