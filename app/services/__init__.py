from __future__ import annotations

from sqlalchemy.orm import Session


class BaseService:
    """
    Base service class for all services in the application.

    Provides a common interface for services to interact with the database.
    """

    def __init__(self, db: Session):
        self.db = db
