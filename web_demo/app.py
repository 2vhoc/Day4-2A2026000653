import sys
import os
from pathlib import Path

# Add project root to sys.path so we can import from src
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from src.agent.graph import run_agent

app = Flask(__name__, static_folder="static")
CORS(app)

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    if not data or "query" not in data:
        return jsonify({"error": "Missing query parameter"}), 400
    
    query = data["query"]
    
    try:
        # Run the agent using the user's custom base provider
        result = run_agent(query, provider="base")
        
        # Format the response
        response = {
            "answer": result.final_answer,
            "tool_calls": [{"name": tc.name, "args": tc.args} for tc in result.tool_calls],
            "saved_order": result.saved_order,
            "saved_order_path": result.saved_order_path
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Ensure artifacts directory exists for save_order tool
    artifacts_dir = project_root / "artifacts" / "orders"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    app.run(host="0.0.0.0", port=5000, debug=True)
