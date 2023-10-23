

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


