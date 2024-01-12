// SPDX-License-Identifier: MIT

pragma solidity 0.8.17;

import "../../packages/contracts/contracts/SortedCdps.sol";
import "../../packages/contracts/contracts/Dependencies/SafeERC20.sol";

contract SortedCdpsHarness is SortedCdps { 
     using SafeERC20 for IERC20;
    
    constructor(
        uint256 _size,
        address _cdpManagerAddress,
        address _borrowerOperationsAddress
    ) SortedCdps(_size, _cdpManagerAddress, _borrowerOperationsAddress) {

    }

    function decreaseNonce() external {
        --nextCdpNonce;
    }   
    // function getPrevUINT(bytes32 _id) external view returns (uint256){
    //     uint256 tmp = getPrev(_id);
    //     return tmp;
    // }   
    // function getNextUINT(bytes32 _id) external view returns (uint256){
    //     uint256 tmp = getNext(_id);
    //     return tmp;
    // } 

    function zeroAsbytes32()  external view returns (bytes32){
        return 0;
    }


    function tokenBalanceOf(address token, address user) external view returns (uint256) {
        return IERC20(token).balanceOf(user);
    }
}
