import "./sanity.spec";
import "./erc20.spec";

/*
Status: all rules passing, coverage with 30 mutations was 90%
*/

// For referring to the automatically (created &) linked instance of other contracts
using CollateralTokenTester as collToken;
using CollSurplusPool as collSurplusPool;
using CdpManager as cdpManager;
using EBTCToken as ebtcToken;     // refers to cdpManager.ebtcToken

methods {
    function call_isAuthorized(address user, uint32 functionSig) external returns (bool) envfree;
    function getSystemCollShares() external returns uint256 envfree;
    function getFeeRecipientClaimableCollShares() external returns uint256 envfree;
    function getSystemDebt() external returns uint256 envfree;
    function collSurplusPoolAddress() external returns address envfree;
    function authorityInitialized() external returns bool envfree;

    function CollateralTokenTester.sharesOf(address) external returns (uint256) envfree;
    function CollateralTokenTester.balanceOf(address) external returns (uint256) envfree;
    function CollateralTokenTester.getPooledEthByShares(uint256) external returns (uint256) envfree;

    function CollSurplusPool.getTotalSurplusCollShares() external returns uint256 envfree;
    function CdpManager.getActiveCdpsCount() external returns (uint256) envfree;
    function EBTCToken.totalSupply() external returns (uint256) envfree;

    function _.increaseTotalSurplusCollShares(uint256) external => DISPATCHER(true);
    function _.onFlashLoan(address, address, uint256, uint256, bytes) external => DISPATCHER(true);

    // Need something nonzero for constructor to behave properly. This is safe because CdpManager.authority() will always be nonzero.
    function _.authority() external => ALWAYS(0x5);

    // Attempt to reduce complexity and avoid timeouts
    function PriceFeed.fetchPrice() external returns (uint256) => NONDET;
}

use rule sanity;

// Used for finding cause of timeouts: identified PriceFeed library
//use builtin rule deepSanity;

invariant authorityInitialized()
    // Always initialized if CdpManager is initialized (which always is, due to CdpManagerStorage's constructor)
    authorityInitialized();

/* AP-01 | The collateral balance in the active pool is greater than or equal to its accounting number | High Level
    I've strengthened this to also consider the internal accounting value feeRecipientCollShares.
*/
invariant systemCollateralBalanceAccountingOk()
    to_mathint(collToken.sharesOf(currentContract)) >= to_mathint(getSystemCollShares() + getFeeRecipientClaimableCollShares())
    { 
        preserved transferSystemCollSharesAndLiquidatorReward(address _account, uint256 _shares, uint256 _liquidatorRewardShares) with (env e) {
            // Invariant fails if this function transfers rewards greater than the excess avail.
            // Only called when closing a CDP and there *should* be sufficient rewards for the last CDP (if other invariants hold).
            require to_mathint(collToken.sharesOf(currentContract)) >= to_mathint(_liquidatorRewardShares + getSystemCollShares() + getFeeRecipientClaimableCollShares());
        }
        preserved claimFeeRecipientCollShares(uint256 _shares) with (env e) {
            // Invariant fails if ActivePool's stETH balance does not have _shares in excess when havac'd feeRecipientCollShares implies
            // that it does. But excess does exist since the function requires it.
            require to_mathint(collToken.sharesOf(currentContract) - _shares) >= to_mathint(getSystemCollShares());
        }
        preserved increaseSystemCollShares(uint256 _shares) with (env e) {
            // Invariant fails when increasing internal accounting if actual stETH balance doesn't reflect it (or have sufficient excess). 
            require to_mathint(collToken.sharesOf(currentContract)) >= to_mathint(_shares + getSystemCollShares() + getFeeRecipientClaimableCollShares());
        }
    }


/* AP-02 | The collateral balance of the ActivePool is positive if there is at least one CDP open | High Level */
invariant systemCollateralInternalBalancePositive()
    (cdpManager.getActiveCdpsCount() > 0) => (getSystemCollShares() > 0)
    {
        preserved allocateSystemCollSharesToFeeRecipient(uint256 _shares) with (env e) {
            require getSystemCollShares() > _shares;
        }
        preserved transferSystemCollShares(address _account, uint256 _shares) with (env e) {
            require getSystemCollShares() > _shares;
        }
        preserved transferSystemCollSharesAndLiquidatorReward(address _account, uint256 _shares, uint256 _liquidatorRewardShares) with (env e) {
            require getSystemCollShares() > _shares;
        }
    }

