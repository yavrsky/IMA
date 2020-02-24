/**
 *   TokenFactory.sol - SKALE Interchain Messaging Agent
 *   Copyright (C) 2019-Present SKALE Labs
 *   @author Artem Payvin
 *
 *   SKALE-IMA is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU Affero General Public License as published
 *   by the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   SKALE-IMA is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU Affero General Public License for more details.
 *
 *   You should have received a copy of the GNU Affero General Public License
 *   along with SKALE-IMA.  If not, see <https://www.gnu.org/licenses/>.
 */

pragma solidity ^0.6.0;

import "./PermissionsForSchain.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20Capped.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20Detailed.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721Full.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721Metadata.sol";
import "@openzeppelin/contracts/access/Roles.sol";
import "@openzeppelin/contracts/GSN/Context.sol";


contract MinterRole is Context {
    using Roles for Roles.Role;

    event MinterAdded(address indexed account);
    event MinterRemoved(address indexed account);

    Roles.Role private _minters;

    constructor() public {
        if (!isMinter(_msgSender())) {
            _addMinter(_msgSender());
        }
    }

    modifier onlyMinter() {
        require(isMinter(_msgSender()), "MinterRole: caller does not have the Minter role");
        _;
    }

    function isMinter(address account) public view returns (bool) {
        return _minters.has(account);
    }

    function addMinter(address account) public onlyMinter {
        _addMinter(account);
    }

    function renounceMinter() public {
        _removeMinter(_msgSender());
    }

    function _addMinter(address account) internal {
        _minters.add(account);
        emit MinterAdded(account);
    }

    function _removeMinter(address account) internal {
        _minters.remove(account);
        emit MinterRemoved(account);
    }
}


contract ERC20OnChain is ERC20Detailed, ERC20, MinterRole {

    uint private _totalSupplyOnMainnet;

    address private addressOfErc20Module;

    constructor(
        string memory contractName,
        string memory contractSymbol,
        uint8 contractDecimals,
        uint256 newTotalSupply,
        address erc20Module
        )
        ERC20Detailed(contractName, contractSymbol, contractDecimals)
        public
    {
        _totalSupplyOnMainnet = newTotalSupply;
        addressOfErc20Module = erc20Module;
    }

    function totalSupplyOnMainnet() external view returns (uint) {
        return _totalSupplyOnMainnet;
    }

    function setTotalSupplyOnMainnet(uint newTotalSupply) external {
        require(addressOfErc20Module == msg.sender, "Call does not go from ERC20Module");
        _totalSupplyOnMainnet = newTotalSupply;
    }

    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
    }

    function burnFrom(address account, uint256 amount) external {
        _burnFrom(account, amount);
    }

    function mint(address account, uint value) external onlyMinter returns (bool) {
        require(totalSupply().add(value) <= _totalSupplyOnMainnet, "Total supply on mainnet exceeded");
        _mint(account, value);
        return true;
    }
}


contract ERC721OnChain is ERC721Full, MinterRole {
    constructor(
        string memory contractName,
        string memory contractSymbol
        )
        ERC721Full(contractName, contractSymbol)
        public
    {
        // solium-disable-previous-line no-empty-blocks
    }

    function mint(address to, uint256 tokenId)
        external
        onlyMinter
        returns (bool)
    {
        _mint(to, tokenId);
        return true;
    }

    function burn(uint256 tokenId) external {
        require(_isApprovedOrOwner(msg.sender, tokenId), "ERC721Burnable: caller is not owner nor approved");
        _burn(tokenId);
    }

    function setTokenURI(uint256 tokenId, string calldata tokenUri)
        external
        returns (bool)
    {
        require(_exists(tokenId), "Token does not exists");
        require(_isApprovedOrOwner(msg.sender, tokenId), "The sender can not set token URI");
        _setTokenURI(tokenId, tokenUri);
        return true;
    }
}


