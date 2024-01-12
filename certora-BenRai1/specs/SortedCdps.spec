import "./CdpManager.spec";


/*
verification of SortedCdps
This is an advnaced project and requires probably qunatifiers and more summarization.
see https://github.com/Certora/Examples/tree/master/CVLByExample/QuantifierExamples 
*/

using CdpManager as CdpManager;

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

    function toCdpId(address owner, uint256 blockHeight, uint256 nonce) external returns (bytes32) envfree;

    // ----------------------------- OWN FUNCTIONS --------------------------------

        function headToTailHarness(bytes32 headId, uint256 size) external returns (bytes32) envfree;
        function tailToHeadHarness(bytes32 tailId, uint256 size) external returns (bytes32) envfree;
        function isInListHarness(bytes32 id) external returns (bool) envfree;

    // ----------------------------- OWN FUNCTIONS END --------------------------------


    /* summarizing as a deterministic and unique function. need to prove that this.
        see certora/specs/SortedCdps_DpdIds.spec 
    */
    function toCdpId(
        address owner,
        uint256 blockHeight,
        uint256 nonce
    ) internal returns (bytes32) => uniqueId(owner,blockHeight,nonce);

    function getNext(bytes32 _id) external returns (bytes32) => uniqueNextId(_id);

    function getPrev(bytes32 _id) external returns (bytes32) => uniquePrevId(_id);


    // ----------------------------- OWN SUMMARIZATIONS --------------------------------

        function toCdpIdHarness(address owner, uint256 blockHeight, uint256 nonce) internal returns (bytes32) => uniqueId(owner,blockHeight,nonce);
        //issue summarization only works with ghost variable/function


    // ----------------------------- OWN SUMMARIZATIONS END --------------------------------




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

// ------------------------- ghosts OK ----------------------------

//ghostZero
 ghost bytes32 zero {
    axiom zero == to_bytes32(0);
}

 //ghostHead
    ghost bytes32 ghostHead;

    hook Sstore currentContract.data.head bytes32 new_value  STORAGE {
        ghostHead = new_value;
    }
   
    hook Sload bytes32 head currentContract.data.head STORAGE {
        require ghostHead == head;
}

//ghostTail
    ghost bytes32 ghostTail;

    hook Sstore currentContract.data.tail bytes32 new_value STORAGE {
        ghostTail = new_value;
    }
   
    hook Sload bytes32 head currentContract.data.tail STORAGE {
        require ghostTail == head;
}

//ghostSize
    ghost uint256 ghostSize{
        init_state axiom ghostSize == 0;
    }

    hook Sstore currentContract.data.size uint256 new_value STORAGE {
        ghostSize = new_value;
    }
   
    hook Sload uint256 size currentContract.data.size STORAGE {
        require ghostSize == size;
}

// nextCdpNonce ghost
    ghost uint256 nextCdpNonceGhost{
        init_state axiom nextCdpNonceGhost == 0;

    }

    hook Sstore currentContract.nextCdpNonce uint256 new_value STORAGE {
        nextCdpNonceGhost = new_value;
    }

    hook Sload uint256 nextCdpNonce currentContract.nextCdpNonce STORAGE {
        require nextCdpNonceGhost == nextCdpNonce;
}


//ghostNextId
    ghost mapping(bytes32 => bool) ghostValidNext{
    init_state axiom forall bytes32 id. ghostValidNext[id] == false;
    }

    ghost mapping(bytes32 => bytes32) ghostNextId{
        init_state axiom forall bytes32 id. ghostNextId[id] == zero;
    }


    //ghostReach: starting from id1, can you reach id2 when following the linked list using nextId
    ghost nextReach(bytes32 /*id1*/, bytes32 /*id2*/) returns bool{
        init_state axiom forall bytes32 id1. forall bytes32 id2.
        nextReach(id1, id2) == (id1 == id2 || id2 == zero);
    }

    //hook trigered when a nextId changes
    hook Sstore currentContract.data.nodes[KEY bytes32 key].nextId bytes32 new_value  STORAGE {
        //update ghost successor
        ghostNextId[key] = new_value;

    }
   
    hook Sload bytes32 nextId currentContract.data.nodes[KEY bytes32 id].nextId STORAGE {
        require ghostNextId[id] == nextId;

}


