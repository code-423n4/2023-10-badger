/////////////////// METHODS ///////////////////////

methods {
    function _.authority() external => ghostAuthorityAddress expect address ALL;
    function _.syncGlobalAccountingAndGracePeriod() external => syncGlobalAccountingAndGracePeriodCVL() expect void ALL;
    function _.getCdpStatus(bytes32 _cdpId) external => cdpStatus(_cdpId) expect uint256 ALL;
}

///////////////// DEFINITIONS /////////////////////

definition CDP_STATUS_NON_EXISTENT() returns mathint = 0;
definition CDP_STATUS_ACTIVE() returns mathint = 1;
definition CDP_STATUS_CLOSED_BY_OWNER() returns mathint = 2;
definition CDP_STATUS_CLOSED_BY_LIQUIDATION() returns mathint = 3;
definition CDP_STATUS_CLOSED_BY_REDEMPTION() returns mathint = 4;

////////////////// FUNCTIONS //////////////////////

function cdpStatus(bytes32 _cdpId) returns uint256 {
    return require_uint256(ghostCdpStatus[_cdpId]);
}

function syncGlobalAccountingAndGracePeriodCVL() {
    syncGlobalAccountingAndGracePeriodCalled = true;
}

///////////////// GHOSTS & HOOKS //////////////////

ghost address ghostAuthorityAddress;

ghost mapping (bytes32 => mathint) ghostCdpStatus {
    axiom forall bytes32 i. ghostCdpStatus[i] >= CDP_STATUS_NON_EXISTENT() 
        && ghostCdpStatus[i] <= CDP_STATUS_CLOSED_BY_REDEMPTION(); 
}

ghost bool syncGlobalAccountingAndGracePeriodCalled;

///////////////// PROPERTIES //////////////////////
