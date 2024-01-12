
using SortedCdpsHarness as _SortedCdps;

/////////////////// METHODS ///////////////////////

methods {

    // SortedCdpsHarness
    function isListStructureValid() external returns (bool) envfree;
    function isNodeInList(bytes32 _id) external returns (bool) envfree; 
    function toCdpIdHarness(address owner, uint256 blockHeight, uint256 nonce) external returns (bytes32) envfree;
    function toCdpIdFunc(address owner, uint256 blockHeight, uint256 nonce) external returns (bytes32) envfree;
    function verifyAddressFormatting(bytes32 cdpId, address expectedAddress) external returns (bool) envfree;
    function countOwnerIds(address owner) external returns (uint256) envfree;
    function batchRemoveHarness(bytes32 _start, bytes32 _end) external;
    function insertHarness(address owner, uint256 _NICR, bytes32 _prevId, bytes32 _nextId) external returns (bytes32);
    function reInsertHarness(bytes32 _id, uint256 _newNICR, bytes32 _prevId, bytes32 _nextId) external;

    // SortedCdps
    function _SortedCdps.NAME() external returns (string) envfree;
    function _SortedCdps.borrowerOperationsAddress() external returns (address) envfree;
    function _SortedCdps.cdpManager() external returns (address) envfree;
    function _SortedCdps.maxSize() external returns (uint256) envfree;
    function _SortedCdps.nextCdpNonce() external returns (uint256) envfree;
    function _SortedCdps.dummyId() external returns (bytes32) envfree;
    // Summarizing as a deterministic and unique function. need to prove that this
    function _SortedCdps.toCdpId(address owner, uint256 blockHeight, uint256 nonce) external returns (bytes32) envfree;
    function _SortedCdps.toCdpId(address owner, uint256 blockHeight, uint256 nonce) internal returns (bytes32) 
        => uniqueId(owner, blockHeight, nonce);
    function _SortedCdps.getOwnerAddress(bytes32 cdpId) external returns (address) envfree;
    function _SortedCdps.nonExistId() external returns (bytes32) envfree;
    function _SortedCdps.cdpOfOwnerByIndex(address owner, uint256 index) external returns (bytes32) envfree;
    function _SortedCdps.cdpOfOwnerByIdx(address owner, uint256 index, bytes32 startNodeId, uint maxNodes) external returns (bytes32, bool) envfree;
    function _SortedCdps.cdpCountOf(address owner) external returns (uint256) envfree;
    function _SortedCdps.getCdpCountOf(address owner, bytes32 startNodeId, uint maxNodes) external returns (uint256, bytes32) envfree;
    function _SortedCdps.getCdpsOf(address owner) external returns (bytes32[]) envfree;
    function _SortedCdps.getAllCdpsOf(address owner, bytes32 startNodeId, uint maxNodes) external returns (bytes32[], uint256, bytes32) envfree;
    function _SortedCdps.insert(address owner, uint256 _NICR, bytes32 _prevId, bytes32 _nextId) external returns (bytes32);
    function _SortedCdps.remove(bytes32 _id) external;
    function _SortedCdps.batchRemove(bytes32[]) external;
    function _SortedCdps.reInsert(bytes32 _id, uint256 _newNICR, bytes32 _prevId, bytes32 _nextId) external;
    function _SortedCdps.contains(bytes32 _id) external returns (bool) envfree;
    function _SortedCdps.isFull() external returns (bool) envfree;
    function _SortedCdps.isEmpty() external returns (bool) envfree;
    function _SortedCdps.getSize() external returns (uint256) envfree;
    function _SortedCdps.getMaxSize() external returns (uint256) envfree;
    function _SortedCdps.getFirst() external returns (bytes32) envfree;
    function _SortedCdps.getLast() external returns (bytes32) envfree;
    function _SortedCdps.getNext(bytes32 _id) external returns (bytes32) envfree;
    function _SortedCdps.getPrev(bytes32 _id) external returns (bytes32) envfree;
    function _SortedCdps.validInsertPosition(uint256 _NICR, bytes32 _prevId, bytes32 _nextId) external returns (bool);
    function _SortedCdps.findInsertPosition(uint256 _NICR, bytes32 _prevId, bytes32 _nextId) external returns (bytes32, bytes32);

    // CdpManager
    function _.getCachedNominalICR(bytes32 _cdpId) external 
        => cachedNominalICR(_cdpId) expect uint256 ALL;
}

