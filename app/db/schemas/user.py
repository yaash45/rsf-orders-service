from sqlalchemy import UUID, Column, DateTime, String

from app.db import Base


class UserDb(Base):
    __tablename__ = "User"

    id = Column(UUID, primary_key=True)
    created = Column(DateTime, nullable=False)
    modified = Column(DateTime, nullable=False)
    name = Column(String, nullable=False)  # TODO: consider capping length
    email = Column(String, unique=True, nullable=False)
    kind = Column(String(10), nullable=False)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}, email={self.email}, created={self.created}, kind={self.kind}, id={self.id}>"
