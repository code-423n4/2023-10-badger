// SPDX-License-Identifier: MIT

pragma solidity 0.8.17;

import "../../packages/contracts/contracts/CollSurplusPool.sol";

contract CollSurplusPoolHarness is CollSurplusPool {
    constructor(
        address _borrowerOperationsAddress,
        address _cdpManagerAddress,
        address _activePoolAddress,
        address _collTokenAddress
    )
        CollSurplusPool(
            _borrowerOperationsAddress,
            _cdpManagerAddress,
            _activePoolAddress,
            _collTokenAddress
        )
    {}

    function call_isAuthorized(address user, bytes4 functionSig) external view returns (bool) {
        return isAuthorized(user, functionSig);
    }

    function getTotalSurplusCollSharesHarness() external view returns (uint256) {
        return totalSurplusCollShares;
    }

    function getSurplusCollSharesHarness(address _account) external view returns (uint256) {
        return balances[_account];
    }
}
