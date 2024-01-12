// SPDX-License-Identifier: MIT

pragma solidity 0.8.17;

import "../../packages/contracts/contracts/EBTCToken.sol";

contract EBTCTokenHarness is EBTCToken { 
    // keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)");
    bytes32 private constant _PERMIT_TYPEHASH =
        0x6e71edae12b1b97f4d1f60370fef10105fa2faae0126114a169c64845d6126c9;
    // keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)");
    bytes32 private constant _TYPE_HASH =
        0x8b73c3c69bb8fe3d512ecc4cf759cc79239f7b179b0ffacaa9a75d522b39400f;

    bytes32 private immutable _CACHED_DOMAIN_SEPARATOR;
    uint256 private immutable _CACHED_CHAIN_ID;

    bytes32 private immutable _HASHED_NAME;
    bytes32 private immutable _HASHED_VERSION;

    constructor(
        address _cdpManagerAddress,
        address _borrowerOperationsAddress,
        address _authorityAddress
    ) EBTCToken(_cdpManagerAddress, _borrowerOperationsAddress, _authorityAddress) {
        bytes32 hashedName = keccak256(bytes(_NAME));
        bytes32 hashedVersion = keccak256(bytes(_VERSION));

        // Important to use getChainId() here because the spec summarize it to force a constant value.
        //  (Using block.chainid directly gave me inconsistent values during proving.)
        _HASHED_NAME = hashedName;
        _HASHED_VERSION = hashedVersion;
        _CACHED_CHAIN_ID = getChainId();
        _CACHED_DOMAIN_SEPARATOR = keccak256(abi.encode(_TYPE_HASH, hashedName, hashedVersion, getChainId(), address(this)));

        // Constrain to realistic values
        require(_cdpManagerAddress != address(0) && _borrowerOperationsAddress != address(0));
    }

    function call_isAuthorized(address user, uint32 functionSig) external view returns (bool) {
        return isAuthorized(user, bytes4(functionSig));
    }

    function internalTransfer(address sender, address recipient, uint256 amount) external {
        _transfer(sender, recipient, amount);
    }


    function internalBurn(address account, uint256 amount) external {
        _burn(account, amount);
    }

    function internalRequireCallerIsBorrowerOperations() external view {
        _requireCallerIsBorrowerOperations();
    }

    function internalRequireCallerIsCdpM() external view {
        _requireCallerIsCdpM();
    }

    function getCachedDomainSeparator() external view returns (bytes32) {
        return _CACHED_DOMAIN_SEPARATOR;
    }

    function getCachedChainId() external view returns (uint256) {
        return _CACHED_CHAIN_ID;
    }

    function getChainId() public view returns (uint256) {
        return block.chainid;
    }

    function getRecoveredAddress(
        address owner,
        address spender,
        uint256 amount,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external view returns (address) {
        // Copied from EBTCToken.permit()
        // The nonce fetch is a hack to get prev nonce (to allow validating the prev digest)
        uint256 nonce = _nonces[owner] - 1;
        bytes32 digest = keccak256(
            abi.encodePacked(
                "\x19\x01",
                domainSeparator(),
                keccak256(
                    abi.encode(_PERMIT_TYPEHASH, owner, spender, amount, nonce, deadline)
                )
            )
        );
        address recoveredAddress = ecrecover(digest, v, r, s);
        return recoveredAddress;
    }
}
