import "./sanity.spec";

/*************
 * INTERFACE *
 *************/
methods {
    // view
    function allowance(address,address) external returns(uint) envfree;
    function totalSupply() external returns (uint) envfree;
    function balanceOf(address) external returns (uint256) envfree;
    function borrowerOperationsAddress() external returns (address) envfree;
    function cdpManagerAddress() external returns (address) envfree;
    function call_isAuthorized(address,uint32) external returns (bool) envfree;
    // public & external
    function mint(address, uint256) external ;
    function burn(uint256) external;
    function burn(address _account, uint256 _amount) external; 
    function transfer(address recipient, uint256 amount) external returns (bool);
    function transferFrom(
        address sender,
        address recipient,
        uint256 amount
    ) external returns (bool);
    function increaseAllowance(address spender, uint256 addedValue) external returns (bool);
    function decreaseAllowance(address spender, uint256 subtractedValue) external returns (bool);
}

use rule sanity;

function checkPermission(address msgSender,uint32 figSig) returns bool{
    address cdpManager = cdpManagerAddress();
    address borrowerOperations = borrowerOperationsAddress();

    bool hasPermission = call_isAuthorized(msgSender,figSig);
    return msgSender == cdpManager || msgSender == borrowerOperations || hasPermission;              // checking that the caller is authorized
}


/*************
 * INVARIANT *
 *************/

ghost mathint sum_of_balances {
    init_state axiom sum_of_balances == 0;
}

hook Sstore _balances[KEY address a] uint new_value (uint old_value) STORAGE {
    // when balance changes, update ghost
    sum_of_balances = sum_of_balances + new_value - old_value;
}


invariant totalSupplyIsSumOfUserBalances()
    to_mathint(totalSupply()) == sum_of_balances; 
    

/*********
 * RULES *
 *********/

rule mintIntegrity(env e) {
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

    assert checkPermission(e.msg.sender,sig:mint(address,uint256).selector); // checking that the caller is authorized
}


rule transferIntegrity(address recipient, uint amount) {
    env e;

    address sender = e.msg.sender; 
    address user;
    require(user != sender && user != recipient);

    mathint balance_sender_before = balanceOf(sender);
    mathint balance_recipient_before = balanceOf(recipient);
    mathint balance_user_before = balanceOf(user);
    
    transfer(e,recipient, amount);

    mathint balance_sender_after = balanceOf(sender);
    mathint balance_recipient_after = balanceOf(recipient);
    mathint balance_user_after = balanceOf(user);

    assert recipient != sender => balance_sender_after == balance_sender_before - amount; // checking that sender's balance was properly updated

    assert recipient != sender => balance_recipient_after == balance_recipient_before + amount; // checking that recipient's balance was properly updated

    assert recipient == sender => balance_sender_after == balance_sender_before ; // checking that sender's balance was not affected

    assert balance_user_before == balance_user_after; // balance of user who is not sender or recipient does not change

}

rule transferFromIntegrity(address sender, address recipient, uint256 amount){
    env e;
    address user;
    require(user != sender && user != recipient);

    mathint balance_sender_before = balanceOf(sender);
    mathint balance_recipient_before = balanceOf(recipient);
    mathint balance_user_before = balanceOf(user);
    mathint allowance_msg_sender_before = allowance(sender, e.msg.sender);
    
    
    transferFrom(e,sender,recipient, amount);

    mathint balance_sender_after = balanceOf(sender);
    mathint balance_recipient_after = balanceOf(recipient);
    mathint balance_user_after = balanceOf(user);
    mathint allowance_msg_sender_after = allowance(sender, e.msg.sender);

    assert recipient != sender => balance_sender_after == balance_sender_before - amount; // checking that sender's balance was properly updated

    assert recipient != sender => balance_recipient_after == balance_recipient_before + amount; // checking that recipient's balance was properly updated

    assert recipient == sender => balance_sender_after == balance_sender_before ; // checking that sender's balance was not affected

    assert(e.msg.sender != sender && allowance_msg_sender_before != max_uint => allowance_msg_sender_after == allowance_msg_sender_before - amount, "Allowance was not reduced propperly"); // check if the allowance changed correctly

    assert(e.msg.sender != sender && allowance_msg_sender_before == max_uint => allowance_msg_sender_after == max_uint, "Allowance is no longer uint_max"); // check if the allowance did not changed when allowance was max_uint 

    assert balance_user_after == balance_user_before, "User balance changed"; // check if the transaction touches a third balance    



}


rule burnIntegrity(uint256 amount){
    env e;

    address burner = e.msg.sender; 
    address user;
    require(user != burner);

    mathint balance_burner_before = balanceOf(burner);
    mathint balance_user_before = balanceOf(user);

    // require balance_burner_before >= to_mathint(amount);  infoBen: removed so proover can check if call reverts if amount is to big

    burn(e,amount);

    mathint balance_burner_after = balanceOf(burner);
    mathint balance_user_after = balanceOf(user);

    assert  balance_burner_before - balance_burner_after == to_mathint(amount); // checking that burner's balance was properly updated
    assert(balance_burner_before >= to_mathint(amount), "Amount is bigger than the balance of the user");
    assert(balance_user_after == balance_user_before, "User balance changed");
    assert(checkPermission(e.msg.sender,sig:burn(uint256).selector), "Caller should not be able to call this"); 

}


