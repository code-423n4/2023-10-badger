// SPDX-License-Identifier: MIT

pragma solidity 0.8.17;

import "../../packages/contracts/contracts/EBTCToken.sol";
import "../../packages/contracts/contracts/Dependencies/SafeERC20.sol";

contract EBTCTokenHarness is EBTCToken { 
     using SafeERC20 for IERC20;
    
    // constructor(
    constructor(
        address _cdpManagerAddress,
        address _borrowerOperationsAddress,
        address _authorityAddress
    )   EBTCToken(_cdpManagerAddress, _borrowerOperationsAddress, _authorityAddress) {
    }

    uint32 constant public burnSelector = 0x9dc29fac;
    uint32 constant public burnSelector2 = 0x42966c68;
    uint32 constant public mintSelector = 0x40c10f19;

    function call_isAuthorized(address user, uint32 functionSig) external view returns (bool) {
        return 
                user == borrowerOperationsAddress ||
                user == cdpManagerAddress ||
                isAuthorized(user, bytes4(functionSig));
    }

    function call_requireValidRecipient(address recipient) external view {
        _requireValidRecipient(recipient);
    }

    function tokenBalanceOf(address token, address user) external view returns (uint256) {
        return IERC20(token).balanceOf(user);
    }
}
