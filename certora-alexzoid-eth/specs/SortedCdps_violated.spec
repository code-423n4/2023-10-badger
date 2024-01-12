import "./base/sortedCdps.spec";
import "./dependencies/CdpManager.spec";
import "./dependencies/helper.spec";

///////////////// SETUP PROPERTIES ////////////////

// Possibility of not been reverted 
use rule helperSanity;

// Require valid list structure initially
use invariant isListStructureValidInv;

// Max size could not be zero
use invariant sortedCdpsMaxSizeGtZero;

// Could not add more than maxSize
use invariant sortedCdpsSizeLeqMaxSize;

// Empty list solvency
use invariant sortedCdpsListEmptySolvency;

// One item list solvency
use invariant sortedCdpsListOneItemSolvency;

// Several items list solvency
use invariant sortedCdpsListSeveralItemsSolvency;

// Item in the list should not link to self
use invariant sortedCdpsListNotLinkedToSelf;

// Item with zero id is not support
use invariant sortedCdpsListZeroIdsNotSupported;

// List should not contain duplicates
use invariant sortedCdpsListNoDuplicates;

// The NICR ranking in the sorted list should follow descending order
use invariant sortedCdpsListNICRDescendingOrder;

///////////////// VIOLATED PROPERTIES /////////////

// Prove fix with certoraMutate: 
//  certoraMutate --prover_conf certora/confs/SortedCdps_violated.conf --mutation_conf certora/confs/gambit/SortedCdps_fix.conf

// When cdpOfOwnerByIdx() return true, Cdp must exist in the list
rule cdpOfOwnerByIdxNodeReturnExistenceCdp(address owner, uint256 index, bytes32 startNodeId, uint maxNodes) {

    // Require a valid list structure
    setupList();

    bytes32 id;
    bool result;
    id, result = cdpOfOwnerByIdx(owner, index, startNodeId, maxNodes);

    // When result is true, Cdp must exist
    assert(result => contains(id));
}

// getAllCdpsOf() must return array less or equal to list size
rule getAllCdpsOfListSizeSolvency(address owner, bytes32 startNodeId, uint256 maxNodes) {

    // Require a valid list structure
    setupList();

    bytes32[] userCdps; 
    uint256 _cdpRetrieved; 
    bytes32 _currentCdpId;
    userCdps, _cdpRetrieved, _currentCdpId = getAllCdpsOf(owner, startNodeId, maxNodes);

    // Amount length must be less or equal to list size
    assert(userCdps.length <= require_uint256(ghostSize));
}

// getCdpCountOf() result must be less or equal to result of cdpCountOf()
rule getCdpCountOfCdpCountOfSolvency(address owner, bytes32 startNodeId, uint maxNodes) {
    
    // Require a valid list structure
    setupList();

    // Number of all active Cdps owned by the address
    mathint maxCount = cdpCountOf(owner);

    mathint count;
    bytes32 id;
    // Number of active Cdps owned by the address in the segment of the list traversed
    count, id = getCdpCountOf(owner, startNodeId, maxNodes);

    assert(count <= maxCount);
}