//ghostPrevId
    ghost prevReach(bytes32 /*id1*/, bytes32 /*id2*/) returns bool{
        init_state axiom forall bytes32 id1. forall bytes32 id2.
        prevReach(id1, id2) == (id1 == id2 || id2 == zero);
    }

    ghost mapping(bytes32 => bool) ghostValidPrev{
    init_state axiom forall bytes32 id. ghostValidPrev[id] == false;
    }

    ghost mapping(bytes32 => bytes32) ghostPrevId{
        init_state axiom forall bytes32 id. ghostPrevId[id] == zero;
    }


    definition isPrevId(bytes32 id1, bytes32 id2) returns bool = 
        prevReach(id1,id2) && //aid1 can reached id2
        id1 !=id2 && // id1 not id2
        (forall bytes32 x. prevReach(id1, x) && prevReach(x, id2) => (id1 == x || id2 == x)); //if a and b can both reach x, a or b must be x

    definition prevReachInvariant(bytes32 id) returns bool =
        (id == zero && ghostPrevId[id] == zero) // PrevID of zero is always zero
        || (id != zero && isPrevId(id, ghostPrevId[id])
    ); // if ID is not zero, the id and its PrevId are next to each other in the linked list


    hook Sstore currentContract.data.nodes[KEY bytes32 id].prevId bytes32 newPrevId STORAGE {
        //update ghost successor
        ghostPrevId[id] = newPrevId;

    }

        hook Sload bytes32 prevId currentContract.data.nodes[KEY bytes32 id].prevId STORAGE {
        require ghostPrevId[id] == prevId;
        require prevReachInvariant(id); 
}



    ghost uniqueId(address /*owner*/, uint256 /*blockHeight*/, uint256 /*nonce*/ ) returns bytes32 {
        axiom forall address o1. forall address o2. 
        forall uint256 b1. forall uint256 b2.
        forall uint256 n1. forall uint256 n2.
        ( o1 != o2 || b1 != b2 || n1 != n2 ) => uniqueId(o1, b1, n1) != uniqueId(o2, b2, n2);
    }


    ghost uniquePrevId(bytes32 /*_id*/) returns bytes32 {
        axiom forall bytes32 id1. forall bytes32 id2. 
        ( id1 != id2 ) => uniquePrevId(id1) != uniquePrevId(id2);
    }

    ghost uniqueNextId(bytes32 /*_id*/) returns bytes32 {
        axiom forall bytes32 id1. forall bytes32 id2. 
        ( id1 != id2 ) => uniqueNextId(id1) != uniqueNextId(id2);
    }



/// -------------------------------------  ISSUES -------------------------------------

 // @audit-issue ISSUE:does not work but shows issue in the code
 rule ISSUEcdpOfOwnerByIndexWorks(){
        env e;
        address owner;
        uint256	index;
        bytes32 startNodeId;
        uint maxNodes;
        bool boolResult;
        bool boolTarget; 
        bytes32 bytes32Result;
        bytes32 bytes32Target;
        uint _currentIndex;

        bytes32Result = cdpOfOwnerByIndex(e, owner, index);
        bytes32Target, boolTarget, _currentIndex = cdpOfOwnerByIndexHarness(e, owner, index, dummyId(e), 0);
        address ownerOfReturnedId = getOwnerAddress(e, bytes32Result);

        assert(bytes32Result == bytes32Target, "Returned bytes32 is wrong");
        assert(ownerOfReturnedId == owner, "The owner of the returned cdp is not the target Owner");
        assert(_currentIndex == index, "The index of the returned cdpId is wrong");

 }