///////////////// DEFINITIONS /////////////////////

definition ID_IN_LIST(bytes32 _id) returns bool =
    _id != DUMMY_ID() && (_id == ghostHead || ghostPrevId[_id] != DUMMY_ID() || ghostNextId[_id] != DUMMY_ID());

definition DUMMY_ID() returns bytes32 = _SortedCdps.dummyId();

definition HARNESS_FUNCTIONS(method f) returns bool =
    f.selector == sig:batchRemoveHarness(bytes32, bytes32).selector
    || f.selector == sig:insertHarness(address, uint256, bytes32, bytes32).selector
    || f.selector == sig:reInsertHarness(bytes32, uint256, bytes32, bytes32).selector
    ;

definition REMOVE_FUNCTIONS(method f) returns bool =
    f.selector == sig:remove(bytes32).selector
    || f.selector == sig:batchRemove(bytes32[]).selector;

definition INSERT_FUNCTION(method f) returns bool =
    f.selector == sig:insert(address, uint256, bytes32, bytes32).selector;

definition REINSERT_FUNCTION(method f) returns bool =
    f.selector == sig:reInsert(bytes32, uint256, bytes32, bytes32).selector;

definition INSERT_FUNCTIONS(method f) returns bool =
    INSERT_FUNCTION(f) || REINSERT_FUNCTION(f);

definition HARNESS_REPLACED_FUNCTIONS(method f) returns bool =
    f.selector == sig:batchRemove(bytes32[]).selector
    || INSERT_FUNCTIONS(f)
    ;

definition HARNESS_REPLACED_OR_VIEW_FUNCTIONS(method f) returns bool =
    HARNESS_REPLACED_FUNCTIONS(f) || VIEW_PURE_FUNCTIONS(f);

definition HARNESS_OR_VIEW_FUNCTIONS(method f) returns bool =
    HARNESS_FUNCTIONS(f) || VIEW_PURE_FUNCTIONS(f);

////////////////// FUNCTIONS //////////////////////

// Summarizion for CdpManager.getCachedNominalICR()
function cachedNominalICR(bytes32 _cdpId) returns uint256 {
    return require_uint256(ghostCachedNominalICR[_cdpId]);
}

// Require a valid list structure
function setupList() {

    // Size could be from 0 to 4, it's enough to test all possible scenarios
    require(_SortedCdps.maxSize() <= 4);

    requireInvariant isListStructureValidInv;
    requireInvariant sortedCdpsMaxSizeGtZero;
    requireInvariant sortedCdpsSizeLeqMaxSize;
    requireInvariant sortedCdpsListEmptySolvency;
    requireInvariant sortedCdpsListOneItemSolvency;
    requireInvariant sortedCdpsListSeveralItemsSolvency;
    requireInvariant sortedCdpsListNotLinkedToSelf;
    requireInvariant sortedCdpsListZeroIdsNotSupported;
    requireInvariant sortedCdpsListNoDuplicates;
    requireInvariant sortedCdpsListNICRDescendingOrder;
}

///////////////// GHOSTS & HOOKS //////////////////

// toCdpId() summarization
ghost uniqueId(address, uint256, uint256) returns bytes32 {
    axiom forall address o1. forall address o2. forall uint256 b1. forall uint256 b2. forall uint256 n1. forall uint256 n2.
        (o1 != o2 || b1 != b2 || n1 != n2) => uniqueId(o1, b1, n1) != uniqueId(o2, b2, n2);
}

//
// Ghost copy of `data.head`
//

ghost bytes32 ghostHead {
    init_state axiom ghostHead == to_bytes32(0);
}

hook Sload bytes32 val _SortedCdps.data.head STORAGE {
    require(ghostHead == val);
}

hook Sstore _SortedCdps.data.head bytes32 val STORAGE {
    ghostHead = val;
}

//
// Ghost copy of `data.tail`
//

ghost bytes32 ghostTail {
    init_state axiom ghostTail == to_bytes32(0);
}

