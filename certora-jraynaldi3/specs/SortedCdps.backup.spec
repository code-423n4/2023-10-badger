
using CdpManager as _cdpManager;
/*

verification of SortedCdps
This is an advnaced project and requires probably qunatifiers and more summarization.
see https://github.com/Certora/Examples/tree/master/CVLByExample/QuantifierExamples 


*/
methods {
    function contains(bytes32 _id) external  returns (bool) envfree;
    function contains(bytes32 _id) external  returns (bool) => isExists(_id);

    function isFull() external  returns (bool) envfree; 

    function isEmpty() external  returns (bool) envfree;

    function nonExistId() external returns (bytes32) envfree;

    function getSize() external  returns (uint256) envfree;

    function getMaxSize() external  returns (uint256) envfree;

    function getFirst() external  returns (bytes32) envfree;

    function getLast() external  returns (bytes32) envfree;

    function getNext(bytes32 _id) external  returns (bytes32) envfree;

    function getPrev(bytes32 _id) external  returns (bytes32) envfree;

    function getOwnerAddress(bytes32 cdpId) external returns(address) envfree;

    function nextCdpNonce() external returns(uint256) envfree;

    function findInsertPosition(uint256, bytes32, bytes32) external returns(bytes32, bytes32) envfree;

    function cdpManager() external returns(address) envfree;

    function borrowerOperationsAddress() external returns(address) envfree;

    // harness 
    function descendList(uint256, bytes32) external returns(bytes32, bytes32) envfree;
    function ascendList(uint256, bytes32) external returns(bytes32, bytes32) envfree;
    function getNICR(bytes32) external returns(uint256) envfree;
    /* summarizing as a deterministic and unique function. need to prove that this.
        see certora/specs/SortedCdps_DpdIds.spec 
    */
    function toCdpId(
        address owner,
        uint256 blockHeight,
        uint256 nonce
    ) internal returns (bytes32) => uniqueId(owner,blockHeight,nonce);

    function toCdpId(
        address owner,
        uint256 blockHeight,
        uint256 nonce
    ) external returns (bytes32) envfree;


    // CdpManager
    /* placeholder - NONDET is the default (safe) summarization but might be 
    too over apporximation for certrain properties
    */
    function _.getNominalICR(bytes32) external  => NONDET;
    function _.getCdpStatus(bytes32) external => NONDET;
    function _cdpManager.getCachedNominalICR(bytes32 _cdpId ) external returns(uint256) => _getNICR(_cdpId);
    function _cdpManager.getCachedNominalICR(bytes32 _cdpId ) external returns(uint256) envfree;

}

ghost _getNICR(bytes32 ) returns uint256 {
    axiom forall bytes32 id. forall bytes32 id2.
    (id == to_bytes32(0x0) <=> _getNICR(id) == 0) && _getNICR(id) < 2 ^ 32 && (id != id2 => _getNICR(id) != _getNICR(id2));
}
ghost uniqueId(address /*owner*/, uint256 /*blockHeight*/, uint256 /*nonce*/ ) returns bytes32 {
    axiom forall address o1. forall address o2. 
    forall uint256 b1. forall uint256 b2.
    forall uint256 n1. forall uint256 n2.
    ( o1 != o2 || b1 != b2 || n1 != n2 ) => uniqueId(o1, b1, n1) != uniqueId(o2, b2, n2);
}

rule uniqunessOfId(address o1,  address o2,
        uint256 b1,  uint256 b2, 
        uint256 n1,  uint256 n2) 
{
// calls to toCdpId are to the public solidity function which calls the internal one that is summarized
// therefore, this rule actually checks the summarization uniqueId 
assert ( o1 != o2 || b1 != b2 || n1 != n2 ) => toCdpId(o1, b1, n1) != toCdpId(o2, b2, n2);

}
    

rule reachability(method f) {
    env e;
    calldataarg args;
    f(e,args);
    satisfy true;
}

rule changeToFirst(method f) {
    bytes32 before = getFirst();

    env e;
    calldataarg args;
    f(e,args);

    bytes32 after = getFirst();
    assert after != before =>
        (   f.selector == sig:insert(address,uint256,bytes32,bytes32).selector ||  
            f.selector == sig:reInsert(bytes32,uint256,bytes32,bytes32).selector ||
            f.selector == sig:remove(bytes32).selector ||
            f.selector == sig:batchRemove(bytes32[]).selector ); 
}

