import "./sanity.spec";
import "./erc20.spec";

using CollateralTokenTester as collateralToken;
using CollSurplusPool as _CollSurplusPool;
using MockFlashBorrower as flashBorrower;
using CdpManager as _CdpManager;
using DummyERC20A as tokenA;

methods {
    function call_isAuthorized(address user, uint32 functionSig) external  returns (bool) envfree;

    function _.increaseTotalSurplusCollShares(uint256) external => DISPATCHER(true);
    function _.onFlashLoan(address, address, uint256, uint256, bytes) external => DISPATCHER(true);

    //view
    function getSystemCollShares() external returns(uint256) envfree;
    function getSystemDebt() external returns(uint256) envfree;
    function getFeeRecipientClaimableCollShares() external returns(uint256) envfree;
    function borrowerOperationsAddress() external returns(address) envfree;
    function cdpManagerAddress() external returns(address) envfree;
    function collSurplusPoolAddress() external returns(address) envfree;
    function collateral() external returns(address) envfree;
    function feeRecipientAddress() external returns(address) envfree;
    function flashFee(address, uint256) external returns(uint256) envfree;
    function maxFlashLoan(address) external returns(uint256) envfree;

    //collateral Token
    function collateralToken.getPooledEthByShares(uint256) external returns(uint256) envfree;
    function collateralToken.balanceOf(address) external returns(uint256) envfree;
    function collateralToken.sharesOf(address) external returns(uint256) envfree;

    // _CollSurplusPool
    function _CollSurplusPool.getTotalSurplusCollShares() external returns(uint256) envfree;

    // flashBorrower 
    function flashBorrower.counter() external returns(uint8) envfree;

    // ERC3156FlashLender
    function feeBps() external returns(uint16) envfree;
    function flashLoansPaused() external returns(bool) envfree;
    function MAX_BPS() external returns(uint256) envfree;
    function MAX_FEE_BPS() external returns(uint256) envfree;

    // CdpManager
    function _CdpManager.stEthIndex() external returns(uint256) envfree;
    function _CdpManager.syncGlobalAccountingAndGracePeriod() external => sum_syncGlobalAccounting();

    // ERC20
    function tokenA.balanceOf(address) external returns(uint256) envfree;
}


use rule sanity;

/***********************    PARTICIPANT  ************************/

/***********************    MISC   ************************/

definition requiresAuthFunc(method f) returns bool = (
    f.selector == sig:claimFeeRecipientCollShares(uint256).selector
    || f.selector == sig:sweepToken(address,uint256).selector
    || f.selector == sig:setFeeRecipientAddress(address).selector
    || f.selector == sig:setFeeBps(uint256).selector
    || f.selector == sig:setFlashLoansPaused(bool).selector
);

ghost uint256 feeTaken;

function sum_syncGlobalAccounting() {
    env e;
    require feeTaken < getSystemCollShares();
    allocateSystemCollSharesToFeeRecipient(e, feeTaken);
}

/***********************    HIGH LEVEL  ************************/

/// @notice immutable variable cannot changed
rule immutableVariable(env e, method f, calldataarg args){
    address _borrowerOperationsAddress = borrowerOperationsAddress();
    address _cdpManagerAddress = cdpManagerAddress();
    address _collateral = collateral();
    address _collSurplusPoolAddress = collSurplusPoolAddress();

    f(e,args);
        
    address borrowerOperationsAddress_ = borrowerOperationsAddress();
    address cdpManagerAddress_ = cdpManagerAddress();
    address collateral_ = collateral();
    address collSurplusPoolAddress_ = collSurplusPoolAddress();

    assert _borrowerOperationsAddress == borrowerOperationsAddress_;
    assert _cdpManagerAddress == cdpManagerAddress_;
    assert _collateral == collateral_;
    assert _collSurplusPoolAddress == collSurplusPoolAddress_;
}

//TODO still failing, violation can be posible 
rule minimumBalance(
    env e ,
    method f,
    calldataarg args
) filtered {
    f -> f.selector != sig:increaseSystemCollShares(uint256).selector && f.selector != sig:transferSystemCollSharesAndLiquidatorReward(address,uint256,uint256).selector
}{
    uint256 feeRecipientCollShares = getFeeRecipientClaimableCollShares();
    uint256 _systemCollShares = getSystemCollShares();
    require to_mathint(collateralToken.balanceOf(currentContract)) 
        >= collateralToken.getPooledEthByShares(_systemCollShares) + collateralToken.getPooledEthByShares(feeRecipientCollShares) ;

    f(e,args);

    uint256 systemCollShares_ = getSystemCollShares();
    assert collateralToken.balanceOf(currentContract) >= collateralToken.getPooledEthByShares(systemCollShares_);
}

