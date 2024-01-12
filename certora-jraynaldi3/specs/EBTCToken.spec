import "./sanity.spec";



methods {
    function call_isAuthorized(address user, uint32 functionSig) external  returns (bool) envfree;
    function balanceOf(address) external returns (uint256) envfree;
    function allowance(address, address) external returns(uint256) envfree;

    //view function 
    function totalSupply() external returns(uint256) envfree;

    //public variable 
    function cdpManagerAddress() external returns (address) envfree;
    function borrowerOperationsAddress() external returns (address) envfree;
}



use rule sanity;



// This is an example of one of the simplest types of properties that we can implement
// unit-test like / integrity prtoperties, checking correctness of basic functionalities
rule mingIntegrity(env e) {
    address account;
    address user;
    uint256 amount;

    uint256 accountBalanceBefore = balanceOf(account);
    uint256 userBalanceBefore = balanceOf(user);

    mint(e, account, amount);

    uint256 accountBalanceAfter = balanceOf(account);
    uint256 userBalanceAfter = balanceOf(user);

    assert to_mathint(accountBalanceAfter) == accountBalanceBefore + amount;        // checking that account's balance was properly updated
    assert user != account => userBalanceBefore == userBalanceAfter;                // checking that other users' balances were not affected
}

/***********************    PARTICIPANT  ************************/

/***********************    MISC   ************************/
ghost mathint sumOfAllBalance{
    init_state axiom sumOfAllBalance == 0;
}

hook Sload uint256 val _balances[KEY address account] STORAGE{
    require to_mathint(val) <= sumOfAllBalance;
}

hook Sstore _balances[KEY address account] uint256 val (uint256 oldVal) STORAGE {
    sumOfAllBalance = sumOfAllBalance - oldVal + val;
}

definition BOorCDPorAuth(address account, uint32 selector) returns bool = (
    account == cdpManagerAddress()
    || account == borrowerOperationsAddress()
    || call_isAuthorized(account, selector)
);

definition validRecipient(address account) returns bool = (
    account != 0
    && account != currentContract
    && account != cdpManagerAddress()
    && account != borrowerOperationsAddress()
);

/***********************    HIGH LEVEL   ************************/

/// @notice totalSupply should be summary of all single account balances
invariant setup()
    to_mathint(totalSupply()) == sumOfAllBalance;

/// @notice immutable varibale should not changed
rule immutableVariable(env e, method f, calldataarg args){
    address _cdpManagerAddress = cdpManagerAddress();
    address _borrowerOperationsAddress = borrowerOperationsAddress();

    f(e,args);

    address cdpManagerAddress_ = cdpManagerAddress();
    address borrowerOperationsAddress_ = borrowerOperationsAddress();
    assert _cdpManagerAddress == cdpManagerAddress_;
    assert _borrowerOperationsAddress == borrowerOperationsAddress_;
}

/// @notice totalSupply can only changed by several address using mint or burn function
rule totalSupplyChanged(env e,method f, calldataarg args) {
    uint256 _totalSupply = totalSupply();
    f(e,args);
    uint256 totalSupply_ = totalSupply();

    assert _totalSupply != totalSupply_ 
        => (e.msg.sender == cdpManagerAddress()
        || e.msg.sender == borrowerOperationsAddress()
        || call_isAuthorized(e.msg.sender, f.selector))
        && (f.selector == sig:mint(address,uint256).selector 
        || f.selector == sig:burn(address,uint256).selector 
        || f.selector == sig:burn(uint256).selector);
}

/// @notice address zero have no balance
invariant addressZeroNoBalance()
    balanceOf(0) == 0;

