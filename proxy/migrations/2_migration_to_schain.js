let fs = require("fs");
require('dotenv').config();
const fsPromises = fs.promises;

const gasMultiplierParameter = 'gas_multiplier';
const argv = require('minimist')(process.argv.slice(2), {string: [gasMultiplierParameter]});
const gasMultiplier = argv[gasMultiplierParameter] === undefined ? 1 : Number(argv[gasMultiplierParameter])

let MessageProxyForSchain = artifacts.require("./predeployed/MessageProxyForSchain.sol");
let TokenManager = artifacts.require("./predeployed/TokenManager.sol");
let LockAndDataForSchain = artifacts.require("./predeployed/LockAndDataForSchain.sol");
let EthERC20 = artifacts.require("./predeployed/EthERC20.sol");
let ERC20ModuleForSchain = artifacts.require("./predeployed/ERC20ModuleForSchain.sol");
let LockAndDataForSchainERC20 = artifacts.require("./predeployed/LockAndDataForSchainERC20.sol");
let ERC721ModuleForSchain = artifacts.require("./predeployed/ERC721ModuleForSchain.sol");
let LockAndDataForSchainERC721 = artifacts.require("./predeployed/LockAndDataForSchainERC721.sol");
let TokenFactory = artifacts.require("./predeployed/TokenFactory.sol");

let networks = require("../truffle-config.js");
let proxyMainnet = require("../data/proxyMainnet.json");
let gasLimit = 8000000;

async function deploy(deployer, network) {

    if (network == "test" || network == "coverage") {
        // skip this part of deployment if we run tests
        return;
    }
    
    if (process.env.SCHAIN_NAME == undefined || process.env.SCHAIN_NAME == "") {
        console.log(network);
        console.log(networks['networks'][network]);
        console.log("Please set SCHAIN_NAME to .env file");
        process.exit(1);
    }
    let schainName = process.env.SCHAIN_NAME;
    await deployer.deploy(LockAndDataForSchain, {gas: gasLimit}).then(async function(lockAndDataForSchain) {
        await deployer.deploy(MessageProxyForSchain, schainName, process.env.BLS_ENABLED, LockAndDataForSchain.address, {gas: gasLimit});
        await lockAndDataForSchain.setContract("MessageProxy", MessageProxyForSchain.address);
        await deployer.deploy(TokenManager, schainName, LockAndDataForSchain.address, {gas: gasLimit * gasMultiplier});
        await deployer.deploy(EthERC20, {gas: gasLimit * gasMultiplier}).then(async function(EthERC20Inst) {
            await EthERC20Inst.transferOwnership(LockAndDataForSchain.address, {gas: gasLimit});
        });
        await lockAndDataForSchain.setContract("TokenManager", TokenManager.address);
        await lockAndDataForSchain.setEthERC20Address(EthERC20.address);
        await deployer.deploy(ERC20ModuleForSchain, LockAndDataForSchain.address, {gas: gasLimit * gasMultiplier});
        await lockAndDataForSchain.setContract("ERC20Module", ERC20ModuleForSchain.address);
        await deployer.deploy(LockAndDataForSchainERC20, LockAndDataForSchain.address, {gas: gasLimit * gasMultiplier});
        await lockAndDataForSchain.setContract("LockAndDataERC20", LockAndDataForSchainERC20.address);
        await deployer.deploy(ERC721ModuleForSchain, LockAndDataForSchain.address, {gas: gasLimit * gasMultiplier});
        await lockAndDataForSchain.setContract("ERC721Module", ERC721ModuleForSchain.address);
        await deployer.deploy(LockAndDataForSchainERC721, LockAndDataForSchain.address, {gas: gasLimit * gasMultiplier});
        await lockAndDataForSchain.setContract("LockAndDataERC721", LockAndDataForSchainERC721.address);
        await deployer.deploy(TokenFactory, LockAndDataForSchain.address, {gas: gasLimit * gasMultiplier});
        await lockAndDataForSchain.setContract("TokenFactory", TokenFactory.address);

        let jsonObject = {
            lock_and_data_for_schain_address: LockAndDataForSchain.address,
            lock_and_data_for_schain_abi: LockAndDataForSchain.abi,
            eth_erc20_address: EthERC20.address,
            eth_erc20_abi: EthERC20.abi,
            token_manager_address: TokenManager.address,
            token_manager_abi: TokenManager.abi,
            lock_and_data_for_schain_erc20_address: LockAndDataForSchainERC20.address,
            lock_and_data_for_schain_erc20_abi: LockAndDataForSchainERC20.abi,
            erc20_module_for_schain_address: ERC20ModuleForSchain.address,
            erc20_module_for_schain_abi: ERC20ModuleForSchain.abi,
            lock_and_data_for_schain_erc721_address: LockAndDataForSchainERC721.address,
            lock_and_data_for_schain_erc721_abi: LockAndDataForSchainERC721.abi,
            erc721_module_for_schain_address: ERC721ModuleForSchain.address,
            erc721_module_for_schain_abi: ERC721ModuleForSchain.abi,
            token_factory_address: TokenFactory.address,
            token_factory_abi: TokenFactory.abi,
            // erc721_on_chain_address: ERC721OnChain.address,
            // erc721_on_chain_abi: ERC721OnChain.abi,
            message_proxy_chain_address: MessageProxyForSchain.address,
            message_proxy_chain_abi: MessageProxyForSchain.abi
        }

        let jsonObject2 = {
            lock_and_data_for_schain_address: LockAndDataForSchain.address,
            lock_and_data_for_schain_bytecode: LockAndDataForSchain.bytecode,
            eth_erc20_address: EthERC20.address,
            eth_erc20_bytecode: EthERC20.bytecode,
            token_manager_address: TokenManager.address,
            token_manager_bytecode: TokenManager.bytecode,
            lock_and_data_for_schain_erc20_address: LockAndDataForSchainERC20.address,
            lock_and_data_for_schain_erc20_bytecode: LockAndDataForSchainERC20.bytecode,
            erc20_module_for_schain_address: ERC20ModuleForSchain.address,
            erc20_module_for_schain_bytecode: ERC20ModuleForSchain.bytecode,
            lock_and_data_for_schain_erc721_address: LockAndDataForSchainERC721.address,
            lock_and_data_for_schain_erc721_bytecode: LockAndDataForSchainERC721.bytecode,
            erc721_module_for_schain_address: ERC721ModuleForSchain.address,
            erc721_module_for_schain_bytecode: ERC721ModuleForSchain.bytecode,
            token_factory_address: TokenFactory.address,
            token_factory_bytecode: TokenFactory.bytecode,
            // erc721_on_chain_address: ERC721OnChain.address,
            // erc721_on_chain_bytecode: ERC721OnChain.bytecode,
            message_proxy_chain_address: MessageProxyForSchain.address,
            message_proxy_chain_bytecode: MessageProxyForSchain.bytecode
        }

        await fsPromises.writeFile(`data/proxySchain_${schainName}.json`, JSON.stringify(jsonObject));
        await fsPromises.writeFile(`data/proxySchain_${schainName}_bytecode.json`, JSON.stringify(jsonObject2));
        await sleep(10000);
        console.log(`Done, check proxySchain_${schainName}.json file in data folder.`);
    });
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

module.exports = deploy;