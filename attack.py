import asyncio
import loxi.of13 as ofp 

async def inject_malicious_flow(sw_writer, observer, comparator, controller_stub, message_store, delay=10):
    '''
    Function we used to simulate the attack scenario from the paper.

    Instead of making and sending a fake network packet, it's easier to just make the loxigen object
    that has the malicious flow and then insert it into our architecture flow to see if it's picked up.

    Parameters are self-explanatory, see where this is used in interceptor.py
    '''
    await asyncio.sleep(delay)

    msg = ofp.message.flow_add(
        xid=0x41414141,
        priority=40000,
        buffer_id=ofp.OFP_NO_BUFFER,
        out_port=ofp.OFPP_ANY,
        out_group=ofp.OFPG_ANY,
        match=ofp.match([
            ofp.oxm.in_port(1),
            ofp.oxm.eth_src([0x00, 0x00, 0x00, 0x00, 0x00, 0x01]), 
            # destination mac address is just a dummy mac address
            ofp.oxm.eth_dst([0xde, 0xad, 0xbe, 0xef, 0x00, 0x01]),
        ]),
        instructions=[
            ofp.instruction.apply_actions([
                ofp.action.output(port=2, max_len=0),
            ])
        ],
    )

    print("[!] injecting dummy malicious FLOW_MOD")

    #
    # EXACT SAME handling logic as in the interceptor proxy's handler
    #

    observer_succeeded = observer.add_message(msg)

    if msg.type == 14 and observer_succeeded:
        print("[!] network programming attempt detected! calling comparator.")
        status, flow_obj = comparator.compare(controller_stub, observer)

        if status:
            print("[!] Allow flow to be applied")
            sw_writer.write(msg.pack())
            await sw_writer.drain()
        else:
            print("[!] BLOCKED MALICIOUS NETWORK MODIFICATION ATTEMPT")
            message_store.append_entry(flow_obj)
