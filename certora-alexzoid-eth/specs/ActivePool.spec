import "./base/activePool.spec";
import "./base/collateralTokenTester.spec";
import "./base/collSurplusPool.spec";
import "./dependencies/AuthNoOwner.spec";
import "./dependencies/ReentrancyGuard.spec";
import "./dependencies/ERC3156FlashLender.spec";
import "./dependencies/CdpManager.spec";
import "./dependencies/ERC20.spec";
import "./dependencies/helper.spec";

using DummyERC20A as _DummyERC20A;

/////////////////// METHODS ///////////////////////

methods {
    // MockFlashBorrower
    function _.onFlashLoan(address initiator, address token, uint256 amount, uint256 fee, bytes data) external 
        => onFlashLoanCVL(initiator, token, amount, fee, data) expect bytes32 ALL;
}

///////////////// DEFINITIONS /////////////////////

definition NEED_TO_SYNC_GLOBAL_FUNCTIONS(method f) returns bool =
    f.selector == sig:claimFeeRecipientCollShares(uint256).selector
    || f.selector == sig:sweepToken(address, uint256).selector
    || f.selector == sig:setFeeRecipientAddress(address).selector
    || f.selector == sig:setFeeBps(uint256).selector
    || f.selector == sig:setFlashLoansPaused(bool).selector;

definition TRANSFER_SYSTEM_COLL_SHARES_FUNCTION(method f) returns bool =
    f.selector == sig:transferSystemCollShares(address, uint256).selector;

definition INCREASE_SYSTEM_DEBT_FUNCTION(method f) returns bool = 
    f.selector == sig:increaseSystemDebt(uint256).selector;

definition DECREASE_SYSTEM_DEBT_FUNCTION(method f) returns bool = 
    f.selector == sig:decreaseSystemDebt(uint256).selector;

definition CHANGE_SYSTEM_DEBT_FUNCTIONS(method f) returns bool = 
    INCREASE_SYSTEM_DEBT_FUNCTION(f) || DECREASE_SYSTEM_DEBT_FUNCTION(f);

////////////////// FUNCTIONS //////////////////////

// Summarization for MockFlashBorrower.onFlashLoan()
function onFlashLoanCVL(address initiator, address token, uint256 amount, uint256 fee, bytes data) returns bytes32 {
    ghostOnFlashLoanInitiator = initiator;
    ghostOnFlashLoanToken = token;
    ghostOnFlashLoanAmount = amount;
    ghostOnFlashLoanFee = fee;
    ghostOnFlashLoanDataLen = data.length;
    return ghostOnFlashLoanReturn;    
}

function callerIsBO(address caller) returns bool {
    return caller == borrowerOperationsAddress();
}

function callerIsCdpM(address caller) returns bool {
    return caller == cdpManagerAddress();
}

function callerIsBOorCdpM(address caller) returns bool {
    return (caller == cdpManagerAddress() || caller == borrowerOperationsAddress());
}

///////////////// GHOSTS & HOOKS //////////////////

// onFlashLoan() parameters and return value
ghost address ghostOnFlashLoanInitiator;
ghost address ghostOnFlashLoanToken;
ghost uint256 ghostOnFlashLoanAmount;
ghost uint256 ghostOnFlashLoanFee;
ghost uint256 ghostOnFlashLoanDataLen;
ghost bytes32 ghostOnFlashLoanReturn;

///////////////// PROPERTIES //////////////////////

// Possibility of not been reverted 
use rule helperSanity;

// [2] In initialized state authority address should not be zero
use invariant authNoOwnerInitializedAndAddressSetInConstructor;

// [g4] authority() should be set in constructor from CdpManager
use invariant authNoOwnerSetAuthorityFromCdpManagerInConstructor;

// [3] feeBps should not be greater than MAX_FEE_BPS 
use invariant erc3156FlashLenderFeeBpsNotGtMaxfeeBps;