/* AP-02-B | The collateral balance of the ActivePool is positive if there is at least one CDP open | High Level
    The invariant for fuzz testing uses getSystemCollShares() as above. This one checks stETH balance instead.
*/
invariant systemCollateralActualBalancePositive()
    (cdpManager.getActiveCdpsCount() > 0) => (collToken.sharesOf(currentContract) > 0)
    {
        preserved claimFeeRecipientCollShares(uint256 _shares) with (env e) {
            require collToken.sharesOf(currentContract) > _shares;
        }
        preserved transferSystemCollShares(address _account, uint256 _shares) with (env e) {
            require collToken.sharesOf(currentContract) > _shares;
        }
        preserved transferSystemCollSharesAndLiquidatorReward(address _account, uint256 _shares, uint256 _liquidatorRewardShares) with (env e) {
            require to_mathint(collToken.sharesOf(currentContract)) > to_mathint(_shares + _liquidatorRewardShares);
        }
    }

/* AP-03 | The eBTC debt accounting number in active pool equal to the EBTC total supply | High Level */
invariant systemDebtBalanceAccurate()
    getSystemDebt() == ebtcToken.totalSupply()
    filtered {
        f -> f.selector != sig:increaseSystemDebt(uint256).selector && 
             f.selector != sig:decreaseSystemDebt(uint256).selector
    }

/* AP-04 | The total collateral in active pool should be equal to the sum of all individual CDP collateral | High Level */
ghost mathint sumOfCdpColl {
    init_state axiom sumOfCdpColl == 0;
}
hook Sstore cdpManager.Cdps[KEY bytes32 _cdpId].(offset 32) uint256 new_coll (uint256 old_coll) STORAGE {
    sumOfCdpColl = sumOfCdpColl + new_coll - old_coll;
}
hook Sload uint256 coll cdpManager.Cdps[KEY bytes32 _cdpId].(offset 32)  STORAGE {
    // This Sload requirement makes `sumOfCdpColl >= coll` hold at the beginning of each rule.
  require sumOfCdpColl >= to_mathint(coll);
}
invariant systemCollateralInternalBalanceSumsAllColl()
    to_mathint(getSystemCollShares() + getFeeRecipientClaimableCollShares()) == sumOfCdpColl
    filtered {
        // These functions modify the internal accounting independent of the CDPs. This invariant can't reason about them(?)
        f -> f.selector != sig:increaseSystemCollShares(uint256).selector 
          && f.selector != sig:transferSystemCollShares(address, uint256).selector
          && f.selector != sig:transferSystemCollSharesAndLiquidatorReward(address, uint256, uint256).selector
          && f.selector != sig:claimFeeRecipientCollShares(uint256).selector
    }

/* AP-05 | The sum of debt accounting in active pool should be equal to sum of debt accounting of individual CDPs | High Level */
ghost mathint sumOfCdpDebts {
    init_state axiom sumOfCdpDebts == 0;
}
hook Sstore cdpManager.Cdps[KEY bytes32 _cdpId].(offset 0) uint256 new_debt (uint256 old_debt) STORAGE {
    sumOfCdpDebts = sumOfCdpDebts + new_debt - old_debt;
}
hook Sload uint256 debt cdpManager.Cdps[KEY bytes32 _cdpId].(offset 0)  STORAGE {
    // This Sload requirement makes `sumOfCdpDebts >= debt` hold at the beginning of each rule.
  require sumOfCdpDebts >= to_mathint(debt);
}
invariant systemDebtInternalBalanceSumsAllDebts()
    to_mathint(getSystemDebt()) == sumOfCdpDebts
    filtered {
        f -> f.selector != sig:increaseSystemDebt(uint256).selector && 
             f.selector != sig:decreaseSystemDebt(uint256).selector
    }


