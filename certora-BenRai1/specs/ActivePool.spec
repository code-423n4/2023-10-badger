import "./sanity.spec";
import "./erc20.spec";

using CdpManager as CdpManager;
using BorrowerOperations as BorrowerOp;
using CollSurplusPool as CollSurplusPool;
using DummyERC20A as ERC20A;
using DummyERC20B as ERC20B;
// using EBTCToken as Collateral;
using CollateralTokenTester as Collateral;
using ActivePoolHarness as ActivePool;
using MockFlashBorrower as FlashloanBorrower;



methods {
    function _.increaseTotalSurplusCollShares(uint256) external => DISPATCHER(true);
    function _.onFlashLoan(address, address, uint256, uint256, bytes) external => DISPATCHER(true);
   
    // 
}


use rule sanity;




/// -------------------------------------  RULES OK -------------------------------------

    rule claimFeeRecipientCollSharesWorks(){

        env e; 
        uint256 amount; 
        require(amount >0);
        address feeRecipientAddress = feeRecipientAddress(e);
        require(feeRecipientAddress != ActivePool);

        address collateral = collateral(e);
        require(collateral == Collateral);

        uint256 feeRecipientCollSharesBefore = getFeeRecipientClaimableCollShares(e);
        uint256 sharesBeforePool = Collateral.sharesOf(e, ActivePool);
        uint256 sharesBeforeRecipient = Collateral.sharesOf(e, feeRecipientAddress);

        claimFeeRecipientCollShares(e, amount);

        uint256 feeRecipientCollSharesAfter = getFeeRecipientClaimableCollShares(e);
        uint256 sharesAfterPool = Collateral.sharesOf(e, ActivePool);
        uint256 sharesAfterRecipient = Collateral.sharesOf(e, feeRecipientAddress);

        assert(amount <= sharesBeforePool, "Amount bigger than pool shares");
        // assert(amount <= feeRecipientCollSharesBefore, "Amount bigger than feeRecipientCollSharesBefore");
        // assert(feeRecipientCollSharesAfter < feeRecipientCollSharesBefore, "feeRecipientCollShares were not reduced");
        assert(to_mathint(sharesAfterPool) == sharesBeforePool - amount, "Pool shares was not reduced by amount");
        assert(to_mathint(sharesAfterRecipient) == sharesBeforeRecipient + amount, "Recipient did not get amount");
    }

    rule flashLoanWorks(){
        env e;
        address token;
        uint256 amount;
        bytes data;

        uint256 poolBalanceBefore = Collateral.balanceOf(e, ActivePool);
        uint256 feeRecipientBalanceBefore = Collateral.balanceOf(e, feeRecipientAddress(e));
        require(FlashloanBorrower != feeRecipientAddress(e));
        uint256 fee = flashFee(e, token, amount);
        uint256 oldRate = Collateral.getPooledEthByShares(e, DECIMAL_PRECISION(e));
        uint256 systemCollShares = getSystemCollShares(e);
        require(ActivePool != feeRecipientAddress(e));


        flashLoan(e, FlashloanBorrower, token, amount, data);

        uint256 poolBalanceAfter = Collateral.balanceOf(e, ActivePool);
        uint256 feeRecipientBalanceAfter = Collateral.balanceOf(e, feeRecipientAddress(e));
        uint256 newRate = Collateral.getPooledEthByShares(e, DECIMAL_PRECISION(e));

        assert(newRate == oldRate, "Rate changed");
        assert(token == Collateral, "Flashloan works for other tokens than the collateral");
        assert(amount <= Collateral.balanceOf(e, ActivePool), "Amount bigger than PoolBalance");
        assert(amount != 0, "Amount = 0");
        assert(amount <= Collateral.balanceOf(e, ActivePool), "Amount is bigger than the balance of the pool");
        assert(poolBalanceAfter  >= poolBalanceBefore, "Poolbalance has decreased");
        assert(to_mathint(feeRecipientBalanceAfter) >= feeRecipientBalanceBefore + fee-1, "Fees did not go to the feeRecipient"); //compensating for rounding error 
        assert(Collateral.balanceOf(e, ActivePool) >= Collateral.getPooledEthByShares(e, systemCollShares), "Check1 failed");
        assert(Collateral.sharesOf(e, ActivePool) >= systemCollShares, "Check2 failed");
        assert(Collateral.getPooledEthByShares(e, DECIMAL_PRECISION(e)) == oldRate, "Check3 failed");
    }


    rule changesFeeRecipientCollShares(method f) filtered{f -> !f.isView
        }{
        env e;
        calldataarg arg;
        mathint feeRecipientCollSharesBefore = getFeeRecipientClaimableCollShares(e);
        f(e,arg);
        mathint feeRecipientCollSharesAfter = getFeeRecipientClaimableCollShares(e);

        assert (feeRecipientCollSharesAfter != feeRecipientCollSharesBefore => 
        f.selector == sig:allocateSystemCollSharesToFeeRecipient(uint256).selector ||
        f.selector == sig:setFeeBps(uint256).selector ||
        f.selector == sig:setFeeRecipientAddress(address).selector ||
        f.selector == sig:claimFeeRecipientCollShares(uint256).selector ||
        f.selector == sig:setFlashLoansPaused(bool).selector ||
        f.selector == sig:sweepToken(address,uint256).selector ||
        f.selector == sig:claimFeeRecipientCollShares(uint256).selector,
        "FeeRecipientCollShares changed unexpectedly");
    }

    rule changesSystemCollShares(method f) filtered{f -> !f.isView
        }{
        env e;
        calldataarg arg;
        mathint SystemCollSharesBefore = getSystemCollShares(e);
        f(e,arg);
        mathint SystemCollSharesAfter = getSystemCollShares(e);

        assert (SystemCollSharesBefore != SystemCollSharesAfter => 
        f.selector == sig:transferSystemCollShares(address,uint256).selector ||
        f.selector == sig:transferSystemCollSharesAndLiquidatorReward(address,uint256,uint256).selector ||
        f.selector == sig:allocateSystemCollSharesToFeeRecipient(uint256).selector ||
        f.selector == sig:setFeeBps(uint256).selector ||
        f.selector == sig:setFeeRecipientAddress(address).selector ||
        f.selector == sig:claimFeeRecipientCollShares(uint256).selector ||
        f.selector == sig:setFlashLoansPaused(bool).selector ||
        f.selector == sig:sweepToken(address,uint256).selector ||
        f.selector == sig:increaseSystemCollShares(uint256).selector,
        "SystemCollShares changed unexpectedly");
    }

    rule transferSystemCollSharesAndLiquidatorRewardWorks(){
        env e;
        address account;
        require(account != ActivePool);
        uint256 shares;
        uint256 liquidatorRewardShares;
        uint256 systemCollSharesBefore = getSystemCollShares(e);

        
        uint256 poolSharesBefore = Collateral.sharesOf(e, ActivePool);
        uint256 accountSharesBefore = Collateral.sharesOf(e, account);
        uint256 totalSurplusCollSharesBefore = CollSurplusPool.getTotalSurplusCollShares(e);
        require(totalSurplusCollSharesBefore + shares <= to_mathint(max_uint256));


        transferSystemCollSharesAndLiquidatorReward(e, account, shares,liquidatorRewardShares);

        uint256 systemCollSharesAfter = getSystemCollShares(e);
        uint256 poolSharesAfter = Collateral.sharesOf(e, ActivePool);
        uint256 accountSharesAfter = Collateral.sharesOf(e, account);
        uint256 totalSurplusCollSharesAfter = CollSurplusPool.getTotalSurplusCollShares(e);


        assert(e.msg.sender == BorrowerOp || e.msg.sender == CdpManager, "Other caller than BorrowerOp or CDP Manager");
        assert(systemCollSharesBefore >= shares, "systemCollSharesBefore smaller than shares");
        assert(to_mathint(systemCollSharesAfter) == systemCollSharesBefore - shares, "systemCollShares are not updated propperly");
        assert(to_mathint(poolSharesAfter) == poolSharesBefore - shares - liquidatorRewardShares, "poolShares is not updated propperly");
        assert(to_mathint(accountSharesAfter) == accountSharesBefore + shares + liquidatorRewardShares, "accountSharesAfter are not updated propperly");
        assert(account == collSurplusPoolAddress(e) => to_mathint(totalSurplusCollSharesAfter) == totalSurplusCollSharesBefore + shares + liquidatorRewardShares, "totalSurplusCollShares are not updated propperly");

    }

    rule transferSystemCollSharesWorks(){
        env e;
        address account;
        require(account != ActivePool);
        uint256 shares;
        uint256 systemCollSharesBefore = getSystemCollShares(e);
        uint256 poolSharesBefore = Collateral.sharesOf(e, ActivePool);
        uint256 accountSharesBefore = Collateral.sharesOf(e, account);
        uint256 totalSurplusCollSharesBefore = CollSurplusPool.getTotalSurplusCollShares(e);
        require(totalSurplusCollSharesBefore + shares <= to_mathint(max_uint256));


        transferSystemCollShares(e, account, shares);

        uint256 systemCollSharesAfter = getSystemCollShares(e);
        uint256 poolSharesAfter = Collateral.sharesOf(e, ActivePool);
        uint256 accountSharesAfter = Collateral.sharesOf(e, account);
        uint256 totalSurplusCollSharesAfter = CollSurplusPool.getTotalSurplusCollShares(e);


        assert(e.msg.sender == BorrowerOp || e.msg.sender == CdpManager, "Other caller than BorrowerOp or CDP Manager");
        assert(systemCollSharesBefore >= shares, "systemCollSharesBefore smaller than shares");
        assert(to_mathint(systemCollSharesAfter) == systemCollSharesBefore - shares, "systemCollShares are not updated propperly");
        assert(to_mathint(poolSharesAfter) == poolSharesBefore - shares, "poolShares is not updated propperly");
        assert(to_mathint(accountSharesAfter) == accountSharesBefore + shares, "accountSharesAfter are not updated propperly");
        assert(account == collSurplusPoolAddress(e) => to_mathint(totalSurplusCollSharesAfter) == totalSurplusCollSharesBefore + shares, "totalSurplusCollShares are not updated propperly");

    }

    rule getFeeRecipientClaimableCollSharesWorks(){
        env e;

        assert(getFeeRecipientClaimableCollShares(e) == getFeeRecipientClaimableCollSharesHarness(e), "getFeeRecipientClaimableCollShares does not work");
    }

    rule getSystemDebtWorks(){
        env e;

        assert(getSystemDebt(e) == getSystemDebtHarness(e), "getSystemDebt does not work");
    }

    rule getSystemCollSharesWorks(){
        env e;

        assert(getSystemCollShares(e) == getSystemCollSharesHarness(e), "getSystemCollShares does not work");
    }

    rule allocateSystemCollSharesToFeeRecipientWorks(){
        env e;
        uint256 _shares;
        uint256 systemCollSharesBefore = getSystemCollShares(e);
        uint256 feeRecipientCollSharesBefore = getFeeRecipientClaimableCollShares(e);

        allocateSystemCollSharesToFeeRecipient(e, _shares);

        uint256 systemCollSharesAfter = getSystemCollShares(e);
        uint256 feeRecipientCollSharesAfter = getFeeRecipientClaimableCollShares(e);
        
        assert(e.msg.sender == CdpManager, "Other caller than CDP Manager");
        assert(systemCollSharesBefore >= _shares, "systemCollSharesBefore smaller than _shares");
        assert(to_mathint(systemCollSharesAfter) == systemCollSharesBefore - _shares, "systemCollShares are not updated propperly");
        assert(to_mathint(feeRecipientCollSharesAfter) == feeRecipientCollSharesBefore + _shares, "feeRecipientCollSharesBefore are not updated propperly");
    }

    rule increaseSystemDebtWorks(){
        env e;
        uint256 _value;
        uint256 systemDebtBefore = getSystemDebt(e);

        increaseSystemDebt(e, _value);

        uint256 systemDebtAfter = getSystemDebt(e);

        assert(e.msg.sender == BorrowerOp || e.msg.sender == CdpManager, "Other caller than BorrowerOp or CDP Manager");
        assert(to_mathint(systemDebtAfter) == systemDebtBefore + _value, "Did not increase systemDebt by _value");
    }

    rule decreaseSystemDebtWorks(){
        env e;
        uint256 _value;
        uint256 systemDebtBefore = getSystemDebt(e);

        decreaseSystemDebt(e, _value);

        uint256 systemDebtAfter = getSystemDebt(e);

        assert(e.msg.sender == BorrowerOp || e.msg.sender == CdpManager, "Other caller than BorrowerOp or CDP Manager");
        assert(to_mathint(systemDebtAfter) == systemDebtBefore - _value, "Did not increase systemDebt by _value");
    }

    rule increaseSystemCollSharesWorks(){

        env e;
        uint256 _value;
        uint256 systemCollSharesBefore = getSystemCollShares(e);

        increaseSystemCollShares(e, _value);

        uint256 systemCollSharesAfter = getSystemCollShares(e);

        assert(e.msg.sender == BorrowerOp, "Other caller than BorrowerOp");
        assert(to_mathint(systemCollSharesAfter) == systemCollSharesBefore + _value, "Did not increase systemCollShares by _value");

    }

    rule maxFlashLoanWorks(){

        env e;
        address token;

        uint256 maxFlashLoan = maxFlashLoan(e, token);

        address collateral = collateral(e);

        require(collateral == Collateral);

        assert(token == Collateral && flashLoansPaused(e) == false => maxFlashLoan == Collateral.balanceOf(e, ActivePool), "Error Collateral Flashloan when not paused");
        assert(token == Collateral && flashLoansPaused(e) == true => maxFlashLoan == 0, "Error Collateral Flashloan when paused");
        assert(token != Collateral => maxFlashLoan == 0, "Error flashloan not collateral");
        
    }

    rule flashFeeWorks(){

        env e;

        address token;
        uint256 amount;

        uint256 flashFee = flashFee(e, token, amount);

        assert(token == Collateral, "Works also for non collateral tokens");
        assert(flashLoansPaused(e) == false, "Works when paused");
        assert( to_mathint(flashFee) == (amount * feeBps(e))/ MAX_BPS(e), "Fee is calculated wrong");
    }

    rule functionsNeedAuth(method f) filtered{f -> 
      f.selector ==sig:claimFeeRecipientCollShares(uint256).selector ||
     f.selector ==sig:sweepToken(address,uint256).selector ||
     f.selector ==sig:setFeeRecipientAddress(address).selector ||
     f.selector ==sig:setFeeBps(uint256).selector ||
     f.selector ==sig:setFlashLoansPaused(bool).selector 
        }{
        env e;
        calldataarg arg;
        f(e,arg);
        bytes4 functionSig = to_bytes4(f.selector);
        assert (checkAuth(e, e.msg.sender, functionSig),
        "Functions can be called without auth");
    }

    rule setFlashLoansPausedWorks(){

        env e;
        bool _paused;

        setFlashLoansPaused(e, _paused);

        assert(flashLoansPaused(e) == _paused, "FlashLoansPaused does not work");
    }

    rule setFeeBpsWorks(){

        env e;
        uint256 _newFee;

        setFeeBps(e, _newFee);

        assert(to_mathint(feeBps(e)) <= to_mathint(MAX_FEE_BPS(e)), "FeeBps to high");
        assert(to_mathint(feeBps(e)) == to_mathint(_newFee), "setFeeBps does not work");
    }

    rule setFeeRecipientAddressWorks(){

        env e;
        address _feeRecipientAddress;

        setFeeRecipientAddress(e, _feeRecipientAddress);

        assert(feeRecipientAddress(e) == _feeRecipientAddress, "setFeeRecipientAddress set wrong address");
        assert(feeRecipientAddress(e) != 0, "feeRecipientAddress is address(0)");
    }

    rule sweepTokenWorks(){

        env e;
        uint256 amount;
        address feeRecipientAddress = feeRecipientAddress(e);
        require(feeRecipientAddress != ActivePool);
        require(ERC20A != ERC20B);

        uint256 balanceTokenABefore = ERC20A.balanceOf(e, ActivePool);
        uint256 balanceTokenBBefore = ERC20B.balanceOf(e, ActivePool);
        uint256 balanceTokenABeforeRecipient = ERC20A.balanceOf(e, feeRecipientAddress);

        sweepToken(e, ERC20A, amount);

        uint256 balanceTokenAAfter = ERC20A.balanceOf(e, ActivePool);
        uint256 balanceTokenBAfter = ERC20B.balanceOf(e, ActivePool);
        uint256 balanceTokenAAfterRecipient = ERC20A.balanceOf(e, feeRecipientAddress);

        assert(ERC20A != Collateral, "Collateral should not be swept");
        assert(amount <= balanceTokenABefore, "Cant sweep more than balanceTokenABefore");
        assert(to_mathint(balanceTokenAAfter) == to_mathint(balanceTokenABefore - amount), "amount was not swept from Pool");
        assert(to_mathint(balanceTokenAAfterRecipient) == balanceTokenABeforeRecipient + amount, "Recipient did not get amount");
    }

    rule changesTotalSurplusCollShares(method f) filtered{f -> !f.isView
        }{
        env e;
        calldataarg arg;

        address CollSurplusPoolAddress = collSurplusPoolAddress(e);
        require(CollSurplusPoolAddress == CollSurplusPool);
        mathint valueBefore = CollSurplusPool.getTotalSurplusCollShares(e);
        f(e,arg);
        mathint valueAfter = CollSurplusPool.getTotalSurplusCollShares(e);

        assert (valueBefore != valueAfter => 
        f.selector == sig:transferSystemCollShares(address,uint256).selector ||
        f.selector == sig:transferSystemCollSharesAndLiquidatorReward(address,uint256,uint256).selector,
        "TotalSurplusCollShares changed unexpectedly");
    }
    
    rule changesFeeRecipientAddress(method f) filtered{f -> !f.isView
        }{
        env e;
        calldataarg arg;
        
        address valueBefore = feeRecipientAddress(e);
        f(e,arg);
        address valueAfter = feeRecipientAddress(e);

        assert (valueBefore != valueAfter => 
        f.selector == sig:setFeeRecipientAddress(address).selector,
        "feeRecipientAddress changed unexpectedly");
    }

    rule changesFeeBps(method f) filtered{f -> !f.isView
        }{
        env e;
        calldataarg arg;
        
        mathint valueBefore = feeBps(e);
        f(e,arg);
        mathint valueAfter = feeBps(e);

        assert (valueBefore != valueAfter => 
        f.selector == sig:setFeeBps(uint256).selector,
        "feeBps changed unexpectedly");
    }

    rule changesFlashloanPaused(method f) filtered{f -> !f.isView
        }{
        env e;
        calldataarg arg;
        
        bool valueBefore = flashLoansPaused(e);
        f(e,arg);
        bool valueAfter = flashLoansPaused(e);

        assert (valueBefore != valueAfter => 
        f.selector == sig:setFlashLoansPaused(bool).selector,
        "flashLoansPaused changed unexpectedly");
    }

    rule changesSystemDebt(method f) filtered{f -> !f.isView
        }{
        env e;
        calldataarg arg;
        mathint SystemDebtBefore = getSystemDebt(e);
        f(e,arg);
        mathint SystemDebtAfter = getSystemDebt(e);

        assert (SystemDebtBefore != SystemDebtAfter => 
        f.selector == sig:increaseSystemDebt(uint256).selector ||
        f.selector == sig:decreaseSystemDebt(uint256).selector,
        "SystemDebt changed unexpectedly");
    }

    rule onlyBorrowerOpOrCDPManager(method f) filtered{f -> 
        f.selector == sig:transferSystemCollShares(address,uint256).selector ||
        f.selector == sig:transferSystemCollSharesAndLiquidatorReward(address,uint256,uint256).selector ||
        f.selector == sig:increaseSystemDebt(uint256).selector||
        f.selector == sig:decreaseSystemDebt(uint256).selector
        
        }{
        env e;
        calldataarg arg;
        address borrowerOperationAddress = borrowerOperationsAddress(e);
        require(borrowerOperationAddress == BorrowerOp);
        address cdpManagerAddress = cdpManagerAddress(e);
        require(cdpManagerAddress == CdpManager);

        f(e,arg);

        assert (e.msg.sender == borrowerOperationAddress || e.msg.sender == cdpManagerAddress, "Other caller than CDP manager");
    }

    rule onlyCdpManager(method f) filtered{f -> f.selector == sig:allocateSystemCollSharesToFeeRecipient(uint256).selector}{
        env e;
        calldataarg arg;
        address cdpManagerAddress = cdpManagerAddress(e);
        require(cdpManagerAddress == CdpManager);

        f(e,arg);

        assert (e.msg.sender == cdpManagerAddress, "Other caller than CDP manager");
    }

    rule onlyBorrowerOp(method f) filtered{f -> f.selector == sig:increaseSystemCollShares(uint256).selector}{
        env e;
        calldataarg arg;
        address borrowerOperationAddress = borrowerOperationsAddress(e);
        require(borrowerOperationAddress == BorrowerOp);

        f(e,arg);

        assert (e.msg.sender == borrowerOperationAddress, "Other caller than BorrowerOp");
    }


