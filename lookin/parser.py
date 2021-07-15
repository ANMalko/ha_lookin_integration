from typing import Optional, Union

from .const import UDP_ALIVE, UDP_UPDATED
from .udp_message import UDPAlive, UDPUpdate


class MessageParser:

    @classmethod
    def parser(cls, message: str) -> Optional[Union[UDPAlive, UDPUpdate]]:
        tag, data = message.split("!")

        message = cls.serializer(tag=tag, data=data)

        return message

    @classmethod
    def serializer(cls, tag: str, data: str) -> Optional[Union[UDPAlive, UDPUpdate]]:

        message = None
        splited_data = data.split(":")

        if tag == UDP_ALIVE and len(splited_data) == 6:
            message = UDPAlive(
                id=splited_data[0],
                device_type_hex=splited_data[1],
                batteries=bool(splited_data[2]),
                ip=splited_data[3],
                version=splited_data[4],
                storage=splited_data[5]
            )
        elif tag == UDP_UPDATED and len(splited_data) == 4:
            message = UDPUpdate(
                id=splited_data[0],
                sensor=splited_data[1],
                event=splited_data[2],
                value=splited_data[3],
            )

        return message
