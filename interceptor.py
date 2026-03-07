#!/usr/bin/env python3
import asyncio
import struct
import requests
import threading
import time
import loxi.of13 as ofp 

from architecture import Observer, SDNControllerView
from util import of_type_map

ONOS_API_USERNAME = 'onos'
ONOS_API_PASSWORD = 'rocks'

PROXY_HOST = "0.0.0.0"
PROXY_PORT = 16653      # mininet will connect to this
CONTROL_HOST = "127.0.0.1"
CONTROL_PORT = 6653        # onos port
#DROP_FLOW_MOD = False   # test blocking controller flow installs

obs_msg_filter = [] # 14=flow mod
observer = Observer(obs_msg_filter)

controller_view = SDNControllerView('http://127.0.0.1:8181/onos/v1/flows', ONOS_API_USERNAME, ONOS_API_PASSWORD)
print(controller_view.fetch_network_state())
exit()

async def relay(reader, writer, direction, drop_ctl_flow_mod=False):
    try:
        while True:
            # read the OF header bytes 
            hdr = await reader.readexactly(8)
            ver, typ, length, xid = ofp.message.parse_header(hdr)
            body = await reader.readexactly(length - 8)

            msg = ofp.message.parse_message(hdr + body)
            type_name = of_type_map[msg.type]

            print(f"[{type_name}] {direction}: len={length} xid={xid}")

            observer.add_message(msg, filter_enabled=False)
            #observer.display_stats()

            # if drop_ctl_flow_mod and typ == 14:
            #     print("!!!!!!dropped FLOW_MOD")
            #     continue

            writer.write(hdr + body)
            await writer.drain()
    except Exception as e:
        print('Something wrong in relay!!!')
        print(e)
        #exit()
    finally:
        writer.close()
        await writer.wait_closed()

async def handle_switch(sw_reader, sw_writer):
    ctrl_reader, ctrl_writer = await asyncio.open_connection(CONTROL_HOST, CONTROL_PORT)
    await asyncio.gather(
        relay(sw_reader, ctrl_writer, "To Controller"),
        relay(ctrl_reader, sw_writer, "To Network Device"),
    )

async def main():
    server = await asyncio.start_server(handle_switch, PROXY_HOST, PROXY_PORT)
    print(f"Proxy on {PROXY_HOST}:{PROXY_PORT} -> {CONTROL_HOST}:{CONTROL_PORT}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
