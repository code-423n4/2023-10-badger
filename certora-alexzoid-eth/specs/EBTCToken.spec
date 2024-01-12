import "./base/eBTCToken.spec";
import "./dependencies/AuthNoOwner.spec";
import "./dependencies/PermitNonce.spec";
import "./dependencies/helper.spec";

/////////////////// METHODS ///////////////////////

///////////////// DEFINITIONS /////////////////////

////////////////// FUNCTIONS //////////////////////

///////////////// GHOSTS & HOOKS //////////////////

///////////////// INITIAL PROPERTIES //////////////

// This is an example of one of the simplest types of properties that we can implement
//  unit-test like / integrity prtoperties, checking correctness of basic functionalities
rule mingIntegrity(env e, address account, address user, uint256 amount) {

    uint256 accountBalanceBefore = balanceOf(account);
    uint256 userBalanceBefore = balanceOf(user);

    mint(e, account, amount);

    uint256 accountBalanceAfter = balanceOf(account);
    uint256 userBalanceAfter = balanceOf(user);

    // checking that account's balance was properly updated
    assert(to_mathint(accountBalanceAfter) == accountBalanceBefore + amount); 
    // checking that other users' balances were not affected       
    assert(user != account => userBalanceBefore == userBalanceAfter);         
}

// Possibility of not been reverted 
use rule helperSanity;

///////////////// ADDED PROPERTIES ////////////////

// [1] Nonce always incremented
use invariant permitNonceAlwaysIncremented;

// [2] Balance of max two users could be changed at time
use invariant eBTCTokenBalanceOfMax2UsersChanged;

// [3] Total supply storage variable equal to sum of balances
use invariant eBTCTokenTotalSupplySolvency;

// [4] Set two users with positive balance. Sum of all balances will be equal to these users plus other random user
use invariant eBTCTokenSumOfAllBalancesEqTotalSupply;

// [5] Cannot communicate with address(0)
use invariant eBTCTokenBalanceOfAddressZeroNotChanged;

// [6] Recipient could not be address(0), current contract, cdpManagerAddress, borrowerOperationsAddress
use invariant eBTCTokenTransferToRecipientRestrictions;

// [7-8] Allowance at address zero should not changed
use invariant eBTCTokenAllowanceOfAddressZeroNotChanged;