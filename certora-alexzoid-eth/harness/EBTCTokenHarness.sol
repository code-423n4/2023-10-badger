// SPDX-License-Identifier: MIT

pragma solidity 0.8.17;

import "../../packages/contracts/contracts/EBTCToken.sol";

contract EBTCTokenHarness is EBTCToken { 
    
    constructor(
        address _cdpManagerAddress,
        address _borrowerOperationsAddress,
        address _authorityAddress
    ) EBTCToken(
        _cdpManagerAddress, _borrowerOperationsAddress, _authorityAddress
    ) { }
}
