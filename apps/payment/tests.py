from unittest.mock import MagicMock, patch

from decouple import config
from django.conf import settings
from django.test import TestCase

from .service import Metadata, TransactionRequest, send_payment_request, verify_payment_request
from .utils import CurrencyEnum

MERCHANT_ID = config("MERCHANT_ID")


class PaymentServiceTest(TestCase):
    @patch("apps.payment.service.httpx.Client.post")
    def test_send_payment_request_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"code": 100, "authority": "test_authority"}}
        mock_post.return_value = mock_response

        tx = TransactionRequest(
            merchant_id=MERCHANT_ID,
            amount=10000,
            currency=CurrencyEnum.IRT,
            note="Test payment",
            callback_url="https://example.com/callback",
            metadata=Metadata(mobile="09121234567", email="test@example.com", order_id="1234"),
        )

        result = send_payment_request(tx)
        print(result)
        self.assertTrue(result["status"])
        self.assertEqual(result["authority"], "test_authority")
        self.assertIn("url", result)

    @patch("apps.payment.service.httpx.Client.post")
    def test_send_payment_request_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"code": -1}}
        mock_post.return_value = mock_response

        tx = TransactionRequest(
            merchant_id=MERCHANT_ID,
            amount=5000,
            currency=CurrencyEnum.IRT,
            note="Invalid payment",
            callback_url="https://example.com/callback",
        )

        result = send_payment_request(tx)
        print(result)
        self.assertFalse(result["status"])
        self.assertEqual(result["code"], "-1")

    @patch("apps.payment.service.httpx.Client.post")
    def test_verify_payment_request_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"code": 100, "ref_id": "ref_123456"}}
        mock_post.return_value = mock_response

        result = verify_payment_request("test_authority", 10000, settings)
        self.assertTrue(result["status"])
        self.assertEqual(result["RefID"], "ref_123456")

    @patch("apps.payment.service.httpx.Client.post")
    def test_verify_payment_request_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"code": -22}}
        mock_post.return_value = mock_response

        result = verify_payment_request("invalid_authority", 10000, settings)
        self.assertFalse(result["status"])
        self.assertEqual(result["code"], "-22")
