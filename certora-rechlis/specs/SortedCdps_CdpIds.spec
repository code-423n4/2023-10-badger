

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
    
    function toCdpId(
        address owner,
        uint256 blockHeight,
        uint256 nonce
    ) external returns (bytes32) envfree;

    function getOwnerAddress(bytes32 cdpId) external returns (address) envfree; 
}


rule uniqunessOfId(address o1,  address o2,
        uint256 b1,  uint256 b2, 
        uint256 n1,  uint256 n2) 
{
assert ( o1 != o2 || b1 != b2 || n1 != n2 ) => toCdpId(o1, b1, n1) != toCdpId(o2, b2, n2);

}
    
rule inverseOwnerCpdId(address owner, uint256 blockHeight, uint256 nonce) {
    bytes32 cpdId = toCdpId(owner, blockHeight, nonce); 
    assert getOwnerAddress(cpdId) ==owner;
}