/// -------------------------------------  RULES OK -------------------------------------
   
 // --------------------- Invariants work --------------------------

    invariant size0HeadTail0() ghostSize == 0 => ghostHead == zero && ghostTail == zero filtered{
        f->f.selector != sig:batchRemove(bytes32[]).selector}

    //Ids are unique if at least one input is different
    invariant idsAreUnique(address o1,  address o2, uint256 b1, uint256 b2, uint256 n1, uint256 n2) o1 != o2 || b1 != b2 || n1 != n2 => toCdpId(o1, b1, n1) != toCdpId(o2, b2, n2);

    //size is always <= maxSize
    invariant sizeIsNotBiggerThanMaxSize() getSize() <= getMaxSize();

 // --------------------- Invariants work end--------------------------

     rule insertWorks(){
        env e1;
        env e2;
        address owner;
        uint256 _NICR;
        bytes32 _prevId;
        bytes32 _nextId;
        bytes32 id = toCdpId(owner, e1.block.number, nextCdpNonceGhost);
        

        bool containsBefore = contains(id);
        uint256 cdpStatusBefore = CdpManager.getCdpStatus(e1, id);
        require(cdpStatusBefore == 0);
        mathint nextCdpNonceBefore = nextCdpNonceGhost;
        require(nextCdpNonceBefore < max_uint);
        bool isFull = isFull();

        insert(e1, owner,  _NICR, _prevId, _nextId);

        bool containsAfter = contains(id);
        mathint nextCdpNonceAfter = nextCdpNonceGhost;
        bytes32 nextId = ghostNextId[id];
        bool nextIncluded = contains(nextId);
        uint256 nextNICR = CdpManager.getCachedNominalICR(e2, nextId);
        bytes32 prevId = ghostPrevId[id];
        bool prevIncluded = contains(prevId);
        uint256 prevNICR = CdpManager.getCachedNominalICR(e2, prevId);



        assert(containsAfter == true, "Id was not included");
        assert(e1.msg.sender == borrowerOperationsAddress(e1) || e1.msg.sender == cdpManager(e1), "Callers should not be allowed");
        assert(cdpStatusBefore == 0, "CdpStatus of Id is not 0");
        assert(nextCdpNonceAfter == nextCdpNonceBefore +1, "cdpNonce did not increase");
        assert(isFull == false, "Full is true");
        assert(containsBefore == false, "Was added even though id was already in list");
        assert(containsAfter == true, "containsAfter is false");
        assert(id != dummyId(e1), "DummyId was added");
        assert(_NICR > 0, "_NICR <= 0 was added");
        // assert(nextId != zero => nextIncluded == true, "NextId is not included");
        // assert(prevId != zero => prevIncluded == true, "PrevId is not included");
        // assert(prevNICR <= _NICR, "prevNICR bigger than _NICR");
        // assert(nextNICR >= _NICR, "nextNICR smaller than _NICR");

    }

    rule containsWorks(){

        env e;
        bytes32 id;

        bool result = contains(e, id);

        assert(id != zero && (id == getFirst() || id == getLast() || ghostPrevId[id] != zero && ghostNextId[id] != zero) => result == true, "Returns true even though the id is not included");
        assert(id != getFirst() && id != getLast() && ghostPrevId[id] == zero && ghostNextId[id] == zero => result == false, "Returns true even though the id is not included");

    }

    rule cdpCountOfWorks(){
        env e;
        address owner;
        bytes32 emptyId = nonExistId(e);

        uint256 result = cdpCountOf(e, owner);

        assert(result == cdpCountOfHarness(e, owner, emptyId, 0), "Number of cdp for owner wrong");
    }

    rule onlyChangeNextCdpNonce(method f) filtered{f-> !f.isView}{
        env e;
        calldataarg arg;
        uint256 nextCdpNonceBefore = nextCdpNonce(e);

        f(e,arg);

        uint256 nextCdpNonceAfter = nextCdpNonce(e);

        assert(nextCdpNonceBefore != nextCdpNonceAfter => 
        f.selector == sig:insert(address,uint256,bytes32,bytes32).selector
        );
    }

    rule onlyCdpManager(method f) filtered{f-> 
        f.selector == sig:batchRemove(bytes32[]).selector ||
        f.selector == sig:remove(bytes32).selector }{
        env e;
        calldataarg arg;

        f(e,arg);

        assert(e.msg.sender == cdpManager(e), "Caller not cdpManager");
    }
   
    rule onlyCdpManagerOrBorrowerOp(method f) filtered{f-> 
        f.selector == sig:insert(address,uint256,bytes32,bytes32).selector ||
        f.selector == sig:reInsert(bytes32,uint256,bytes32,bytes32).selector }{
        env e;
        calldataarg arg;

        f(e,arg);

        assert(e.msg.sender == cdpManager(e) || e.msg.sender == borrowerOperationsAddress(e), "Caller not cdpManager or borrowerOperations");
    }

    rule onlyChangeHeadTail(method f) filtered{f-> !f.isView}{
        env e;
        calldataarg arg;
        bytes32 headBefore = getFirst();
        bytes32 tailBefore = getLast();

        f(e,arg);

        bytes32 headAfter = getFirst();
        bytes32 tailAfter = getLast();

        assert(headAfter != headBefore || tailAfter != tailBefore => 
        f.selector == sig:batchRemove(bytes32[]).selector ||
        f.selector == sig:insert(address,uint256,bytes32,bytes32).selector ||
        f.selector == sig:reInsert(bytes32,uint256,bytes32,bytes32).selector ||
        f.selector == sig:remove(bytes32).selector
        );


    }

    rule onlyChangeSize(method f) filtered{f-> !f.isView}{
        env e;
        calldataarg arg;
        uint256 sizeBefore = getSize();

        f(e,arg);

        uint256 sizeAfter = getSize();

        assert(sizeBefore != sizeAfter => 
        f.selector == sig:insert(address,uint256,bytes32,bytes32).selector ||
        f.selector == sig:batchRemove(bytes32[]).selector ||
        f.selector == sig:remove(bytes32).selector
        );


    }

    rule toCdpIdWorks(){
        env e;
        address owner;
        uint256 blockHeight;
        uint256 nonce;
        address dummy;

        bytes32 result = toCdpId(e, owner, blockHeight, nonce);
        bytes32 target = toCdpIdHarness(e,owner, blockHeight, nonce);
        assert(result == target, "toCdpIdWorks does not work");
    }

    rule nonExistIdWorks(){
        env e;
        bytes32 result = nonExistId(e);
        assert(result == dummyId(e), "nonExistId does not work");
    }
    
    rule isFullWorks(){
        env e;
        bool result = isFull(e);
        require(getSize() <= maxSize(e));
        assert(getSize() == maxSize(e) => result == true, "isFull does not work if it is full");
        assert(getSize() != maxSize(e) => result == false, "isFull does not work if it is NOT full");
    }

    rule isEmptyWorks(){
        env e;
        bool result = isEmpty(e);
        assert(getSize() == 0 => result == true, "isEmpty does not work if it is empty");
        assert(getSize() != 0 => result == false, "isEmpty does not work if it is NOT empty");
    }

    rule getOwnerAddressWorks(){
        env e;
        bytes32 cdpId;
        address result = getOwnerAddress(e, cdpId);
        assert(result == getOwnerAddressHarness(e, cdpId), "getOwnerAddress does not return the right value");
    }

    rule getCdpsOfWorks(){
        env e;
        address _address;
        uint256 index;
        bytes32[] userCdps = getCdpsOf(e, _address);
        bytes32[] userCdpsH = getCdpsOf(e, _address);
        require(index < userCdps.length);
        assert(userCdps[index] == userCdpsH[index], "userCdps does not return the right value");
    }

    rule getSizeWorks(){
        env e;
        uint256 result = getSize(e);
        assert(result == getSizeHarness(e), "getSize does not return the right value");
    }

    rule getMaxSizeWorks(){
        env e;
        uint256 result = getMaxSize(e);
        assert(result == getMaxSizeHarness(e), "getMaxSize does not return the right value");
    }

    rule getFirstWorks(){
        env e;
        bytes32 result = getFirst(e);
        assert(result == getFirstHarness(e), "getFirst does not return the right value");
    }

    rule getLastWorks(){
        env e;
        bytes32 result = getLast(e);
        assert(result == getLastHarness(e), "getLast does not return the right value");
    }

    rule getNextWorks(){
        env e;
        bytes32 _id;
        bytes32 result = getNext(e, _id);
        assert(result == getNextHarness(e, _id), "getNext does not return the right value");
    }

    rule getPrevWorks(){
        env e;
        bytes32 _id;
        bytes32 result = getPrev(e, _id);
        assert(result == getPrevHarness(e, _id), "getPrev does not return the right value");
    }

    rule getAllCdpsOfWorks(){
        env e;
        address _address;
        bytes32 _bytes32;
        uint _uint;
        bytes32[] userCdps;
        uint256 _cdpRetrieved;
        bytes32 _currentCdpId;
        bytes32[] userCdpsH;
        uint256 _cdpRetrievedH;
        bytes32 _currentCdpIdH;
        uint256 index;

        userCdps,  _cdpRetrieved, _currentCdpId = getAllCdpsOf(e, _address, _bytes32, _uint);
        userCdpsH, _cdpRetrievedH, _currentCdpIdH = getAllCdpsOfHarness(e, _address, _bytes32, _uint);
        require(index < userCdps.length);
        assert(userCdps[index] == userCdpsH[index], "userCdps value wrong");
        assert(_cdpRetrieved == _cdpRetrievedH, "_cdpRetrieved value wrong");
        assert(_currentCdpId == _currentCdpIdH, "_currentCdpId value wrong");
    }

    rule getCdpCountOfWorks(){
        env e;
        address _address;
        bytes32 _bytes32;
        uint _uint;
        uint256 _ownedCount;
        bytes32 _currentCdpId;
        uint256 _ownedCountH;
        bytes32 _currentCdpIdH;

        _ownedCount, _currentCdpId = getCdpCountOf(e, _address, _bytes32, _uint);
        _ownedCountH, _currentCdpIdH = getCdpCountOfHarness(e, _address, _bytes32, _uint);
        assert(_ownedCount == _ownedCountH,"_ownedCount does not return the right value");
        assert(_currentCdpId == _currentCdpIdH,"_currentCdpId does not return the right value");
    }



/// -------------------------------------  OLD RULES -------------------------------------


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

    invariant maxSizeIntegrity() getSize() <= getMaxSize();