rule isFullCanNotIncrease(method f) {
    bool isFullBefore = isFull();
    uint256 sizeBefore = getSize();

    env e;
    calldataarg args;
    f(e,args);

    assert  isFullBefore =>  getSize() <= sizeBefore ;
}

invariant maxSizeIntegrity() 
    getSize() <= getMaxSize();



/***********************    PARTICIPANT  ************************/

/***********************    MISC         ************************/

ghost isExists(bytes32 ) returns bool  {
    axiom forall bytes32 _id.
    size == 0  => !isExists(_id);
}

ghost uint256 size{
    init_state axiom size == 0;
}

hook Sload uint256 v currentContract.data.size STORAGE {
    require size == v;
}

hook Sstore currentContract.data.size uint256 v STORAGE {
    size = v; 
}

/** FIRST ID **/
ghost bytes32 first{
    init_state axiom first == to_bytes32(0x0);
}

hook Sload bytes32 v currentContract.data.head STORAGE {
    require first == v;
}

hook Sstore currentContract.data.head bytes32 v STORAGE {
    first = v; 
}
/** LAST ID **/
ghost bytes32 last{
    init_state axiom last == to_bytes32(0x0);
}

hook Sload bytes32 v currentContract.data.tail STORAGE {
    require last == v;
}

hook Sstore currentContract.data.tail bytes32 v STORAGE {
    last = v; 
}
/** NEXT ID **/ 
ghost mapping(bytes32 => bytes32) next{
    init_state axiom forall bytes32 id. next[id] == to_bytes32(0x0);
}

hook Sload bytes32 v currentContract.data.nodes[KEY bytes32 id].nextId STORAGE {
    require next[id] == v && prev[v] == id;
    require next[id] != first;
    require next[id] != id;
    require id == last => next[id] == to_bytes32(0x0);
    require size == 1  => next[id] == to_bytes32(0x0);
}

hook Sstore currentContract.data.nodes[KEY bytes32 id].nextId bytes32 v STORAGE {
    next[id] = v; 
}

/** PREV ID **/ 
ghost mapping(bytes32 => bytes32) prev{
    init_state axiom forall bytes32 id. prev[id] == to_bytes32(0x0);
}

hook Sload bytes32 v currentContract.data.nodes[KEY bytes32 id].prevId STORAGE {
    require prev[id] == v && next[v] == id;
    require prev[id] != last;
    require prev[id] != id;
    require id == first => prev[id] == to_bytes32(0x0);
    require size == 1  => prev[id] == to_bytes32(0x0);
}

hook Sstore currentContract.data.nodes[KEY bytes32 id].prevId bytes32 v STORAGE {
    prev[id] = v; 
}

/**
 * SetupId explaination 
 * because every invariant have several requirement for each other, linked each other so 
 * we need this setup to compile all invariants in one then check it with invariant if the argument still hold
*/ 
function setupId(bytes32 id, bytes32 other) {
    require first == id => prev[id] == nonExistId();
    require first == id && last != id => contains(next[id]) ;
    require last == id => next[id] == nonExistId();
    require last == id && first != id => contains(prev[id]) ;
    require first == other => prev[other] == nonExistId();
    require last == other => next[other] == nonExistId();
    require prev[id] != last;
    require next[id] != first;
    require prev[other] != last;
    require next[other] != first;
    require next[id] != nonExistId() <=> contains(next[id]);
    require prev[id] != nonExistId() <=> contains(prev[id]);
    require next[other] != nonExistId() <=> contains(next[other]);
    require prev[other] != nonExistId() <=> contains(prev[other]);
    require (next[id] != nonExistId() => prev[next[id]] == id) && (prev[id] != nonExistId() => next[prev[id]] == id);
    require (next[other] != nonExistId() => prev[next[other]] == other) && (prev[other] != nonExistId() => next[prev[other]] == other);
    require contains(id) && first != id && last != id => prev[id] != nonExistId() && next[id] != nonExistId();
    require contains(other) && first != other && last != other => prev[other] != nonExistId() && next[other] != nonExistId();
    require id != nonExistId() && other != nonExistId() => (next[id] == other <=> prev[other] == id);
    require id != nonExistId() && other != nonExistId() => (next[other] == id <=> prev[id] == other);
    require id != nonExistId() && other != nonExistId() && next[other] != nonExistId() && next[id] != nonExistId() => next[id] != next[other];
    require id != nonExistId() && other != nonExistId() && next[other] != nonExistId() && next[id] != nonExistId() => prev[id] != prev[other];
    require id != nonExistId() && prev[id] != nonExistId() && next[id] != nonExistId() => prev[id] != next[id]; 
    require id != nonExistId() => prev[id] != id && next[id] != id;
    require size == 1 => first == last;
    require first == last => size == 1 && (first == id => !contains(other)) &&  (first == other => !contains(id)) && (first == id <=> contains(id)) && (first == other <=> contains(other));
    require isEmpty() => last == nonExistId() && first == nonExistId() && !contains(other) && !contains(id);
    require !isEmpty() => last != nonExistId() && first != nonExistId();
    require prev[id] != nonExistId() || next[id] != nonExistId() => contains(id);
}
/***********************    HIGH LEVEL   ************************/