/// @notice transfer only to valid recipient address
rule validRecipientCheck(
    env e, 
    method f, 
    calldataarg args, 
    address account, 
    address recipient
){
    uint256 accountBalanceBefore = balanceOf(account);
    uint256 recipientBalanceBefore = balanceOf(recipient);

    f(e,args);

    uint256 accountBalanceAfter = balanceOf(account);
    uint256 recipientBalanceAfter = balanceOf(recipient);
    assert accountBalanceBefore > accountBalanceAfter 
        && (recipient == 0
        || recipient == currentContract
        || recipient == cdpManagerAddress()
        || recipient == borrowerOperationsAddress())
        =>  recipientBalanceBefore >= recipientBalanceAfter;
}

/// @notice who can decrease balance 
rule decreaseBalance(
    env e,
    method f,
    calldataarg args,
    address account
) {
    uint256 balanceBefore = balanceOf(account);
    uint256 allowanceBefore = allowance(account, e.msg.sender);

    f(e,args);

    uint256 balanceAfter = balanceOf(account);
    uint256 allowanceAfter = allowance(account, e.msg.sender);
    assert balanceAfter < balanceBefore 
        => (BOorCDPorAuth(e.msg.sender, f.selector) 
        && (f.selector == sig:mint(address,uint256).selector
        || f.selector == sig:burn(address,uint256).selector
        || f.selector == sig:burn(uint256).selector))
        || e.msg.sender == account 
        || allowanceBefore != 0;
}

/// @notice address zero should not have spender allowed
invariant addressZeroNoAllowance(address other)
    allowance(0, other) == 0 && allowance(other, 0) == 0;

/// @notice address zero should not have allowance
invariant addressZeroNoSpender(address other)
    allowance(other, 0) == 0;

/// @notice cannot change balance from address zero 
rule addressZeroBalanceNoChange(
    env e,
    calldataarg args,
    method f
){
    uint256 before = balanceOf(0);

    f(e, args);

    uint256 after = balanceOf(0);
    assert before == after;
}
/***********************    Unit Test   ************************/
/// @notice mint should add balance to account and add total supply
rule mint_integrity(
    env e,
    address account,
    uint256 amount
) {
    uint256 balanceBefore = balanceOf(account);
    uint256 _totalSupply = totalSupply();

    mint(e, account,amount);

    uint256 balanceAfter = balanceOf(account);
    uint256 totalSupply_ = totalSupply();
    assert to_mathint(balanceAfter) == balanceBefore + amount 
        <=> account != 0 
        && BOorCDPorAuth(e.msg.sender, sig:mint(address,uint256).selector);
    assert to_mathint(totalSupply_) == _totalSupply + amount;
}

/// @notice burn should decrease balance from account and decrease total supply
rule burn_integrity(
    env e,
    address account,
    uint256 amount
) {
    uint256 balanceBefore = balanceOf(account);
    uint256 _totalSupply = totalSupply();

    burn(e, account,amount);

    uint256 balanceAfter = balanceOf(account);
    uint256 totalSupply_ = totalSupply();
    assert to_mathint(balanceAfter) == balanceBefore - amount 
        <=>  BOorCDPorAuth(e.msg.sender, sig:burn(address,uint256).selector);
    assert to_mathint(totalSupply_) == _totalSupply - amount;
}

/// @notice burn(uint256) should decrease balance from msg.sender and decrease total supply
rule burnSelf_integrity(
    env e,
    uint256 amount
) {
    uint256 balanceBefore = balanceOf(e.msg.sender);
    uint256 _totalSupply = totalSupply();

    burn(e,amount);

    uint256 balanceAfter = balanceOf(e.msg.sender);
    uint256 totalSupply_ = totalSupply();
    assert BOorCDPorAuth(e.msg.sender, sig:burn(uint256).selector) 
        <=> to_mathint(balanceAfter) == balanceBefore - amount; 
    assert to_mathint(totalSupply_) == _totalSupply - amount;
}

