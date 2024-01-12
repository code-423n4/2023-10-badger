import "./sanity.spec";
import "./erc20.spec";


using CollateralTokenTester as collateral;
methods {
    
    function call_isAuthorized(address user, uint32 functionSig) external  returns (bool) envfree;
    function borrowerOperationsAddress() external  returns (address) envfree;

    // collateral methods
    function collateral.balanceOf(address) external returns (uint256) envfree;
    function collateral.sharesOf(address) external returns (uint256) envfree;
}

rule mutCollSurplusPool(address token,uint256 amount){
    env e;
    address source;
    uint256 sourceBalanceBefore = tokenBalanceOf(e,token,source);

    sweepToken(e,token,amount);

    assert tokenBalanceOf(e,token,source) < sourceBalanceBefore => source == currentContract;
}

rule callingClaimTwice(env e,address account){
    claimSurplusCollShares(e, account);
    claimSurplusCollShares@withrevert(e, account);
    
    assert lastReverted;
}

rule collateralOnlyIncreases(env e, method f){
    
    uint256 balanceBefore = collateral.balanceOf(currentContract);
    calldataarg args;
    f(e,args);
    uint256 balanceAfter = collateral.balanceOf(currentContract);
   
   assert !(balanceAfter >= balanceBefore) => f.selector == sig:claimSurplusCollShares(address).selector;
}

invariant surplusColShares(address account, env e)
    getTotalSurplusCollShares(e) >= getSurplusCollShares(e,account)
filtered { f -> !f.isView && !f.isFallback &&
           f.selector != sig:increaseSurplusCollShares(address,uint256).selector &&
           f.selector != sig:claimSurplusCollShares(address).selector}

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
