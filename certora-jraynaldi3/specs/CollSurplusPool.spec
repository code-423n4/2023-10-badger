import "./sanity.spec";
import "./erc20.spec";


using CollateralTokenTester as collateral;
using DummyERC20A as tokenA;
methods {
    
    function call_isAuthorized(address user, uint32 functionSig) external  returns (bool) envfree;
    function borrowerOperationsAddress() external  returns (address) envfree;

    // collateral methods
    function collateral.balanceOf(address) external returns (uint256) envfree;
    function collateral.sharesOf(address) external returns (uint256) envfree;

    // variable 
    function borrowerOperationsAddress() external returns (address) envfree;
    function cdpManagerAddress() external returns (address) envfree;
    function activePoolAddress() external returns (address) envfree;
    function feeRecipientAddress() external returns (address) envfree;
    function collateral() external returns (address) envfree;
    function getSurplusCollShares(address) external returns (uint256) envfree;
    function getTotalSurplusCollShares() external returns(uint256) envfree;

    // erc20
    function tokenA.balanceOf(address) external returns(uint256) envfree;
}

use rule sanity; 

rule reachability(method f) {
    env e;
    calldataarg args;
    f(e,args);
    satisfy true;
}


rule changeToCollateralBalance(method f) {
    uint256 before = collateral.balanceOf(currentContract);
    env e;
    calldataarg args;
    f(e,args);
    uint256 after = collateral.balanceOf(currentContract);
    assert after < before =>  
        ( call_isAuthorized(e.msg.sender, f.selector) || e.msg.sender == borrowerOperationsAddress()); 
}

/***********************    PARTICIPANT  ************************/

/***********************    HIGH LEVEL   ************************/

/// @notice immutable variable cannot changed
rule immutableVariable(env e, method f, calldataarg args){
    address _borrowerOperationsAddress = borrowerOperationsAddress();
    address _cdpManagerAddress = cdpManagerAddress();
    address _activePoolAddress = activePoolAddress();
    address _feeRecipientAddress = feeRecipientAddress(); 
    address _collateral = collateral(); 

    f(e,args);

    address borrowerOperationsAddress_ = borrowerOperationsAddress();
    address cdpManagerAddress_ = cdpManagerAddress();
    address activePoolAddress_ = activePoolAddress();
    address feeRecipientAddress_ = feeRecipientAddress(); 
    address collateral_ = collateral(); 
    assert borrowerOperationsAddress_ == _borrowerOperationsAddress; 
    assert cdpManagerAddress_ == _cdpManagerAddress; 
    assert activePoolAddress_ == _activePoolAddress; 
    assert feeRecipientAddress_ == _feeRecipientAddress; 
    assert collateral_ == _collateral; 
}

/// @notice some function and variable changes should handled by borrowerOperation only 
rule borrowerOperationsOnly(env e, method f, calldataarg args, address account) {
    uint256 balanceBefore = getSurplusCollShares(account);
    uint256 _totalSurplusCollShares = getTotalSurplusCollShares();

    f(e,args);

    uint256 balanceAfter = getSurplusCollShares(account);
    uint256 totalSurplusCollShares_ = getTotalSurplusCollShares();

    assert balanceBefore != 0 && balanceAfter == 0 => e.msg.sender == borrowerOperationsAddress() && f.selector == sig:claimSurplusCollShares(address).selector;
    assert _totalSurplusCollShares > totalSurplusCollShares_ => e.msg.sender == borrowerOperationsAddress() && f.selector == sig:claimSurplusCollShares(address).selector;
}

/// @notice some function and variable changes should handled by cdpManager only
rule cdpManagerOnly(env e, method f, calldataarg args, address account) {
    uint256 balancesBefore = getSurplusCollShares(account);

    f(e,args);

    uint256 balancesAfter = getSurplusCollShares(account);
    assert balancesBefore < balancesAfter => e.msg.sender == cdpManagerAddress() && f.selector == sig:increaseSurplusCollShares(address, uint256).selector;
}

