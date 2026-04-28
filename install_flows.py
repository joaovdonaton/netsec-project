import requests
import argparse

from collections import Counter
import requests
import time

DEVICE = "of:0000000000000001"
auth = ("onos", "rocks")
url = f"http://127.0.0.1:8181/onos/v1/flows/{DEVICE}"

time.sleep(2)

flows = requests.get(url, auth=auth).json()["flows"]

print("total:", len(flows))
print("by app:", Counter(flow["appId"] for flow in flows))
print("rest:", sum(flow["appId"] == "org.onosproject.rest" for flow in flows))
print("states:", Counter(flow["state"] for flow in flows))


ONOS_API_USERNAME = 'onos'
ONOS_API_PASSWORD = 'rocks'
DEVICE = "of:0000000000000001"

def install(COUNT):
    URL = f"http://127.0.0.1:8181/onos/v1/flows/{DEVICE}?appId=org.onosproject.rest"

    for i in range(COUNT):
        mac = f"00:00:00:00:{i // 256:02x}:{i % 256:02x}"

        flow = {
            "priority": 40000,
            "timeout": 30,
            "isPermanent": False,
            "deviceId": DEVICE,
            "selector": {
                "criteria": [
                    {"type": "IN_PORT", "port": "1"},
                    {"type": "ETH_DST", "mac": mac},
                ]
            },
            "treatment": {
                "instructions": [
                    {"type": "OUTPUT", "port": "2"}
                ]
            },
        }

        r = requests.post(URL, json=flow, auth=(ONOS_API_USERNAME, ONOS_API_PASSWORD))
        print(i, r.status_code, mac)


def check():
    url = f"http://127.0.0.1:8181/onos/v1/flows/{DEVICE}"
    r = requests.get(url, auth=(ONOS_API_USERNAME, ONOS_API_PASSWORD))
    flows = r.json()["flows"]

    rest_flows = sum(flow["appId"] == "org.onosproject.rest" for flow in flows)

    print(f"There are {rest_flows} REST-installed flows on {DEVICE}")


def clear_flows():
    url = "http://127.0.0.1:8181/onos/v1/flows/application/org.onosproject.rest"
    r = requests.delete(url, auth=(ONOS_API_USERNAME, ONOS_API_PASSWORD))
    print(r.status_code)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--install', action='store_true')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--clear', action='store_true')
    args = parser.parse_args()

    INSTALL_FLOWS = args.install
    CHECK_FLOWS = args.check
    CLEAR_FLOWS = args.clear

    if INSTALL_FLOWS:
        install(1000)

    if CHECK_FLOWS:
        check()

    if CLEAR_FLOWS:
        clear_flows()