rule accessControlRequiresAuth(method m) filtered {
    m -> m.selector == sig:claimFeeRecipientCollShares(uint256).selector
      || m.selector == sig:sweepToken(address, uint256).selector
      || m.selector == sig:setFeeRecipientAddress(address).selector
      || m.selector == sig:setFeeBps(uint256).selector
      || m.selector == sig:setFlashLoansPaused(bool).selector
} {
    env e;
    calldataarg args;
    m@withrevert(e, args);
    bool reverted = lastReverted;
    assert !call_isAuthorized(e.msg.sender, m.selector) => reverted;
}

rule accessControlBOorCdpM(method m) filtered {
    m -> m.selector == sig:transferSystemCollShares(address, uint256).selector
      || m.selector == sig:transferSystemCollSharesAndLiquidatorReward(address, uint256, uint256).selector
      || m.selector == sig:increaseSystemDebt(uint256).selector
      || m.selector == sig:decreaseSystemDebt(uint256).selector
} {
    env e;
    calldataarg args;
    bool userAuthorized = e.msg.sender == borrowerOperationsAddress(e) ||
                          e.msg.sender == cdpManagerAddress(e);
    m@withrevert(e, args);
    assert !userAuthorized => lastReverted;
}

rule adjustingSystemDebt {
    env e;
    uint256 amount;
    uint256 oldAmount = currentContract.systemDebt;

    increaseSystemDebt(e, amount);
    assert currentContract.systemDebt == assert_uint256(oldAmount + amount), "Did not increase systemDebt as expected";

    uint256 amount2;
    uint256 oldAmount2 = currentContract.systemDebt;
    decreaseSystemDebt(e, amount2);
    assert currentContract.systemDebt == assert_uint256(oldAmount2 - amount2), "Did not decrease systemDebt as expected";
}

rule transferSystemCollReducesShares(address a, uint256 sharesToTransfer) {
    env e;
    require(a != currentContract);
    uint256 poolSharesStoredBefore = getSystemCollShares();

    uint256 aSharesBefore = collToken.sharesOf(a);
    uint256 activePoolSharesBefore = collToken.sharesOf(currentContract);
    mathint surplusPoolTotalSharesBefore = collSurplusPool.getTotalSurplusCollShares();

    transferSystemCollShares(e, a, sharesToTransfer);

    assert (getSystemCollShares() == assert_uint256(poolSharesStoredBefore - sharesToTransfer)), 
        "systemCollShares in storage was not reduced by transfer amount";

    // Check actual stETH share balances
    assert (collToken.sharesOf(currentContract) == assert_uint256(activePoolSharesBefore - sharesToTransfer)), 
        "Collateral token transfer out of pool did not occur as expected";
    assert (collToken.sharesOf(a) == assert_uint256(aSharesBefore + sharesToTransfer)), 
        "Collateral token transfer to recipient did not occur as expected";

    // special case for transfer to collSurplusPoolAddress
    mathint newCollSurplusPoolTotalShares = collSurplusPool.getTotalSurplusCollShares();
    assert (a == collSurplusPoolAddress(e)) => (newCollSurplusPoolTotalShares == surplusPoolTotalSharesBefore + sharesToTransfer),
        "totalSurplusCollShares in CollSurplusPool storage was not increased by transfer amount";
    assert (a != collSurplusPoolAddress(e)) => (newCollSurplusPoolTotalShares == surplusPoolTotalSharesBefore),
        "totalSurplusCollShares in CollSurplusPool storage changed when it shouldn't";
}

