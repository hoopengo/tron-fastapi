from tronpy import Tron
from app.config import settings

tron_client = Tron(network=settings.TRON_NETWORK)

__all__ = ["tron_client"]