/// @notice only borrowerOperator and cdpManager can changed systemCollShares
rule onlyBOorcdpM(
    env e ,
    method f,
    calldataarg args
){

    f@withrevert(e,args);
    bool isRevert = lastReverted;
    assert (f.selector == sig:decreaseSystemDebt(uint256).selector
        || f.selector == sig:increaseSystemDebt(uint256).selector
        || f.selector == sig:transferSystemCollSharesAndLiquidatorReward(address,uint256,uint256).selector
        || f.selector == sig:transferSystemCollShares(address, uint256).selector)
        && (e.msg.sender != borrowerOperationsAddress()
        && e.msg.sender != cdpManagerAddress())
        => isRevert;

    assert f.selector == sig:allocateSystemCollSharesToFeeRecipient(uint256).selector
        && e.msg.sender != cdpManagerAddress()
        => isRevert;

    assert f.selector == sig:increaseSystemCollShares(uint256).selector
        && e.msg.sender != borrowerOperationsAddress()
        => isRevert;
}

/// @notice several rules need authentication
rule requiresAuthCheck(
    env e,
    method f,
    calldataarg args
){

    f@withrevert(e,args);
    bool isRevert = lastReverted;
    assert requiresAuthFunc(f)
        && !call_isAuthorized(e.msg.sender, f.selector)
        => isRevert;
}
/// @notice only several rules can decrease or increase systemCollShares
rule systemCollShares_increaseDecrease(
    env e ,
    method f ,
    calldataarg args
){
    uint256 _systemCollShares = getSystemCollShares();

    f(e,args);

    uint256 systemCollShares_ = getSystemCollShares();
    assert _systemCollShares != systemCollShares_ && f.selector != sig:increaseSystemCollShares(uint256).selector
        => _systemCollShares > systemCollShares_;
    assert _systemCollShares != systemCollShares_ && f.selector == sig:increaseSystemCollShares(uint256).selector
        => _systemCollShares < systemCollShares_;
}

/***********************    UNIT TEST  ************************/

/// @notice transferSystemCollShares should transfer shares and reduce systemCollShares
rule transferSystemCollShares_integrity(
    env e,
    address account,
    uint256 amount
) {
    uint256 _systemCollShares = getSystemCollShares();
    uint256 _thisShares = collateralToken.sharesOf(currentContract);
    uint256 _accountShares = collateralToken.sharesOf(account);
    uint256 _totalSurplusCollShares = _CollSurplusPool.getTotalSurplusCollShares();

    transferSystemCollShares(e, account,amount); 

    uint256 systemCollShares_ = getSystemCollShares();
    uint256 thisShares_ = collateralToken.sharesOf(currentContract);
    uint256 accountShares_ = collateralToken.sharesOf(account);
    uint256 totalSurplusCollShares_ = _CollSurplusPool.getTotalSurplusCollShares();

    assert to_mathint(systemCollShares_) == _systemCollShares - amount;
    assert account != currentContract => to_mathint(thisShares_) == _thisShares - amount;
    assert account != currentContract => to_mathint(accountShares_) == _accountShares + amount;
    assert account == _CollSurplusPool || amount == 0 <=> to_mathint(totalSurplusCollShares_) == _totalSurplusCollShares + amount;
}

/// @notice transferSystemCollShares should able to transfer to any account
rule transferSystemCollShares_accountSatisfy(
    env e,
    address account,
    uint256 amount
) {
    transferSystemCollShares(e, account,amount); 
    satisfy account != _CollSurplusPool;
}

/// @notice transferSystemCollSharesAndLiquidatorReward should transfer shares + liquidation reward and reduce systemCollShares
rule transferSystemCollSharesAndLiquidatorReward(
    env e,
    address account,
    uint256 amount,
    uint256 liquidatorReward
) {
    uint256 _systemCollShares = getSystemCollShares();
    uint256 _thisShares = collateralToken.sharesOf(currentContract);
    uint256 _accountShares = collateralToken.sharesOf(account);

    transferSystemCollSharesAndLiquidatorReward(e, account, amount, liquidatorReward);

    uint256 systemCollShares_ = getSystemCollShares();
    uint256 thisShares_ = collateralToken.sharesOf(currentContract);
    uint256 accountShares_ = collateralToken.sharesOf(account);


    assert to_mathint(systemCollShares_) == _systemCollShares - amount;
    assert account != currentContract => to_mathint(thisShares_) == _thisShares - (amount + liquidatorReward);
    assert account != currentContract => to_mathint(accountShares_) == _accountShares + (amount + liquidatorReward);
}

