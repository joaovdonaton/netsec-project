#!/usr/bin/env python3
import asyncio
import struct

PROXY_HOST = "0.0.0.0"
PROXY_PORT = 16653      # Mininet connects here
CTRL_HOST = "127.0.0.1"
CTRL_PORT = 6653        # ONOS listens here

DROP_FLOW_MOD = False   # set True to test blocking controller flow installs


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
            hdr = await reader.readexactly(8)              # OF header
            ver, typ, length, xid = struct.unpack("!BBHI", hdr)
            body = await reader.readexactly(length - 8)

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
    ctrl_reader, ctrl_writer = await asyncio.open_connection(CTRL_HOST, CTRL_PORT)
    await asyncio.gather(
        relay(sw_reader, ctrl_writer, "SW->CTL"),
        relay(ctrl_reader, sw_writer, "CTL->SW", drop_ctl_flow_mod=DROP_FLOW_MOD),
    )

async def main():
    server = await asyncio.start_server(handle_switch, PROXY_HOST, PROXY_PORT)
    print(f"Proxy on {PROXY_HOST}:{PROXY_PORT} -> {CTRL_HOST}:{CTRL_PORT}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