rule transferSystemCollSharesAndLiquidatorReward(address a, uint256 sharesToTransfer, uint256 liquidatorRewardShares) {
    env e;
    require(a != currentContract);
    uint256 poolSharesStoredBefore = getSystemCollShares();

    uint256 aSharesBefore = collToken.sharesOf(a);
    uint256 activePoolSharesBefore = collToken.sharesOf(currentContract);
    mathint surplusPoolTotalSharesBefore = collSurplusPool.getTotalSurplusCollShares();

    transferSystemCollSharesAndLiquidatorReward(e, a, sharesToTransfer, liquidatorRewardShares);

    // "Liquidator reward shares are not tracked via internal accounting in the active pool and are assumed to be present in expected amount as part of the intended behavior of BorowerOperations and CdpManager"
    assert (getSystemCollShares() == assert_uint256(poolSharesStoredBefore - sharesToTransfer)), 
        "systemCollShares in storage was not reduced by transfer amount";

    // Check actual stETH share balances
    mathint totalTransferred = sharesToTransfer + liquidatorRewardShares;
    assert (collToken.sharesOf(currentContract) == assert_uint256(activePoolSharesBefore - totalTransferred)), 
        "Collateral token transfer out of pool did not occur as expected";
    assert (collToken.sharesOf(a) == assert_uint256(aSharesBefore + totalTransferred)), 
        "Collateral token transfer to recipient did not occur as expected";

    // special case for transfer to collSurplusPoolAddress
    mathint newCollSurplusPoolTotalShares = collSurplusPool.getTotalSurplusCollShares();
    assert (a == collSurplusPoolAddress(e)) => (newCollSurplusPoolTotalShares == surplusPoolTotalSharesBefore + totalTransferred),
        "totalSurplusCollShares in CollSurplusPool storage was not increased by transfer amount";
    assert (a != collSurplusPoolAddress(e)) => (newCollSurplusPoolTotalShares == surplusPoolTotalSharesBefore),
        "totalSurplusCollShares in CollSurplusPool storage changed when it shouldn't";
}

rule allocateSystemCollSharesToFeeRecipient {
    env e;
    uint256 shares;
    bool userAuthorized = e.msg.sender == cdpManagerAddress(e);

    mathint sumBefore = currentContract.systemCollShares + currentContract.feeRecipientCollShares;
    allocateSystemCollSharesToFeeRecipient@withrevert(e, shares);
    mathint sumAfter = currentContract.systemCollShares + currentContract.feeRecipientCollShares;

    assert !userAuthorized => lastReverted;
    assert !lastReverted => sumBefore == sumAfter, "ActivePool shift of internal collateral allocation should maintain total";
}

rule increaseSystemCollShares {
    env e;
    uint256 shares;
    bool userAuthorized = e.msg.sender == borrowerOperationsAddress(e);

    mathint before = currentContract.systemCollShares;
    increaseSystemCollShares@withrevert(e, shares);

    assert !userAuthorized => lastReverted;
    assert !lastReverted => currentContract.systemCollShares == assert_uint256(before + shares), "ActivePool internal collateral shares didn't increase as expected";
}

rule claimFeeRecipientCollShares {
    env e;
    require(feeRecipientAddress(e) != currentContract);
    uint256 sharesToClaim;
    uint256 feeRecipientCollSharesBefore = currentContract.feeRecipientCollShares;
    uint256 activePoolSharesBefore = collToken.sharesOf(currentContract);
    uint256 recipientSharesBefore = collToken.sharesOf(feeRecipientAddress(e));
    
    claimFeeRecipientCollShares@withrevert(e, sharesToClaim);
    bool claimReverted = lastReverted;

    // The function does a "global sync" of accounting, which may cause feeRecipientCollShare to increase just prior to 
    //  the check for sufficient funds. That could have allowed the call to succeed when this rule expects it to fail. So,
    //  this rule needs to allow for the possible "delta" added during sync.
    mathint actual = currentContract.feeRecipientCollShares;
    mathint expected = to_mathint(feeRecipientCollSharesBefore - sharesToClaim);
    mathint deltaAddedByAccountingSync = claimReverted ? 0 : actual - expected;
    mathint maxClaimable = feeRecipientCollSharesBefore + deltaAddedByAccountingSync; 
    assert to_mathint(sharesToClaim) > maxClaimable => claimReverted, "Claiming invalid fee amount from collateral shares did not revert";

    // Can't assert anything useful here without including the delta above ... but that was calculated from these values, so would be vacuous.
    //assert (currentContract.feeRecipientCollShares == assert_uint256(feeRecipientCollSharesBefore - sharesToClaim)), 
    //    "feeRecipientCollShares was not reduced as expected when claiming fees";

    // Check actual stETH share balances
    assert !claimReverted => (collToken.sharesOf(currentContract) == assert_uint256(activePoolSharesBefore - sharesToClaim)), 
        "Collateral token transfer out of pool did not occur as expected";
    assert !claimReverted => (collToken.sharesOf(feeRecipientAddress(e)) == assert_uint256(recipientSharesBefore + sharesToClaim)), 
        "Collateral token transfer to recipient did not occur as expected";
}

