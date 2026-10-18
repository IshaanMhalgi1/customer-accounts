from flask import Flask, jsonify
from flask import request

app = Flask(__name__)

# Temporary in-memory customer accounts
accounts = {}


@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_account(account_id):
    """Retrieve a customer account by ID."""
    account = accounts.get(account_id)

    if account is None:
        return jsonify({"error": "Account not found"}), 404

    return jsonify(account), 200


@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_account(account_id):
    """Update an existing customer account."""
    account = accounts.get(account_id)

    if account is None:
        return jsonify({"error": "Account not found"}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"error": "Invalid request body"}), 400

    account.update(data)
    return jsonify(account), 200


@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_account(account_id):
    """Delete an existing customer account."""
    account = accounts.get(account_id)

    if account is None:
        return jsonify({"error": "Account not found"}), 404

    del accounts[account_id]
    return "", 204


@app.route("/accounts", methods=["GET"])
def list_accounts():
    """Return all customer accounts."""
    return jsonify([
        accounts[account_id]
        for account_id in sorted(accounts)
    ]), 200
