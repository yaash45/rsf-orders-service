from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select

from app.core.logging import get_logger
from app.db.schemas import BillDb, UserDb
from app.exceptions import EntityNotFoundError
from app.models.bill import (
    BillIssueRequest,
    BillPublic,
    BillUpdateAmount,
    BillUpdateImage,
    BillUpdatePaid,
)

from . import BaseService

logger = get_logger(__name__)


class BillService(BaseService):
    def issue_bill(self, request: BillIssueRequest) -> BillPublic | None:
        """
        Create a new bill.

        Args:
            bill (BillIssueRequest): The bill to create for a user.

        Returns:
            BillPublic: The created bill.

        Raises:
            ConflictError: If a bill with the same id already exists.
        """

        user = self.db.get(UserDb, request.user_id)

        if not user:
            return None

        new_bill = BillPublic(**request.model_dump())
        db_bill = BillDb(
            id=new_bill.id,
            amount=new_bill.amount,
            image_url=str(new_bill.image_url) if new_bill.image_url else None,
            paid=new_bill.paid,
            created=new_bill.created,
            modified=new_bill.modified,
            user_id=new_bill.user_id,
        )

        self.db.add(db_bill)
        self.db.commit()

        user.bills.append(db_bill)

        return new_bill

    def _find_existing_bill(self, id: UUID) -> BillDb | None:
        """
        Find a bill by its id.

        Args:
            id (UUID): The id of the bill to find.

        Returns:
            BillDb | None: The bill if found, otherwise None.
        """
        return self.db.execute(
            select(BillDb).where(BillDb.id == id)
        ).scalar_one_or_none()

    def get_bill(self, id: UUID) -> BillPublic | None:
        """
        Get a bill by its id.

        Args:
            id (UUID): The id of the bill to get.

        Returns:
            BillPublic | None: The bill if found, otherwise None.

        """
        return self._find_existing_bill(id)

    def upload_image(self, id: UUID, request: BillUpdateImage) -> BillPublic:
        bill = self._find_existing_bill(id)

        if bill is None:
            raise EntityNotFoundError.from_id(entity="Bill", id=id)

        bill.image_url = str(request.image_url)
        bill.modified = datetime.now(tz=timezone.utc)

        self.db.commit()

        return bill

    def update_amount(self, id: UUID, request: BillUpdateAmount) -> BillPublic:
        """
        Update a bill's amount.

        Args:
            updated (BillUpdateAmount): The bill id and new amount.

        Returns:
            BillPublic: The updated bill.

        Raises:
            EntityNotFoundError: If the bill with the given id is not found.
        """
        if request.amount is None:
            raise ValueError("Bill amount cannot be None.")

        bill = self._find_existing_bill(id)

        if bill is None:
            raise EntityNotFoundError.from_id(entity="Bill", id=id)

        bill.amount = request.amount
        bill.modified = datetime.now(tz=timezone.utc)

        self.db.commit()

        return bill

    def mark_paid(self, id: UUID, request: BillUpdatePaid) -> BillPublic | None:
        bill = self._find_existing_bill(id)

        if not bill:
            return None

        bill.paid = request.paid
        bill.modified = datetime.now(tz=timezone.utc)

        self.db.commit()

        return bill

    def delete_bill(self, id: UUID) -> BillPublic | None:
        """
        Deletes a bill by its id.

        Args:
            id (UUID): The id of the bill to delete.

        Returns:
            BillPublic | None: The deleted bill if found, otherwise None.
        """

        result = self.db.execute(
            delete(BillDb)
            .where(BillDb.id == id)
            .returning(
                BillDb.id,
                BillDb.amount,
                BillDb.image_url,
                BillDb.paid,
                BillDb.created,
                BillDb.modified,
                BillDb.user_id,
            )
        ).fetchall()

        if not result:
            return None

        self.db.commit()

        deleted_bill = result[0]

        return BillPublic(
            id=deleted_bill.id,
            amount=deleted_bill.amount,
            image_url=deleted_bill.image_url,
            paid=deleted_bill.paid,
            created=deleted_bill.created,
            modified=deleted_bill.modified,
            user_id=deleted_bill.user_id,
        )
