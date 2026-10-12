
import unittest
from unittest.mock import patch

from app.app import app


class CloudOpsAppTests(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"CloudOps Enterprise Platform",
            response.data
        )

    def test_health_endpoint(self):
        with patch("app.app.get_db_connection") as mock_db:
            mock_connection = mock_db.return_value
            mock_cursor = mock_connection.cursor.return_value
            mock_cursor.fetchone.return_value = (1,)

            response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
