import "./SortedCdps_CdpIds.spec";

///@notice toCdpId should produce owner same as getOwnerAddress show
rule toCdpId_inverse(
    env e,
    address owner,
    uint256 blockHeight,
    uint256 nonce
) {
    bytes32 cdpId = toCdpId(owner, blockHeight,nonce );
    assert getOwnerAddress(cdpId) == owner;
}