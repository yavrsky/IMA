require('dotenv').config();
const Web3 = require('web3');
const Tx = require('ethereumjs-tx');
let mainnetData = require("../data/proxyMainnet.json");

let schainName = "proxySchain_" + process.env.SCHAIN_NAME;

let schainData = require(`../data/${schainName}`);

let mainnetRPC = process.env.MAINNET_RPC_URL;
let schainRPC = process.env.SCHAIN_RPC_URL;
let accountSchain = process.env.ACCOUNT_FOR_SCHAIN;
let privateKeyForMainnet = process.env.MNEMONIC_FOR_MAINNET;
let privateKeyForSchain = process.env.MNEMONIC_FOR_SCHAIN;

let messageProxyMainnetAddress = mainnetData.message_proxy_mainnet_address;
let messageProxyMainnetABI = mainnetData.message_proxy_mainnet_abi;

let messageProxySchainAddress = schainData.message_proxy_chain_address;
let messageProxySchainABI = schainData.message_proxy_chain_abi;

let lockAndDataForMainnetAddress = mainnetData.lock_and_data_for_mainnet_address;
let lockAndDataForMainnetABI = mainnetData.lock_and_data_for_mainnet_abi;

let lockAndDataForSchainAddress = schainData.lock_and_data_for_schain_address;
let lockAndDataForSchainABI = schainData.lock_and_data_for_schain_abi;

let web3Mainnet = new Web3(new Web3.providers.HttpProvider(mainnetRPC));
let web3Schain = new Web3(new Web3.providers.HttpProvider(schainRPC));

let privateKeyMainnetBuffer = new Buffer(privateKeyForMainnet, 'hex');
let privateKeySchainBuffer = new Buffer(privateKeyForSchain, 'hex');


let LockAndDataForMainnet = new web3Mainnet.eth.Contract(lockAndDataForMainnetABI, lockAndDataForMainnetAddress);
let MessageProxyMainnet = new web3Mainnet.eth.Contract(messageProxyMainnetABI, messageProxyMainnetAddress);
let MessageProxySchain = new web3Schain.eth.Contract(messageProxySchainABI, messageProxySchainAddress);
let LockAndDataForSchain = new web3Schain.eth.Contract(lockAndDataForSchainABI, lockAndDataForSchainAddress);

let addressCaller = process.env.NODE_ADDRESS1;
let addressCaller1 = process.env.NODE_ADDRESS2;

async function sendTransaction(web3Inst, account, privateKey, data, receiverContract) {
    let nonce = await web3Inst.eth.getTransactionCount(account);

    const rawTx = {
        from: account,
        nonce: "0x" + nonce.toString(16),
        data: data,
        to: receiverContract,
        gasPrice: 10000000000,
        gas: 6900000
    };

    const tx = new Tx(rawTx);
    tx.sign(privateKey);

    const serializedTx = tx.serialize();

    await web3Inst.eth.sendSignedTransaction('0x' + serializedTx.toString('hex')).on('receipt', receipt => {
        console.log(receipt);
    });

    console.log("Transaction done!");
    console.log("=====================================================================");
}

async function addAuthorizedCallersSchain() {
    let addAuthCallerMPS = MessageProxySchain.methods.addAuthorizedCaller(addressCaller).encodeABI();
    let addAuthCallerLDS = LockAndDataForSchain.methods.addAuthorizedCaller(addressCaller).encodeABI();
    await sendTransaction(web3Schain, accountSchain, privateKeySchainBuffer, addAuthCallerLDS, lockAndDataForSchainAddress);
    await sendTransaction(web3Schain, accountSchain, privateKeySchainBuffer, addAuthCallerMPS, messageProxySchainAddress);
    addAuthCallerMPS = MessageProxySchain.methods.addAuthorizedCaller(addressCaller1).encodeABI();
    addAuthCallerLDS = LockAndDataForSchain.methods.addAuthorizedCaller(addressCaller1).encodeABI();
    await sendTransaction(web3Schain, accountSchain, privateKeySchainBuffer, addAuthCallerLDS, lockAndDataForSchainAddress);
    await sendTransaction(web3Schain, accountSchain, privateKeySchainBuffer, addAuthCallerMPS, messageProxySchainAddress);
}

addAuthorizedCallersSchain();