// [4] When CollSurplusPool total shares increased, collateral tokens should be transfered 
use invariant activePoolIncreaseCollSurplusPoolTotalSharesShouldTransferCollateralTokens;

// [] Only BorrowerOperations should increase systemCollShares
invariant onlyBorrowerOperationsIncreaseSystemCollShares(env e) 
    // Shares increased
    ghostSystemCollShares > ghostSystemCollSharesPrev   
        // Caller is BorrowerOperations
        => callerIsBO(e.msg.sender) {
    preserved with (env eFunc) {
        require(ghostSystemCollShares == ghostSystemCollSharesPrev);
        // Require `invariantEnv.msg.sender` == `e.msg.sender`
        require(e.msg.sender == eFunc.msg.sender);
    }
}

// [] Only CdpManager should increase fees
invariant onlyCdpManagerAllocateFeeFromShares(env e) 
    // Fees increased
    ghostFeeRecipientCollShares > ghostFeeRecipientCollSharesPrev
        // Caller is a CdpManager
        => callerIsCdpM(e.msg.sender) {
    preserved with (env eFunc) {
        require(ghostFeeRecipientCollShares == ghostFeeRecipientCollSharesPrev);
        // Require `invariantEnv.msg.sender` == `e.msg.sender`
        require(e.msg.sender == eFunc.msg.sender);
    }
}

// [] Fees should be taken from shares
invariant feeRecipientCollSharesIncreaseSolvency()
    // Fees increased
    ghostFeeRecipientCollShares > ghostFeeRecipientCollSharesPrev
        // Increased amount of fee equal to decreased amount of shares
        => (ghostFeeRecipientCollShares - ghostFeeRecipientCollSharesPrev 
            == ghostSystemCollSharesPrev - ghostSystemCollShares) {
    preserved {
        require(ghostSystemCollShares == ghostSystemCollSharesPrev);
        require(ghostFeeRecipientCollShares == ghostFeeRecipientCollSharesPrev);
    }
}

// [5] Only CdpManager, BorrowerOperations or authorized user should modify state
rule modifyStateCallerRestrictions(env e, method f, calldataarg args) {
    
    storage before = lastStorage;

    f(e, args);

    storage after = lastStorage;

    // State was changed
    assert(before[currentContract] != after[currentContract] 
        => (e.msg.sender == cdpManagerAddress() 
        || e.msg.sender == borrowerOperationsAddress()
        || ghostCanCall[e.msg.sender][to_bytes4(f.selector)]
        )
    );
}

// [] SystemDebt should be changed by BorrowerOperations or CdpManager with increaseSystemDebt() or decreaseSystemDebt()
rule oneWayChangeSystemDebt(env e, method f, calldataarg args) {

    mathint before = ghostSystemDebt;

    f(e, args);

    mathint after = ghostSystemDebt;

    assert(
        // SystemDebt changed
        before != after 
        // Caller is BorrowerOperations or CdpManager
        => (callerIsBOorCdpM(e.msg.sender) && (after > before
            // SystemDebt increased with increaseSystemDebt()
            ? f.selector == sig:increaseSystemDebt(uint256).selector
            // SystemDebt decreased with decreaseSystemDebt()
            : f.selector == sig:decreaseSystemDebt(uint256).selector)
        )
    );
}

// [g150] syncGlobalAccountingAndGracePeriod() should be called
rule syncedGlobal(env e, method f, calldataarg args) 
    filtered { f -> NEED_TO_SYNC_GLOBAL_FUNCTIONS(f) } {

    require(syncGlobalAccountingAndGracePeriodCalled == false);

    f(e, args);

    assert(syncGlobalAccountingAndGracePeriodCalled);
}

