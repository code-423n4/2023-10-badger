/////////////////// METHODS ///////////////////////

///////////////// DEFINITIONS /////////////////////

////////////////// FUNCTIONS //////////////////////

///////////////// GHOSTS & HOOKS //////////////////

//
// Ghost copy of `_nonces`
//

ghost mapping (address => mathint) ghostNonces {
    init_state axiom forall address i. ghostNonces[i] == 0;
    axiom forall address i. ghostNonces[i] >= 0 && ghostNonces[i] < max_uint64;
}

ghost mapping (address => mathint) ghostNoncesPrev {
    init_state axiom forall address i. ghostNoncesPrev[i] == 0;
    axiom forall address i. ghostNoncesPrev[i] >= 0 && ghostNoncesPrev[i] < max_uint64;
}

hook Sload uint256 val currentContract._nonces[KEY address i] STORAGE {
    require(assert_uint256(ghostNonces[i]) == val);
} 

hook Sstore currentContract._nonces[KEY address i] uint256 val (uint256 valPrev) STORAGE {
    ghostNoncesPrev[i] = ghostNonces[i];
    ghostNonces[i] = to_mathint(val);
}

///////////////// PROPERTIES ////////////////////// 

invariant permitNonceAlwaysIncremented() forall address i. ghostNonces[i] != ghostNoncesPrev[i] 
    => ghostNonces[i] - ghostNoncesPrev[i] == to_mathint(1);