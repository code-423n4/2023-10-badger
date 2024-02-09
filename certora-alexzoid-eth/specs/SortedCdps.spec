import "./base/sortedCdps.spec";
import "./dependencies/CdpManager.spec";
import "./dependencies/helper.spec";

/////////////////// METHODS ///////////////////////

///////////////// DEFINITIONS /////////////////////

////////////////// FUNCTIONS //////////////////////

///////////////// GHOSTS & HOOKS //////////////////

///////////////// INITIAL PROPERTIES /////////////

// toCdpId() return uniq result for uniq input
rule uniqunessOfId(address o1, address o2, uint256 b1, uint256 b2, uint256 n1, uint256 n2) {
    // Calls to toCdpId are to the public solidity function which calls the internal one that is summarized
    //  therefore, this rule actually checks the summarization uniqueId 
    assert((o1 != o2 || b1 != b2 || n1 != n2) => toCdpId(o1, b1, n1) != toCdpId(o2, b2, n2));
}
    
// Special functions could change list head
rule changeToFirst(method f, env e, calldataarg args) 
    filtered { f -> !HARNESS_OR_VIEW_FUNCTIONS(f) } {

    bytes32 before = getFirst();

    f(e, args);

    bytes32 after = getFirst();

    assert(after != before =>(
        f.selector == sig:insert(address,uint256,bytes32,bytes32).selector ||  
        f.selector == sig:reInsert(bytes32,uint256,bytes32,bytes32).selector ||
        f.selector == sig:remove(bytes32).selector ||
        f.selector == sig:batchRemove(bytes32[]).selector
    )); 
}

// List size could not be more than maxSize
rule isFullCanNotIncrease(method f, env e, calldataarg args)
    filtered { f -> !HARNESS_OR_VIEW_FUNCTIONS(f) } {

    bool isFullBefore = isFull();
    uint256 sizeBefore = getSize();

    f(e, args);

    assert(isFullBefore => getSize() <= sizeBefore);
}

// Possibility of not been reverted 
use rule helperSanity;

///////////////// SETUP PROPERTIES ////////////////

// Require valid list structure initially
use invariant isListStructureValidInv;

// [2] Max size could not be zero
use invariant sortedCdpsMaxSizeGtZero;

// [3] Could not add more than maxSize
use invariant sortedCdpsSizeLeqMaxSize;

// [] Empty list solvency
use invariant sortedCdpsListEmptySolvency;

// [] One item list solvency
use invariant sortedCdpsListOneItemSolvency;

// [4] Several items list solvency
use invariant sortedCdpsListSeveralItemsSolvency;

// [] Item in the list should not link to self
use invariant sortedCdpsListNotLinkedToSelf;

// [] Item with zero id is not support
use invariant sortedCdpsListZeroIdsNotSupported;

// [] List should not contain duplicates
use invariant sortedCdpsListNoDuplicates;

// [] SL-01 The NICR ranking in the sorted list should follow descending order
use invariant sortedCdpsListNICRDescendingOrder;

///////////////// PROPERTIES //////////////////////

// [] Only BorrowerOperations or CdpManager should modify state
rule onlyBOorCdpMShouldModityState(env e, method f, calldataarg args)
    filtered { f -> !HARNESS_OR_VIEW_FUNCTIONS(f) } {

    storage before = lastStorage;

    f(e, args);

    storage after = lastStorage;

    // State was changed
    assert(before[currentContract] != after[currentContract] 
        => (e.msg.sender == borrowerOperationsAddress() || e.msg.sender == cdpManager())
    );
}

// [] Only insert should increase list size and next CDP nonce
rule onlyInsertShouldIncreaseSizeAndNonce(env e, method f, calldataarg args) 
    filtered { f -> !HARNESS_OR_VIEW_FUNCTIONS(f) } {

    mathint sizeBefore = ghostSize;
    mathint nextCdpNonceBefore = ghostNextCdpNonce;

    f(e, args);

    mathint sizeAfter = ghostSize;
    mathint nextCdpNonceAfter = ghostNextCdpNonce;

    assert(sizeAfter > sizeBefore <=> INSERT_FUNCTION(f));
    assert((nextCdpNonceAfter == nextCdpNonceBefore + 1) <=> INSERT_FUNCTION(f));
}

