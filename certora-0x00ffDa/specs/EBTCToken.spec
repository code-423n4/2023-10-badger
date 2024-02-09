import "./sanity.spec";

/*
Status: all passing, coverage 95% w/ 21 mutations
*/

methods {
    function authorityInitialized() external returns bool envfree;
    function balanceOf(address) external returns (uint256) envfree;
    function totalSupply() external returns (uint256) envfree;
    function cdpManagerAddress() external returns (address) envfree;
    function borrowerOperationsAddress() external returns (address) envfree;

    // Ensure chain ID used in harness code doesn't change, AND matches private _chainID()
    //  Using "internal" to ensure it shims the internal calls rather than only external calls: https://docs.certora.com/en/latest/docs/cvl/methods.html#visibility-modifiers
    function getChainId() internal returns (uint256) => ALWAYS(42);

    // Ensure ID used in EBTCToken code doesn't change AND matches value used in harness.
    function EBTCToken._chainID() internal returns (uint256)=> ALWAYS(42);
}

/* Don't need it this time (but it works)
ghost uint256 chainIdGhost;
hook CHAINID uint v { // Hooking the opcode that sets the chain ID
    chainIdGhost = v;
}*/

use rule sanity;

invariant initialized()
    authorityInitialized() && cdpManagerAddress() != 0 && borrowerOperationsAddress() != 0;

rule accessControlBOorCdpM(method m) filtered {
    m -> m.selector == sig:mint(address, uint256).selector
      || m.selector == sig:burn(address, uint256).selector
      || m.selector == sig:burn(uint256).selector
} {
    env e;
    calldataarg args;
    bool userAuthorized = e.msg.sender == borrowerOperationsAddress(e) ||
                          e.msg.sender == cdpManagerAddress(e) ||
                          call_isAuthorized(e, e.msg.sender, m.selector);
    m@withrevert(e, args);
    assert !userAuthorized => lastReverted, "Unauthorized call";
}

rule mintIntegrity(env e) {
    address account;
    address user;
    uint256 amount;

    uint256 accountBalanceBefore = balanceOf(account);
    uint256 userBalanceBefore = balanceOf(user);
    mathint totalBefore = totalSupply();
    require totalBefore >= to_mathint(user == account ? userBalanceBefore : userBalanceBefore + accountBalanceBefore);

    mint(e, account, amount);

    uint256 accountBalanceAfter = balanceOf(account);
    uint256 userBalanceAfter = balanceOf(user);
    uint256 totalAfter = totalSupply();
    
    assert to_mathint(accountBalanceAfter) == accountBalanceBefore + amount, "Balance wasn't updated properly";
    assert user != account => userBalanceBefore == userBalanceAfter, "Unexpected change to a balance";
    assert user != account => to_mathint(totalAfter) >= to_mathint(userBalanceAfter + accountBalanceAfter), "Total supply is less than sum of  user balances";
    assert user == account => totalAfter >= userBalanceAfter, "Total supply is less than user's balance";
}

function validRecipient(address recipient) returns bool {
    return recipient != 0 && recipient != currentContract 
        && recipient != cdpManagerAddress() && recipient != borrowerOperationsAddress();
}

/* EBTC-01 | Anyone with an Ethereum address can send or receive eBTC tokens, whether they have an open CDP or not | Unit Tests */
rule transfer(address recipient, uint amount) {
    env e;
    mathint balanceSenderBefore = balanceOf(e.msg.sender);
    mathint balanceRecipBefore = balanceOf(recipient);
    require to_mathint(balanceSenderBefore + balanceRecipBefore) <= to_mathint(totalSupply());

    transfer@withrevert (e, recipient, amount);
    bool reverted = lastReverted;
    mathint balanceSenderAfter = balanceOf(e.msg.sender);
    mathint balanceRecipAfter = balanceOf(recipient);

    if (!reverted) {
        assert recipient == e.msg.sender => balanceSenderAfter == balanceSenderBefore, "Transfer to self changed balance unexpectedly";
        assert recipient != e.msg.sender => balanceSenderAfter == balanceSenderBefore - amount, "Transfer did not decrease sender's balance by amount";
        assert recipient != e.msg.sender => balanceRecipAfter == balanceRecipBefore + amount, "Transfer did not increase recipient's balance by amount";
    }
    assert !validRecipient(recipient) => reverted, "Invalid recipient didn't cause revert";
}

