using CollSurplusPoolHarness as _CollSurplusPool;

/////////////////// METHODS ///////////////////////

methods {
    
    // CollSurplusPoolHarness
    function _CollSurplusPool.call_isAuthorized(address user, uint32 functionSig) external returns (bool) envfree;
    
    // CollSurplusPool
    function _CollSurplusPool.NAME() external returns (string) envfree;
    function _CollSurplusPool.borrowerOperationsAddress() external returns (address) envfree;
    function _CollSurplusPool.cdpManagerAddress() external returns (address) envfree;
    function _CollSurplusPool.activePoolAddress() external returns (address) envfree;
    function _CollSurplusPool.feeRecipientAddress() external returns (address) envfree;
    function _CollSurplusPool.collateral() external returns (address) envfree;
    function _CollSurplusPool.getTotalSurplusCollShares() external returns (uint256) envfree;
    function _CollSurplusPool.getSurplusCollShares(address _account) external returns (uint256) envfree;
    function _CollSurplusPool.increaseSurplusCollShares(address _account, uint256 _amount) external;
    function _CollSurplusPool.claimSurplusCollShares(address _account) external;
    function _CollSurplusPool.increaseTotalSurplusCollShares(uint256 _value) external;
    function _CollSurplusPool.sweepToken(address token, uint256 amount) external;
    
    // CollSurplusPool (external calls)
    function _.increaseTotalSurplusCollShares(uint256 _value) external => DISPATCHER(true);
}

///////////////// DEFINITIONS /////////////////////

////////////////// FUNCTIONS //////////////////////

///////////////// GHOSTS & HOOKS //////////////////

//
// Ghost copy of `totalSurplusCollShares`
//

ghost mathint ghostTotalSurplusCollShares {
    init_state axiom ghostTotalSurplusCollShares == 0;
}

ghost mathint ghostTotalSurplusCollSharesPrev {
    init_state axiom ghostTotalSurplusCollSharesPrev == 0;
}

ghost bool ghostTotalSurplusCollSharesChanged {
    init_state axiom ghostTotalSurplusCollSharesChanged == false;
}

hook Sload uint256 val _CollSurplusPool.totalSurplusCollShares STORAGE {
    require(require_uint256(ghostTotalSurplusCollShares) == val);
}

hook Sstore _CollSurplusPool.totalSurplusCollShares uint256 val STORAGE {
    ghostTotalSurplusCollSharesPrev = ghostTotalSurplusCollShares;
    ghostTotalSurplusCollSharesChanged = require_uint256(ghostTotalSurplusCollShares) != val;
    ghostTotalSurplusCollShares = val;
}

//
// Ghost copy of `balances`
//

ghost mapping (address => mathint) ghostBalances {
    init_state axiom forall address i. ghostBalances[i] == 0;
}

ghost mapping (address => mathint) ghostBalancesPrev {
    init_state axiom forall address i. ghostBalancesPrev[i] == 0;
}

ghost mapping (address => bool) ghostBalancesChanged {
    init_state axiom forall address i. ghostBalancesChanged[i] == false;
}

ghost address ghostUserAddressBalancesChanged {
    init_state axiom ghostUserAddressBalancesChanged == 0;
}

hook Sload uint256 val _CollSurplusPool.balances[KEY address i] STORAGE {
    require(require_uint256(ghostBalances[i]) == val);
} 

hook Sstore _CollSurplusPool.balances[KEY address i] uint256 val STORAGE {
    
    // Use zero address in invariant checks
    require(i != 0);

    ghostBalancesPrev[i] = ghostBalances[i];
    ghostBalancesChanged[i] = require_uint256(ghostBalances[i]) != val;
    ghostUserAddressBalancesChanged = ghostBalancesChanged[i] ? i : ghostUserAddressBalancesChanged;
    ghostBalances[i] = val;
}

///////////////// PROPERTIES //////////////////////

