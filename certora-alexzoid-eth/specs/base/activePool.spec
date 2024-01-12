using ActivePoolHarness as _ActivePool;

/////////////////// METHODS ///////////////////////

methods {
    
    // ActivePoolHarness

    // ActivePool
    function _ActivePool.DECIMAL_PRECISION() external returns (uint256) envfree;
    function _ActivePool.NAME() external returns (string) envfree;
    function _ActivePool.borrowerOperationsAddress() external returns (address) envfree;
    function _ActivePool.cdpManagerAddress() external returns (address) envfree;
    function _ActivePool.collSurplusPoolAddress() external returns (address) envfree;
    function _ActivePool.feeRecipientAddress() external returns (address) envfree;
    function _ActivePool.collateral() external returns (address) envfree;
    function _ActivePool.getSystemCollShares() external returns (uint256) envfree;
    function _ActivePool.getSystemDebt() external returns (uint256) envfree;
    function _ActivePool.getFeeRecipientClaimableCollShares() external returns (uint256) envfree;
    function _ActivePool.transferSystemCollShares(address _account, uint256 _shares) external;
    function _ActivePool.transferSystemCollSharesAndLiquidatorReward(address _account, uint256 _shares, uint256 _liquidatorRewardShares) external;
    function _ActivePool.allocateSystemCollSharesToFeeRecipient(uint256 _shares) external;
    function _ActivePool.increaseSystemDebt(uint256 _amount) external;
    function _ActivePool.decreaseSystemDebt(uint256 _amount) external;
    function _ActivePool.increaseSystemCollShares(uint256 _value) external;
    function _ActivePool.flashLoan(address receiver, address token, uint256 amount, bytes data) external returns (bool); 
    function _ActivePool.flashFee(address token, uint256 amount) external returns (uint256) envfree;
    function _ActivePool.maxFlashLoan(address token) external returns (uint256);
    function _ActivePool.claimFeeRecipientCollShares(uint256 _shares) external;
    function _ActivePool.sweepToken(address token, uint256 amount) external;
    function _ActivePool.setFeeRecipientAddress(address _feeRecipientAddress) external;
    function _ActivePool.setFeeBps(uint256 _newFee) external;
    function _ActivePool.setFlashLoansPaused(bool _paused) external;
    
    // ActivePool (external calls)
    function _.feeRecipientAddress() external => DISPATCHER(true);
}

///////////////// DEFINITIONS /////////////////////

////////////////// FUNCTIONS //////////////////////

///////////////// GHOSTS & HOOKS //////////////////

//
// Ghost copy of `feeRecipientAddress`
//

ghost address ghostFeeRecipientAddress {
    init_state axiom ghostFeeRecipientAddress == 0;
}

ghost address ghostFeeRecipientAddressPrev {
    init_state axiom ghostFeeRecipientAddressPrev == 0;
}

hook Sload address val _ActivePool.feeRecipientAddress STORAGE {
    require(ghostFeeRecipientAddress == val);
}

hook Sstore _ActivePool.feeRecipientAddress address val STORAGE {
    ghostFeeRecipientAddressPrev = ghostFeeRecipientAddress;
    ghostFeeRecipientAddress = val;
}

//
// Ghost copy of `systemCollShares`
//

ghost uint256 ghostSystemCollShares {
    init_state axiom ghostSystemCollShares == 0;
}

ghost uint256 ghostSystemCollSharesPrev {
    init_state axiom ghostSystemCollSharesPrev == 0;
}

ghost bool ghostSystemCollSharesChanged {
    init_state axiom ghostSystemCollSharesChanged == false;
}

hook Sload uint256 val _ActivePool.systemCollShares STORAGE {
    require(ghostSystemCollShares == val);
}

hook Sstore _ActivePool.systemCollShares uint256 val STORAGE {
    ghostSystemCollSharesPrev = ghostSystemCollShares;
    ghostSystemCollShares = val;
    ghostSystemCollSharesChanged = true;
}

//
// Ghost copy of `systemDebt`
//

ghost uint256 ghostSystemDebt {
    init_state axiom ghostSystemDebt == 0;
}

ghost uint256 ghostSystemDebtPrev {
    init_state axiom ghostSystemDebtPrev == 0;
}

hook Sload uint256 val _ActivePool.systemDebt STORAGE {
    require(ghostSystemDebt == val);
}

hook Sstore _ActivePool.systemDebt uint256 val STORAGE {
    ghostSystemDebtPrev = ghostSystemDebt;
    ghostSystemDebt = val;
}

//
// Ghost copy of `feeRecipientCollShares`
//

ghost uint256 ghostFeeRecipientCollShares {
    init_state axiom ghostFeeRecipientCollShares == 0;
}

ghost uint256 ghostFeeRecipientCollSharesPrev {
    init_state axiom ghostFeeRecipientCollSharesPrev == 0;
}

ghost bool ghostFeeRecipientCollSharesChanged {
    init_state axiom ghostFeeRecipientCollSharesChanged == false;
}

hook Sload uint256 val _ActivePool.feeRecipientCollShares STORAGE {
    require(ghostFeeRecipientCollShares == val);
}

hook Sstore _ActivePool.feeRecipientCollShares uint256 val STORAGE {
    ghostFeeRecipientCollSharesPrev = ghostFeeRecipientCollShares;
    ghostFeeRecipientCollShares = val;
    ghostFeeRecipientCollSharesChanged = true;
}

///////////////// PROPERTIES //////////////////////

invariant activePoolIncreaseCollSurplusPoolTotalSharesShouldTransferCollateralTokens() 
    // If CollSurplusPool total shares changed
    ghostTotalSurplusCollSharesChanged
        // CollSurplusPool collateral token balance should be changed as well
        => ghostTotalSurplusCollShares - ghostTotalSurplusCollSharesPrev 
            == ghostCollateralBalances[_CollSurplusPool] - ghostCollateralBalancesPrev[_CollSurplusPool] {
    preserved {
        require(ghostFeeRecipientAddress != _CollSurplusPool);
        require(ghostTotalSurplusCollSharesChanged == false);
        require(ghostCollateralBalancesChanged[_CollSurplusPool] == false);
    }
}