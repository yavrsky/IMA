// SPDX-License-Identifier: AGPL-3.0-only

/**
 *   LockAndDataForSchainERC721.sol - SKALE Interchain Messaging Agent
 *   Copyright (C) 2019-Present SKALE Labs
 *   @author Artem Payvin
 *
 *   SKALE IMA is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU Affero General Public License as published
 *   by the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   SKALE IMA is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU Affero General Public License for more details.
 *
 *   You should have received a copy of the GNU Affero General Public License
 *   along with SKALE IMA.  If not, see <https://www.gnu.org/licenses/>.
 */

pragma solidity ^0.6.10;

import "./PermissionsForSchain.sol";

interface ERC721MintAndBurn {
    function mint(address to, uint256 tokenId) external returns (bool);
    function burn(uint256 tokenId) external;
    function ownerOf(uint256 tokenId) external view returns (address);
}


contract LockAndDataForSchainERC721 is PermissionsForSchain {

    mapping(uint256 => address) public erc721Tokens;
    mapping(address => uint256) public erc721Mapper;
    // mapping(uint256 => uint256) public mintToken;


    event SendERC721(bool result);
    event ReceiveERC721(bool result);

    constructor(address _lockAndDataAddress) public PermissionsForSchain(_lockAndDataAddress) {
        // solhint-disable-previous-line no-empty-blocks
    }

    function sendERC721(address contractHere, address to, uint256 tokenId)
        external
        allow("ERC721Module")
        returns (bool)
    {
        require(ERC721MintAndBurn(contractHere).mint(to, tokenId), "Could not mint ERC721 Token");
        emit SendERC721(true);
        return true;
    }

    function receiveERC721(address contractHere, uint256 tokenId) external allow("ERC721Module") returns (bool) {
        require(ERC721MintAndBurn(contractHere).ownerOf(tokenId) == address(this), "Token not transfered");
        ERC721MintAndBurn(contractHere).burn(tokenId);
        emit ReceiveERC721(true);
        return true;
    }

    function addERC721Token(address addressERC721, uint256 contractPosition) external allow("ERC721Module") {
        erc721Tokens[contractPosition] = addressERC721;
        erc721Mapper[addressERC721] = contractPosition;
    }
}
