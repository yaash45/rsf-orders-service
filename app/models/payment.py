from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from . import Identifiable, TimeStamped


class PaymentMethod(str, Enum):
    """
    Form of payment represented as an enum
    """

    CASH = "cash"
    UPI = "upi"
    BANK = "bank"
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    CHEQUE = "cheque"
    OTHER = "other"


class PaymentBase(BaseModel):
    """
    Base model containing attributes for a payment

    If a negative amount is provided, it signifies a refund
    """

    amount: float
    bill_id: UUID
    method: PaymentMethod


class PaymentCreate(PaymentBase):
    """
    Creation request model for a payment
    """


class PaymentPublic(PaymentCreate, Identifiable, TimeStamped):
    """
    Public-facing payment model
    """

    model_config = ConfigDict(from_attributes=True)
