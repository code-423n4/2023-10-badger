/////////////////// METHODS ///////////////////////

methods {
    function MAX_BPS() external returns uint256 envfree;
    function MAX_FEE_BPS() external returns uint256 envfree;
}

///////////////// DEFINITIONS /////////////////////

////////////////// FUNCTIONS //////////////////////

///////////////// GHOSTS & HOOKS //////////////////

//
// Ghost copy of `feeBps`
//

ghost uint16 ghostFeeBps {
    init_state axiom ghostFeeBps == 3;
}

hook Sload uint16 val currentContract.feeBps STORAGE {
    require(ghostFeeBps == val);
}

hook Sstore currentContract.feeBps uint16 val STORAGE {
    ghostFeeBps = val;
}

//
// Ghost copy of `flashLoansPaused`
//

ghost bool ghostFlashLoansPaused {
    init_state axiom ghostFlashLoansPaused == false;
}

hook Sload bool val currentContract.flashLoansPaused STORAGE {
    require(ghostFlashLoansPaused == val);
}

hook Sstore currentContract.flashLoansPaused bool val STORAGE {
    ghostFlashLoansPaused = val;
}

///////////////// PROPERTIES //////////////////////

invariant erc3156FlashLenderFeeBpsNotGtMaxfeeBps() ghostFeeBps <= assert_uint16(MAX_FEE_BPS());