contract TokenFactory is PermissionsForSchain {


    constructor(address _lockAndDataAddress) PermissionsForSchain(_lockAndDataAddress) public {
        // solium-disable-previous-line no-empty-blocks
    }

    function createERC20(bytes calldata data)
        external
        allow("ERC20Module")
        returns (address)
    {
        string memory name;
        string memory symbol;
        uint8 decimals;
        uint256 totalSupply;
        (name, symbol, decimals, totalSupply) = fallbackDataCreateERC20Parser(data);
        address erc20ModuleAddress = IContractManagerForSchain(getLockAndDataAddress()).getContract("ERC20Module");
        ERC20OnChain newERC20 = new ERC20OnChain(
            name,
            symbol,
            decimals,
            totalSupply,
            erc20ModuleAddress
        );
        address lockAndDataERC20 = IContractManagerForSchain(getLockAndDataAddress()).getContract("LockAndDataERC20");
        newERC20.addMinter(lockAndDataERC20);
        newERC20.renounceMinter();
        return address(newERC20);
    }

    function createERC721(bytes calldata data)
        external
        allow("ERC721Module")
        returns (address)
    {
        string memory name;
        string memory symbol;
        (name, symbol) = fallbackDataCreateERC721Parser(data);
        ERC721OnChain newERC721 = new ERC721OnChain(name, symbol);
        address lockAndDataERC721 = IContractManagerForSchain(getLockAndDataAddress()).
            getContract("LockAndDataERC721");
        newERC721.addMinter(lockAndDataERC721);
        newERC721.renounceMinter();
        return address(newERC721);
    }

    function fallbackDataCreateERC20Parser(bytes memory data)
        internal
        pure
        returns (
            string memory name,
            string memory symbol,
            uint8,
            uint256
        )
    {
        bytes1 decimals;
        bytes32 totalSupply;
        bytes32 nameLength;
        bytes32 symbolLength;
        // solium-disable-next-line security/no-inline-assembly
        assembly {
            nameLength := mload(add(data, 129))
        }
        name = new string(uint(nameLength));
        for (uint i = 0; i < uint(nameLength); i++) {
            bytes(name)[i] = data[129 + i];
        }
        uint lengthOfName = uint(nameLength);
        // solium-disable-next-line security/no-inline-assembly
        assembly {
            symbolLength := mload(add(data, add(161, lengthOfName)))
        }
        symbol = new string(uint(symbolLength));
        for (uint i = 0; i < uint(symbolLength); i++) {
            bytes(symbol)[i] = data[161 + lengthOfName + i];
        }
        uint lengthOfSymbol = uint(symbolLength);
        // solium-disable-next-line security/no-inline-assembly
        assembly {
            decimals := mload(add(data,
                add(193, add(lengthOfName, lengthOfSymbol))))
            totalSupply := mload(add(data,
                add(194, add(lengthOfName, lengthOfSymbol))))
        }
        return (
            name,
            symbol,
            uint8(decimals),
            uint256(totalSupply)
            );
    }

    function fallbackDataCreateERC721Parser(bytes memory data)
        internal
        pure
        returns (
            string memory name,
            string memory symbol
        )
    {
        bytes32 nameLength;
        bytes32 symbolLength;
        // solium-disable-next-line security/no-inline-assembly
        assembly {
            nameLength := mload(add(data, 129))
        }
        name = new string(uint(nameLength));
        for (uint i = 0; i < uint(nameLength); i++) {
            bytes(name)[i] = data[129 + i];
        }
        uint lengthOfName = uint(nameLength);
        // solium-disable-next-line security/no-inline-assembly
        assembly {
            symbolLength := mload(add(data, add(161, lengthOfName)))
        }
        symbol = new string(uint(symbolLength));
        for (uint i = 0; i < uint(symbolLength); i++) {
            bytes(symbol)[i] = data[161 + lengthOfName + i];
        }
    }
}





