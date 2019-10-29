from time import sleep, time
from logging import debug, error

from tools.test_case import TestCase
from tools.test_pool import test_pool
from tools.utils import await_receipt


class LoadSendERC721ToMainnetViaSchain(TestCase):
    erc721 = None
    erc721_clone = None
    token_id = 1

    def __init__(self, config):
        super().__init__('Load Send ERC721 to mainnet via schain', config)

    def _execute(self):
        #
        range_int = 5
        # deploy token
        self.erc721 = self.blockchain.deploy_erc721_on_mainnet(self.config.mainnet_key, 'elv721', 'ELV')
        # mint
        address = self.blockchain.key_to_address(self.config.mainnet_key)
        mint_txn = self.erc721.functions.mint(address, self.token_id)\
            .buildTransaction({
                'gas': 8000000,
                'nonce': self.blockchain.get_transactions_count_on_mainnet(address)})

        signed_txn = self.blockchain.web3_mainnet.eth.account.signTransaction(mint_txn,
                                                                              private_key=self.config.mainnet_key)
        transaction_hash = self.blockchain.web3_mainnet.eth.sendRawTransaction(signed_txn.rawTransaction)
        await_receipt(self.blockchain.web3_mainnet, transaction_hash)

        # send to schain
        amount_of_eth = 9 * 10 ** 17
        self.agent.transfer_eth_from_mainnet_to_schain(self.config.mainnet_key,
                                                       self.config.schain_key,
                                                       amount_of_eth,
                                                       self.timeout)
        self.blockchain.add_eth_cost(self.config.schain_key,
                                     amount_of_eth)

        destination_address = ''
        i = 0
        # for x in range(range_int):
        while i < range_int:
            i += 1
            # send to schain
            self.agent.transfer_erc721_from_mainnet_to_schain(self.erc721,
                                                              self.config.mainnet_key,
                                                              self.config.schain_key,
                                                              self.token_id,
                                                              self.timeout)
            # sleep(7)
            self.erc721_clone = self.blockchain.get_erc721_on_schain(self.token_id)
            sleep(1)
            source_address = self.blockchain.key_to_address(self.config.schain_key)
            destination_address = self.blockchain.key_to_address(self.config.mainnet_key)
            sleep(1)
            if self.erc721_clone.functions.ownerOf(self.token_id).call() != source_address:
                error("Token was not send")
                return
            # send to mainnet
            self.agent.transfer_erc721_from_schain_to_mainnet(self.erc721_clone,
                                                              self.config.schain_key,
                                                              self.config.mainnet_key,
                                                              self.token_id,
                                                              self.timeout)

        # expectation
        new_owner_address = self.erc721.functions.ownerOf(self.token_id).call()
        if destination_address == new_owner_address:
            self._mark_passed()

test_pool.register_test(LoadSendERC721ToMainnetViaSchain)
