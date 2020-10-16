# How to

## Prerequisites
To run Scrapli script, you need to load the devel branch of scrapli_netconf:
- sudo pip3 install -e git+https://github.com/scrapli/scrapli_netconf.git@develop#egg=scrapli_netconf
- nornir                        3.0.0
- nornir-jinja2                 0.1.0
- nornir-scrapli                2020.9.23
- nornir-utils                  0.1.0

## How does it work

### Parameters

- --file is the name of the YAML file for service description (mandatory)
- --create or --delete, operation you want to execute (mandatory)
- --sap, if you want to create/delete SAPs config
- --svc, if you want to create/delete VPLS service
- --port, if you want to create/delete Ports config<br/><br/>
One of the 3 values is at least mandatory (sap or svc or port)<br/><br/>
usage: vpls_service_config.py [-h] --file FILE [--port] [--sap] [--svc] (--create | --delete)

### Example

python3 vpls_service_config.py --file "../vars/wan_l2vpn.yaml" --create --svc --sap --port<br/>
python3 vpls_service_config.py --file "../vars/wan_l2vpn.yaml" --delete --svc --sap --port<br/>