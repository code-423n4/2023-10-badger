using CollateralTokenTester as _CollateralTokenTester;

/////////////////// METHODS ///////////////////////

methods {
    
    // CollateralTokenTester
    function _CollateralTokenTester.balanceOf(address) external returns (uint256) envfree;
    function _CollateralTokenTester.sharesOf(address) external returns (uint256) envfree;
    // ...

    // CollateralTokenTester (external calls)
    function _.getPooledEthByShares(uint256 _sharesAmount) external => DISPATCHER(true);
}

///////////////// DEFINITIONS /////////////////////

////////////////// FUNCTIONS //////////////////////

///////////////// GHOSTS & HOOKS //////////////////

//
// Ghost copy of `collateral._totalBalance`
//

ghost mathint ghostCollateralTotalBalance {
    init_state axiom ghostCollateralTotalBalance == 0;
}

hook Sload uint256 val _CollateralTokenTester._totalBalance STORAGE {
    require(require_uint256(ghostCollateralTotalBalance) == val);
}

hook Sstore _CollateralTokenTester._totalBalance uint256 val STORAGE {
    ghostCollateralTotalBalance = val;
}

//
// Ghost copy of `_CollateralTokenTester.balances[]`
//

ghost mathint ghostCollateralSumAllBalances {
    init_state axiom ghostCollateralSumAllBalances == 0;
}

ghost mapping (address => mathint) ghostCollateralBalances {
    init_state axiom forall address i. ghostCollateralBalances[i] == 0;
    axiom forall address i. ghostCollateralBalances[i] < max_uint128;
}

ghost mapping (address => mathint) ghostCollateralBalancesPrev {
    init_state axiom forall address i. ghostCollateralBalancesPrev[i] == 0;
}

ghost mapping (address => bool) ghostCollateralBalancesChanged {
    init_state axiom forall address i. ghostCollateralBalancesChanged[i] == false;
}

hook Sload uint256 val _CollateralTokenTester.balances[KEY address i] STORAGE {
    require(require_uint256(ghostCollateralBalances[i]) == val);
} 

hook Sstore _CollateralTokenTester.balances[KEY address i] uint256 val STORAGE {
    ghostCollateralBalancesPrev[i] = ghostCollateralBalances[i];
    ghostCollateralBalancesChanged[i] = require_uint256(ghostCollateralBalances[i]) != val;
    ghostCollateralBalances[i] = val;
    ghostCollateralSumAllBalances = ghostCollateralSumAllBalances + val - ghostCollateralBalancesPrev[i];
}

///////////////// PROPERTIES //////////////////////

invariant collateralBalancesSolvency() ghostCollateralTotalBalance == ghostCollateralSumAllBalances;