rule flashFee {
    env e;
    address token;
    uint256 amount;

    uint256 fee = flashFee@withrevert(e, token, amount);
    bool flashFeeReverted = lastReverted;

    assert token != collateral(e) => flashFeeReverted;
    assert currentContract.flashLoansPaused => flashFeeReverted;
    assert !flashFeeReverted => (fee == assert_uint256((amount * currentContract.feeBps) / MAX_BPS(e))), "Calculated uexpected flash fee ";
}

rule maxFlashLoan {
    env e;
    address token;
    uint256 result = maxFlashLoan(e, token);

    assert token != collateral(e) => result == 0, "Nonzero loan allowed for unsupported token.";
    assert currentContract.flashLoansPaused => result == 0, "Flash loan allowed while paused";
    assert result > 0 => result == collToken.balanceOf(currentContract), "maxFlashLoan amount doesn't match ActivePool collateral balance";
}

rule flashLoan {
    env e;
    require(feeRecipientAddress(e) != currentContract);
    address receiver;
    uint256 amount;
    bytes data;
    uint256 fee = flashFee(e, collateral(e), amount);
    uint256 poolBalanceBefore = collToken.sharesOf(currentContract);
    uint256 recipientBalanceBefore = collToken.balanceOf(feeRecipientAddress(e));

    bool result = flashLoan@withrevert(e, receiver, collateral(e), amount, data);
    bool reverted = lastReverted;

    if (!reverted) {
        assert result == true, "Incorrect return value";

        mathint expectedFeeRecipientBalance = to_mathint(recipientBalanceBefore + fee);
        mathint actualFeeRecipientBalance = to_mathint(collToken.balanceOf(feeRecipientAddress(e)));
        // Need to account for precision loss in CollateralTokenTester conversion to & from shares.
        assert feeRecipientAddress(e) != receiver =>
            actualFeeRecipientBalance > expectedFeeRecipientBalance - 3 && actualFeeRecipientBalance <= expectedFeeRecipientBalance,
            "Fee transfer to recipient did not occur as expected";
        assert collToken.sharesOf(currentContract) >= poolBalanceBefore, "Flash loan reduced ActivePool collateral share balance";
    }
    assert amount == 0 || amount > collToken.balanceOf(currentContract) => reverted, "Invalid flash loan amount did not revert";
    assert collToken.sharesOf(currentContract) < currentContract.systemCollShares => reverted, "Flash loan reducing ActivePool collateral shares did not revert";
    
    // This is vacuous because CollateralTokenTester.getPooledEthByShares() cannot change (always == shares * 3 / 2)
    //assert collToken.getPooledEthByShares(currentContract.DECIMAL_PRECISION) == oldCollShareRate, "Flash loan did not keep same collateral share rate";
}

rule setFeeRecipientAddress {
    env e;
    address newFeeRecipient;
    setFeeRecipientAddress@withrevert(e, newFeeRecipient);
    assert newFeeRecipient == 0 => lastReverted, "Invalid address did not cause revert";
    assert !lastReverted => currentContract.feeRecipientAddress == newFeeRecipient, "feeRecipientAddress was not set correctly";
}

rule setFeeBps {
    env e;
    uint256 newFee;
    setFeeBps(e, newFee);
    bool unauthorized = !call_isAuthorized(e.msg.sender, sig:setFeeBps(uint256).selector);
    setFeeBps@withrevert(e, newFee);
    bool reverted = lastReverted;
    assert (unauthorized || newFee > MAX_FEE_BPS(e)) => reverted, "setFeeBps() did not revert as expected";
    assert !reverted => currentContract.feeBps == assert_uint16(newFee), "feeBps was not set correctly";
}

rule setFlashLoansPaused {
    env e;
    bool newState;
    setFlashLoansPaused(e, newState);
    assert currentContract.flashLoansPaused == newState, "flashLoanPause state incorrect";   
}
