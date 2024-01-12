import "./dependencies/AuthNoOwner.spec";
import "./dependencies/helper.spec";

/////////////////// METHODS ///////////////////////

///////////////// DEFINITIONS /////////////////////

////////////////// FUNCTIONS //////////////////////

///////////////// GHOSTS & HOOKS //////////////////

///////////////// PROPERTIES //////////////////////

// Possibility of not been reverted 
use rule helperSanity;

///////////////// VIOALTED PROPERTIES /////////////

// Prove fix with certoraMutate: 
//  certoraMutate --prover_conf certora/confs/EBTCToken_violated.conf --mutation_conf certora/confs/gambit/EBTCToken_fix.conf

// In initialized state authority address should not be zero 
use invariant authNoOwnerInitializedAndAddressSetInConstructor;

