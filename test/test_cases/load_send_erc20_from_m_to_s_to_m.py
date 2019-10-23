from time import sleep, time
from logging import debug, error

from tools.test_case import TestCase
from tools.test_pool import test_pool


class LoadSendERC20ToMainnetViaSchain(TestCase):
    erc20 = None
    erc20_clone = None
    amount = 4
    # index of token in lock_and_data_for_schain_erc20.sol
    index = 1


    def __init__(self, config):
        super().__init__('Load Send ERC20 to mainnet via schain', config)

    def _execute(self):
        #
        range_int = 5
        # deploy token

        self.erc20 = self.blockchain.deploy_erc20_on_mainnet(self.config.mainnet_key, 'D2-Token', 'D2', 18)

        # mint
        address = self.blockchain.key_to_address(self.config.mainnet_key)
        mint_txn = self.erc20.functions.mint(address, self.amount)\
            .buildTransaction({
                'gas': 8000000,
                'nonce': self.blockchain.get_transactions_count_on_mainnet(address)})

        signed_txn = self.blockchain.web3_mainnet.eth.account.signTransaction(mint_txn,
                                                                              private_key=self.config.mainnet_key)
        self.blockchain.web3_mainnet.eth.sendRawTransaction(signed_txn.rawTransaction)

        # send to schain
        amount_of_eth = 9 * 10 ** 17

        self.agent.transfer_eth_from_mainnet_to_schain(self.config.mainnet_key,
                                                       self.config.schain_key,
                                                       amount_of_eth,
                                                       self.timeout)

        self.blockchain.add_eth_cost(self.config.schain_key,
                                     amount_of_eth)

        #
        # source_address = self.blockchain.key_to_address(self.config.schain_key)
        destination_address = ''
        i = 0
        # for x in range(range_int):
        while i < range_int:
            i += 1
            self.agent.transfer_erc20_from_mainnet_to_schain(self.erc20,
                                                             self.config.mainnet_key,
                                                             self.config.schain_key,
                                                             self.amount,
                                                             self.index,
                                                             self.timeout)
            sleep(7)
            self.erc20_clone = self.blockchain.get_erc20_on_schain(self.index)
            sleep(3)
            source_address = self.blockchain.key_to_address(self.config.schain_key)
            destination_address = self.blockchain.key_to_address(self.config.mainnet_key)
            if self.erc20_clone.functions.balanceOf(source_address).call() < self.amount:
                error("Not enough tokens to send")
                return

            self.agent.transfer_erc20_from_schain_to_mainnet(self.erc20_clone,  # token
                                                             self.config.schain_key,  # from
                                                             self.config.mainnet_key,  # to
                                                             self.amount,  # 4 tokens
                                                             self.index,
                                                             self.timeout)

        # expectation
        if self.erc20.functions.balanceOf(destination_address).call() == (self.amount):
            self._mark_passed()

test_pool.register_test(LoadSendERC20ToMainnetViaSchain)
