// SPDX-License-Identifier: MIT

pragma solidity 0.8.17;

import "../../packages/contracts/contracts/CollSurplusPool.sol";
import "../../packages/contracts/contracts/Dependencies/SafeERC20.sol";

contract CollSurplusPoolHarness is CollSurplusPool { 
     using SafeERC20 for IERC20;
    
    constructor(
        address _borrowerOperationsAddress,
        address _cdpManagerAddress,
        address _activePoolAddress,
        address _collTokenAddress
    ) CollSurplusPool(_borrowerOperationsAddress, _cdpManagerAddress, _activePoolAddress, _collTokenAddress) {

    }

    
    function call_isAuthorized(address user, uint32 functionSig) external view returns (bool) {
        return isAuthorized(user, bytes4(functionSig));
    }

    function tokenBalanceOf(address token, address user) external view returns (uint256) {
        return IERC20(token).balanceOf(user);
    }
}