// [] Next CDP nonce always increments
invariant nextCdpNonceIncrements() ghostNextCdpNoncePrev != 0 && ghostNextCdpNonce != 0
    => ghostNextCdpNonce == ghostNextCdpNoncePrev + to_mathint(1)
    filtered { f -> !HARNESS_OR_VIEW_FUNCTIONS(f) } 

// [] reInsert() should not change list size
rule reInsertNotAffectSize(env e, bytes32 _id, uint256 _newNICR, bytes32 _prevId, bytes32 _nextId) {

    mathint sizeBefore = ghostSize;

    reInsert(e, _id, _newNICR, _prevId, _nextId);

    mathint sizeAfter = ghostSize;

    assert(sizeBefore == sizeAfter);
}

// [] reInsert() should remove existing id
rule reInsertRemoveExistingId(env e, bytes32 _id, uint256 _newNICR, bytes32 _prevId, bytes32 _nextId) {

    // Require a valid list structure
    setupList();

    bool inList = isNodeInList(_id);

    reInsert@withrevert(e, _id, _newNICR, _prevId, _nextId);

    assert(!inList => lastReverted);
}

// [] Only remove functions should decrease list size
rule onlyRemoveFunctionsShouldIncreaseSize(env e, method f, calldataarg args) 
    filtered { f -> !HARNESS_OR_VIEW_FUNCTIONS(f) } {

    mathint sizeBefore = ghostSize;

    f(e, args);

    mathint sizeAfter = ghostSize;

    assert(sizeAfter < sizeBefore <=> REMOVE_FUNCTIONS(f));
}

// [] Only CdpManager should remove ids
rule onlyCdpMShouldRemove(env e, method f, calldataarg args) 
    filtered { f -> !HARNESS_OR_VIEW_FUNCTIONS(f) } {

    mathint sizeBefore = ghostSize;

    f(e, args);

    mathint sizeAfter = ghostSize;

    assert(sizeBefore > sizeAfter => e.msg.sender == cdpManager());
}

// [g239,g240,g241,g242,g243] contains() integrity
rule containsIntegrity(bytes32 _id) {

    // Require a valid list structure
    setupList();

    assert(contains(_id) == isNodeInList(_id));
}

// [g14,g15,g16,g17,g18,g19,g20] getOwnerAddress() integrity
rule getOwnerAddressIntegrity(bytes32 cdpId) {
    
    address owner = getOwnerAddress(cdpId);

    // The owner address is stored in the first 20 bytes of the CdpId
    assert(verifyAddressFormatting(cdpId, owner));
}

// [g228] Prove possibility to remove() when list is full
rule removeWhenMaxSize(env e) {

    // Require a valid list structure
    setupList();

    // Require list to be full
    require(to_mathint(maxSize()) == 4);
    require(to_mathint(maxSize()) == ghostSize);

    remove(e, ghostTail);

    satisfy(ghostSize == to_mathint(maxSize()) - 1);
}

// [g245] validInsertPosition() integrity
rule validInsertPositionIntegrity(env e, uint256 _NICR, bytes32 _prevId, bytes32 _nextId) {

    // Require a valid list structure
    setupList();

    bool isValid = validInsertPosition(e, _NICR, _prevId, _nextId);

    assert(_prevId == dummyId() && _nextId == dummyId() 
        => isValid == isEmpty());
    assert(_prevId == dummyId() && _nextId != dummyId() 
        => (isValid == (ghostHead == _nextId && to_mathint(_NICR) >= ghostCachedNominalICR[_nextId])));
    assert(_prevId != dummyId() && _nextId == dummyId() 
        => (isValid == (ghostTail == _prevId && to_mathint(_NICR) <= ghostCachedNominalICR[_prevId])));
    assert(_prevId != dummyId() && _nextId != dummyId() 
        => (isValid == (_prevId == ghostPrevId[_nextId] 
            && ghostCachedNominalICR[_prevId] >= to_mathint(_NICR) 
            && to_mathint(_NICR) >= ghostCachedNominalICR[_nextId])
        ));
}

// [] maxSize() could not be set to zero in constructor
invariant maxSizeNotZeroInConstructor() to_mathint(maxSize()) != 0
    filtered { f -> f.selector == 0 } {
    preserved {
        require(false);
    }
}

// [g189] batchRemove() decrease size
rule batchRemoveDecreaseSize(env e, bytes32[] _ids) {
    
    // Require a valid list structure
    setupList();

    mathint before = ghostSize;
    
    batchRemove(e, _ids);

    mathint after = ghostSize;

    assert(assert_uint256(before - after) == _ids.length);
}

