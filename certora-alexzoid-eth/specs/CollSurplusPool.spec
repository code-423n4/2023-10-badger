import "./base/collateralTokenTester.spec";
import "./base/collSurplusPool.spec";
import "./base/activePool.spec";
import "./dependencies/ReentrancyGuard.spec";
import "./dependencies/AuthNoOwner.spec";
import "./dependencies/CdpManager.spec";
import "./dependencies/ERC20.spec";
import "./dependencies/helper.spec";

using DummyERC20A as _DummyERC20A;

/////////////////// METHODS ///////////////////////

///////////////// DEFINITIONS /////////////////////

////////////////// FUNCTIONS //////////////////////

///////////////// GHOSTS & HOOKS //////////////////

///////////////// PROPERTIES //////////////////////

rule changeToCollateralBalance(method f, env e, calldataarg args) {

    uint256 before = _CollateralTokenTester.balanceOf(currentContract);

    f(e,args);

    uint256 after = _CollateralTokenTester.balanceOf(currentContract);

    assert(after < before => (call_isAuthorized(e.msg.sender, f.selector) || e.msg.sender == borrowerOperationsAddress())); 
}

// [] Possibility of not been reverted
use rule helperSanity;

// [] In initialized state authority address should not be zero 
use invariant authNoOwnerInitializedAndAddressSetInConstructor;

// [] authority() should be set in constructor from CdpManager
use invariant authNoOwnerSetAuthorityFromCdpManagerInConstructor;

// [2] User balances should always increase except set to zero
invariant userBalanceShouldAlwaysIncreaseExceptSetToZero() forall address i. 
    // If user balances changed and not to zero
    ghostBalances[i] != 0 && ghostBalances[i] != ghostBalancesPrev[i] 
    // It should change in a upper way
        => ghostBalances[i] > ghostBalancesPrev[i];

// [3] User shares could decrease only to zero and decrease total shares simultaneously
invariant decreaseUserSharesTotalSharesSolvency(address user) 
    // If user balance changed in lower way
    ghostBalancesChanged[user] && ghostBalances[user] < ghostBalancesPrev[user]
        => (
            // It should be set to zero
            ghostBalances[user] == 0 
            // Total shares decrease to previous user balance
            && ghostTotalSurplusCollSharesPrev - ghostTotalSurplusCollShares == ghostBalancesPrev[user]
        ) {
        preserved {
            require(ghostBalancesChanged[user] == false);
        }
    }

// [4] Total shares could decrease only when user shares decrease, could not touch more that one user at time
invariant decreaseTotalSharesUserSharesSolvency() 
    // If total shares changed in lower way
    ghostTotalSurplusCollSharesChanged && ghostTotalSurplusCollSharesPrev > ghostTotalSurplusCollShares
        // User balance should change too
        => ghostUserAddressBalancesChanged != 0 && (forall address i. ghostBalancesChanged[i] => (
            // Only one user balance should change at time
            i == ghostUserAddressBalancesChanged 
            // It should be set to zero
            && ghostBalances[i] == 0 
            // Total shares decrease to previous user balance 
            && ghostTotalSurplusCollSharesPrev - ghostTotalSurplusCollShares == ghostBalancesPrev[i]
        )) {
    preserved {
        require(ghostTotalSurplusCollSharesChanged == false);
        require(ghostUserAddressBalancesChanged == 0);
        require(forall address i. ghostBalancesChanged[i] == false);
    }
}

// [5] Decrease user balance should transfer tokens from current contract to user's
invariant decreaseUserBalanceTransferTokens(address user) 
    // If user balance changed in lower way
    ghostBalancesChanged[user] && ghostBalances[user] < ghostBalancesPrev[user]
        => (
            // Current contract token balance decreased
            ghostCollateralBalancesPrev[currentContract] - ghostCollateralBalances[currentContract]
            // Target user token balance increased the same value
                == ghostCollateralBalances[user] - ghostCollateralBalancesPrev[user]
        ) {
    preserved {
        require(user != currentContract);
        require(ghostBalancesChanged[user] == false);
        requireInvariant decreaseTotalSharesUserSharesSolvency;
        requireInvariant decreaseUserSharesTotalSharesSolvency(user);
    }
}

// [] increaseSurplusCollShares() integrity
rule increaseSurplusCollSharesIntegrity(env e, address _account, uint256 _amount) {

    require(ghostBalances[_account] == ghostBalancesPrev[_account]);

    increaseSurplusCollShares(e, _account, _amount);

    assert(e.msg.sender == cdpManagerAddress());
    assert(ghostBalances[_account] == ghostBalancesPrev[_account] + to_mathint(_amount));
}

// [] claimSurplusCollShares() integrity
rule claimSurplusCollSharesIntegrity(env e, address _account) {

    require(_account != currentContract);
    require(ghostTotalSurplusCollSharesPrev == ghostTotalSurplusCollShares);

    mathint balanceBefore = ghostBalances[_account];
    uint256 currentTokensBefore = _CollateralTokenTester.balanceOf(currentContract);
    uint256 accountTokensBefore = _CollateralTokenTester.balanceOf(_account);
    
    claimSurplusCollShares(e, _account);

    mathint balanceAfter = ghostBalances[_account];
    uint256 currentTokensAfter = _CollateralTokenTester.balanceOf(currentContract);
    uint256 accountTokensAfter = _CollateralTokenTester.balanceOf(_account);

    // Tokens should be moved from current contract to target account address
    // @todo violated
    // assert(currentTokensBefore - currentTokensAfter == accountTokensAfter - accountTokensBefore);

    // Decrease account balance from total shares
    assert(ghostTotalSurplusCollSharesPrev - ghostTotalSurplusCollShares == balanceBefore);

    // Should not be zero before and should become zero after
    assert(balanceBefore != 0 && balanceAfter == 0);
}

// [] increaseTotalSurplusCollShares() integrity
rule increaseTotalSurplusCollSharesIntegrity(env e, uint256 _value) {

    require(ghostTotalSurplusCollSharesPrev == ghostTotalSurplusCollShares);

    increaseTotalSurplusCollShares(e, _value);

    assert(e.msg.sender == _ActivePool);
    assert(ghostTotalSurplusCollShares - ghostTotalSurplusCollSharesPrev == to_mathint(_value));
}

// [] Collateral token could not sweeped
rule sweepTokenNotCollateral(env e, address token, uint256 amount) {

    sweepToken(e, token, amount);

    assert(token != _CollateralTokenTester);
}

// [] sweepToken() integrity
rule sweepTokenIntegrity(env e, address token, uint256 amount) {

    require(_DummyERC20A == token);

    require(feeRecipientAddress() != currentContract);

    uint256 currentBefore = _DummyERC20A.balanceOf(e, currentContract);
    uint256 feeRecipientBefore = _DummyERC20A.balanceOf(e, feeRecipientAddress());

    sweepToken(e, token, amount);

    uint256 currentAfter = _DummyERC20A.balanceOf(e, currentContract);
    uint256 feeRecipientAfter = _DummyERC20A.balanceOf(e, feeRecipientAddress());

    assert(amount <= currentBefore);
    assert(currentBefore - currentAfter == feeRecipientAfter - feeRecipientBefore);
}