import asyncio
import warnings
from datetime import datetime
from typing import Optional

from .const import LOGGER
from .parser import MessageParser

__all__ = ("Endpoint", "open_datagram_endpoint",)


class Endpoint:
    def __init__(self, queue_size=None):
        if queue_size is None:
            queue_size = 0
        self._queue = asyncio.Queue(queue_size)
        self._closed = False
        self._transport = None
        self._write_ready_future = None

    def feed_datagram(self, data, addr):
        if not (message := MessageParser.parser(data.decode())):
            return

        print(f"{addr=}")
        print(f"{message=}")
        LOGGER.warning("addr <%s>", addr)
        LOGGER.warning("message <%s>", message)

        try:
            self._queue.put_nowait((message, addr))
        except asyncio.QueueFull:
            warnings.warn('Endpoint queue is full')

    def close(self):
        if self._closed:
            return
        self._closed = True
        if self._queue.empty():
            self.feed_datagram(None, None)
        if self._transport:
            self._transport.close()

    def send(self, message):
        """Send a datagram to the given address."""
        if self._closed:
            raise OSError("Endpoint is closed")
        message = message if isinstance(message, bytes) else message.encode("ascii")
        self._transport.sendto(message)

    async def receive(self):
        if self._queue.empty() and self._closed:
            raise OSError("Endpoint is closed")
        message = await self._queue.get()
        if message is None:
            raise OSError("Endpoint is closed")
        return message

    def abort(self):
        if self._closed:
            raise OSError("Endpoint is closed")
        self._transport.abort()
        self.close()

    async def drain(self):
        if self._write_ready_future is not None:
            await self._write_ready_future

    @property
    def address(self):
        return self._transport.get_extra_info("socket").getsockname()

    @property
    def closed(self):
        return self._closed


class LookInClientProtocol:
    def __init__(self, endpoint: Endpoint):
        self._endpoint = endpoint

    def connection_made(self, transport):
        self._endpoint._transport = transport

    def datagram_received(self, data, addr):
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Received:", data.decode())
        self._endpoint.feed_datagram(data, addr)
        # message = MessageParser.parser(data.decode())
        # print(f"{message=}")

    def error_received(self, exc):
        print('Error received:', exc)
        msg = 'Endpoint received an error: {!r}'
        warnings.warn(msg.format(exc))

    def connection_lost(self, exc):
        print("Socket closed, stop the event loop")
        assert exc is None
        if self._endpoint._write_ready_future is not None:
            self._endpoint._write_ready_future.set_result(None)
        self._endpoint.close()

    def pause_writing(self):
        assert self._endpoint._write_ready_future is None
        loop = self._endpoint._transport._loop
        self._endpoint._write_ready_future = loop.create_future()

    def resume_writing(self):
        assert self._endpoint._write_ready_future is not None
        self._endpoint._write_ready_future.set_result(None)
        self._endpoint._write_ready_future = None


async def open_datagram_endpoint(
    local_host: str,
    local_port: int,
    remote_host: str,
    remote_port: int,
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> Endpoint:
    loop = loop or asyncio.get_event_loop()
    endpoint = Endpoint()

    await loop.create_datagram_endpoint(
        protocol_factory=lambda: LookInClientProtocol(endpoint),
        remote_addr=(remote_host, remote_port),
        local_addr=(local_host, local_port),
        reuse_port=True,
        allow_broadcast=True,
    )

    return endpoint
