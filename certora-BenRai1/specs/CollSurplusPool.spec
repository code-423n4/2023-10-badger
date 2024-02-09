import "./sanity.spec";
import "./erc20.spec";

using CdpManager as CdpManager;
using CollateralTokenTester as Collateral;
using DummyERC20A as ERC20A;
using DummyERC20B as ERC20B;


using CollateralTokenTester as collateral;
methods {
    
    function call_isAuthorized(address user, bytes4 functionSig) external  returns (bool) envfree;
    function borrowerOperationsAddress() external  returns (address) envfree;

    // collateral methods
    function collateral.balanceOf(address) external returns (uint256) envfree;
    function collateral.sharesOf(address) external returns (uint256) envfree;
}


/// -------------------------------------  RULES OK -------------------------------------


    rule sweepTokenWorks(){

        env e;
        uint256 amount;
        address feeRecipientAddress = feeRecipientAddress(e);
        require(feeRecipientAddress != currentContract);
        require(ERC20A != ERC20B);

        uint256 balanceTokenABefore = ERC20A.balanceOf(e, currentContract);
        uint256 balanceTokenBBefore = ERC20B.balanceOf(e, currentContract);
        uint256 balanceTokenABeforeRecipient = ERC20A.balanceOf(e, feeRecipientAddress);

        sweepToken(e, ERC20A, amount);

        uint256 balanceTokenAAfter = ERC20A.balanceOf(e, currentContract);
        uint256 balanceTokenBAfter = ERC20B.balanceOf(e, currentContract);
        uint256 balanceTokenAAfterRecipient = ERC20A.balanceOf(e, feeRecipientAddress);

        bytes4 functionSig = to_bytes4(sig:sweepToken(address,uint256).selector);
        // bytes4 functionSig = to_bytes4(e.msg.sig);
        

        assert(call_isAuthorized(e.msg.sender, functionSig) == true, "Caller not authorized");
        assert(ERC20A != collateral(e), "Collateral should not be swept");
        assert(amount <= balanceTokenABefore, "Cant sweep more than balanceTokenABefore");
        assert(to_mathint(balanceTokenAAfter) == balanceTokenABefore - amount, "amount was not swept from Pool");
        assert(to_mathint(balanceTokenAAfterRecipient) == balanceTokenABeforeRecipient + amount, "Recipient did not get amount");
    }

    rule claimSurplusCollSharesWorks(){
        env e;
        address user1;
        address user2;
        require(user1 != user2);
        require(user1 != currentContract);
        require(user2 != currentContract);
        uint256 balanceUser1Before = getSurplusCollShares(e, user1);
        uint256 balanceUser2Before = getSurplusCollShares(e, user2);
        uint256 sharesCollateralUser1Before = collateral.sharesOf(user1);
        uint256 sharesCollateralUser2Before = collateral.sharesOf(user2);
        uint256 sharesCollateralThisContractBefore = collateral.sharesOf(currentContract);
        uint256 totalSurplusCollSharesBefore = getTotalSurplusCollShares(e);


        claimSurplusCollShares(e, user1);

        uint256 balanceUser1After = getSurplusCollShares(e, user1);
        uint256 balanceUser2After = getSurplusCollShares(e, user2);
        uint256 sharesCollateralUser1After = collateral.sharesOf(user1);
        uint256 sharesCollateralUser2After = collateral.sharesOf(user2);
        uint256 sharesCollateralThisContractAfter = collateral.sharesOf(currentContract);
        uint256 totalSurplusCollSharesAfter = getTotalSurplusCollShares(e);

        assert(balanceUser1After == 0, "Balance for user1 is not 0");
        assert(balanceUser2After == balanceUser2Before, "Balance for user2 changed");
        assert(to_mathint(sharesCollateralUser1After) == sharesCollateralUser1Before + balanceUser1Before, "Collateral Shares for user1 did not change propperly");
        assert(sharesCollateralUser2After == sharesCollateralUser2Before , "Collateral Balance for user2 changed");
        assert(to_mathint(sharesCollateralThisContractAfter) == sharesCollateralThisContractBefore - balanceUser1Before , "Collateral Balance for this conract did not change propperly");
        assert(to_mathint(totalSurplusCollSharesAfter) == totalSurplusCollSharesBefore - balanceUser1Before , "totalSurplusCollSharesBefore did not change propperly");
        assert(e.msg.sender == borrowerOperationsAddress(e), "Caller is not borrowerOperationsAddress");
        assert(balanceUser1Before <= totalSurplusCollSharesBefore, "Claimed amount is to big");
        assert(balanceUser1Before > 0, "0 can not be claimed");
    }

    rule increaseTotalSurplusCollSharesWorks(){
        env e;
        address user;
        address user2;
        require(user != user2);
        uint256 amount;

        uint256 sharesUserBefore = getSurplusCollShares(e, user);
        uint256 sharesUser2Before = getSurplusCollShares(e, user2);

        increaseSurplusCollShares(e, user, amount);

        uint256 sharesUserAfter = getSurplusCollShares(e, user);
        uint256 sharesUser2After = getSurplusCollShares(e, user2);

        assert(e.msg.sender == cdpManagerAddress(e), "Caller not cdpManager");
        assert(to_mathint(sharesUserAfter) == sharesUserBefore + amount, "Shares of user did not increase by amount");
        assert(sharesUser2After == sharesUser2Before, "Shares of user2 changed");
    }

    rule changesUserBalances(method f) filtered{f -> !f.isView}{
        env e;
        calldataarg arg;
        address user;

        uint256 balaceBefore = getSurplusCollShares(e, user);

        f(e,arg);

        uint256 balaceAfter = getSurplusCollShares(e, user);

        assert(balaceAfter != balaceBefore => 
        f.selector ==sig:increaseSurplusCollShares(address,uint256).selector ||
        f.selector ==sig:claimSurplusCollShares(address).selector, "Wrong function is changing the user balaces");

    }

    rule changesTotalSurplusCollShares(method f) filtered {f-> !f.isView}{
        env e;
        calldataarg arg;
        uint256 totalSurplusCollSharesBefore = getTotalSurplusCollShares(e);

        f(e, arg);

        uint256 totalSurplusCollSharesAfter = getTotalSurplusCollShares(e);

        assert(totalSurplusCollSharesAfter != totalSurplusCollSharesBefore => 
        f.selector == sig:increaseSurplusCollShares(address,uint256).selector ||
        f.selector == sig:claimSurplusCollShares(address).selector ||   
        f.selector == sig:increaseTotalSurplusCollShares(uint256).selector, "Wrong functions are changing totalSurplusCollShares");
    }

    rule getTotalSurplusCollSharesWorks(){
        env e;
        uint256 amount = getTotalSurplusCollShares(e);

        assert( amount == getTotalSurplusCollSharesHarness(e), "getTotalSurplusCollShares does not work");
    }

    rule getSurplusCollSharesWorks(){
        env e;
        address user;

        uint256 amount = getSurplusCollShares(e, user);

        assert( amount == getSurplusCollSharesHarness(e, user), "getTotalSurplusCollShares does not work");
    }

/// -------------------------------------  OLD RULES -------------------------------------


    rule changeToCollateralBalance(method f) {
        uint256 before = collateral.balanceOf(currentContract);
        env e;
        calldataarg args;
        f(e,args);
        uint256 after = collateral.balanceOf(currentContract);
        assert after < before =>  
            ( call_isAuthorized(e.msg.sender, to_bytes4(f.selector)) || e.msg.sender == borrowerOperationsAddress()); 
    }

    rule reachability(method f) {
        env e;
        calldataarg args;
        f(e,args);
        satisfy true;
    }
