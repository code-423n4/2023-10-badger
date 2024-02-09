// SPDX-License-Identifier: MIT

pragma solidity 0.8.17;

import "../../packages/contracts/contracts/SortedCdps.sol";

contract SortedCdpsHarness is SortedCdps { 
    
    constructor(uint256 _size, address _cdpManagerAddress, address _borrowerOperationsAddress
    ) SortedCdps(_size, _cdpManagerAddress, _borrowerOperationsAddress) {
        //empty
    }

    function descendList(
        uint256 _NICR, 
        bytes32 _startId
    ) public view returns (bytes32, bytes32){
        return _descendList(_NICR, _startId);
    }

    function ascendList(
        uint256 _NICR, 
        bytes32 _startId
    ) public view returns (bytes32, bytes32){
        return _ascendList(_NICR, _startId);
    }

    function getNICR(
        bytes32 id 
    ) external view returns(uint256){
        return cdpManager.getCachedNominalICR(id);
    }

    function batchRemove_one(bytes32 id1) external {
        bytes32[] memory ids = new bytes32[](1);
        ids[0] = id1;
        this.batchRemove(ids);
    }

    function batchRemove_two(bytes32 id1, bytes32 id2) external {
        bytes32[] memory ids = new bytes32[](2);
        ids[0] = id1;
        ids[1] = id2;
        this.batchRemove(ids);
    }
}