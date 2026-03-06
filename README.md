# netsec-project

My project involves recreating this paper: [Preventing Malicious SDN Applications From Hiding Adverse Network
Manipulations](https://dl.acm.org/doi/pdf/10.1145/3229616.3229620)

Below you can find the information for the SDN simulation setup that I recreated from the paper, in addition to other useful links are resources I used when developing this.

### Setup Information
- Ran on x86 Ubuntu Server 22.04
- Installed: docker, mininet, ONOS docker container (latest version)

- Run the ONOS container with ports mapped so they are accessible on Ubuntu host
- Note that: 
    - 6653 is the port that mininet will use to connect (AKA "southbound" connection)
    - 8181 is the http rest API to talk to ONOS
    - 8101 allows us to connect to ONOS using `ssh -p 8101 karaf@127.0.0.1` (password karaf)
```
docker run -d --name onos --restart unless-stopped \
  -p 6653:6653 -p 8181:8181 -p 8101:8101 \
  -e ONOS_APPS="drivers,openflow,hostprovider,lldpprovider,proxyarp,rest,fwd" \
  onosproject/onos:latest
```
- Run mininet connected to ONOS Controller
```
sudo mn --controller=remote,ip=127.0.0.1,port=6653 --switch ovsk,protocols=OpenFlow13 --topo single,2 --mac
```

- This mininet command connects to the SDN controller and specifies a topology of 1 switch and 2 hosts


### Debugging and Utility stuff
- Sometimes I have to run `sudo mn -c` to clean up mininet because there are still things running even after I exited the CLI

### Useful links, resources and more:
- [Target Paper](https://dl.acm.org/doi/pdf/10.1145/3229616.3229620)
- [OpenFlow spec for version in paper](https://opennetworking.org/wp-content/uploads/2014/10/openflow-switch-v1.3.4.pdf)
- [Good explanation of SDN and openflow](https://research.cec.sc.edu/files/cyberinfra/files/Lab%206%20-%20Introduction%20to%20OpenFlow.pdf)
- [ONOS docker setup (I have it basically summarized above too)](https://wiki.onosproject.org/display/ONOS/Single%2BInstance%2BDocker%2Bdeployment)
- [Mininet basics guide](https://mininet.org/walkthrough/)