/// @notice transfer should move balance from msg.sender to receiver
rule transfer_integrity(
    env e ,
    address sender,
    address receiver,
    uint256 amount,
    address other
) {
    uint256 _senderBalance = balanceOf(sender);
    uint256 _receiverBalance = balanceOf(receiver);
    uint256 _otherBalance = balanceOf(other);

    transfer(e, receiver, amount);

    uint256 senderBalance_ = balanceOf(sender);
    uint256 receiverBalance_ = balanceOf(receiver);
    uint256 otherBalance_ = balanceOf(other);

    assert sender == e.msg.sender && receiver != e.msg.sender => to_mathint(senderBalance_) == _senderBalance - amount;
    assert validRecipient(receiver) && receiver != e.msg.sender => to_mathint(receiverBalance_) == _receiverBalance + amount;
    assert other != receiver && other != sender && other != e.msg.sender => _otherBalance == otherBalance_;
}

/// @notice transferFrom should move balance from sender to receiver, and reduce allowance for msg.sender
rule transferFrom_integrity(
    env e ,
    address sender,
    address receiver,
    uint256 amount,
    address other
) {
    uint256 _senderBalance = balanceOf(sender);
    uint256 _receiverBalance = balanceOf(receiver);
    uint256 _otherBalance = balanceOf(other);
    uint256 _allowance = allowance(sender, e.msg.sender);

    transferFrom(e, sender, receiver, amount);

    uint256 senderBalance_ = balanceOf(sender);
    uint256 receiverBalance_ = balanceOf(receiver);
    uint256 otherBalance_ = balanceOf(other);
    uint256 allowance_ = allowance(sender, e.msg.sender);

    assert receiver != sender => to_mathint(senderBalance_) == _senderBalance - amount;
    assert validRecipient(receiver) && receiver != sender => to_mathint(receiverBalance_) == _receiverBalance + amount;
    assert other != receiver && other != sender && other != e.msg.sender => _otherBalance == otherBalance_;
    assert _allowance != max_uint => to_mathint(allowance_) == _allowance - amount;
    assert _allowance == max_uint => allowance_ == _allowance;
}

/// @notice approve should changed allowance to some value 
rule approve_integrity(env e, address spender, uint256 amount) {
    approve(e, spender,amount);
    assert allowance(e.msg.sender, spender) == amount;
}

/// @notice decreaseAllowance should reduce allowance of msg.sender for spender
rule decreaseAllowance_integrity(env e, address spender, uint256 amount) {
    uint256 _allowance = allowance(e.msg.sender, spender);

    decreaseAllowance(e,spender,amount);

    uint256 allowance_ = allowance(e.msg.sender, spender);
    assert to_mathint(allowance_) == _allowance - amount;
}

/// @notice increase allowance should add allowance of msg.sender for spender
rule increaseAllowance_integrity(env e, address spender, uint256 amount) {
    uint256 _allowance = allowance(e.msg.sender, spender);

    increaseAllowance(e,spender,amount);

    uint256 allowance_ = allowance(e.msg.sender, spender);
    assert to_mathint(allowance_) == _allowance + amount;
}

/// @notice permit revert on expired
rule permit_revertion(
    env e,
    address owner,
    address spender,
    uint256 amount,
    uint256 deadline,
    uint8 v,
    bytes32 r,
    bytes32 s
){
    permit@withrevert(e, owner,spender, amount, deadline, v, r, s);
    assert deadline < e.block.timestamp => lastReverted;
}

/// @notice permit should able to approve 
rule permit_integrity(
    env e,
    address owner,
    address spender,
    uint256 amount,
    uint256 deadline,
    uint8 v,
    bytes32 r,
    bytes32 s
){
    permit(e, owner,spender, amount, deadline, v, r, s);
    assert allowance(owner, spender) == amount;
}
/***********************    Multi Return Sanity Check   ************************/
/**
 * @notice all rules below have spesific purpose which is for checking multiple 
 * returns conditions of a function
*/

rule transferFrom_sanity(
    env e ,
    address sender,
    address receiver,
    uint256 amount
) {
    uint256 _allowance = allowance(sender, e.msg.sender);

    transferFrom(e, sender, receiver, amount);

    satisfy _allowance != max_uint;
}