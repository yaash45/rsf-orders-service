from dataclasses import dataclass

from app.bill.domain.models import BillCreate, BillPublic
from app.bill.domain.ports import BillPort
from app.core.logging import get_logger
from app.core.service import BaseService

logger = get_logger(__name__)


@dataclass
class BillService(BaseService):
    """
    Service meant for bill management
    """

    port: BillPort

    @classmethod
    def instance(cls, port: BillPort) -> "BillService":
        return cls(port=port)

    def issue_bill(self, request: BillCreate) -> BillPublic:
        return self.port.create_bill(request)
