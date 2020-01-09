class Config:
    src_root = '.'
    agent_root = 'agent'
    skale_ima_root = 'npms/skale-ima'
    proxy_root = 'proxy'
    test_root = 'test'
    test_working_dir = 'working'
    test_sign_messages_dir = 'sign_messages'
    test_resource_dir = 'resources'
    network_for_mainnet = 'mainnet'
    network_for_schain = 'schain'
    mainnet_key=''
    mainnet_rpc_url='http://localhost:8545'
    schain_key = ''
    schain_rpc_url = 'http://localhost:8545'
    schain_name = 'd2'
    abi_mainnet = 'data/proxyMainnet.json'
    abi_schain = 'data/proxySchain_'
    mainnet_acc = ''
    schain_acc = ''
    user_key = ''

    def __init__(self, src_root, config_json):
        self.src_root = src_root
        self.proxy_root = src_root + '/' + self.proxy_root
        self.agent_root = src_root + '/' + self.agent_root
        self.skale_ima_root = src_root + '/' + self.skale_ima_root
        self.test_root = src_root + '/' + self.test_root
        self.test_working_dir = self.test_root + '/' + self.test_working_dir
        self.test_resource_dir = self.test_root + '/' + self.test_resource_dir
        self.test_sign_messages_dir = self.test_root + '/' + self.test_sign_messages_dir

        # mainnet
        if 'NETWORK_FOR_MAINNET' in config_json:
            self.network_for_mainnet = config_json['NETWORK_FOR_MAINNET']
        self.mainnet_key = config_json['ETH_PRIVATE_KEY_FOR_MAINNET']
        if 'MAINNET_RPC_URL' in config_json:
            self.mainnet_rpc_url = config_json['MAINNET_RPC_URL']
        if 'ACCOUNT_FOR_MAINNET' in config_json:
            self.mainnet_acc = config_json['ACCOUNT_FOR_MAINNET']
        # schain
        if 'NETWORK_FOR_SCHAIN' in config_json:
            self.network_for_schain = config_json['NETWORK_FOR_SCHAIN']
        self.schain_key = config_json['ETH_PRIVATE_KEY_FOR_SCHAIN']
        if 'SCHAIN_RPC_URL' in config_json:
            self.schain_rpc_url = config_json['SCHAIN_RPC_URL']
        if 'SCHAIN_NAME' in config_json:
            self.schain_name = config_json['SCHAIN_NAME']
        if 'ACCOUNT_FOR_SCHAIN' in config_json:
            self.schain_acc = config_json['ACCOUNT_FOR_SCHAIN']
        self.abi_mainnet = self.proxy_root + '/' + self.abi_mainnet
        self.abi_schain = self.proxy_root + '/' + self.abi_schain + self.schain_name + '.json'