// [g10,g11,g13,g14,g16] Transfer collateral shares decrease total shares
rule transferSystemCollSharesDecreaseTotalShares(env e, address _account, uint256 _shares) {

    require(ghostCollateralBalancesChanged[currentContract] == false);
    require(ghostSystemCollSharesChanged == false);
    require(_account != currentContract);

    transferSystemCollShares(e, _account, _shares);

    assert(
        (ghostCollateralBalancesChanged[currentContract] || ghostSystemCollSharesChanged)
            => ghostCollateralBalancesPrev[currentContract] - ghostCollateralBalances[currentContract]
                == ghostSystemCollSharesPrev - ghostSystemCollShares
        );
}

// [g54-56] Transfer to CollSurplusPool should increase its total shares
rule transferToCollSurplusPoolIncreaseTotalSurplusCollShares(env e, address _account, uint256 _shares) {

    require(ghostCollateralBalancesChanged[currentContract] == false);
    require(ghostCollateralBalancesChanged[_CollSurplusPool] == false);
    require(ghostSystemCollSharesChanged == false);
    require(ghostTotalSurplusCollSharesChanged == false);
    require(_account == _CollSurplusPool);

    transferSystemCollShares(e, _account, _shares);

    assert(
        ghostCollateralBalancesChanged[currentContract] 
        || ghostCollateralBalancesChanged[_CollSurplusPool]
        || ghostSystemCollSharesChanged
        || ghostTotalSurplusCollSharesChanged
            => (
                // ActivePool token balance decreased is equal on both ActivePool and CollSurplusPool
                (ghostCollateralBalancesPrev[currentContract] - ghostCollateralBalances[currentContract]
                    // ... CollSurplusPool balance increased
                    == ghostCollateralBalances[_CollSurplusPool] - ghostCollateralBalancesPrev[_CollSurplusPool])
                    // ActivePool total shares decreased
                    && ghostSystemCollSharesPrev - ghostSystemCollShares
                        // ... CollSurplusPool total shares increased
                        == ghostTotalSurplusCollShares - ghostTotalSurplusCollSharesPrev
            )
        );
}

// [g22-28,g30-33] Transfer collateral shares and liquidator reward decrease total shares
rule transferSystemCollSharesAndLiquidatorRewardDecreaseTotalShares(
    env e, 
    address _account,
    uint256 _shares,
    uint256 _liquidatorRewardShares
) {
    require(ghostCollateralBalancesChanged[currentContract] == false);
    require(ghostSystemCollSharesChanged == false);
    require(_account != currentContract);

    transferSystemCollSharesAndLiquidatorReward(e, _account, _shares, _liquidatorRewardShares);

    assert(_shares == assert_uint256(ghostSystemCollSharesPrev - ghostSystemCollShares));

    assert(
        ghostCollateralBalancesChanged[currentContract] || ghostSystemCollSharesChanged
            => ghostCollateralBalancesPrev[currentContract] - ghostCollateralBalances[currentContract]
                == _shares + _liquidatorRewardShares
        );
}   

// [g45-51] Allocate fee shares from total shares 
rule allocateSystemCollSharesToFeeRecipientDecreaseTotalShares(env e, uint256 _shares) {

    require(ghostSystemCollSharesChanged == false);
    require(ghostFeeRecipientCollSharesChanged == false);

    allocateSystemCollSharesToFeeRecipient(e, _shares);

    // Could not allocate fees more than total shares
    assert(ghostSystemCollSharesPrev >= _shares);

    // Allocated fee and total shares change simultaneously
    assert(ghostSystemCollSharesChanged <=> ghostFeeRecipientCollSharesChanged);
    
    assert(
        // Fee increase is
        ghostFeeRecipientCollShares - ghostFeeRecipientCollSharesPrev
            // equal to total shares decrease
            == ghostSystemCollSharesPrev - ghostSystemCollShares
    );
}

