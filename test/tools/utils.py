#for ssh
from __future__ import print_function
from pssh.clients import ParallelSSHClient
#
from logging import error
import os
from os import system
import time
import subprocess
import json



dir_path = os.path.dirname(os.path.realpath(__file__))
proj_dir = os.path.join(dir_path, '../../')


def execute(command: str, print_command=False):
    if print_command:
        print('Execute:', command)
    exit_code = system(command)
    if exit_code:
        error(f'Command "{command}" failed with exit code {exit_code}')
        exit(1)


def await_receipt(web3, tx, retries=10, timeout=5):
    for _ in range(0, retries):
        receipt = get_receipt(web3, tx)
        if (receipt != None):
            return receipt
        time.sleep(timeout)
    return None


def get_receipt(web3, tx):
    return web3.eth.getTransactionReceipt(tx)


def set_ima_to_schain_nodes(schain_name, mainnet_url):
    ips = get_nodes_ips_from_file(schain_name)
    ima_mainnet_addr, ima_chain_addr = get_ima_addrs_for_mainnet_and_schain()
    index = 0
    # overwrite config_schain.json loop on nodes
    for ip in ips:
        # copy schain_{schain_name}.json to config folder
        cmd_config_copy_from_node = \
            f'scp -r root@{ip}:.skale/node_data/schains/{schain_name}/schain_{schain_name}.json ' \
            + f'{dir_path}/tmp_files/schain_{schain_name}_{index}.json'
        print(subprocess.run(cmd_config_copy_from_node, shell=True))
        # set path to schain_config.json on local machine (dir_path - path to `tools` dir)
        path_to_schain = f'{dir_path}/tmp_files/schain_{schain_name}_{index}.json'
        # create dictionary from .json file
        with open(f'{path_to_schain}', 'r') as f:
            data_schain = json.load(f)
        # add data to wallets field
        # data_schain['skaleConfig']['nodeInfo']['imaMainNet'] = mainnet_url
        data_schain['skaleConfig']['nodeInfo']['imaMessageProxySChain'] = ima_chain_addr
        # data_schain['skaleConfig']['nodeInfo']['imaMessageProxyMainNet'] = ima_mainnet_addr
        # write dictionary to .json file
        with open(path_to_schain, 'w') as json_file:
            json.dump(data_schain, json_file, indent=4)
        # rewrite file back to node
        cmd_copy_to_node = f'scp -r {dir_path}/tmp_files/schain_{schain_name}_{index}.json ' \
                           + f'root@{ip}:.skale/node_data/schains/{schain_name}/schain_{schain_name}.json'
        print(subprocess.run(cmd_copy_to_node, shell=True))
        index += 1
        print(index)


def get_nodes_ips_from_file(schain_name):
    skale_tests_py = os.path.join(proj_dir, f'../skale_tests_py/config/nodes/array_of_ips_{schain_name}.json')
    print(skale_tests_py)
    # create dictionary from .json file
    with open(f'{skale_tests_py}', 'r') as f:
        data = json.load(f)
    print('IPS: ', data['ips'])
    return data['ips']


def get_ima_addrs_for_mainnet_and_schain():
    #
    ima_mainnet = os.path.join(proj_dir, 'proxy/data/proxyMainnet.json')
    ima_schain = os.path.join(proj_dir, 'proxy/data/proxySchain.json')
    # create dictionary from .json file
    with open(f'{ima_mainnet}', 'r') as f:
        ima_mainnet_dict = json.load(f)
    # create dictionary from .json file
    with open(f'{ima_schain}', 'r') as f:
        ima_schain_dict = json.load(f)

    ima_mainnet_addr = ima_mainnet_dict['message_proxy_mainnet_address']
    ima_chain_addr = ima_schain_dict['message_proxy_chain_address']
    #
    return ima_mainnet_addr, ima_chain_addr


def restart_skaled(schain_name):
    print('inside in `restart_skaled`')
    ips = get_nodes_ips_from_file(schain_name)
    client = ParallelSSHClient(ips, user='root', port=22)
    output = client.run_command(f'docker rm -f skale_schain_{schain_name}')
    for host, host_output in output.items():
        for line in host_output.stdout:
            print(line)
    print('waiting %s ' % '120 seconds')
    time.sleep(120)
    print('waiting %s ' % 'is over')
