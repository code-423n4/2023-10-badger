/////////////////// METHODS ///////////////////////

///////////////// DEFINITIONS /////////////////////

////////////////// FUNCTIONS //////////////////////

///////////////// GHOSTS & HOOKS //////////////////

//
// Ghost copy of `locked`
//

ghost uint256 ghostLocked {
    init_state axiom ghostLocked == 1;          // OPEN
    axiom ghostLocked == 1 || ghostLocked == 2; // OPEN or LOCKED
}

hook Sload uint256 val currentContract.locked STORAGE {
    require(ghostLocked == val);
}

hook Sstore currentContract.locked uint256 val STORAGE {
    ghostLocked = val;
}