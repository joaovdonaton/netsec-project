# netsec-project

### Setup Information (as of now)
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

### Useful links, resources and more:
- ADD STUFF FROM FOLDER HERE