rule burnOthersIntegrity(address account, uint256 amount){
    env e;

    address msgSender = e.msg.sender;
    address user;
    require(user != account); 

    mathint balance_account_before = balanceOf(account);
    mathint balance_user_before = balanceOf(user);


    burn(e,account,amount);

    mathint balance_account_after = balanceOf(account);
    mathint balance_user_after = balanceOf(user);

    assert balance_account_before - balance_account_after == to_mathint(amount); // checking that account's balance was properly updated
    assert checkPermission(msgSender,sig:burn(address,uint256).selector); // checking that the caller is authorized
    assert(balance_account_before >= to_mathint(amount), "Amount to mint bigger than balance");
    assert(balance_user_after == balance_user_before, "User balance changed");
}


rule approveIntegrity(address spender,uint256 amount){
    env e;
    address owner = e.msg.sender;
    address user;
    require (user != owner && user != spender);

    uint256 allowance_user_before = allowance(user,spender);
    uint256 allowance_ownerUser_before = allowance(owner,user);

    approve(e,spender,amount);

    uint256 allowance_after = allowance(owner,spender);
    uint256 allowance_user_after = allowance(user,spender);
    uint256 allowance_ownerUser_after = allowance(owner,user);

    assert allowance_after == amount;
    assert(allowance_user_after == allowance_user_before,"User allowance changed");
    assert(allowance_ownerUser_after == allowance_ownerUser_before,"ownerUser allowance changed");
    assert(spender != 0,"Should not be possible to approve address 0");
}


rule increaseAllowanceIntegrity(address spender,uint256 amount){
    env e;
    address owner = e.msg.sender;
    address user;
    require (user != owner && user != spender);
    mathint allowance_before = allowance(owner,spender);
    uint256 allowance_user_before = allowance(user,spender);
    uint256 allowance_ownerUser_before = allowance(owner,user);

    increaseAllowance(e,spender,amount);

    mathint alowance_after = allowance(owner,spender);
    uint256 allowance_user_after = allowance(user,spender);
    uint256 allowance_ownerUser_after = allowance(owner,user);

    assert alowance_after == allowance_before + amount;
    assert(allowance_user_after == allowance_user_before,"User allowance changed");
    assert(allowance_ownerUser_after == allowance_ownerUser_before,"ownerUser allowance changed");
}


rule decreaseAllowanceIntegrity(address spender,uint256 amount){
    env e;
    address owner = e.msg.sender;
    address user;
    require (user != owner && user != spender);
    uint256 allowance_before = allowance(owner,spender);
    uint256 allowance_user_before = allowance(user,spender);
    uint256 allowance_ownerUser_before = allowance(owner,user);

    decreaseAllowance(e,spender,amount);

    uint256 alowance_after = allowance(owner,spender);
    uint256 allowance_user_after = allowance(user,spender);
    uint256 allowance_ownerUser_after = allowance(owner,user);

    assert to_mathint(alowance_after) == allowance_before - amount;
    assert(amount <= allowance_before, "Amount was bigger than the initial allowance");
    assert(allowance_user_after == allowance_user_before,"User allowance changed");
    assert(allowance_ownerUser_after == allowance_ownerUser_before,"ownerUser allowance changed");

    
}

//only spesific functions can change the allowance of a user
rule onlyToChangeAllowance(){
    method f;
    env e;
    calldataarg arg;
    address owner;
    address spender;

    mathint allowance_before = allowance(owner,spender);

    f(e,arg);

    mathint allowance_after = allowance(owner,spender);

    assert(allowance_after != allowance_before => 
        f.selector == sig:approve(address,uint256).selector ||
        f.selector == sig:increaseAllowance(address,uint256).selector ||
        f.selector == sig:decreaseAllowance(address,uint256).selector ||       
        f.selector == sig:transferFrom(address,address,uint256).selector ||       
        f.selector == sig:permit(address,address,uint256,uint256,uint8,bytes32,bytes32).selector ||       
        f.selector == sig:transfer(address,uint256).selector, "Other function changes the allowance"      
        );
}


//only spesific functions can change the balance of a user
rule onlyToChangeBalance(){
    method f;
    env e;
    calldataarg arg;
    address user;

    mathint balance_before = balanceOf(user);

    f(e,arg);

    mathint balance_after = balanceOf(user);

    assert(balance_before != balance_after => 
        f.selector == sig:mint(address,uint256).selector ||
        f.selector == sig:burn(address,uint256).selector ||
        f.selector == sig:burn(uint256).selector ||
        f.selector == sig:transfer(address,uint256).selector ||
        f.selector == sig:transferFrom(address,address,uint256).selector, "Other function changes the balance"      
        );
}

//only spesific functions can change the balance of a user
rule onlyToChangeTotalSupply(){
    method f;
    env e;
    calldataarg arg;

    mathint supply_before = totalSupply();

    f(e,arg);

    mathint supply_after = totalSupply();

    assert(supply_before != supply_after => 
        f.selector == sig:mint(address,uint256).selector ||
        f.selector == sig:burn(address,uint256).selector ||
        f.selector == sig:burn(uint256).selector, "Other function changes the total Supply"      
        );
}