/// @notice some function and variable changes should handled by activePool only
rule activePoolOnly(env e, method f, calldataarg args) {
    
    uint256 _totalSurplusCollShares = getTotalSurplusCollShares();

    f(e,args); 

    uint256 totalSurplusCollShares_ = getTotalSurplusCollShares();
    assert _totalSurplusCollShares < totalSurplusCollShares_ => e.msg.sender == activePoolAddress() && f.selector == sig:increaseTotalSurplusCollShares(uint256).selector;
}


/***********************    UNIT TEST   ************************/
/// @notice increaseSurplusCollShares should increase balances[account] by amount
rule increaseSurplusCollShares_integrity(
    env e,
    address account,
    uint256 amount
) {

    uint256 balancesBefore = getSurplusCollShares(account);

    increaseSurplusCollShares(e, account, amount);

    uint256 balancesAfter = getSurplusCollShares(account);
    assert to_mathint(balancesAfter) == balancesBefore + amount;
}

/// @notice claimSurplusCollShares should make balances[account] to 0 
/// decrease totalSurplusCollShares 
/// transfer shares to account
rule claimSurplusCollShares_integrity(
    env e,
    address account
) {

    uint256 balancesBefore = getSurplusCollShares(account);
    uint256 _totalSurplusCollShares = getTotalSurplusCollShares();
    uint256 sharesBefore = collateral.sharesOf(account);

    claimSurplusCollShares(e, account);

    uint256 balancesAfter = getSurplusCollShares(account);
    uint256 totalSurplusCollShares_ = getTotalSurplusCollShares();
    uint256 sharesAfter = collateral.sharesOf(account);

    assert balancesAfter == 0;
    assert to_mathint(_totalSurplusCollShares) == totalSurplusCollShares_ + balancesBefore 
        <=> _totalSurplusCollShares >= balancesBefore;
    assert account != currentContract => to_mathint(sharesAfter) == sharesBefore + balancesBefore;
}

/// @notice claimSurplusCollShares have several revert condition that should be checked
rule claimSurplusCollShares_revertion(
    env e,
    address account
) {
    uint256 balancesBefore = getSurplusCollShares(account);
    uint256 _totalSurplusCollShares = getTotalSurplusCollShares();

    claimSurplusCollShares@withrevert(e, account);
    assert balancesBefore == 0 => lastReverted;
    assert _totalSurplusCollShares < balancesBefore => lastReverted;
}

/// @notice increaseTotalSurplusCollShares should increase totalSurplusCollShares by amount 
rule increaseTotalSurplusCollShares_integrity(
    env e,
    uint256 value
) {
    uint256 _totalSurplusCollShares = getTotalSurplusCollShares();

    increaseTotalSurplusCollShares(e, value);

    uint256 totalSurplusCollShares_ = getTotalSurplusCollShares();
    assert to_mathint(totalSurplusCollShares_) == _totalSurplusCollShares + value;
}

/// @notice sweepToken should able to transfer token except collateral to feeRecipient
rule sweepToken_integrity(
    env e,
    address token,
    uint256 amount
) {
    require token == tokenA;
    require feeRecipientAddress() != currentContract;
    uint256 contractBalance = tokenA.balanceOf(currentContract);
    uint256 _feeRecipientBalance = tokenA.balanceOf(feeRecipientAddress());
    
    sweepToken(e, token, amount);

    uint256 feeRecipientBalance_ = tokenA.balanceOf(feeRecipientAddress());
    assert to_mathint(feeRecipientBalance_) == _feeRecipientBalance + amount 
        <=> token != collateral()
        && amount <= contractBalance;
}

/// @notice sweepToken have several Revert condition that have to check
rule sweepToken_revertion(
    env e,
    address token,
    uint256 amount
) {
    require token == tokenA;
    require feeRecipientAddress() != currentContract;
    uint256 contractBalance = tokenA.balanceOf(currentContract);
    address collateralAddr = collateral();
    
    sweepToken@withrevert(e, token, amount);

    assert token == collateralAddr => lastReverted;
    assert amount > contractBalance => lastReverted;
}

/// @notice sweepToken have several returns to check
rule sweepToken_sanity(
    env e ,
    address token, 
    uint256 amount
) {
    require token == tokenA;
    require feeRecipientAddress() != currentContract;
    uint256 contractBalance = tokenA.balanceOf(currentContract);
    address collateralAddr = collateral();
    
    sweepToken(e, token, amount);

    satisfy (amount < contractBalance);
}