from logging import error

from os import system
import time

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