rule transferFrom(address sender, address recipient, uint256 amount) {
    env e;    
    require sender != recipient;
    require amount != 0;
    mathint allowanceBefore = allowance(e, sender, e.msg.sender);
    uint256 balanceBefore = balanceOf(sender);

    transferFrom@withrevert(e, sender, recipient, amount);
    bool reverted = lastReverted;
    mathint allowanceAfter = allowance(e, sender, e.msg.sender);
    
    if (!reverted) {
        assert (allowanceBefore != max_uint256) => allowanceAfter < allowanceBefore, "Allowance did not decrease as expected";
        assert (allowanceBefore == max_uint256) => allowanceAfter == allowanceBefore, "Unlimited allowance changed by transfer";
    }
    assert !validRecipient(recipient) => reverted, "Invalid recipient didn't cause revert";

    // Cover some internal _transfer() logic
    assert sender == 0 => reverted, "Invalid sender didn't cause revert";
    assert amount > balanceBefore => reverted, "Excessive transfer didn't revert";
}

rule internalTransfer(address sender, address recipient, uint256 amount) {
    // This is only needed to catch a mutation affecting a require() that is redundant in the code 
    // (so if it changes, can't detect lack of revert via the public functions)
    env e;
    internalTransfer@withrevert(e, sender, recipient, amount);
    assert recipient == 0 => lastReverted, "Invalid recipient didn't revert";
}

rule onlyHolderCanChangeAllowance(address holder, address spender, method f) {
    env e;
    calldataarg args;
    mathint allowanceBefore = allowance(e, holder, spender);

    f(e, args);                        
    mathint allowanceAfter = allowance(e, holder, spender);

    assert allowanceAfter != allowanceBefore => 
        (
            e.msg.sender == holder || 
            f.selector == sig:permit(address, address, uint, uint, uint8, bytes32, bytes32).selector ||
            f.selector == sig:transferFrom(address, address, uint256).selector
        ),
        "User changed an allowance on another balance (without approval)";
    assert allowanceAfter != allowanceBefore =>
        (
            f.selector == sig:approve(address, uint).selector ||
            f.selector == sig:increaseAllowance(address, uint).selector ||
            f.selector == sig:decreaseAllowance(address, uint).selector ||
            f.selector == sig:permit(address, address, uint, uint, uint8, bytes32, bytes32).selector ||
            f.selector == sig:transferFrom(address, address, uint256).selector
        ),
        "Unexpected function was able to change allowance";
}

rule changingAllowance(address spender, uint256 amount) {
    env e;

    approve@withrevert(e, spender, amount);
    bool reverted = lastReverted;

    assert e.msg.sender == 0 => reverted, "Impossible sender should have reverted";
    assert spender == 0 => reverted, "Impossible spender should have reverted";
    uint256 allowance = allowance(e, e.msg.sender, spender);
    assert !reverted => allowance == amount, "Allowance not set correctly";

    uint256 increaseBy;
    increaseAllowance(e, spender, increaseBy);
    assert to_mathint(allowance(e, e.msg.sender, spender)) == to_mathint(allowance + increaseBy), "Allowance not increased correctly";

    uint256 allowance2 = allowance(e, e.msg.sender, spender);
    uint256 decreaseBy;
    decreaseAllowance(e, spender, decreaseBy);
    assert to_mathint(allowance(e, e.msg.sender, spender)) == to_mathint(allowance2 - decreaseBy), "Allowance not decreased correctly";
}

rule permit(
        address owner,
        address spender,
        uint256 amount,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s) {
    env e;

    permit@withrevert(e, owner, spender, amount, deadline, v, r, s);
    bool reverted = lastReverted;

    assert deadline < e.block.timestamp => reverted, "Expired deadline didn't cause revert";

    address recoveredAddress = getRecoveredAddress(e, owner, spender, amount, deadline, v, r, s);
    assert recoveredAddress != owner => reverted, "Invalid signature didn't cause revert"; // 0 should cause _approve() to revert

    assert !reverted => allowance(e, owner, spender) == amount, "Allowance not set correctly";
}

