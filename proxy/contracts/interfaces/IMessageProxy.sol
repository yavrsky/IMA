pragma solidity ^0.6.0;

interface IMessageProxy {
    function postOutgoingMessage(
        string calldata dstChainID,
        address dstContract,
        uint amount,
        address to,
        bytes calldata data
    )
        external;
}