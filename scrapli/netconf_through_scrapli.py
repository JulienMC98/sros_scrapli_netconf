from nornir import InitNornir
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
from nornir_jinja2.plugins.tasks import template_file
from nornir_scrapli.tasks import netconf_edit_config
import yaml
import argparse

# Function to generate Service XML payload
def svc_cfg_xml_generation(task, svc_dict, attr_dict):
    try:
        cfg = task.run(task=template_file,
                       name='Service Configuration',
                       template='templates/vpls_template.j2',
                       path=f'..',
                       svc=svc_dict['svc'],
                       pe=attr_dict['pe']
                       )
    except Exception as e:
        print(e)
    task.host['svc_cfg'] = cfg.result

# Function to generate Port XML payload
def port_cfg_xml_generation(task, svc_dict, attr_dict):
    try:
        cfg = task.run(task=template_file,
                       name='Port Configuration',
                       template='templates/port_template.j2',
                       path=f'..',
                       svc=svc_dict['svc'],
                       pe=attr_dict['pe']
                       )
    except Exception as e:
        print(e)
    task.host['port_cfg'] = cfg.result

# Function to generate SAP XML payload
def sap_cfg_xml_generation(task, svc_dict, attr_dict):
    try:
        cfg = task.run(task=template_file,
                       name='SAP Configuration',
                       template='templates/sap_template.j2',
                       path=f'..',
                       svc=svc_dict['svc'],
                       pe=attr_dict['pe']
                       )
    except Exception as e:
        print(e)
    task.host['sap_cfg'] = cfg.result

# Function to generate SAP XML payload
def full_cfg_xml_generation(task, svc_dict):
    try:
        cfg = task.run(task=template_file,
                       name='Full XML payload generation',
                       template='templates/full_config_template.j2',
                       path=f'..',
                       svc=svc_dict['svc']
                       )
    except Exception as e:
        print(e)
    task.host['full_cfg'] = cfg.result
    print(task.host['full_cfg'])

# Function to send XML Payload through Netconf
def send_xml_payload(task):
    try:
        task.run(task=netconf_edit_config, name='XML payload through Netconf', config=task.host['full_cfg'])
    except Exception as e:
        print(e)

# Main function
def main(port_cfg, sap_cfg, svc_cfg):
    # Parse external YAML for service and equipment attributes
    svc_modelisation = open('../vars/wan_l2vpn.yaml')
    parsed_svc_modelisation = yaml.load(svc_modelisation, Loader=yaml.FullLoader)
    pe_attributes = open('../vars/pe_attributes.yaml')
    parsed_pe_attributes = yaml.load(pe_attributes, Loader=yaml.FullLoader)
    # Read host from service YAML
    hosts = []
    for hst in parsed_svc_modelisation['svc']['attach_circuit_wan']:
        hosts.append(hst['hostname'])
    hosts = list(set(hosts))
    # Init Nornir and build dynamic inventory
    nr = InitNornir(config_file='../config.yaml')
    devices = nr.filter(F(hostname__any=hosts))
    if port_cfg:
        devices.run(task=port_cfg_xml_generation, svc_dict=parsed_svc_modelisation,
                             attr_dict=parsed_pe_attributes)
    if svc_cfg:
        devices.run(task=svc_cfg_xml_generation, svc_dict=parsed_svc_modelisation,
                             attr_dict=parsed_pe_attributes)
    if sap_cfg:
        devices.run(task=sap_cfg_xml_generation, svc_dict=parsed_svc_modelisation,
                             attr_dict=parsed_pe_attributes)
    devices.run(task=full_cfg_xml_generation, svc_dict=parsed_svc_modelisation)
    result = devices.run(task=send_xml_payload)
    print_result(result)

if __name__ == '__main__':
    # Arguments passed to the script
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', action='store_true', help='Deploy Port configuration')
    parser.add_argument('--sap', action='store_true', help='Deploy SAP configuration')
    parser.add_argument('--svc', action='store_true', help='Deploy Service configuration')
    args = parser.parse_args()
    if not (args.port or args.sap or args.svc):
        parser.error('No action requested, add any of the following: --port, --svc, --sap')
    # Main program
    main(args.port, args.sap, args.svc)