/// @notice isEmpty means first and last is nonExist
invariant isEmptyIntegrity()
    isEmpty() <=> last == nonExistId() && first == nonExistId()
    filtered {
        f -> f.selector != sig:batchRemove(bytes32[]).selector && !f.isView
    }{
        preserved with (env e) {
            bytes32 other;bytes32 id;
            setupId(id, other);
        }
    }

/// @notice head should never have prevId
invariant head_integrity(bytes32 id)
    first == id || !contains(id) <=> prev[id] == nonExistId()
    {
        preserved with (env e) {
            bytes32 other;
            setupId(id, other);
        }
    }

/// @notice tail should never have nextId
invariant tail_integrity(bytes32 id)
    last == id || !contains(id) <=> next[id] == nonExistId()
    {
        preserved with (env e) {
            bytes32 other;
            setupId(id, other);
        }
    }

/// @notice if neither head or tail id that exist should have prev and next
// invariant contains_integrity(bytes32 id)
//     contains(id) && first != id && last != id => prev[id] != nonExistId() && next[id] != nonExistId()
//     {
//         preserved with (env e) {
//             bytes32 other;
//             setupId(id, other);
//         }
//     }

/// @notice if next of id is other then prev of other is id
invariant next_prev_correlation(bytes32 id, bytes32 other)
    id != nonExistId() && other != nonExistId() => (next[id] == other <=> prev[other] == id)
    filtered {
        f -> f.selector != sig:batchRemove(bytes32[]).selector && !f.isView
    }
    {
        preserved with (env e) {
            setupId(id, other);
        }
    }

/// @notice next id should not sama one and another since id is unique, except for nonExistId
invariant nextId_uniquieness(bytes32 id, bytes32 other)
    id != nonExistId() && other != nonExistId() && next[other] != nonExistId() && next[id] != nonExistId() && id != other => next[id] != next[other]
    {
        preserved with (env e) {
            setupId(id, other);
        }
    }

/// @notice prev id should not sama one and another since id is unique, except for nonExistId
invariant prevId_uniquieness(bytes32 id, bytes32 other)
    id != nonExistId() && other != nonExistId() && prev[other] != nonExistId() && prev[id] != nonExistId() && id != other => prev[id] != prev[other]
    {
        preserved with (env e) {
            setupId(id, other);
        }
    }

/// @notice next and prev cannot be the same since all id is unique
invariant prev_next_uniqueness(bytes32 id)
    id != nonExistId() && prev[id] != nonExistId() && next[id] != nonExistId() => prev[id] !=  next[id]
    filtered {
        f -> f.selector != sig:batchRemove(bytes32[]).selector && !f.isView
    }{
        preserved with (env e) {
            bytes32 other;
            setupId(id, other);
        }
    }

/// @notice contains mean the id have either prev or next id 
invariant prev_next_contains_connection(bytes32 id )
    prev[id] != nonExistId() || next[id] != nonExistId() || size == 1 || first == last <=> contains(id)
    {
        preserved with (env e) {
            bytes32 other; 
            setupId(id, other);
        }
    }