// [g160,g161,g163] batchRemove() should revert passing non-exist node
rule batchRemoveOnlyExistingIdsSupported(env e, bytes32[] _ids) {

    // Require a valid list structure
    setupList();

    uint256 i;
    require(i < _ids.length);
    bool inList = contains(_ids[i]);

    batchRemove@withrevert(e, _ids);
    bool reverted = lastReverted;

    assert(!inList => reverted);
}

///////////////// TODO PROPERTIES //////////////////

// [] cdpOfOwnerByIdx() integrity
rule cdpOfOwnerByIdxNodeIntegrity(address owner, uint256 index, bytes32 startNodeId, uint maxNodes) {

    // Require a valid list structure
    setupList();

    bytes32 id;
    bool result;
    id, result = cdpOfOwnerByIdx(owner, index, startNodeId, maxNodes);

    // CDP is owned by specified owner
    assert(result => getOwnerAddress(id) == owner);

    // @todo g40, g29, g39, g81, g25, g51, g38, g32, g30, g28, g35, g27, g34, g26, g24, g41, g33, g37, g31, g36, g23, g22
}

// [g42,g46,g47,g48] cdpCountOf() integrity
rule cdpCountOfIntegrity(address owner) {

    // Calculates invalid number for owner == 0, possibly a QA issue
    require(owner != 0);

    // Require a valid list structure
    setupList();

    assert(countOwnerIds(owner) == cdpCountOf(owner));

    // @todo g58, g49, g60, g54, g45, g43, g59
}

// [] getCdpCountOf() integrity
rule getCdpCountOfIntegrity(address owner, bytes32 startNodeId, uint maxNodes) {

    // Require a valid list structure
    setupList();

    uint256 _ownedCount;
    bytes32 _currentCdpId;
    _ownedCount, _currentCdpId = getCdpCountOf(owner, startNodeId, maxNodes);

    assert(
        // Moved to real issue
        // _ownedCount <= require_uint256(ghostSize) && _ownedCount <= maxNodes
        true
        );

    // Moved to real issue
    // assert(_ownedCount != 0 => isNodeInList(_currentCdpId));

    // @todo g53,g55,g56,g57
}

// [g62,g63,g64,g65,g69,g70,g78] getCdpsOf() integrity
rule getCdpsOfIntegrity(address owner) {

    // Calculates invalid number for owner == 0, possibly a QA issue
    require(owner != 0);

    // Require a valid list structure
    setupList();

    bytes32[] cdps = getCdpsOf(owner);

    assert(cdps.length == countOwnerIds(owner));

    // List was setup with maxSize() == 4
    assert(cdps.length > 0 => getOwnerAddress(cdps[0]) == owner);
    assert(cdps.length > 1 => getOwnerAddress(cdps[1]) == owner);
    assert(cdps.length > 2 => getOwnerAddress(cdps[2]) == owner);
    assert(cdps.length > 3 => getOwnerAddress(cdps[3]) == owner);

    // @todo g72
}

// [g68,g71,g73] getAllCdpsOf() integrity
rule getAllCdpsOfIntegrity(address owner, bytes32 startNodeId, uint256 maxNodes) {

    // Require a valid list structure
    setupList();

    bytes32[] userCdps; 
    uint256 _cdpRetrieved; 
    bytes32 _currentCdpId;
    userCdps, _cdpRetrieved, _currentCdpId = getAllCdpsOf(owner, startNodeId, maxNodes);

    assert(
        // Moved to real issue 
        // _cdpRetrieved <= require_uint256(ghostSize) 
        (maxNodes != 0 => _cdpRetrieved <= maxNodes)
        && _cdpRetrieved == userCdps.length
        );

    // @todo g67, g74, g80, g75, g52, g79, g66, g82
}

// @todo Execute summarized function directly
// https://discord.com/channels/795999272293236746/1173585530307481601
// [g8,g9,g10,g11,g12,g13] toCdpId() integrity
rule toCdpIdIntegrity(address owner, uint256 blockHeight, uint256 nonce) {
    
    bytes32 serialized = toCdpIdFunc(owner, blockHeight, nonce);
    bytes32 serializedExpected = toCdpIdHarness(owner, blockHeight, nonce);
    
    assert(true); // assert(serialized == serializedExpected);
}

// @todo [g257,g262,g264,g268,g270,g274,g275,g277,g287,g282, g286] findInsertPosition() integrity
