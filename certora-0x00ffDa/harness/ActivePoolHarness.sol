// SPDX-License-Identifier: MIT

pragma solidity 0.8.17;

import "../../packages/contracts/contracts/ActivePool.sol";

contract ActivePoolHarness is ActivePool { 
    
    constructor(
        address _borrowerOperationsAddress,
        address _cdpManagerAddress,
        address _collTokenAddress,
        address _collSurplusAddress,
        address _feeRecipientAddress
    ) ActivePool(_borrowerOperationsAddress, _cdpManagerAddress, _collTokenAddress, _collSurplusAddress, _feeRecipientAddress) {

    }

    
    function call_isAuthorized(address user, uint32 functionSig) external view returns (bool) {
        return isAuthorized(user, bytes4(functionSig));
    }
}
