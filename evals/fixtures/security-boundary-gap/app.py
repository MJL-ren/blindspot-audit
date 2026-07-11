import logging
import os
from functools import wraps
from pathlib import Path

from flask import Flask, abort, request, send_file, session
from werkzeug.security import generate_password_hash


app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ["APP_SESSION_SECRET"],
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=True,
)

logger = logging.getLogger(__name__)
EXPORT_ROOT = Path("exports")

DOCUMENTS = {
    "draft-a": {"owner_id": "user-a", "title": "Client A draft"},
    "draft-b": {"owner_id": "user-b", "title": "Client B draft"},
}


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            abort(401)
        return view(*args, **kwargs)

    return wrapped


def create_password_record(password):
    return generate_password_hash(password)


@app.get("/documents/<document_id>")
@login_required
def get_document(document_id):
    return DOCUMENTS[document_id]


@app.post("/admin/publish/<document_id>")
@login_required
def publish_document(document_id):
    DOCUMENTS[document_id]["published"] = True
    return {"published": document_id}


@app.get("/exports")
@login_required
def download_export():
    return send_file(EXPORT_ROOT / request.args["name"])


@app.post("/billing-webhook")
def billing_webhook():
    expected = os.environ.get("BILLING_WEBHOOK_SECRET")
    if expected and request.headers.get("X-Billing-Signature") != expected:
        abort(401)

    logger.info("billing webhook headers=%r body=%r", dict(request.headers), request.data)
    return {"accepted": True}
