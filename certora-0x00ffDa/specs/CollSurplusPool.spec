import "./sanity.spec";
import "./erc20.spec";

using CollateralTokenTester as collateral;
using DummyERC20A as someToken;

methods {
    function getTotalSurplusCollShares() external returns uint256 envfree;    
    function getSurplusCollShares(address) external returns uint256 envfree;
    function feeRecipientAddress() external returns address envfree;
    function authorityInitialized() external returns bool envfree;
    function call_isAuthorized(address user, uint32 functionSig) external  returns (bool) envfree;
    function borrowerOperationsAddress() external  returns (address) envfree;

    // collateral methods
    function collateral.balanceOf(address) external returns (uint256) envfree;
    function collateral.sharesOf(address) external returns (uint256) envfree;

    // Need something nonzero for constructor to behave properly. This is safe because CdpManager.authority() will always be nonzero.
    function _.authority() external => ALWAYS(0x5);
}

invariant authorityInitialized()
    // Always initialized if CdpManager is initialized (which always is, due to CdpManagerStorage's constructor)
    authorityInitialized();

/* CSP-01 | The collateral balance in the collSurplus pool is greater than or equal to its accounting number | High Level */
invariant collateralSurplusBalanceAccountingOk()
    collateral.sharesOf(currentContract) >= getTotalSurplusCollShares()
    { 
        preserved increaseTotalSurplusCollShares(uint256 _shares) with (env e) {
            // Invariant fails when increasing internal accounting if actual stETH balance doesn't reflect it (or have sufficient excess). 
            require to_mathint(collateral.sharesOf(currentContract)) >= to_mathint(_shares + getTotalSurplusCollShares());
        }
    }

/* CSP-02 | The sum of all surpluses is equal to the value of getTotalSurplusCollShares | High Level */
ghost mathint sumOfSurplusColl {
    init_state axiom sumOfSurplusColl == 0;
}
hook Sstore balances[KEY address _account] uint256 newBalance (uint256 oldBalance) STORAGE {
    sumOfSurplusColl = sumOfSurplusColl + newBalance - oldBalance;
}
hook Sload uint256 balance balances[KEY address _account] STORAGE {
    // This Sload requirement makes `sumOfSurplusColl >= balance` hold at the beginning of each rule.
  require sumOfSurplusColl >= to_mathint(balance);
}
invariant collateralSurplusSumsAllBalances()
    to_mathint(getTotalSurplusCollShares()) == sumOfSurplusColl
    filtered {
        // These functions modify only one part of the internal accounting. This invariant can't reason about them(?)
        f -> f.selector != sig:increaseTotalSurplusCollShares(uint256).selector
          && f.selector != sig:increaseSurplusCollShares(address,uint256).selector
    }


use rule sanity;

rule changeToCollateralBalance(method f) {
    uint256 before = collateral.balanceOf(currentContract);
    env e;
    calldataarg args;
    f(e,args);
    uint256 after = collateral.balanceOf(currentContract);
    assert after < before =>  
        ( call_isAuthorized(e.msg.sender, f.selector) || e.msg.sender == borrowerOperationsAddress()),
        "Unauthorized caller modified surplus collateral balance"; 
}

rule increaseSurplusCollShares {
    env e;
    address account;
    uint256 value;
    bool userAuthorized = e.msg.sender == cdpManagerAddress(e);
    mathint before = getSurplusCollShares(account);

    increaseSurplusCollShares@withrevert(e, account, value);

    assert !userAuthorized => lastReverted;
    assert !lastReverted => (getSurplusCollShares(account) == assert_uint256(before + value)), 
        "CollSurplusPool collateral balance for a user didn't increase as expected";
}

rule increaseTotalSurplusCollShares {
    env e;
    uint256 value;
    bool userAuthorized = e.msg.sender == activePoolAddress(e);
    uint256 before = getTotalSurplusCollShares();

    increaseTotalSurplusCollShares@withrevert(e, value);

    assert !userAuthorized => lastReverted;
    assert !lastReverted => (getTotalSurplusCollShares() == assert_uint256(before + value)), 
        "CollSurplusPool internal collateral accounting didn't increase as expected";
}

rule claimSurplusCollShares {
    env e;
    address recipient;
    require(recipient != currentContract);
    bool userAuthorized = e.msg.sender == borrowerOperationsAddress(e);
    uint256 recipientBalanceBefore = getSurplusCollShares(recipient);
    uint256 totalSurplusBefore = getTotalSurplusCollShares();
    uint256 surplusPoolSharesBefore = collateral.sharesOf(currentContract);
    uint256 recipientSharesBefore = collateral.sharesOf(recipient);

    claimSurplusCollShares@withrevert(e, recipient);
    bool claimReverted = lastReverted;

    assert !userAuthorized => claimReverted;
    assert recipientBalanceBefore == 0 => claimReverted;
    assert !claimReverted => getSurplusCollShares(recipient) == 0, "claimSurplusCollShares() did not erase balance for recipient";
    assert !claimReverted => to_mathint(getTotalSurplusCollShares()) == to_mathint(totalSurplusBefore - recipientBalanceBefore), 
        "claimSurplusCollShares() did not reduce internal accounting of total shares";

    // Check actual stETH share balances
    assert !claimReverted => (collateral.sharesOf(currentContract) == assert_uint256(surplusPoolSharesBefore - recipientBalanceBefore)), 
        "Collateral token transfer out of pool did not occur as expected";
    assert !claimReverted => (collateral.sharesOf(recipient) == assert_uint256(recipientSharesBefore + recipientBalanceBefore)), 
        "Collateral token transfer to recipient did not occur as expected";
}

rule sweepToken {
    // Not validating the auth logic because comment (correctly) says this function is safe to be called by anyone, although it currently can't be
    env e;
    uint256 amount;
    require(feeRecipientAddress() != currentContract);

    sweepToken@withrevert(e, collateral, amount);
    assert lastReverted, "Attempt to sweep from collateral balance did not revert";

    uint256 poolBalanceBefore = someToken.balanceOf(e, currentContract);
    uint256 recipientBalanceBefore = someToken.balanceOf(e, feeRecipientAddress());

    sweepToken@withrevert(e, someToken, amount);
    bool sweepReverted = lastReverted;

    uint256 poolBalanceAfter = someToken.balanceOf(e, currentContract);
    uint256 recipientBalanceAfter = someToken.balanceOf(e, feeRecipientAddress());

    assert poolBalanceBefore < amount => sweepReverted, "Attempt to sweep more than balance didn't revert";
    assert !sweepReverted => to_mathint(poolBalanceAfter) == to_mathint(poolBalanceBefore - amount), 
        "sweepToken() didn't reduce pool balance as expected";
    assert !sweepReverted => to_mathint(recipientBalanceAfter) == to_mathint(recipientBalanceBefore + amount), 
        "sweepToken() didn't increase recipient balance as expected";
}
