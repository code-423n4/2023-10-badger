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
