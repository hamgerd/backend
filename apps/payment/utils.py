from rest_framework.exceptions import ValidationError

from apps.payment.choices import BillStatusChoice
from apps.payment.serializer import TransactionResultSerializer


def build_transaction_result(ticket_transaction):
    status = ticket_transaction.status.value
    data = {
        "transaction_id": ticket_transaction.public_id,
        "status": status,
    }

    match BillStatusChoice(status):
        case BillStatusChoice.PENDING:
            data["message"] = "transaction is pending"
        case BillStatusChoice.CANCELLED:
            data["message"] = "transaction canceled"
        case BillStatusChoice.SUCCESS:
            data["message"] = "transaction successful"
            # in free tickets public id has passed into transaction_id
            # so there serializer can't parse it into CharField for ref_id we need to str(...)
            data["ref_id"] = str(ticket_transaction.transaction_id)
        case _:
            raise ValidationError("Invalid transaction status.")

    serializer = TransactionResultSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.data
