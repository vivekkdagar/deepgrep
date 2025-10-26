# app.py (small changes to init components and avoid nltk download in runtime)
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from deepgrep.core.engine import find_matches
from deepgrep.core.history import SearchHistoryDB
from deepgrep.core.semantic_engine import SemanticEngine
import threading

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Initialize engines once (heavy models loaded at import time)
semantic_engine = SemanticEngine()
history_db = SearchHistoryDB()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search_regex():
    data = request.get_json()
    pattern = data.get("pattern")
    text = data.get("text")
    if not pattern or not text:
        return jsonify({"error": "Missing pattern or text"}), 400

    matches = []
    # Process lines in chunks or use map to speed up for long input; keep simple here
    for line in text.splitlines():
        matches.extend(find_matches(line, pattern))

    history_db.log_search(pattern, len(matches), ["web_input"])
    all_history = history_db.list_all(limit=50)

    return jsonify({
        "matches": matches,
        "history": [
            {"pattern": r[0], "matches": r[2], "timestamp": r[1]} for r in all_history
        ]
    })

@app.route("/semantic", methods=["POST"])
def search_semantic():
    data = request.get_json()
    keyword = data.get("keyword")
    text = data.get("text")
    if not keyword or not text:
        return jsonify({"error": "Missing keyword or text"}), 400

    matches = semantic_engine.find_semantic_matches(text, keyword)
    history_db.log_search(keyword, len(matches), ["web_input"])
    all_history = history_db.list_all(limit=50)

    return jsonify({
        "matches": [{"word": w, "similarity": round(s, 3)} for w, s in matches],
        "history": [
            {"pattern": r[0], "matches": r[2], "timestamp": r[1]} for r in all_history
        ]
    })

if __name__ == "__main__":
    # Remove in-production NLTK downloads; expect preinstalled corpora
    # import nltk
    # nltk.download('wordnet')
    app.run(port=8000, debug=True)