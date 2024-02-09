import "./sanity.spec";
import "./erc20.spec";

using CollateralTokenTester as collateralToken;


methods {
    function _.increaseTotalSurplusCollShares(uint256) external => DISPATCHER(true);
    function _.onFlashLoan(address, address, uint256, uint256, bytes) external => DISPATCHER(true);
    function getSystemCollShares() external  returns (uint256) envfree;
    function CollateralTokenTester.balanceOf(address)  external  returns (uint256) envfree;
}


rule mutActivePool(address account,uint256 shares){
    env e;

    uint256 systemCollShares_before = getSystemCollShares();
    
    transferSystemCollShares(e, account, shares);

    assert shares > 0 => getSystemCollShares() < systemCollShares_before;
}

rule collateralOnlyIncreases(env e, method f)
filtered { f -> !f.isView && !f.isFallback &&
           f.selector != sig:transferSystemCollSharesAndLiquidatorReward(address,uint256,uint256).selector &&
           f.selector != sig:claimFeeRecipientCollShares(uint256).selector &&
           f.selector != sig:transferSystemCollShares(address,uint256).selector}
{
    uint256 balanceBefore = collateralToken.balanceOf(currentContract);
    calldataarg args;
    f(e,args);
    uint256 balanceAfter = collateralToken.balanceOf(currentContract);
   
   assert balanceAfter >= balanceBefore;
}
rule rateStaysFixed(env e, method f){
    
    uint256 rateOld = collateralToken.getPooledEthByShares(e,DECIMAL_PRECISION(e));
    calldataarg args;
    f(e,args);
    uint256 rateNew = collateralToken.getPooledEthByShares(e,DECIMAL_PRECISION(e));
   
   assert rateNew == rateOld;
}

invariant require_1(env e)
    collateralToken.balanceOf(currentContract) >= collateralToken.getPooledEthByShares(e,getSystemCollShares());

invariant require_2(env e)
    collateralToken.sharesOf(e,currentContract) >= getSystemCollShares()
filtered { f -> !f.isView && !f.isFallback &&
           f.selector != sig:transferSystemCollSharesAndLiquidatorReward(address,uint256,uint256).selector &&
           f.selector != sig:claimFeeRecipientCollShares(uint256).selector &&
           f.selector != sig:increaseSystemCollShares(uint256).selector}


use rule sanity;


