pragma solidity ^0.5.0;

import "./Permissions.sol";
import "openzeppelin-solidity/contracts/token/ERC721/IERC721Full.sol";

contract LockAndDataForMainnetERC721 is Permissions {

    event ERC721ApprovedAddressAdded(address approvedTokenAddress);

    mapping(uint => address) public ERC721Tokens;
    mapping(address => uint) public ERC721Mapper;
    // mapping(uint => uint) public mintToken;
    mapping(address => bool) public ERC721ApprovedTokens;
    uint newIndexERC721 = 1;

    constructor(address lockAndDataAddress) Permissions(lockAndDataAddress) public {
        
    }

    function sendERC721(address contractHere, address to, uint tokenId) public allow("ERC721Module") returns (bool) {
        if (IERC721Full(contractHere).ownerOf(tokenId) == address(this)) {
            IERC721Full(contractHere).transferFrom(address(this), to, tokenId);
            require(IERC721Full(contractHere).ownerOf(tokenId) == to, "Did not transfer");
        } // else {
        //     //mint!!!
        // }
        return true;
    }

    function addERC721Token(address addressERC721) public allow("ERC721Module") returns (uint) {
        uint index = newIndexERC721;
        ERC721Tokens[index] = addressERC721;
        ERC721Mapper[addressERC721] = index;
        newIndexERC721++;
        return index;
    }

    function addERC721ApprovedToken(address approvedTokenAddress) public onlyOwner {
        ERC721ApprovedTokens[approvedTokenAddress] = true;
        emit ERC721ApprovedAddressAdded(approvedTokenAddress);
    }
}