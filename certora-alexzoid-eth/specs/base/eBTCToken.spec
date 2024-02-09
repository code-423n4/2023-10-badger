using EBTCTokenHarness as _EBTCToken;

/////////////////// METHODS ///////////////////////

methods {

    // EBTCTokenHarness

    // EBTCToken
    function _EBTCToken.cdpManagerAddress() external returns (address) envfree;
    function _EBTCToken.borrowerOperationsAddress() external returns (address) envfree;
    function _EBTCToken.mint(address _account, uint256 _amount) external;
    function _EBTCToken.burn(address _account, uint256 _amount) external;
    function _EBTCToken.burn(uint256 _amount) external;
    function _EBTCToken.totalSupply() external returns (uint256)  envfree;
    function _EBTCToken.balanceOf(address account) external returns (uint256) envfree;
    function _EBTCToken.transfer(address recipient, uint256 amount) external returns (bool);
    function _EBTCToken.allowance(address owner, address spender) external returns (uint256) envfree;
    function _EBTCToken.approve(address spender, uint256 amount) external returns (bool);
    function _EBTCToken.transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function _EBTCToken.increaseAllowance(address spender, uint256 addedValue) external returns (bool);
    function _EBTCToken.decreaseAllowance(address spender, uint256 subtractedValue) external returns (bool);
    function _EBTCToken.DOMAIN_SEPARATOR() external returns (bytes32);
    function _EBTCToken.domainSeparator() external returns (bytes32);
    function _EBTCToken.permit(address owner, address spender, uint256 amount, uint256 deadline,
        uint8 v, bytes32 r, bytes32 s) external;
    function _EBTCToken.nonces(address owner) external returns (uint256) envfree;
    function _EBTCToken.name() external returns (string) envfree;
    function _EBTCToken.symbol() external returns (string) envfree;
    function _EBTCToken.decimals() external returns (uint8) envfree;
    function _EBTCToken.version() external returns (string) envfree;
    function _EBTCToken.permitTypeHash() external returns (bytes32) envfree;
}

///////////////// DEFINITIONS /////////////////////

////////////////// FUNCTIONS //////////////////////

///////////////// GHOSTS & HOOKS //////////////////

//
// Ghost copy of `_totalSupply`
//

ghost mathint ghostTotalSupply {
    init_state axiom ghostTotalSupply == 0;
    axiom ghostTotalSupply >= 0;
}

hook Sload uint256 val _EBTCToken._totalSupply STORAGE {
    require(require_uint256(ghostTotalSupply) == val);
}

hook Sstore _EBTCToken._totalSupply uint256 val STORAGE {
    ghostTotalSupply = val;
}

//
// Ghost copy of `_balances`
//

ghost address ghostUserInit {
    init_state axiom ghostUserInit == 0;
}

ghost address ghostUserOther {
    init_state axiom ghostUserOther == 0;
}

ghost mapping (address => mathint) ghostBalances {
    init_state axiom forall address i. ghostBalances[i] == 0;
    axiom forall address i. ghostBalances[i] >= 0;
}

ghost mapping (address => mathint) ghostBalancesPrev {
    init_state axiom forall address i. ghostBalancesPrev[i] == 0;
    axiom forall address i. ghostBalancesPrev[i] >= 0;
}

ghost mathint sumAllBalance {
    init_state axiom sumAllBalance == 0;
}

hook Sload uint256 val _EBTCToken._balances[KEY address i] STORAGE {
    require(require_uint256(ghostBalances[i]) == val);
} 

hook Sstore _EBTCToken._balances[KEY address i] uint256 val STORAGE {
    
    ghostBalancesPrev[i] = ghostBalances[i];
    ghostBalances[i] = val;
    
    sumAllBalance = sumAllBalance + val - ghostBalancesPrev[i];

    ghostUserOther = i != ghostUserInit ? i : ghostUserOther;
}

//
// Ghost copy of `mapping(address => mapping(address => uint256)) _allowances`
//

ghost mapping(address => mapping(address => mathint)) ghostAllowances {
    init_state axiom forall address key. forall address val. ghostAllowances[key][val] == 0;
}

ghost mapping(address => mapping(address => mathint)) ghostAllowancesPrev {
    init_state axiom forall address key. forall address val. ghostAllowancesPrev[key][val] == 0;
}

hook Sstore _EBTCToken._allowances[KEY address key][KEY address val] uint256 amount (uint256 prevAmount) STORAGE {
    ghostAllowancesPrev[key][val] = prevAmount;
    ghostAllowances[key][val] = amount;
}

hook Sload uint256 amount _EBTCToken._allowances[KEY address key][KEY address val] STORAGE {
    require(require_uint256(ghostAllowances[key][val]) == amount);
}

///////////////// PROPERTIES //////////////////////

invariant eBTCTokenBalanceOfMax2UsersChanged(address user1, address user2, address user3) 
    ghostBalances[user1] != ghostBalancesPrev[user1] && ghostBalances[user2] != ghostBalancesPrev[user2]
        => ghostBalances[user3] == ghostBalancesPrev[user3] {
        preserved {
            require(user1 != user2 && user1 != user3 && user2 != user3);
            require(ghostBalances[user1] == ghostBalancesPrev[user1] 
                && ghostBalances[user2] == ghostBalancesPrev[user2]
                && ghostBalances[user3] == ghostBalancesPrev[user3]
                );
        }
    }

invariant eBTCTokenTotalSupplySolvency() ghostTotalSupply == sumAllBalance;

invariant eBTCTokenSumOfAllBalancesEqTotalSupply(address initUser) 
    ghostTotalSupply == ghostBalances[ghostUserInit] + ghostBalances[ghostUserOther] {
    preserved {
        // Only initUser could have positive balance initially, it is enough to test mint/burn/transfer
        require(forall address i. i != initUser => ghostBalances[i] == 0);
        // Total supply equal balance of initUser
        require(ghostTotalSupply == ghostBalances[initUser]);
        requireInvariant eBTCTokenTotalSupplySolvency;
        // Zero addresses could not be modified
        require(initUser != 0 && initUser == ghostUserInit);
        require(ghostUserOther == 0);
    }
}

invariant eBTCTokenBalanceOfAddressZeroNotChanged() 
    // Balance at address zero should not changed
    ghostBalances[0] == ghostBalancesPrev[0]; 

invariant eBTCTokenTransferToRecipientRestrictions(address sender)   
    // Balance of sender was changed
    ghostBalances[sender] != ghostBalancesPrev[sender]
        // Balance of recipient was changed
        => (forall address i. i != sender && ghostBalances[i] != ghostBalancesPrev[i]
            // Sender and recipient address restrictions
            => (sender != 0 && i != 0 
                && i != _EBTCToken 
                && i != _EBTCToken.cdpManagerAddress() 
                && i != _EBTCToken.borrowerOperationsAddress()
                )
            ) {
    preserved {
        // Only `sender` could have positive balance initially, it is enough to test transfer
        require(forall address i. i != sender => (ghostBalances[i] == 0 && ghostBalancesPrev[i] == 0));
        require(ghostBalances[sender] == ghostBalancesPrev[sender]);
    }
}

invariant eBTCTokenAllowanceOfAddressZeroNotChanged() 
    // Allowance at address zero should not changed
    forall address i. forall address j. (
        ghostAllowances[0][j] == ghostAllowancesPrev[0][j]
        && ghostAllowances[i][0] == ghostAllowancesPrev[i][0]
    ) {
    preserved {
        require(forall address i. forall address j. ghostAllowances[i][j] == ghostAllowancesPrev[i][j]);
    }
}