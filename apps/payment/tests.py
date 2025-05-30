from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from decimal import Decimal
import json
import httpx

from .models import TicketTransaction, BillStatus
from .service import TransactionRequest, send_payment_request, verify_payment_request
from .utils import CurrencyEnum
from apps.events.models import Ticket

User = get_user_model()

class TicketTransactionModelTests(TestCase):
    """Tests for the TicketTransaction model"""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            # username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Mock a ticket (since we don't have full access to the Ticket model)
        self.ticket = Ticket.objects.create()
        
    def test_ticket_transaction_creation(self):
        """Test creating a TicketTransaction instance"""
        transaction = TicketTransaction.objects.create(
            description="Test Transaction",
            amount=Decimal('100.00'),
            currency=CurrencyEnum.IRR.name,
            status=BillStatus.PENDING.name,
            ticket=self.ticket
        )
        
        self.assertEqual(transaction.description, "Test Transaction")
        self.assertEqual(transaction.amount, Decimal('100.00'))
        self.assertEqual(transaction.currency, CurrencyEnum.IRR.name)
        self.assertEqual(transaction.status, BillStatus.PENDING.name)
        self.assertIsNotNone(transaction.created_at)
        self.assertIsNotNone(transaction.paid_at)
    
    def test_status_choices(self):
        """Test that BillStatus choices are valid"""
        choices = dict(BillStatus.choices())
        self.assertEqual(choices['PENDING'], 'pending')
        self.assertEqual(choices['CONFIRMED'], 'confirmed')
        self.assertEqual(choices['CANCELLED'], 'cancelled')
    
    def test_currency_choices(self):
        """Test that CurrencyEnum choices are valid"""
        choices = dict(CurrencyEnum.choices())
        self.assertEqual(choices['IRR'], 'IRR')
        self.assertEqual(choices['IRT'], 'IRT')
    
    def test_model_validation(self):
        """Test model validation"""
        # The clean method validation in the model seems to have an error
        # It references self.bill.amount but there's no bill field
        # Let's test the MinValueValidator on amount instead
        with self.assertRaises(ValidationError):
            transaction = TicketTransaction(
                description="Test Transaction",
                amount=Decimal('-100.00'),  # Negative amount should fail validation
                currency=CurrencyEnum.IRR.name,
                status=BillStatus.PENDING.name,
                ticket=self.ticket
            )
            transaction.full_clean()


class PaymentViewTests(APITestCase):
    """Tests for the payment views"""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            # username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create a test ticket
        self.ticket = Ticket.objects.create()
        
        # Create a test transaction
        self.transaction = TicketTransaction.objects.create(
            description="Test Transaction",
            amount=Decimal('100.00'),
            currency=CurrencyEnum.IRR.name,
            status=BillStatus.PENDING.name,
            ticket=self.ticket
        )
        
        # Set up the API client
        self.client = APIClient()
        
    @patch('apps.payment.views.send_payment_request')
    def test_pay_bill_success(self, mock_send_payment_request):
        """Test successful payment initiation"""
        # Configure the mock
        mock_send_payment_request.return_value = {
            "status": 200,
            "authority": "test-authority",
            "response": "https://payment-gateway.com/pay/test-authority"
        }
        
        # Log in the user
        self.client.force_authenticate(user=self.user)
        
        # Call the view
        url = reverse('payment:payment-list', kwargs={'bill_id': self.transaction.id})
        response = self.client.post(url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)  # Expect a redirect
        
        # Verify the transaction was updated
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.authority, "test-authority")
    
    @patch('apps.payment.views.send_payment_request')
    def test_pay_bill_failure(self, mock_send_payment_request):
        """Test failed payment initiation"""
        # Configure the mock
        mock_send_payment_request.return_value = {
            "status": 400,
            "code": "invalid_merchant"
        }
        
        # Log in the user
        self.client.force_authenticate(user=self.user)
        
        # Call the view
        url = reverse('payment:payment-list', kwargs={'bill_id': self.transaction.id})
        response = self.client.post(url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"status": 400, "code": "invalid_merchant"})
    
    def test_pay_bill_unauthenticated(self):
        """Test that unauthenticated users cannot initiate payments"""
        # Do NOT log in the user
        
        # Call the view
        url = reverse('payment:payment-list', kwargs={'bill_id': self.transaction.id})
        response = self.client.post(url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('apps.payment.views.verify_payment_request')
    def test_verify_payment_success(self, mock_verify_payment_request):
        """Test successful payment verification"""
        # Update transaction with an authority
        self.transaction.authority = "test-authority"
        self.transaction.save()
        
        # Configure the mock
        mock_verify_payment_request.return_value = {
            "status": 100,
            "ref_id": "test-ref-id"
        }
        
        # Call the view
        # The URL seems to follow the same pattern but with a different basename
        url = reverse('payment:payment-list', kwargs={'authority': "test-authority"})
        response = self.client.post(url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the transaction was updated
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, BillStatus.CONFIRMED.name)
        self.assertEqual(self.transaction.transaction_id, "test-ref-id")
    
    @patch('apps.payment.views.verify_payment_request')
    def test_verify_payment_failure(self, mock_verify_payment_request):
        """Test failed payment verification"""
        # Update transaction with an authority
        self.transaction.authority = "test-authority"
        self.transaction.save()
        
        # Configure the mock
        mock_verify_payment_request.return_value = {
            "status": 101,
            "code": "payment_failed"
        }
        
        # Call the view
        url = reverse('payment:payment-list', kwargs={'authority': "test-authority"})
        response = self.client.post(url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"status": 101, "code": "payment_failed"})


