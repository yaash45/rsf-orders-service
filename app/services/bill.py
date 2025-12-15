from datetime import datetime, timezone
from uuid import UUID

from pydantic import HttpUrl
from sqlalchemy import delete, select, update

from app.core.logging import getLogger
from app.db.schemas.bill import BillDb
from app.exceptions import EntityNotFoundError
from app.models.bill import (
    BillCreate,
    BillPublic,
    BillUpdateAmount,
    BillUpdateImage,
    BillUpdatePaid,
)

from . import BaseService

logger = getLogger(__name__)


class BillService(BaseService):
    def create_bill(self, bill: BillCreate) -> BillPublic:
        """
        Create a new bill.

        Args:
            bill (BillCreate): The bill to create.

        Returns:
            BillPublic: The created bill.

        Raises:
            ConflictError: If a bill with the same id already exists.
        """

        new_bill = BillPublic(**bill.model_dump())
        db_bill = BillDb(**new_bill.model_dump())

        self.db.add(db_bill)
        self.db.commit()

        return db_bill

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

        updated_bill = BillPublic(
            id=id,
            amount=bill.amount,
            image_url=request.image_url,
            created=bill.created,
            modified=datetime.now(tz=timezone.utc),
        )

        self.db.execute(
            update(BillDb).where(BillDb.id == id).values(updated_bill.model_dump()),
        )

        return updated_bill

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

        updated_bill = BillPublic(
            id=id,
            amount=request.amount,
            image_url=HttpUrl(bill.image_url) if bill.image_url else None,
            created=bill.created,
            modified=datetime.now(tz=timezone.utc),
        )

        self.db.execute(
            update(BillDb).where(BillDb.id == id).values(updated_bill.model_dump()),
        )

        return updated_bill

    def mark_paid(self, id: UUID, request: BillUpdatePaid) -> BillPublic | None:
        bill = self._find_existing_bill(id)

        if not bill:
            return None

        updated_bill = BillPublic(
            id=id,
            amount=bill.amount,
            image_url=HttpUrl(bill.image_url) if bill.image_url else None,
            paid=request.paid,
            created=bill.created,
            modified=datetime.now(tz=timezone.utc),
        )

        self.db.execute(
            update(BillDb).where(BillDb.id == id).values(updated_bill.model_dump()),
        )

        return updated_bill

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
        )