hook Sload bytes32 val _SortedCdps.data.tail STORAGE {
    require(ghostTail == val);
}

hook Sstore _SortedCdps.data.tail bytes32 val STORAGE {
    ghostTail = val;
}

//
// Ghost copy of `data.size`
//

ghost mathint ghostSize {
    init_state axiom ghostSize == 0;
}

hook Sload uint256 val _SortedCdps.data.size STORAGE {
    require(require_uint256(ghostSize) == val);
}

hook Sstore _SortedCdps.data.size uint256 val STORAGE {
    ghostSize = val;
}

//
// Ghost copy of `data.nodes[].nextId`
//

ghost mapping (bytes32 => bytes32) ghostNextId {
    init_state axiom forall bytes32 i. ghostNextId[i] == to_bytes32(0);
}

hook Sload bytes32 val _SortedCdps.data.nodes[KEY bytes32 i].nextId STORAGE {
    require(ghostNextId[i] == val);
}

hook Sstore _SortedCdps.data.nodes[KEY bytes32 i].nextId bytes32 val STORAGE {
    ghostNextId[i] = val;
}

//
// Ghost copy of `Data.nodes[].prevId`
//

ghost mapping (bytes32 => bytes32) ghostPrevId {
    init_state axiom forall bytes32 i. ghostPrevId[i] == to_bytes32(0);
}

hook Sload bytes32 val _SortedCdps.data.nodes[KEY bytes32 i].prevId STORAGE {
    require(ghostPrevId[i] == val);
}

hook Sstore _SortedCdps.data.nodes[KEY bytes32 i].prevId bytes32 val STORAGE {
    ghostPrevId[i] = val;
}

//
// Ghost copy of `nextCdpNonce`
//

ghost mathint ghostNextCdpNonce {
    init_state axiom ghostNextCdpNonce == 0;
    axiom ghostNextCdpNonce < max_uint64;
}

ghost mathint ghostNextCdpNoncePrev {
    init_state axiom ghostNextCdpNoncePrev == 0;
    axiom ghostNextCdpNoncePrev < max_uint64;
}

hook Sload uint256 val _SortedCdps.nextCdpNonce STORAGE {
    require(require_uint256(ghostNextCdpNonce) == val);
}

hook Sstore _SortedCdps.nextCdpNonce uint256 val STORAGE {
    ghostNextCdpNoncePrev = ghostNextCdpNonce;
    ghostNextCdpNonce = val;
}

//
// Ghost copy of `cachedNominalICR`
//

ghost mapping (bytes32 => mathint) ghostCachedNominalICR {
    init_state axiom forall bytes32 i. ghostCachedNominalICR[i] == 0;
}

hook Sload uint256 val _SortedCdps.cachedNominalICR[KEY bytes32 i] STORAGE {
    require(require_uint256(ghostCachedNominalICR[i]) == val);
}

hook Sstore _SortedCdps.cachedNominalICR[KEY bytes32 i] uint256 val STORAGE {
    ghostCachedNominalICR[i] = val;
}

///////////////// PROPERTIES //////////////////////

invariant isListStructureValidInv() _SortedCdps.isListStructureValid() 
    filtered { f -> !HARNESS_REPLACED_OR_VIEW_FUNCTIONS(f) } { 
    preserved { 
        // Size could be from 0 to 4, it's enough to test all possible scenarios
        requireInvariant sortedCdpsMaxSizeGtZero;
        requireInvariant sortedCdpsSizeLeqMaxSize;
        require(_SortedCdps.maxSize() <= 4); 
    } 
}

invariant sortedCdpsMaxSizeGtZero() _SortedCdps.maxSize() != 0
    filtered { f -> !HARNESS_REPLACED_OR_VIEW_FUNCTIONS(f) }

invariant sortedCdpsSizeLeqMaxSize() ghostSize <= to_mathint(_SortedCdps.maxSize())
    filtered { f -> !HARNESS_REPLACED_OR_VIEW_FUNCTIONS(f) }

