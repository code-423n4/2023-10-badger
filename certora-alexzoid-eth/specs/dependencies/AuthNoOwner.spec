/////////////////// METHODS ///////////////////////

methods {
    // Authority
    function _.canCall(address user, address target, bytes4 functionSig) external 
        => canCallCVL(user, functionSig) expect bool ALL;
}

///////////////// DEFINITIONS /////////////////////

////////////////// FUNCTIONS //////////////////////

// Summarization for canCall()
ghost mapping (address => mapping (bytes4 => bool)) ghostCanCall;
function canCallCVL(address user, bytes4 functionSig) returns bool {
    return ghostCanCall[user][functionSig];
}

///////////////// GHOSTS & HOOKS //////////////////

//
// Ghost copy of `_authority`
//

ghost address ghostAuthority {
    init_state axiom ghostAuthority == 0;
}

hook Sload address val currentContract._authority STORAGE {
    require(ghostAuthority == val);
}

hook Sstore currentContract._authority address val STORAGE {
    ghostAuthority = val;
}

//
// Ghost copy of `_authorityInitialized`
//

ghost bool ghostAuthorityInitialized {
    init_state axiom ghostAuthorityInitialized == false;
}

hook Sload bool val currentContract._authorityInitialized STORAGE {
    require(ghostAuthorityInitialized == val);
}

hook Sstore currentContract._authorityInitialized bool val STORAGE {
    ghostAuthorityInitialized = val;
}

///////////////// PROPERTIES //////////////////////

invariant authNoOwnerInitializedAndAddressSetInConstructor() ghostAuthorityInitialized == (ghostAuthority != 0) 
    filtered { f -> f.selector == 0 } {
    preserved {
        require(false);
    }
}

invariant authNoOwnerSetAuthorityFromCdpManagerInConstructor() ghostAuthorityAddress != 0
    => ghostAuthority == ghostAuthorityAddress && ghostAuthorityInitialized
    filtered { f -> f.selector == 0 } {
    preserved {
        require(false);
    }
}