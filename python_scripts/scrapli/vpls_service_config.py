from nornir import InitNornir
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
from nornir_jinja2.plugins.tasks import template_file
from nornir_scrapli.tasks import netconf_edit_config
import yaml
import argparse

def generate_xml_payload(task, svc_dict, attr_dict, temp_name, cfg_type):
    """
    Function to generate config XML payload parts
    """
    try:
        cfg = task.run(task=template_file,
                       name='{} Configuration'.format(cfg_type),
                       template=temp_name,
                       path=f'..',
                       svc=svc_dict['svc'],
                       pe=attr_dict['pe']
                       )
    except Exception as e:
        print(e)
    task.host[cfg_type] = cfg.result

def send_xml_payload(task):
    """
    Function to send config XML payload to network equipment through Netconf
    """
    try:
        task.run(task=netconf_edit_config, name='XML payload through Netconf', config=task.host['FULL'])
    except Exception as e:
        print(e)

# Main function
def main(filename, create_cfg, delete_cfg, port_cfg, sap_cfg, svc_cfg):
    # Parse external YAML for service and equipment attributes
    svc_modelisation = open(filename)
    parsed_svc_modelisation = yaml.load(svc_modelisation, Loader=yaml.FullLoader)
    pe_attributes = open('../vars/pe_attributes.yaml')
    parsed_pe_attributes = yaml.load(pe_attributes, Loader=yaml.FullLoader)
    # Read host from service YAML
    hosts = []
    for hst in parsed_svc_modelisation['svc']['attach_circuit_wan']:
        hosts.append(hst['hostname'])
    # Building a unique list of hosts to run Netconf on
    hosts = list(set(hosts))
    # Init Nornir and build dynamic inventory
    nr = InitNornir(config_file='../config.yaml')
    devices = nr.filter(F(hostname__any=hosts))
    # Creation actions
    if create_cfg:
        # Port creation XML payload generation
        if port_cfg:
            devices.run(task=generate_xml_payload, svc_dict=parsed_svc_modelisation,
                        attr_dict=parsed_pe_attributes, temp_name='templates/port_payload_creation.j2',
                        cfg_type='PORT')
        # Service creation XML payload generation
        if svc_cfg:
            devices.run(task=generate_xml_payload, svc_dict=parsed_svc_modelisation,
                        attr_dict=parsed_pe_attributes, temp_name='templates/vpls_payload_creation.j2',
                        cfg_type='SVC')
        # SAP creation XML payload generation
        if sap_cfg:
            devices.run(task=generate_xml_payload, svc_dict=parsed_svc_modelisation,
                        attr_dict=parsed_pe_attributes, temp_name='templates/sap_payload_creation.j2',
                        cfg_type='SAP')
        # Full creation config XML payload generation
        devices.run(task=generate_xml_payload, svc_dict=parsed_svc_modelisation,
                    attr_dict=parsed_pe_attributes, temp_name='templates/full_config_creation.j2',
                    cfg_type='FULL')
    # Deletion actions
    elif delete_cfg:
        # Port deletion XML payload generation
        if port_cfg:
            devices.run(task=generate_xml_payload, svc_dict=parsed_svc_modelisation,
                        attr_dict=parsed_pe_attributes, temp_name='templates/port_payload_deletion.j2',
                        cfg_type='PORT')
        # Service deletion XML payload generation
        if svc_cfg:
            devices.run(task=generate_xml_payload, svc_dict=parsed_svc_modelisation,
                        attr_dict=parsed_pe_attributes, temp_name='templates/vpls_payload_deletion.j2',
                        cfg_type='SVC')
        # SAP deletion XML payload generation
        if sap_cfg:
            devices.run(task=generate_xml_payload, svc_dict=parsed_svc_modelisation,
                        attr_dict=parsed_pe_attributes, temp_name='templates/sap_payload_deletion.j2',
                        cfg_type='SAP')
        # Full deletion config XML payload generation
        devices.run(task=generate_xml_payload, svc_dict=parsed_svc_modelisation,
                    attr_dict=parsed_pe_attributes, temp_name='templates/full_config_deletion.j2',
                    cfg_type='FULL')
    try:
        result = devices.run(task=send_xml_payload)
        print_result(result)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    # Arguments passed to the script
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, help='Path to SVC description YAML file')
    parser.add_argument('--port', action='store_true', help='Deploy Port configuration')
    parser.add_argument('--sap', action='store_true', help='Deploy SAP configuration')
    parser.add_argument('--svc', action='store_true', help='Deploy Service configuration')
    # Making Create or Delete option mandatory
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--create', action='store_true', help='Create configuration')
    group.add_argument('--delete', action='store_true', help='Delete configuration')
    args = parser.parse_args()
    # Making at least one configuration options mandatory
    if not (args.port or args.sap or args.svc):
        parser.error('No item selected, add any of the following: --port, --svc, --sap')
    # Main program
    main(args.file, args.create, args.delete, args.port, args.sap, args.svc)