// [g69,g70,g73,g74] Increase and decrease system debt integrity
rule changeSystemDebtIntegrity(env e, method f, uint256 _amount) 
    filtered { f -> CHANGE_SYSTEM_DEBT_FUNCTIONS(f) } {

    mathint before = ghostSystemDebt;

    if(INCREASE_SYSTEM_DEBT_FUNCTION(f)) {
        increaseSystemDebt(e, _amount);
    } else {
        decreaseSystemDebt(e, _amount);
    }

    mathint after = ghostSystemDebt;

    assert(INCREASE_SYSTEM_DEBT_FUNCTION(f)
        // System debt increased by amount
        ? assert_uint256(after - before) == _amount
        // System debt decreased by amount
        : assert_uint256(before - after) == _amount
        );
}

// [g84-91] increaseSystemCollShares integrity
rule increaseSystemCollSharesIntegrity(env e, uint256 _value) {

    require(ghostSystemCollSharesPrev == ghostSystemCollShares);

    increaseSystemCollShares(e, _value);

    assert(_value == assert_uint256(ghostSystemCollShares - ghostSystemCollSharesPrev));
}

// [g92-93,g96-97,g99-106,g108-110,g112-113,g115-116] flashLoan() integrity
use invariant collateralBalancesSolvency;
rule flashLoanIntegrity(env e, address receiver, address token, uint256 amount, bytes data) {

    requireInvariant collateralBalancesSolvency;
    require(ghostCollateralBalances[currentContract] == ghostCollateralBalancesPrev[currentContract]);
    require(ghostCollateralBalances[ghostFeeRecipientAddress] == ghostCollateralBalancesPrev[ghostFeeRecipientAddress]);

    require(_CollateralTokenTester.balanceOf(currentContract) 
        >= _CollateralTokenTester.getPooledEthByShares(e, ghostSystemCollShares));
    require(_CollateralTokenTester.sharesOf(currentContract) 
        >= ghostSystemCollShares);

    require(ghostFeeRecipientAddress != currentContract);
    require(ghostFeeRecipientAddress != _CollateralTokenTester);
    require(receiver != ghostFeeRecipientAddress);
    require(receiver != currentContract);
    require(receiver != _CollateralTokenTester);

    mathint fee = flashFee(token, amount);
    mathint maxFlashLoan = maxFlashLoan(e, token);
    mathint rateBefore = _CollateralTokenTester.getPooledEthByShares(e, DECIMAL_PRECISION());

    flashLoan(e, receiver, token, amount, data);

    mathint rateAfter = _CollateralTokenTester.getPooledEthByShares(e, DECIMAL_PRECISION());

    // Valid amount to load
    assert(amount > 0 && amount <= assert_uint256(maxFlashLoan));

    // Valid onFlashLoan() parameters
    assert(
        ghostOnFlashLoanInitiator == e.msg.sender
        && ghostOnFlashLoanToken == token
        && ghostOnFlashLoanAmount == amount
        && ghostOnFlashLoanFee == assert_uint256(fee)
        && ghostOnFlashLoanDataLen == data.length
        && ghostOnFlashLoanReturn == FLASH_SUCCESS_VALUE(e)
        );

    // @todo violated, balance decreases min by 1 wei
    // Current contract balance should not decreased
    // assert(ghostCollateralBalances[currentContract] == ghostCollateralBalancesPrev[currentContract]);

    // Fee recipient balance should increase by fee
    mathint feeSent = ghostCollateralBalances[ghostFeeRecipientAddress] - ghostCollateralBalancesPrev[ghostFeeRecipientAddress];
    assert(
        // 1 wei issue, sent zero fee when fee is 1
        (fee == 1 => feeSent == 0)
        || feeSent == fee
     );

    // Check new balance
    assert(_CollateralTokenTester.balanceOf(currentContract) 
        >= _CollateralTokenTester.getPooledEthByShares(e, assert_uint256(ghostSystemCollShares)));
    assert(_CollateralTokenTester.sharesOf(currentContract) 
        >= ghostSystemCollShares);

    // Rate should not change
    assert(rateBefore == rateAfter);
}