/// @notice allocateSystemCollSharesToFeeRecipient should transfer systemCollShares 
/// to feeRecipientCollShares
rule allocateSystemCollSharesToFeeRecipient_integrity(env e, uint256 amount) {
    uint256 _systemCollShares = getSystemCollShares();
    uint256 _feeRecipientCollShares = getFeeRecipientClaimableCollShares();

    allocateSystemCollSharesToFeeRecipient(e, amount);

    uint256 systemCollShares_ = getSystemCollShares();
    uint256 feeRecipientCollShares_ = getFeeRecipientClaimableCollShares();
    assert to_mathint(systemCollShares_) == _systemCollShares - amount
        <=> e.msg.sender == cdpManagerAddress();
    assert to_mathint(feeRecipientCollShares_) == _feeRecipientCollShares + amount;
}

/// @notice integrity of increase decrease systemDebt, should increasing or decreasing systemDebt
rule increaseDecreaseSystemDebt_integrity(env e, uint256 amount){
    uint256 systemDebt_1 = getSystemDebt();

    increaseSystemDebt(e, amount);

    uint256 systemDebt_2 = getSystemDebt();

    decreaseSystemDebt(e, amount);

    uint256 systemDebt_3 = getSystemDebt();

    assert to_mathint(systemDebt_2) == systemDebt_1 + amount 
        <=> e.msg.sender == cdpManagerAddress() 
        || e.msg.sender == borrowerOperationsAddress();
    assert systemDebt_3 == systemDebt_1;
}

/// @notice integrity of decrease increase ssytemDebt, should able to decreasing and return to the same value
rule decreaseIncreaseSystemDebt_integrity(env e, uint256 amount){
    uint256 systemDebt_1 = getSystemDebt();

    decreaseSystemDebt(e, amount);

    uint256 systemDebt_2 = getSystemDebt();

    increaseSystemDebt(e, amount);

    uint256 systemDebt_3 = getSystemDebt();

    assert to_mathint(systemDebt_2) == systemDebt_1 - amount 
        <=> e.msg.sender == cdpManagerAddress() 
        || e.msg.sender == borrowerOperationsAddress();
    assert systemDebt_3 == systemDebt_1;
}

/// @notice integrity of increaseSystemCollShares, should increase systemCollShares
rule increaseSystemCollShares_integrity(env e, uint256 amount){
    uint256 _systemCollShares = getSystemCollShares();

    increaseSystemCollShares(e, amount);

    uint256 systemCollShares_ = getSystemCollShares();
    assert to_mathint(systemCollShares_) == _systemCollShares + amount
        <=> e.msg.sender == borrowerOperationsAddress();
}

/// @notice flashLoan integrity
rule flashLoan_integrity(
    env e,
    address receiver,
    address token,
    uint256 amount,
    bytes data
) {
    address feeRecipient = feeRecipientAddress();
    uint256 fee = flashFee( token, amount);
    uint256 balanceBefore = collateralToken.balanceOf(currentContract);
    uint256 feeBalanceBefore = collateralToken.balanceOf(feeRecipient);
    uint256 systemCollShares = getSystemCollShares();
    uint256 oldRate = collateralToken.getPooledEthByShares(10 ^ 18);
    uint256 _counter = flashBorrower.counter();
    
    flashLoan(e,receiver,token,amount,data);

    uint256 balanceAfter = collateralToken.balanceOf(currentContract);
    uint256 sharesAfter = collateralToken.sharesOf(currentContract);
    uint256 feeBalanceAfter = collateralToken.balanceOf(feeRecipient);
    uint256 counter_ = flashBorrower.counter();

    assert feeRecipientAddress() != currentContract => to_mathint(balanceBefore) <= balanceAfter + 2 && to_mathint(balanceBefore) >= balanceAfter - 2;
    assert feeRecipientAddress() != currentContract && feeRecipientAddress() != receiver => feeBalanceBefore + fee <= feeBalanceAfter + 2 && feeBalanceBefore + fee >= feeBalanceAfter - 2
        <=> amount != 0 
        && amount <= maxFlashLoan(token);
    assert balanceAfter >= collateralToken.getPooledEthByShares(systemCollShares);
    assert sharesAfter >= systemCollShares;
    assert oldRate == collateralToken.getPooledEthByShares(10 ^ 18);
    assert _counter + 1 == to_mathint(counter_);
}

