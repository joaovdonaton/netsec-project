#!/usr/bin/env python3
import asyncio
import struct
import requests
import threading
import time
import loxi.of13 as ofp 

print(ofp.message.parse_header)

ONOS_API_USERNAME = 'onos'
ONOS_API_PASSWORD = 'rocks'

PROXY_HOST = "0.0.0.0"
PROXY_PORT = 16653      # mininet will connect to this
CONTROL_HOST = "127.0.0.1"
CONTROL_PORT = 6653        # onos port
DROP_FLOW_MOD = False   # set True to test blocking controller flow installs

def onos_rest_test():
    '''
    Quick test function to experiment with making REST API calls
    to the onos api while things are running
    '''
    while True:
        time.sleep(3)

        r = requests.get('http://127.0.0.1:8181/onos/v1/devices',
            auth=(ONOS_API_USERNAME, ONOS_API_PASSWORD))

        if r.status_code == 200:
            print('successfully queried onos rest api')

            json_data = r.json()

            for device in json_data["devices"]:
                print(f'\tThis is device id {device["id"]}')
                print(f'\t\t{device["humanReadableLastUpdate"]}')
            
            # debug
            #print(json_data)

        else:
            print(f'error querying onos rest, http code {r.status_code}')


# temporary stuff
mt = threading.Thread(target=onos_rest_test)
mt.start()

##################


# these are from the spec 
# https://opennetworking.org/wp-content/uploads/2014/10/openflow-switch-v1.3.5.pdf
# todo: use loxigen or some other kind of solution to make
# it so we don't have to manually parse and detail with it at byte-level
# this is just a proof of concept

OF_TYPES = {
    10: "PACKET_IN",
    14: "FLOW_MOD",
    20: "BARRIER_REQUEST",
    21: "BARRIER_REPLY",
}

async def relay(reader, writer, direction, drop_ctl_flow_mod=False):
    try:
        while True:
            # read the OF header bytes 
            hdr = await reader.readexactly(8)
            ver, typ, length, xid = struct.unpack("!BBHI", hdr)
            body = await reader.readexactly(length - 8)

            if typ == 10:
                print('received a packet in')

            name = OF_TYPES.get(typ, f"TYPE_{typ}")
            print(f"{direction} v={ver} {name} len={length} xid={xid}")

            if drop_ctl_flow_mod and typ == 14:
                print("  -> dropped FLOW_MOD")
                continue

            writer.write(hdr + body)
            await writer.drain()
    except Exception:
        pass
    finally:
        writer.close()
        await writer.wait_closed()

async def handle_switch(sw_reader, sw_writer):
    ctrl_reader, ctrl_writer = await asyncio.open_connection(CONTROL_HOST, CONTROL_PORT)
    await asyncio.gather(
        relay(sw_reader, ctrl_writer, "SW->CTL"),
        relay(ctrl_reader, sw_writer, "CTL->SW", drop_ctl_flow_mod=DROP_FLOW_MOD),
    )

async def main():
    server = await asyncio.start_server(handle_switch, PROXY_HOST, PROXY_PORT)
    print(f"Proxy on {PROXY_HOST}:{PROXY_PORT} -> {CONTROL_HOST}:{CONTROL_PORT}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