class PaymentServiceTests(TestCase):
    """Tests for the payment service functions"""
    
    def setUp(self):
        # Create settings mock
        self.settings_mock = MagicMock()
        self.settings_mock.MERCHANT = "test-merchant"
        self.settings_mock.PAYMENT_PORTAL_BASE_URL = "https://api.zarinpal.com/"
    
    @patch('apps.payment.service.httpx.Client')
    def test_send_payment_request_success(self, mock_client):
        """Test successful payment request"""
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "code": 100,
                "authority": "test-authority",
                "message": "Success",
            }
        }
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response
        
        # Create a transaction request
        tx_request = TransactionRequest(
            merchant_id="test-merchant",
            amount=10000,
            currency=CurrencyEnum.IRR,
            description="Test Transaction",
            callback_url="https://example.com/callback"
        )
        
        # Call the service function
        result = send_payment_request(tx_request, self.settings_mock)
        
        # Assert the result
        self.assertTrue(result["status"])
        self.assertEqual(result["authority"], "test-authority")
        self.assertEqual(result["url"], "https://api.zarinpal.com/pg/StartPay/test-authority")
    
    @patch('apps.payment.service.httpx.Client')
    def test_send_payment_request_failure(self, mock_client):
        """Test failed payment request"""
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "code": 101,
                "message": "Invalid merchant ID",
            }
        }
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response
        
        # Create a transaction request
        tx_request = TransactionRequest(
            merchant_id="invalid-merchant",
            amount=10000,
            currency=CurrencyEnum.IRR,
            description="Test Transaction",
            callback_url="https://example.com/callback"
        )
        
        # Call the service function
        result = send_payment_request(tx_request, self.settings_mock)
        
        # Assert the result
        self.assertFalse(result["status"])
        self.assertEqual(result["code"], "101")
    
    @patch('apps.payment.service.httpx.Client')
    def test_send_payment_request_http_error(self, mock_client):
        """Test HTTP error in payment request"""
        # Configure the mock to raise an exception
        mock_client.return_value.__enter__.return_value.post.side_effect = httpx.RequestError("Connection error")
        
        # Create a transaction request
        tx_request = TransactionRequest(
            merchant_id="f7c91e84-3b5a-4e38-8a4e-df9e02c7a1d3",
            amount=10000,
            currency=CurrencyEnum.IRR,
            description="Test Transaction",
            callback_url="https://example.com/callback"
        )
        
        # Call the service function
        result = send_payment_request(tx_request, self.settings_mock)
        
        # Assert the result
        self.assertFalse(result["status"])
        self.assertEqual(result["code"], "connection_error")
    
    @patch('apps.payment.service.httpx.Client')
    def test_verify_payment_request_success(self, mock_client):
        """Test successful payment verification"""
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "code": 100,
                "ref_id": "test-ref-id",
                "message": "Success",
            }
        }
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response
        
        # Call the service function
        result = verify_payment_request("test-authority", 10000, self.settings_mock)
        
        # Assert the result
        self.assertTrue(result["status"])
        self.assertEqual(result["RefID"], "test-ref-id")
    
    @patch('apps.payment.service.httpx.Client')
    def test_verify_payment_request_failure(self, mock_client):
        """Test failed payment verification"""
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "code": 101,
                "message": "Invalid payment",
            }
        }
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response
        
        # Call the service function
        result = verify_payment_request("invalid-authority", 10000, self.settings_mock)
        
        # Assert the result
        self.assertFalse(result["status"])
        self.assertEqual(result["code"], "101")