/// @notice flashFee integrity should revert at token != collateral and when paused
rule flashFee_integrity(address token, uint256 amount){

    uint256 fee = flashFee(token,amount);
    assert token == collateralToken && !flashLoansPaused()
        <=> to_mathint(fee) == (amount * feeBps()) / MAX_BPS();
}

/// @notice maxFlashLoan should return 0 in certain conditions 
rule maxFlashLoan_integrity(address token) {
    uint256 max = maxFlashLoan(token);
    assert token != collateralToken => max == 0;
    assert flashLoansPaused() => max == 0;
    assert token == collateralToken && !flashLoansPaused() => max == collateralToken.balanceOf(currentContract);
}

/// @notice claimFeeRecipientCollShares should transfer shares to feeRecipient 
rule claimFeeRecipientCollShares_integrity(env e, uint256 shares){

    address feeRecipient = feeRecipientAddress();
    uint256 _feeRecipientCollShares = getFeeRecipientClaimableCollShares();
    uint256 _thisShares = collateralToken.sharesOf(currentContract);
    uint256 _recipientShares = collateralToken.sharesOf(feeRecipient);

    claimFeeRecipientCollShares(e, shares);

    uint256 feeRecipientCollShares_ = getFeeRecipientClaimableCollShares();
    uint256 thisShares_ = collateralToken.sharesOf(currentContract);
    uint256 recipientShares_ = collateralToken.sharesOf(feeRecipient);

    assert to_mathint(feeRecipientCollShares_) == _feeRecipientCollShares - shares + feeTaken;
    assert feeRecipient != currentContract => to_mathint(thisShares_) == _thisShares - shares;
    assert feeRecipient != currentContract => to_mathint(recipientShares_) == _recipientShares + shares;
}

/// @notice sweepToken should transfer other token than collateral to feeRecipientAddress
rule sweepToken_integrity(env e, address token, uint256 amount) {
    uint256 _thisBalance = tokenA.balanceOf(currentContract);
    uint256 _recipientBalance = tokenA.balanceOf(feeRecipientAddress());
    uint256 _feeRecipientCollShares = getFeeRecipientClaimableCollShares();

    sweepToken(e, token, amount);

    uint256 thisBalance_ = tokenA.balanceOf(currentContract);
    uint256 recipientBalance_ = tokenA.balanceOf(feeRecipientAddress());
    uint256 feeRecipientCollShares_ = getFeeRecipientClaimableCollShares();

    assert token == tokenA && feeRecipientAddress() != currentContract => to_mathint(thisBalance_) == _thisBalance - amount;
    assert token == tokenA && feeRecipientAddress() != currentContract => to_mathint(recipientBalance_) == _recipientBalance + amount;
    assert token == collateralToken => _thisBalance == thisBalance_;
    assert to_mathint(feeRecipientCollShares_) == _feeRecipientCollShares + feeTaken;
}

/// @notice setFeeBps should set feeBps to certain number
rule setFeeBps_integrity(env e, uint256 _new){
    uint256 _feeRecipientCollShares = getFeeRecipientClaimableCollShares();
    setFeeBps(e, _new);
    uint256 feeRecipientCollShares_ = getFeeRecipientClaimableCollShares();
    assert to_mathint(_new) == to_mathint(feeBps()) 
        && to_mathint(feeBps()) <= to_mathint(MAX_FEE_BPS());
    assert to_mathint(feeRecipientCollShares_) == _feeRecipientCollShares + feeTaken;
}

/// @notice setFeeRecipientAddress should set feeRecipientAddress to certain address
rule setFeeRecipientAddress_integrity(env e, address _new){
    uint256 _feeRecipientCollShares = getFeeRecipientClaimableCollShares();
    setFeeRecipientAddress(e, _new);
    uint256 feeRecipientCollShares_ = getFeeRecipientClaimableCollShares();
    assert feeRecipientAddress() != 0 && feeRecipientAddress() == _new;
    assert to_mathint(feeRecipientCollShares_) == _feeRecipientCollShares + feeTaken;
}

/// @notice setFlashLoansPaused should set flashLoansPaused
rule setFlashLoansPaused_integrity(env e, bool _new) {

    uint256 _feeRecipientCollShares = getFeeRecipientClaimableCollShares();
    setFlashLoansPaused(e, _new);
    uint256 feeRecipientCollShares_ = getFeeRecipientClaimableCollShares();
    assert flashLoansPaused() == _new;
    assert to_mathint(feeRecipientCollShares_) == _feeRecipientCollShares + feeTaken;
}