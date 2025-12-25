from typing import Iterator
from uuid import UUID

from fastapi import Depends, Response, status
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.bill import (
    BillIssueRequest,
    BillPublic,
    BillUpdateAmount,
    BillUpdateImage,
    BillUpdatePaid,
)
from app.services.bill import BillService

router = APIRouter(prefix="/v0")


def get_bill_service(db: Session = Depends(get_db)) -> Iterator[BillService]:
    """
    Returns a BillService instance using the provided database session.

    The BillService instance is used to encapsulate database operations
    related to bills.
    """
    yield BillService(db=db)


@router.get(
    "/bills/{id}",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Bill not found",
        },
    },
    response_model=BillPublic,
    status_code=status.HTTP_200_OK,
)
def get_bill(
    id: UUID,
    service: BillService = Depends(get_bill_service),
) -> BillPublic:
    """
    Returns a single Bill queried by id

    Args:
        id: the UUID of the Bill

    Returns:
        a Bill object if the id matches an existing bill in the database

    Raises:
        HttpException with a 404 status if the bill cannot be found
    """

    bill = service.get_bill(id=id)

    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found",
        )

    return bill


@router.post(
    "/bills",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found",
        },
    },
    status_code=status.HTTP_201_CREATED,
    response_model=BillPublic,
)
def issue_bill(
    request: BillIssueRequest,
    service: BillService = Depends(get_bill_service),
) -> BillPublic:
    """
    Creates a new bill.

    Args:
        bill (BillIssueRequest): The bill to create for a user

    Returns:
        BillPublic: The created bill.

    Raises:
        HTTPException: when a user with provided id is not found
    """
    bill = service.issue_bill(request=request)

    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id = '{request.user_id}' not found",
        )

    return bill


@router.patch(
    "/bills/{id}/image",
    status_code=status.HTTP_200_OK,
    response_model=BillPublic,
)
def upload_image(
    id: UUID,
    request: BillUpdateImage,
    service: BillService = Depends(get_bill_service),
) -> BillPublic:
    """
    Updates a bill's image.

    Args:
        id (UUID): The id of the bill to update.
        request (BillUpdateImage): The new image url.

    Returns:
        BillPublic: The updated bill.
    """
    return service.upload_image(id=id, request=request)


@router.patch(
    "/bills/{id}/amount",
    status_code=status.HTTP_200_OK,
    response_model=BillPublic,
)
def update_amount(
    id: UUID,
    request: BillUpdateAmount,
    service: BillService = Depends(get_bill_service),
) -> BillPublic:
    """
    Updates a bill's amount.

    Args:
        id (UUID): The id of the bill to update.
        request (BillUpdateAmount): The new amount.

    Returns:
        BillPublic: The updated bill.
    """
    return service.update_amount(id=id, request=request)


@router.patch(
    "/bills/{id}/paid",
    status_code=status.HTTP_200_OK,
    response_model=BillPublic,
)
def mark_paid(
    id: UUID,
    request: BillUpdatePaid,
    service: BillService = Depends(get_bill_service),
):
    """
    Marks a bill as paid.

    Args:
        id (UUID): The id of the bill to mark as paid.
        request (BillUpdatePaid): The request to mark the bill as paid.

    Returns:
        BillPublic: The updated bill.
    """
    return service.mark_paid(id=id, request=request)


@router.delete(
    "/bills/{id}",
    status_code=status.HTTP_200_OK,
    response_model=BillPublic,
)
def delete_bill(
    id: UUID,
    service: BillService = Depends(get_bill_service),
) -> Response | BillPublic:
    """
    Deletes a bill by its id.

    Args:
        id (UUID): The id of the bill to delete.

    Returns:
        Response | BillPublic: The deleted bill if found, otherwise a response with a 200 status code and "Bill not found" content.

    """
    result = service.delete_bill(id=id)

    if result is None:
        return Response(status_code=status.HTTP_200_OK, content="Bill not found")

    return result