/// @notice next and prev cannot be the same as id since all id is unique
invariant id_uniqueness(bytes32 id)
    id != nonExistId() => prev[id] != id && next[id] != id
    filtered {
        f -> f.selector != sig:batchRemove(bytes32[]).selector && !f.isView
    }{
        preserved with (env e) {
            bytes32 other;
            setupId(id, other);
        }
    }

// invariant sizeOne(bytes32 id, bytes32 other) 
//     first == last => size == 1 && (first == id => !contains(other)) &&  (first == other => !contains(id)) && (first == id <=> contains(id)) && (first == other <=> contains(other))
//     {
//         preserved with (env e) {
//             setupId(id, other);
//         }
//     }

/// @notice theres several function that can only called by cdpManager or BorroweOperation
rule onlyCdpManagerOrBO(env e, method f, calldataarg args){
    f@withrevert(e, args);
    bool isRevert = lastReverted;
    assert (f.selector == sig:insert(address,uint256,bytes32,bytes32).selector 
        || f.selector == sig:reInsert(bytes32,uint256,bytes32,bytes32).selector)
        && (e.msg.sender != borrowerOperationsAddress() && e.msg.sender != cdpManager())
        => isRevert;
    assert (f.selector == sig:remove(bytes32).selector || f.selector == sig:batchRemove(bytes32[]).selector)
        && e.msg.sender != cdpManager()
        => isRevert;
}

/// @notice the contract sort NICR descending
invariant NICRPrevIsHigher(bytes32 id)
    prev[id] != nonExistId() => getNICR(id) <= getNICR(prev[id])
    filtered {
        f -> f.selector != sig:batchRemove(bytes32[]).selector && !f.isView
    }{
        preserved with (env e) {
            bytes32 other;
            setupId(id,other);
        } 
        preserved insert(address owner, uint256 _NICR, bytes32 _prevId, bytes32 _nextId) with (env e1){
            bytes32 ownerId = toCdpId(owner, e1.block.number, nextCdpNonce());
            bytes32 other1;
            setupId(id,other1);
            require _NICR == getNICR(ownerId);
        }
        preserved reInsert(bytes32 _id, uint256 _newNICR, bytes32 _prevId, bytes32 _nextId) with (env e2){
            require _newNICR == getNICR(_id);
        }
    }

/***********************    UNIT TEST    ************************/

///@notice toCdpId should produce owner same as getOwnerAddress show
rule toCdpId_inverse(
    env e,
    address owner,
    uint256 blockHeight,
    uint256 nonce
) {
    require blockHeight < 2 ^ 32;
    require nonce <  2 ^ 32;
    bytes32 cdpId = toCdpId(owner, blockHeight,nonce );
    assert getOwnerAddress(cdpId) == owner;
}

/// @notice insert to empty data should start with head
rule insert_empty(
    env e ,
    address owner,
    uint256 NICR,
    bytes32 prevId,
    bytes32 nextId
) {
    requireInvariant isEmptyIntegrity();
    bool empty = isEmpty();
    uint256 nonce = nextCdpNonce();
    bytes32 id = toCdpId(owner, e.block.number, nonce);
    bytes32 other;
    setupId(prevId, nextId);
    setupId(nextId, prevId);
    setupId(id, other);

    insert(e, owner, NICR, prevId, nextId);

    assert empty => first == last && first == id;
    assert empty => prev[id] == next[id] && prev[id] == nonExistId();
}

/// @notice insert should add contains
rule insert_contains(
    env e ,
    address owner,
    uint256 NICR,
    bytes32 prevId,
    bytes32 nextId
) {
    uint256 nonce = nextCdpNonce();
    bytes32 id = toCdpId(owner, e.block.number, nonce);
    bool before = contains(id);
    insert(e, owner, NICR, prevId, nextId);
    bool after = contains(id);
    assert !before => after;
}

/// @notice remove should remove contains
rule remove_contains(
    env e, 
    bytes32 id
) {
    require contains(id) && first != id && last != id => prev[id] != nonExistId() && next[id] != nonExistId();    
    require !isEmpty() => last != nonExistId() && first != nonExistId();
    require size == 1 => first == last;
    require first == last => size == 1 && (first == id <=> contains(id));
    require isEmpty() => last == nonExistId() && first == nonExistId() && !contains(id);
    bool before = contains(id);
    remove(e, id);
    bool after = contains(id);
    assert before => !after;
}

