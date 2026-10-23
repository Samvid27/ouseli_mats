
from flask import Flask

from ingest.routes import ingest_bp

app = Flask(__name__)
app.secret_key = "local-test-secret"
app.register_blueprint(ingest_bp, url_prefix="/api/artha")


def test_upload():
    client = app.test_client()

    # Simulate a logged-in user.
    with client.session_transaction() as session:
        session["user_id"] = 1

    sample_text = """
    UPI TRANSACTION HISTORY
    20-10-2026 Swiggy Paid Rs. 420.00
    20-10-2026 Netflix Paid Rs. 649.00
    21-10-2026 Salary Received Rs. 25000.00
    """

    response = client.post(
        "/api/artha/upload",
        json={"text": sample_text}
    )

    print("HTTP status:", response.status_code)
    print("API response:")
    print(response.get_json())

    assert response.status_code == 200, (
        f"Upload failed: {response.get_json()}"
    )

    data = response.get_json()

    assert data["doc_id"]
    assert data["provider"] == "ollama-gemma3"
    assert len(data["rows"]) == 3

    print("\nUPLOAD API TEST PASSED")


if __name__ == "__main__":
    test_upload()
