// SPDX-License-Identifier: MIT

pragma solidity 0.8.17;

import {ActivePool} from "../../packages/contracts/contracts/ActivePool.sol";
import {Authority} from "../../packages/contracts/contracts/Dependencies/Authority.sol";

contract ActivePoolHarness is ActivePool {
    constructor(
        address _borrowerOperationsAddress,
        address _cdpManagerAddress,
        address _collTokenAddress,
        address _collSurplusAddress,
        address _feeRecipientAddress
    )
        ActivePool(
            _borrowerOperationsAddress,
            _cdpManagerAddress,
            _collTokenAddress,
            _collSurplusAddress,
            _feeRecipientAddress
        )
    {}

    function checkAuth(address user, bytes4 functionSig) public view returns (bool) {
        return isAuthorized(user, functionSig);
    }

    function getFeeRecipientClaimableCollSharesHarness() external view returns (uint256) {
        return feeRecipientCollShares;
    }

    function getSystemDebtHarness() external view returns (uint256) {
        return systemDebt;
    }

    function getSystemCollSharesHarness() external view returns (uint256) {
        return systemCollShares;
    }
}