/// @notice remove mean delete its id and merge the prev and next 
rule remove_prev_next(
    env e,
    bytes32 id 
) {
    require contains(id) && first != id && last != id => prev[id] != nonExistId() && next[id] != nonExistId();    
    require !isEmpty() => last != nonExistId() && first != nonExistId();
    require size == 1 => first == last;
    require first == last => size == 1 && (first == id <=> contains(id));
    require isEmpty() => last == nonExistId() && first == nonExistId() && !contains(id);
    bytes32 prevBefore = prev[id];
    bytes32 nextBefore = next[id];
    requireInvariant next_prev_correlation(prevBefore, id);
    requireInvariant next_prev_correlation(id, nextBefore);
    requireInvariant head_integrity(id);
    requireInvariant tail_integrity(id);

    remove(e,id);

    assert nextBefore != nonExistId() => prev[nextBefore] == prevBefore;
    assert prevBefore != nonExistId() => next[prevBefore] == nextBefore;
}

/// @notice reinsert should satisfy some requirement 
rule reInsert_revertion(env e, bytes32 id, uint256 NICR, bytes32 _prev, bytes32 _next){
    bool containsBefore = contains(id);
    reInsert@withrevert(e, id, NICR, _prev, _next);
    bool isReverted = lastReverted;
    assert NICR == 0 => isReverted;
    assert !containsBefore => isReverted;
}

/// @notice validInsertPosition integrity can gave valid positions
rule validInsertPosition_integrity(
    env e,
    uint256 NICR,
    bytes32 _prev,
    bytes32 _next
) {
    uint256 _prevNICR = getNICR(_prev);
    uint256 _nextNICR = getNICR(_next);
    bool isValidPos = validInsertPosition(e, NICR, _prev, _next);
    assert _prev == nonExistId() && _next == nonExistId() => isValidPos == isEmpty() , "1";
    assert _prev == nonExistId() && _next != nonExistId() => isValidPos == (first == _next && NICR >= _nextNICR) , "2";
    assert _prev != nonExistId() && _next == nonExistId() => isValidPos == (last == _prev && NICR <= _prevNICR) , "3";
    assert _prev != nonExistId() && _next != nonExistId() 
        => isValidPos == 
        (next[_prev] == _next 
        && _prevNICR >= NICR 
        && NICR >= _nextNICR) , "4";
}

/// @notice descendingList should return correct positions
rule _descendList_integrity(
    env e,
    uint256 NICR,
    bytes32 startId
) {
    bytes32 _prev;
    bytes32 _next;
    uint256 startNICR = getNICR(startId);
    _prev, _next = descendList(NICR, startId);
    assert startId == first && NICR >= startNICR => _prev == nonExistId() && _next == first; 
}

/// @notice descendingList should return correct positions
rule _descendList_integrity2(
    env e,
    uint256 NICR,
    bytes32 startId
) {
    bytes32 _prev;
    bytes32 _next;
    uint256 startNICR = getNICR(startId);
    bytes32 startNext = next[startId];
    bool isValid = validInsertPosition(e, NICR, startId, startNext);
    _prev, _next = descendList(NICR, startId);
    assert startId != first && isValid => _prev == startId && _next == startNext; 
}

/// @notice descendingList should return correct positions
rule _ascendList_integrity(
    env e,
    uint256 NICR,
    bytes32 startId
) {
    bytes32 _prev;
    bytes32 _next;
    uint256 startNICR = getNICR(startId);
    _prev, _next = ascendList(NICR, startId);
    assert startId == last && NICR <= startNICR => _next == nonExistId() && _prev == last; 
}

/// @notice descendingList should return correct positions
rule _ascendList_integrity2(
    env e,
    uint256 NICR,
    bytes32 startId
) {
    bytes32 _prev;
    bytes32 _next;
    uint256 startNICR = getNICR(startId);
    bytes32 startPrev = prev[startId];
    bool isValid = validInsertPosition(e, NICR, startPrev, startId);
    _prev, _next = ascendList(NICR, startId);
    assert startId != last && isValid => _prev == startPrev && _next == startId;
}