// SPDX-License-Identifier: MIT

pragma solidity 0.8.17;

import "../../packages/contracts/contracts/EBTCToken.sol";

contract EBTCTokenHarness is EBTCToken { 
    
    constructor(
        address _cdpManagerAddress,
        address _borrowerOperationsAddress,
        address _authorityAddress
    ) EBTCToken(_cdpManagerAddress, _borrowerOperationsAddress, _authorityAddress) {
        //empty
    }

    
    function call_isAuthorized(address user, uint32 functionSig) external view returns (bool) {
        return isAuthorized(user, bytes4(functionSig));
    }
}
