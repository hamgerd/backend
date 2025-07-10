from typing import Any

import httpx
from django.conf import settings
from pydantic import BaseModel, EmailStr, Field, HttpUrl

from .choices import CurrencyChoice

ZP_API_REQUEST = settings.PAYMENT_PORTAL_BASE_URL + "pg/v4/payment/request.json"
ZP_API_STARTPAY = settings.PAYMENT_PORTAL_BASE_URL + "pg/StartPay/"
ZP_API_VERIFY = settings.PAYMENT_PORTAL_BASE_URL + "pg/v4/payment/verify.json"


class Metadata(BaseModel):
    mobile: str | None = None
    email: EmailStr | None = None
    order_id: str | None = None


class TransactionRequest(BaseModel):
    merchant_id: str = Field(..., min_length=36, max_length=36)
    amount: int = Field(..., gt=0)
    currency: CurrencyChoice | None = None
    note: str | None = None
    callback_url: HttpUrl
    metadata: Metadata | None = None


def send_payment_request(tx: TransactionRequest) -> dict[str, Any]:
    payload = {
        "MerchantID": tx.merchant_id,
        "Amount": tx.amount,
        "Description": tx.note,
        "CallbackURL": str(tx.callback_url),
    }

    if tx.metadata:
        if tx.metadata.mobile:
            payload["Phone"] = tx.metadata.mobile
        if tx.metadata.email:
            payload["Email"] = str(tx.metadata.email)
        if tx.metadata.order_id:
            payload["OrderId"] = tx.metadata.order_id

    try:
        with httpx.Client(timeout=10) as client:
            response = client.post(ZP_API_REQUEST, json=payload)
        if response.status_code != 200:
            return {"status": False, "code": f"HTTP {response.status_code}"}

        data = response.json().get("data", {})
        if data.get("code") == 100:
            authority = data["authority"]
            return {
                "status": True,
                "authority": authority,
                "url": f"{ZP_API_STARTPAY}{authority}",
            }
        return {"status": False, "code": str(data.get("code", "unknown"))}

    except httpx.TimeoutException:
        return {"status": False, "code": "timeout"}
    except httpx.RequestError:
        return {"status": False, "code": "connection_error"}


def verify_payment_request(authority: str, amount: int, merchant_id) -> dict[str, Any]:
    payload = {
        "MerchantID": merchant_id,
        "Amount": amount,
        "Authority": authority,
    }

    try:
        with httpx.Client(timeout=10) as client:
            response = client.post(ZP_API_VERIFY, json=payload)
        if response.status_code != 200:
            return {"status": False, "code": f"HTTP {response.status_code}"}

        data = response.json().get("data", {})
        if data.get("code") == 100:
            return {"status": True, "RefID": data["ref_id"]}
        return {"status": False, "code": str(data.get("code", "unknown"))}

    except httpx.TimeoutException:
        return {"status": False, "code": "timeout"}
    except httpx.RequestError:
        return {"status": False, "code": "connection_error"}
