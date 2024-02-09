
using CdpManager as _cdpManager;
/*
Modular verification is an approch for verifing properties of some parts and
later using then assuming the properties as lemmas for other rules.

This file just to check properties of functions that will be summarized:
toCdpId
getOwnerAddress
...


Note that the rules fails, is it a bug in the code? 

*/
methods {
    function contains(bytes32 _id) external  returns (bool) envfree;

    function isEmpty() external  returns (bool) envfree;

    function nonExistId() external returns (bytes32) envfree;

    function getSize() external  returns (uint256) envfree;

    function getMaxSize() external  returns (uint256) envfree;

    function getFirst() external  returns (bytes32) envfree;

    function getLast() external  returns (bytes32) envfree;

    function getNext(bytes32 _id) external  returns (bytes32) envfree;

    function getPrev(bytes32 _id) external  returns (bytes32) envfree;
    
    function toCdpId(
        address owner,
        uint256 blockHeight,
        uint256 nonce
    ) external returns (bytes32) envfree;

    function nextCdpNonce() external returns(uint256) envfree;

    function getOwnerAddress(bytes32 cdpId) external returns (address) envfree; 

    function _.getCachedNominalICR(bytes32) external  => NONDET;
    function _.getCdpStatus(bytes32) external => NONDET;
}


rule uniqunessOfId(address o1,  address o2,
        uint256 b1,  uint256 b2, 
        uint256 n1,  uint256 n2) 
{
assert ( o1 != o2 || b1 != b2 || n1 != n2 ) => toCdpId(o1, b1, n1) != toCdpId(o2, b2, n2);

}
    
rule inverseOwnerCpdId(address owner, uint256 blockHeight, uint256 nonce) {
    require blockHeight < 2 ^ 32;
    require nonce <  2 ^ 32;
    bytes32 cpdId = toCdpId(owner, blockHeight, nonce); 
    assert getOwnerAddress(cpdId) ==owner;
}

/***********************    PARTICIPANT  ************************/

/***********************    MISC         ************************/
function insertCdp(env e, address owner){
    bytes32 _prev;
    bytes32 _next;
    require e.block.number < 2 ^ 32;
    require nextCdpNonce() < 2 ^ 32;
    bytes32 id = toCdpId(owner, e.block.number, nextCdpNonce()); 
    uint256 NICR = _cdpManager.getCachedNominalICR(e, id);
    insert(e, owner, NICR, _prev, _next);
}

function removeCdp(env e, bytes32 id){
    remove(e, id);
}

/**** SIZE ****/
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
    require next[id] == v;
    require v != to_bytes32(0x0) => prev[v] == id;
    require v == to_bytes32(0x0) => last == id;
    require id == to_bytes32(0x0) => next[id] == to_bytes32(0x0);
    require last != id && prev[id] != to_bytes32(0x0) => next[id] != to_bytes32(0x0);
    require first == id && size != 1 => next[id] != to_bytes32(0x0);
    require next[id] != first;
    require id != to_bytes32(0x0) => next[id] != id;
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
    require prev[id] == v;
    require v != to_bytes32(0x0) =>  next[v] == id;
    require v == to_bytes32(0x0) => first == id;
    require id == to_bytes32(0x0) => prev[id] == to_bytes32(0x0);
    require first != id && next[id] != to_bytes32(0x0) => prev[id] != to_bytes32(0x0);
    require last == id && size != 1 => prev[id] != to_bytes32(0x0);
    require prev[id] != last;
    require id != to_bytes32(0x0) => prev[id] != id;
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

/// @notice cdpOfOwnerByIdx should return correctly 
rule cdpOfOwnerByIdx_integrity(
    env e,
    address owner,
    uint256 index,
    bytes32 startNodeId,
    uint256 maxNodes,
    bytes32 id
) {
    bytes32 middle = prev[last];
    require middle != nonExistId() && first != nonExistId() && last != nonExistId();
    require first == prev[middle];
    bytes32 result;
    bool isThere;
    result, isThere = cdpOfOwnerByIdx(e, owner, index, startNodeId, maxNodes);
    assert index == 0 
        && (maxNodes > 2 || maxNodes == 0) 
        && startNodeId == last 
        => (getOwnerAddress(last) == owner => result == last && isThere)
        || (getOwnerAddress(middle) == owner && getOwnerAddress(last) != owner => result == middle && isThere)
        || (getOwnerAddress(first) == owner && getOwnerAddress(last) != owner && getOwnerAddress(middle) != owner=> result == first && isThere);
    
    assert index == 1 
        && (maxNodes > 2 || maxNodes == 0) 
        && startNodeId == last 
        => (getOwnerAddress(middle) == owner && getOwnerAddress(last) == owner => result == middle && isThere)
        || (getOwnerAddress(first) == owner 
        && (getOwnerAddress(last) != owner 
        <=> getOwnerAddress(middle) == owner) => result == first && isThere);
            
    assert index == 2 
        && (maxNodes > 2 || maxNodes == 0) 
        && startNodeId == last 
        => (getOwnerAddress(first) == owner && getOwnerAddress(last) == owner && getOwnerAddress(middle) == owner => result == first && isThere);
    
    assert index == 3 
        && (maxNodes > 2 || maxNodes == 0) 
        && startNodeId == last => !isThere;
}

/// @notice cdpCountOf should return correctly 
rule cdpCountOf_integrity(
    env e,
    address owner,
    uint256 index,
    bytes32 startNodeId,
    uint256 maxNodes,
    bytes32 id
) {
    bytes32 middle = prev[last];
    require middle != nonExistId() && first != nonExistId() && last != nonExistId();
    require first == prev[middle];
    bytes32 result;
    uint256 count;
    count, result = getCdpCountOf(e, owner,startNodeId, maxNodes);

    assert (maxNodes > 2 || maxNodes == 0) 
        && startNodeId == last 
        => (getOwnerAddress(last) == owner 
        || getOwnerAddress(middle) == owner 
        || getOwnerAddress(first) == owner 
        => count != 0) ; 
            
    assert (maxNodes > 2 || maxNodes == 0) 
        && startNodeId == last 
        => (getOwnerAddress(last) == owner 
        && getOwnerAddress(middle) == owner 
        && getOwnerAddress(first) == owner 
        => count == 3) ;    

    assert (maxNodes > 2 || maxNodes == 0) 
        && startNodeId == last 
        => (getOwnerAddress(last) != owner 
        && getOwnerAddress(middle) != owner 
        && getOwnerAddress(first) != owner 
        => count == 0) ;
}