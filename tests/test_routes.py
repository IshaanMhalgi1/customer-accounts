
import unittest
from unittest.mock import MagicMock, patch

from service.routes import app, accounts


class TestCustomerAccounts(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        accounts.clear()

    def test_read_account_not_found(self):
        response = self.client.get("/accounts/999")
        self.assertEqual(response.status_code, 404)

    def test_read_existing_account(self):
        accounts[1] = {
            "id": 1,
            "name": "Alice",
            "email": "alice@example.com"
        }

        response = self.client.get("/accounts/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["id"], 1)
        self.assertEqual(response.json["name"], "Alice")
        self.assertEqual(
            response.json["email"],
            "alice@example.com"
        )

    def test_update_existing_account(self):
        accounts[1] = {
            "id": 1,
            "name": "Alice",
            "email": "alice@example.com"
        }

        response = self.client.put(
            "/accounts/1",
            json={
                "name": "Alice Smith",
                "email": "alice.smith@example.com"
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Alice Smith")
        self.assertEqual(
            response.json["email"],
            "alice.smith@example.com"
        )

    def test_update_account_not_found(self):
        response = self.client.put(
            "/accounts/999",
            json={"name": "Nobody"}
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json["error"],
            "Account not found"
        )

    def test_delete_existing_account(self):
        accounts[1] = {
            "id": 1,
            "name": "Alice",
            "email": "alice@example.com"
        }

        response = self.client.delete("/accounts/1")

        self.assertEqual(response.status_code, 204)
        self.assertNotIn(1, accounts)

    def test_delete_account_not_found(self):
        response = self.client.delete("/accounts/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json["error"],
            "Account not found"
        )

    def test_list_accounts(self):
        accounts[1] = {
            "id": 1,
            "name": "Alice",
            "email": "alice@example.com"
        }
        accounts[2] = {
            "id": 2,
            "name": "Bob",
            "email": "bob@example.com"
        }

        response = self.client.get("/accounts")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]["name"], "Alice")
        self.assertEqual(response.json[1]["name"], "Bob")

    def test_list_accounts_empty(self):
        response = self.client.get("/accounts")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_update_account_empty_body(self):
        accounts[1] = {
            "id": 1,
            "name": "Alice",
            "email": "alice@example.com"
        }

        response = self.client.put("/accounts/1", json={})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json["error"],
            "Invalid request body"
        )

    def test_update_account_invalid_json(self):
        accounts[1] = {
            "id": 1,
            "name": "Alice",
            "email": "alice@example.com"
        }

        response = self.client.put(
            "/accounts/1",
            data="invalid",
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

    @patch.dict("os.environ", {"DATABASE_URL": "postgresql://test"})
    @patch("service.routes.get_db_connection")
    def test_read_account_from_database(self, mock_connection):
        conn = MagicMock()
        mock_connection.return_value.__enter__.return_value = conn
        cursor = conn.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = (
            {"id": 1, "name": "Alice"},
        )

        response = self.client.get("/accounts/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Alice")

    @patch.dict("os.environ", {"DATABASE_URL": "postgresql://test"})
    @patch("service.routes.get_db_connection")
    def test_read_missing_account_from_database(self, mock_connection):
        conn = MagicMock()
        mock_connection.return_value.__enter__.return_value = conn
        cursor = conn.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = None

        response = self.client.get("/accounts/999")

        self.assertEqual(response.status_code, 404)

    @patch.dict("os.environ", {"DATABASE_URL": "postgresql://test"})
    @patch("service.routes.get_db_connection")
    def test_list_accounts_from_database(self, mock_connection):
        conn = MagicMock()
        mock_connection.return_value.__enter__.return_value = conn
        cursor = conn.cursor.return_value.__enter__.return_value
        cursor.fetchall.return_value = [
            ({"id": 1, "name": "Alice"},),
            ({"id": 2, "name": "Bob"},),
        ]

        response = self.client.get("/accounts")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

    @patch.dict("os.environ", {"DATABASE_URL": "postgresql://test"})
    @patch("service.routes.get_db_connection")
    def test_update_account_in_database(self, mock_connection):
        conn = MagicMock()
        mock_connection.return_value.__enter__.return_value = conn
        cursor = conn.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = (
            {"id": 1, "name": "Alice"},
        )

        response = self.client.put(
            "/accounts/1",
            json={"name": "Alice Smith"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Alice Smith")
        cursor.execute.assert_called()

    @patch.dict("os.environ", {"DATABASE_URL": "postgresql://test"})
    @patch("service.routes.get_db_connection")
    def test_delete_account_from_database(self, mock_connection):
        conn = MagicMock()
        mock_connection.return_value.__enter__.return_value = conn
        cursor = conn.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = (
            {"id": 1, "name": "Alice"},
        )

        response = self.client.delete("/accounts/1")

        self.assertEqual(response.status_code, 204)
        cursor.execute.assert_called()


if __name__ == "__main__":
    unittest.main()
