from datetime import datetime, timezone
from uuid import UUID

from app.db.schemas import BillDb, PaymentDb
from app.exceptions import EntityNotFoundError
from app.models.payment import PaymentCreate, PaymentPublic

from . import BaseService


class PaymentService(BaseService):
    """
    Service for handling payment related operations
    """

    def get_payments(self, payment_id: UUID) -> PaymentPublic | None:
        """
        Retrieves a payment by its ID.

        Args:
            payment_id (UUID): The ID of the payment to retrieve.

        Returns:
            PaymentPublic: The payment with the given ID, or None if no such payment exists.
        """
        return self.db.get(PaymentDb, payment_id)

    def make_payment(self, request: PaymentCreate) -> PaymentPublic:
        """
        Makes a payment for the given bill.

        Args:
            request (PaymentCreate): The request to make a payment.

        Returns:
            PaymentPublic: The payment that was made.

        Raises:
            EntityNotFoundError: If the bill with the given ID does not exist.
        """
        bill: BillDb | None = self.db.get(BillDb, request.bill_id)

        if not bill:
            raise EntityNotFoundError.from_id("Bill", request.bill_id)

        new_payment: PaymentPublic = PaymentPublic(**request.model_dump())

        db_payment = PaymentDb(
            id=new_payment.id,
            created=new_payment.created,
            modified=new_payment.modified,
            amount=request.amount,
            method=request.method.value,
            bill_id=request.bill_id,
        )

        self.db.add(db_payment)
        bill.payments.append(db_payment)

        # check and update bill paid status
        remaining_amount = bill.amount - new_payment.amount

        if remaining_amount <= 0.0:
            bill.paid = True
        else:
            # if a refund was issued, bill may no longer be paid
            bill.paid = False

        bill.modified = datetime.now(tz=timezone.utc)

        self.db.commit()

        return new_payment