invariant sortedCdpsListEmptySolvency() 
    // 0 items in the list
    (ghostHead == DUMMY_ID() || ghostTail == DUMMY_ID() || ghostSize == 0)
        // If any is zero, that everything zero
        => (ghostHead == DUMMY_ID() && ghostTail == DUMMY_ID() && ghostSize == 0 
            && (forall bytes32 i. ghostPrevId[i] == DUMMY_ID() && ghostNextId[i] == DUMMY_ID()))
filtered { f -> !HARNESS_REPLACED_OR_VIEW_FUNCTIONS(f) } { 
    preserved { 
        // Require a valid list structure for 1-item initial configuration
        requireInvariant isListStructureValidInv;
        requireInvariant sortedCdpsListOneItemSolvency;
    } 
}

invariant sortedCdpsListOneItemSolvency() 
    // 1 item in the list
    (ghostHead != DUMMY_ID() && ghostNextId[ghostHead] == DUMMY_ID()
        || ghostTail != DUMMY_ID() && ghostPrevId[ghostTail] == DUMMY_ID()
        || ghostHead != DUMMY_ID() && ghostHead == ghostTail
        || ghostSize == 1
    ) => (
        ghostHead != DUMMY_ID() 
        && ghostHead == ghostTail
        && ghostSize == 1 
        // Zero NICR should not be inserted
        && ghostCachedNominalICR[ghostHead] != 0
        // Only non existent CDPs should be inserted
        && ghostCdpStatus[ghostHead] == CDP_STATUS_NON_EXISTENT()
        // No prev or next set
        && (forall bytes32 i. ghostPrevId[i] == DUMMY_ID() && ghostNextId[i] == DUMMY_ID())
    )
filtered { f -> !HARNESS_REPLACED_OR_VIEW_FUNCTIONS(f) } { 
    preserved { 
        // Initially require valid list structure
        requireInvariant isListStructureValidInv;
        requireInvariant sortedCdpsListEmptySolvency;
        requireInvariant sortedCdpsListSeveralItemsSolvency;
        requireInvariant sortedCdpsListZeroIdsNotSupported;
    } 
}

invariant sortedCdpsListSeveralItemsSolvency() 
    // 2-4 items in the list
    (ghostHead != DUMMY_ID() && ghostHead != ghostTail 
        || ghostSize > 1
        || ghostHead != DUMMY_ID() && ghostNextId[ghostHead] != DUMMY_ID()
        || ghostTail != DUMMY_ID() && ghostPrevId[ghostTail] != DUMMY_ID()
    ) => (
        ghostHead != DUMMY_ID() && ghostTail != DUMMY_ID()
        && ghostHead != ghostTail
        && ghostSize > 1
        // Up to 4 nodes could be in a list
        && isNodeInList(ghostHead) && isNodeInList(ghostNextId[ghostHead]) 
        && isNodeInList(ghostTail) && isNodeInList(ghostPrevId[ghostTail])
        // Zero NICR should not be inserted
        && ghostCachedNominalICR[ghostHead] != 0
        && ghostCachedNominalICR[ghostTail] != 0
        && ghostCachedNominalICR[ghostNextId[ghostHead]] != 0
        && ghostCachedNominalICR[ghostPrevId[ghostTail]] != 0
        // Only non existent CDPs should be inserted
        && ghostCdpStatus[ghostHead] == CDP_STATUS_NON_EXISTENT()
        && ghostCdpStatus[ghostTail] == CDP_STATUS_NON_EXISTENT()
        && ghostCdpStatus[ghostNextId[ghostHead]] == CDP_STATUS_NON_EXISTENT()
        && ghostCdpStatus[ghostPrevId[ghostTail]] == CDP_STATUS_NON_EXISTENT()
        && (forall bytes32 i. 
            // All other nodes are empty
            (ghostPrevId[i] == DUMMY_ID() && ghostNextId[i] == DUMMY_ID())
            || (
                // Head linked with next
                (i == ghostHead => (ghostPrevId[ghostHead] == DUMMY_ID() && ghostPrevId[ghostNextId[i]] == i))
                // Body items linked with head and tail
                && (i != DUMMY_ID() && i != ghostHead && i != ghostTail => (
                    (i == ghostNextId[ghostHead]) && ghostPrevId[i] == ghostHead && (ghostNextId[i] == ghostPrevId[ghostTail] || ghostNextId[i] == ghostTail))
                    || (i == ghostPrevId[ghostTail] && ghostNextId[i] == ghostTail && (ghostPrevId[i] == ghostNextId[ghostHead] || ghostPrevId[i] == ghostHead))
                )
                // Tail linked with prev
                && (i == ghostTail => (ghostNextId[ghostTail] == DUMMY_ID() && ghostNextId[ghostPrevId[i]] == i))
            )
        )
    )
