import logging
from typing import Final

DOMAIN = "lookin"

UDP_DISCOVER_TIMEOUT: Final = 10
UDP_LOCAL_PORT = 61201
UDP_REMOTE_PORT = 61201

UDP_DISCOVER: Final = "LOOK.in:Discover!"
UDP_ALIVE: Final = "LOOK.in:Alive"
UDP_UPDATED: Final = "LOOK.in:Updated"

LOGGER = logging.getLogger(__name__)