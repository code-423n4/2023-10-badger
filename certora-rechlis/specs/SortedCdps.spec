

/*

verification of SortedCdps
This is an advnaced project and requires probably qunatifiers and more summarization.
see https://github.com/Certora/Examples/tree/master/CVLByExample/QuantifierExamples 


*/
methods {
    function contains(bytes32 _id) external  returns (bool) envfree;

    function isFull() external  returns (bool) envfree; 

    function isEmpty() external  returns (bool) envfree;

    function getSize() external  returns (uint256) envfree;

    function getMaxSize() external  returns (uint256) envfree;

    function getFirst() external  returns (bytes32) envfree;

    function getLast() external  returns (bytes32) envfree;

    function getNext(bytes32 _id) external  returns (bytes32) envfree;

    function getPrev(bytes32 _id) external  returns (bytes32) envfree;

    // function getNextUINT(bytes32 _id) external  returns (uint256) envfree;

    // function getPrevUINT(bytes32 _id) external  returns (uint256) envfree;

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

}

ghost uniqueId(address /*owner*/, uint256 /*blockHeight*/, uint256 /*nonce*/ ) returns bytes32 {
    axiom forall address o1. forall address o2. 
    forall uint256 b1. forall uint256 b2.
    forall uint256 n1. forall uint256 n2.
    ( o1 != o2 || b1 != b2 || n1 != n2 ) => uniqueId(o1, b1, n1) != uniqueId(o2, b2, n2);
}

rule mutSortedCdps(address owner,uint256 NICR,bytes32 prevId,bytes32 nextId)
{
    env e;

    insert@withrevert(e,owner,NICR,prevId,nextId);
    bool reverted = lastReverted;
    assert (e.msg.sender != borrowerOperationsAddress(e) && e.msg.sender != cdpManager(e)) => reverted;
}

rule insertThenRemove(env e,address owner,uint256 NICR){

    bytes32 _id;
    bytes32 _id2;
    storage init = lastStorage;
    bytes32 prevId = getPrev(e,_id);
    bytes32 nextId = getNext(e,_id);
    
    requireInvariant UniquePrevAndNext(e,_id,_id2);
    require _id != getFirst() && _id != getLast();

    require _id == insert(e, owner, NICR, prevId , nextId);
    remove(e, _id);

    decreaseNonce(e);

    // require prevId == getPrev(e,_id);
    // require nextId == getNext(e,_id);

    storage init2 = lastStorage;
    assert init == init2;
    // assert init == lastStorage;
}

rule eitherInsertOrRemove(address owner,uint256 _NICR,bytes32 _prevId,bytes32 _nextId){
    env e;

    bytes32 _id;

    storage init = lastStorage;

    require _id == insert@withrevert(e, owner, _NICR, _prevId, _nextId);
    bool reverted = lastReverted;

    remove@withrevert(e,_id) at init;

    assert reverted || lastReverted;
}

rule insertedImpliesContains(env e,address owner,uint256 NICR){

    bytes32 _id;
    bytes32 prevId = getPrev(e,_id);
    bytes32 nextId = getNext(e,_id);

    require _id == insert(e, owner, NICR, prevId, nextId);

    assert contains(_id);
}
rule removedImpliesNotContains(env e, bytes32 _id){

    requireInvariant zeroSizeImplies(e);
    requireInvariant ifContainsNextAndPrevNotEqual_id(e,_id);
    requireInvariant ifNotContainsNextAndPrevEqualsZero(e,_id);

    remove(e,_id);

    assert !contains(_id);
}

rule containsAfterReinsert(env e,bytes32 _id,uint256 NICR, bytes32 prevId, bytes32 nextId){
    reInsert(e, _id, NICR, prevId, nextId);

    assert contains(_id);
}

invariant ifContainsNextAndPrevNotEqual_id(env e, bytes32 _id)
    (contains(_id) => getNext(e,_id) != _id && getPrev(e,_id) != _id);

invariant ifNotContainsNextAndPrevEqualsZero(env e, bytes32 _id)
    (!contains(_id) => getNext(e,_id) == zeroAsbytes32(e) && getPrev(e,_id) == zeroAsbytes32(e));

invariant zeroSizeImplies(env e)
     isEmpty(e) => getFirst(e) == zeroAsbytes32(e) && getLast(e) == zeroAsbytes32(e) 
filtered { f -> !f.isView && !f.isFallback &&
           f.selector != sig:batchRemove(bytes32[]).selector}

invariant UniquePrevAndNext(env e, bytes32 id1, bytes32 id2)
    (id1 != id2 && contains(id1) && contains(id2) )=> (getPrev(e,id1) != getPrev(e,id2) && getNext(e,id1) != getNext(e,id2));

invariant headEqualsTail(env e)
    getFirst(e) == getLast(e) => getSize(e) < 2
    {
        preserved with (env e1) {
            requireInvariant zeroSizeImplies(e1);
        }
        
    }

invariant nextVsPrev(env e, bytes32 id1, bytes32 id2)
    contains(id1) && contains(id2) && getNext(e,id1) == id2 => getPrev(e,id2) == id1;

function simpleSetup()
{
    //case 1 - empty
    env e;
    require isEmpty(e) && getFirst(e) == zeroAsbytes32(e) && getLast(e) == zeroAsbytes32(e) ;
    //require forall bytes32 id1.  !contains(id) && getNext(e,id) == zeroAsbytes32(e) && getLast(e,id) == zeroAsbytes32(e) ;
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


