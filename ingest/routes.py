
"""Artha transaction-ingestion API routes."""

from uuid import uuid4

from flask import Blueprint, jsonify, request, session

from ingest.gemma_reader import extract_transactions

ingest_bp = Blueprint("ingest", __name__)


@ingest_bp.route("/upload", methods=["POST"])
def upload_document():
    """Extract proposed transactions without saving them to the database."""

    if not session.get("user_id"):
        return jsonify({
            "error": "Authentication required. Please log in first."
        }), 401

    if not request.is_json:
        return jsonify({
            "error": "Send JSON containing a 'text' field."
        }), 415

    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify({"error": "Invalid JSON request body."}), 400

    source_text = payload.get("text", payload.get("source_text", ""))

    if not isinstance(source_text, str) or not source_text.strip():
        return jsonify({
            "error": "The 'text' field must contain transaction text."
        }), 400

    if len(source_text) > 100_000:
        return jsonify({"error": "Text exceeds the 100,000 character limit."}), 413

    try:
        result = extract_transactions(source_text=source_text)

        return jsonify({
            "doc_id": str(uuid4()),
            "doc_type": result.get("doc_type", "unknown"),
            "provider": result.get("provider", "ollama-gemma3"),
            "rows": result.get("rows", []),
            "checks": result.get(
                "checks",
                {"reconciles": None, "duplicates": 0}
            )
        }), 200

    except ValueError as exc:
        return jsonify({
            "error": "Could not extract transactions.",
            "details": str(exc)
        }), 422

    except Exception:
        return jsonify({
            "error": (
                "Transaction extraction failed. "
                "Check that Ollama is running and Gemma 3 is available."
            )
        }), 502