rule domainSeparator {
    env e;
    require( getChainId(e) == getCachedChainId(e));   // cannot change
    bytes32 domainSep = domainSeparator(e);
    assert domainSep == getCachedDomainSeparator(e), "Unexpected domain separator";
}

rule burn {
    env e;
    require e.msg.sender == cdpManagerAddress();  // An authorized caller
    address account;
    uint256 amount;
    uint256 balanceBefore = balanceOf(account);
    uint256 totalSupplyBefore = totalSupply();

    internalBurn@withrevert(e,account, amount);
    bool reverted = lastReverted;

    assert account == 0 => reverted, "Burn for address 0 didn't revert";
    assert amount > balanceBefore => reverted, "Burn greater than balance didn't revert";
    assert !reverted => to_mathint(balanceOf(account)) == to_mathint(balanceBefore - amount), "Balance didn't decrease correctly";
    assert !reverted => to_mathint(totalSupply()) == to_mathint(totalSupplyBefore - amount), "totalSupply didn't decrease correctly";
}

rule balanceOnlyChangesByExpectedFunctions(method f, address user) filtered {
    f -> f.selector != sig:internalTransfer(address, address, uint256).selector
      && f.selector != sig:internalBurn(address, uint256).selector
}
{
    env e;
    calldataarg args;
    uint256 userBalanceBefore = balanceOf(user);
    f(e, args);
    uint256 userBalanceAfter = balanceOf(user);

    assert userBalanceBefore != userBalanceAfter => 
        (
            f.selector == sig:transfer(address, uint256).selector ||
            f.selector == sig:transferFrom(address, address, uint256).selector ||
            f.selector == sig:mint(address, uint256).selector ||
            f.selector == sig:burn(address, uint256).selector ||
            f.selector == sig:burn(uint256).selector
        ),
        "User balance changed by an unexpected function";
}

rule doesNotAffectAThirdPartyBalance(method f) filtered {
    f -> f.selector != sig:internalTransfer(address, address, uint256).selector
      && f.selector != sig:internalBurn(address, uint256).selector
}
{
    env e;
    uint256 amount;
    address from;
    address to;
    address thirdParty;
    require (thirdParty != from) && (thirdParty != to);

    uint256 thirdBalanceBefore = balanceOf(thirdParty);
    
    if (f.selector == sig:transfer(address, uint256).selector) {
        require e.msg.sender == from;
        transfer(e, to, amount);
    } else if (f.selector == sig:allowance(address, address).selector) {
        allowance(e, from, to);
    } else if (f.selector == sig:approve(address, uint256).selector) {
        approve(e, to, amount);
    } else if (f.selector == sig:transferFrom(address, address, uint256).selector) {
        transferFrom(e, from, to, amount);
    } else if (f.selector == sig:increaseAllowance(address, uint256).selector) {
        increaseAllowance(e, to, amount);
    } else if (f.selector == sig:decreaseAllowance(address, uint256).selector) {
        decreaseAllowance(e, to, amount);
    } else if (f.selector == sig:mint(address, uint256).selector) {
        mint(e, to, amount);
    } else if (f.selector == sig:burn(address, uint256).selector) {
        burn(e, from, amount);
    } else if (f.selector == sig:burn(uint256).selector) {
        require e.msg.sender == from;
        burn(e, amount);
    } else {
        calldataarg args;
        f(e, args);
    }

    assert balanceOf(thirdParty) == thirdBalanceBefore, "Third party balanced changed unexpectedly";
}

rule internalAuthCheck {
    // These functions are not currently used, so this validation is for future code evolution
    env e;
    internalRequireCallerIsBorrowerOperations@withrevert(e);
    bool reverted = lastReverted;
    assert e.msg.sender != borrowerOperationsAddress() => reverted, "Auth failure didn't revert";

    internalRequireCallerIsCdpM@withrevert(e);
    bool reverted2 = lastReverted;
    assert e.msg.sender != cdpManagerAddress() => reverted2, "Auth failure didn't revert";
}
