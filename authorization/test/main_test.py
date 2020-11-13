#!/usr/bin/python3.6

import asyncio

from authorization.UserClient import UserClient


async def main(loop):
    picker = UserClient()
    #await picker.request_driver({"uid": 20, "capacity": 50})
    # await picker.update_route({"uid": 10, "data": {
    #     "route": ["yke{FurzeL{AQ", "une{FgszeLWa@Sa@Eq@Bg@@AV}CPuD`@cMMaCNqA^_CFe@R{@VkAV{@`@qAr@cBT]`@q@NWlBaCr@m@FG",
    #               "_`e{Fsq|eL\\P", "a_e{Faq|eL@RDLFHHDPDb@\\t@lB", "{zd{F}j|eL"],
    #     "latitude": 41.317631, "longitude": 69.290964, "radius": 0
    #     }})
    trip_id = 10
    result = await picker.login({"login": "", "password": ""})
    print(result)

loop = asyncio.get_event_loop()
#loop.run_until_complete(firebase_push(loop))
#loop.run_until_complete(firebase_broadcast(loop))
loop.run_until_complete(main(loop))
#loop.run_until_complete(main(loop))