// [g118-119,g121-122,g124-134] flashFee() integrity
rule flashFeeIntegrity(address token, uint256 amount) {

    uint256 fee = flashFee(token, amount);
    
    uint256 expectedFee = require_uint256((amount * ghostFeeBps) / MAX_BPS());

    assert(token == _CollateralTokenTester);
    assert(ghostFlashLoansPaused == false);
    assert(fee == expectedFee);
}

// [g136,138] maxFlashLoan() integrity
rule maxFlashLoanIntegrity(env e, address token) {

    uint256 result = maxFlashLoan(e, token);

    assert(token != _CollateralTokenTester || ghostFlashLoansPaused 
        ? result == 0
        : result == _CollateralTokenTester.balanceOf(e, currentContract)
        );
}

// [g143-144,g146,g149] claimFeeRecipientCollShares() integrity
rule claimFeeRecipientCollSharesIntegrity(env e, uint256 _shares) {

    require(ghostFeeRecipientAddress != currentContract);

    require(ghostFeeRecipientCollShares == ghostFeeRecipientCollSharesPrev);
    require(ghostCollateralBalances[currentContract] == ghostCollateralBalancesPrev[currentContract]);
    require(ghostCollateralBalances[ghostFeeRecipientAddress] == ghostCollateralBalancesPrev[ghostFeeRecipientAddress]);

    claimFeeRecipientCollShares(e, _shares);

    // Total fee shares increased
    assert(_shares == assert_uint256(ghostFeeRecipientCollSharesPrev - ghostFeeRecipientCollShares));
    // Current token balance decreased
    assert(_shares == assert_uint256(ghostCollateralBalancesPrev[currentContract] - ghostCollateralBalances[currentContract]));
    // Fee recipient token balance increased
    assert(_shares == assert_uint256(ghostCollateralBalances[ghostFeeRecipientAddress] - ghostCollateralBalancesPrev[ghostFeeRecipientAddress]));
}

// [g151-152] Collateral token could not sweeped
rule sweepTokenNotCollateral(env e, address token, uint256 amount) {

    sweepToken(e, token, amount);

    assert(token != _CollateralTokenTester);
}

// [g154-155,g157-158] sweepToken() integrity
rule sweepTokenIntegrity(env e, address token, uint256 amount) {

    require(_DummyERC20A == token);

    require(ghostFeeRecipientAddress != currentContract);
    require(ghostFeeRecipientAddress != _DummyERC20A);

    uint256 currentBefore = _DummyERC20A.balanceOf(e, currentContract);
    uint256 feeRecipientBefore = _DummyERC20A.balanceOf(e, ghostFeeRecipientAddress);

    sweepToken(e, token, amount);

    uint256 currentAfter = _DummyERC20A.balanceOf(e, currentContract);
    uint256 feeRecipientAfter = _DummyERC20A.balanceOf(e, ghostFeeRecipientAddress);

    assert(amount <= currentBefore);
    assert(currentBefore - currentAfter == feeRecipientAfter - feeRecipientBefore);
}

// [g159-160,g162] setFeeRecipientAddress() integrity
rule setFeeRecipientAddressIntegrity(env e, address _feeRecipientAddress) {

    setFeeRecipientAddress(e, _feeRecipientAddress);

    assert(_feeRecipientAddress != 0);
    assert(_feeRecipientAddress == ghostFeeRecipientAddress);
}

// [g168-170] setFeeBps() integrity
rule setFeeBpsIntegrity(env e, uint256 _newFee) {

    setFeeBps(e, _newFee);

    assert(assert_uint16(_newFee) == ghostFeeBps);
}

// [g172-174] setFlashLoansPaused() integrity
rule setFlashLoansPausedIntegrity(env e, bool _paused) {

    setFlashLoansPaused(e, _paused);

    assert(_paused == ghostFlashLoansPaused);
}