filtered { f -> !HARNESS_REPLACED_OR_VIEW_FUNCTIONS(f) } { 
    preserved { 
        // Initially require valid list structure
        requireInvariant isListStructureValidInv;
        requireInvariant sortedCdpsListEmptySolvency;
        requireInvariant sortedCdpsListOneItemSolvency;
    } 
}

invariant sortedCdpsListNotLinkedToSelf() 
    // Non-empty items could not link to each other
    forall bytes32 i. (
        (i != DUMMY_ID() || ghostPrevId[i] != DUMMY_ID() => ghostPrevId[i] != i)
        && (i != DUMMY_ID() || ghostNextId[i] != DUMMY_ID() => ghostNextId[i] != i)
        && (ghostPrevId[i] != DUMMY_ID() || ghostNextId[i] != DUMMY_ID() => ghostPrevId[i] != ghostNextId[i])
        )
filtered { f -> !HARNESS_REPLACED_OR_VIEW_FUNCTIONS(f) } { 
    preserved { 
        // Require a valid list structure
        requireInvariant isListStructureValidInv;
        requireInvariant sortedCdpsListEmptySolvency;
        requireInvariant sortedCdpsListOneItemSolvency;
        requireInvariant sortedCdpsListSeveralItemsSolvency;
    } 
}

invariant sortedCdpsListZeroIdsNotSupported() 
    forall bytes32 i. ghostPrevId[i] != DUMMY_ID() || ghostNextId[i] != DUMMY_ID() 
        => i != DUMMY_ID() 
filtered { f -> !HARNESS_REPLACED_OR_VIEW_FUNCTIONS(f) } { 
    preserved { 
        // Require a valid list structure
        requireInvariant isListStructureValidInv;
        requireInvariant sortedCdpsListOneItemSolvency;
    } 
}

invariant sortedCdpsListNoDuplicates() 
    // Prev and Next should be uniq
    forall bytes32 i. forall bytes32 j. i != j && i != DUMMY_ID() && j != DUMMY_ID()
        => (ghostPrevId[i] == DUMMY_ID() && ghostNextId[i] == DUMMY_ID()
            || ((ghostPrevId[i] != DUMMY_ID() => ghostPrevId[i] != ghostPrevId[j])
                && (ghostNextId[i] != DUMMY_ID() => ghostNextId[i] != ghostNextId[j])))
filtered { f -> !HARNESS_REPLACED_OR_VIEW_FUNCTIONS(f) } { 
    preserved { 
        // Require a valid list structure
        requireInvariant isListStructureValidInv;
        requireInvariant sortedCdpsListEmptySolvency;
        requireInvariant sortedCdpsListOneItemSolvency;
        requireInvariant sortedCdpsListSeveralItemsSolvency;
    } 
} 

invariant sortedCdpsListNICRDescendingOrder() 
    forall bytes32 i. i != DUMMY_ID() 
        => (
            // Not in list (or only one id in list)
            (ghostPrevId[i] == DUMMY_ID() && ghostNextId[i] == DUMMY_ID())
            // Id with valid prev
            || ((ghostPrevId[i] != DUMMY_ID() => ghostCachedNominalICR[i] <= ghostCachedNominalICR[ghostPrevId[i]])
            // Id with valid next
                && (ghostNextId[i] != DUMMY_ID() => ghostCachedNominalICR[i] >= ghostCachedNominalICR[ghostNextId[i]]))
        )
filtered { f -> !HARNESS_REPLACED_OR_VIEW_FUNCTIONS(f) } { 
    preserved { 
        // Require a valid list structure
        requireInvariant isListStructureValidInv;
        requireInvariant sortedCdpsListEmptySolvency;
        requireInvariant sortedCdpsListOneItemSolvency;
        requireInvariant sortedCdpsListSeveralItemsSolvency;
    } 
} 

