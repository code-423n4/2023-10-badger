import "./sanity.spec";



methods {
    function balanceOf(address) external returns (uint256) envfree;
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
