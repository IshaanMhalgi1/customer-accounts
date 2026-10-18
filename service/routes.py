
import os

import psycopg2
from psycopg2.extras import Json

from flask import Flask, jsonify, request
from flask_talisman import Talisman
from flask_cors import CORS

app = Flask(__name__)

Talisman(
    app,
    force_https=False,
    content_security_policy=None
)
CORS(app)

# Used by existing tests and when no database is configured.
accounts = {}


def get_db_connection():
    """Connect to PostgreSQL using the configured database URL."""
    return psycopg2.connect(os.environ["DATABASE_URL"])


def database_enabled():
    """Check whether PostgreSQL has been configured."""
    return bool(os.environ.get("DATABASE_URL"))


def fetch_account(account_id):
    """Retrieve an account from PostgreSQL or memory."""
    if not database_enabled():
        return accounts.get(account_id)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT data FROM accounts WHERE id = %s",
                (account_id,)
            )
            row = cur.fetchone()

    return row[0] if row else None


@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_account(account_id):
    """Retrieve a customer account by ID."""
    account = fetch_account(account_id)

    if account is None:
        return jsonify({"error": "Account not found"}), 404

    return jsonify(account), 200


@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_account(account_id):
    """Update an existing customer account."""
    account = fetch_account(account_id)

    if account is None:
        return jsonify({"error": "Account not found"}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"error": "Invalid request body"}), 400

    account.update(data)

    if database_enabled():
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE accounts SET data = %s WHERE id = %s",
                    (Json(account), account_id)
                )
    else:
        accounts[account_id] = account

    return jsonify(account), 200


@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_account(account_id):
    """Delete an existing customer account."""
    account = fetch_account(account_id)

    if account is None:
        return jsonify({"error": "Account not found"}), 404

    if database_enabled():
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM accounts WHERE id = %s",
                    (account_id,)
                )
    else:
        del accounts[account_id]

    return "", 204


@app.route("/accounts", methods=["GET"])
def list_accounts():
    """Return all customer accounts."""
    if database_enabled():
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT data FROM accounts ORDER BY id")
                rows = cur.fetchall()

        result = [row[0] for row in rows]
    else:
        result = [
            accounts[account_id]
            for account_id in sorted(accounts)
        ]

    return jsonify(result), 200
