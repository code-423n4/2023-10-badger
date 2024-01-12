// SPDX-License-Identifier: MIT

pragma solidity 0.8.17;

import {SortedCdps} from "../../packages/contracts/contracts/SortedCdps.sol";

contract SortedCdpsHarness is SortedCdps {
    mapping(bytes32 => bool) inList;

    constructor(
        uint256 _size,
        address _cdpManagerAddress,
        address _borrowerOperationsAddress
    ) SortedCdps(_size, _cdpManagerAddress, _borrowerOperationsAddress) {}

    function getOwnerAddressHarness(bytes32 cdpId) public pure returns (address) {
        uint256 _tmp = uint256(cdpId) >> ADDRESS_SHIFT;
        return address(uint160(_tmp));
    }

    function getCdpCountOfHarness(
        address owner,
        bytes32 startNodeId,
        uint maxNodes
    ) external view returns (uint256, bytes32) {
        bytes32 _currentCdpId = (startNodeId == dummyId ? data.tail : startNodeId);
        uint _ownedCount = 0;
        uint i = 0;

        while (_currentCdpId != dummyId) {
            // if the current CDP is owned by specified owner
            if (getOwnerAddress(_currentCdpId) == owner) {
                _ownedCount = _ownedCount + 1;
            }
            ++i;

            // move to the next CDP in the list
            _currentCdpId = data.nodes[_currentCdpId].prevId;

            // cut the run if we exceed expected iterations through the loop
            if (maxNodes > 0 && i >= maxNodes) {
                break;
            }
        }
        return (_ownedCount, _currentCdpId);
    }

    function getCdpsOfHarness(address owner) external view returns (bytes32[] memory cdps) {
        (uint _ownedCount, ) = _cdpCountOf(owner, dummyId, 0);
        if (_ownedCount > 0) {
            (bytes32[] memory _allCdps, , ) = _getCdpsOf(owner, dummyId, 0, _ownedCount);
            cdps = _allCdps;
        }
    }

    function getAllCdpsOfHarness(
        address owner,
        bytes32 startNodeId,
        uint maxNodes
    ) external view returns (bytes32[] memory, uint256, bytes32) {
        (uint _ownedCount, ) = _cdpCountOf(owner, startNodeId, maxNodes);
        return _getCdpsOf(owner, startNodeId, maxNodes, _ownedCount);
    }

    function getSizeHarness() public view returns (uint256) {
        return data.size;
    }

    function getMaxSizeHarness() external view returns (uint256) {
        return maxSize;
    }

    function getFirstHarness() public view returns (bytes32) {
        return data.head;
    }

    function getLastHarness() public view returns (bytes32) {
        return data.tail;
    }

    function getNextHarness(bytes32 _id) public view returns (bytes32) {
        return data.nodes[_id].nextId;
    }

    function getPrevHarness(bytes32 _id) public view returns (bytes32) {
        return data.nodes[_id].prevId;
    }

    function toCdpIdHarness(
        address owner,
        uint256 blockHeight,
        uint256 nonce
    ) public pure returns (bytes32) {
        bytes32 serialized;

        serialized |= bytes32(nonce);
        serialized |= bytes32(blockHeight) << BLOCK_SHIFT; // to accommendate more than 4.2 billion blocks
        serialized |= bytes32(uint256(uint160(owner))) << ADDRESS_SHIFT;

        return serialized;
    }

    function getDataNodePrevId(bytes32 cdpId) public view returns (bytes32) {
        return data.nodes[cdpId].prevId;
    }

    function cdpCountOfHarness(
        address owner,
        bytes32 startNodeId,
        uint maxNodes
    ) external view returns (uint256) {
        // walk the list, until we get to the count
        // start at the given node or from the tail of list
        bytes32 _currentCdpId = (startNodeId == dummyId ? data.tail : startNodeId);
        uint _ownedCount = 0;
        uint i = 0;

        while (_currentCdpId != dummyId) {
            // if the current CDP is owned by specified owner
            if (getOwnerAddress(_currentCdpId) == owner) {
                _ownedCount = _ownedCount + 1;
            }
            ++i;

            // move to the next CDP in the list
            _currentCdpId = data.nodes[_currentCdpId].prevId;

            // cut the run if we exceed expected iterations through the loop
            if (maxNodes > 0 && i >= maxNodes) {
                break;
            }
        }
        return _ownedCount;
    }

    function cdpOfOwnerByIndexHarness(
        address owner,
        uint256 index,
        bytes32 startNodeId,
        uint maxNodes
    ) public view returns (bytes32, bool, uint) {
        // walk the list, until we get to the indexed CDP
        // start at the given node or from the tail of list
        bytes32 _currentCdpId = (startNodeId == dummyId ? data.tail : startNodeId);
        uint _currentIndex = 0;
        uint i;

        while (_currentCdpId != dummyId) {
            // if the current CDP is owned by specified owner
            if (getOwnerAddress(_currentCdpId) == owner) {
                // if the current index of the owner CDP matches specified index
                if (_currentIndex == index) {
                    return (_currentCdpId, true, _currentIndex);
                } else {
                    // if not, increment the owner index as we've seen a CDP owned by them
                    _currentIndex = _currentIndex + 1;
                }
            }
            ++i;

            // move to the next CDP in the list
            _currentCdpId = data.nodes[_currentCdpId].prevId;

            // cut the run if we exceed expected iterations through the loop
            if (maxNodes > 0 && i >= maxNodes) {
                break;
            }
        }
        // if we reach maximum iteration or end of list
        // without seeing the specified index for the owner
        // then maybe a new pagination is needed
        return (_currentCdpId, false, _currentIndex);
    }

    function getCachedNominalICR(bytes32 id) external view returns (uint256) {
        return cdpManager.getCachedNominalICR(id);
    }

    function headToTailHarness(bytes32 headId, uint256 size) external view returns (bytes32) {
        require(getFirstHarness() == headId, "Variable not head");
        bytes32 currentId = headId;
        for (uint256 i; i < size - 1; i++) {
            currentId = getNextHarness(currentId);
        }
        return currentId;
    }

    function tailToHeadHarness(bytes32 tailId, uint256 size) external view returns (bytes32) {
        require(getLastHarness() == tailId, "Variable not tail");
        bytes32 currentId = tailId;
        for (uint256 i; i < size - 1; i++) {
            currentId = getPrevHarness(currentId);
        }
        return currentId;
    }

    function isInListHarness(bytes32 id) public view returns (bool) {
        bytes32 currentId = getFirstHarness();
        uint256 size = getSizeHarness();
        for (uint256 i; i < size - 1; i++) {
            if (currentId == id) {
                return true;
            }
            currentId = getNextHarness(currentId);
        }
        return false;
    }

    function allInListAndLinkedHarness(bytes32[] memory ids) public view returns (bool) {
        bool result = true;
        result = isInListHarness(ids[0]);
        if (result == false) {
            return false;
        }
        bytes32 currentId = ids[0];
        uint256 length = ids.length;
        for (uint256 i; i < length - 1; i++) {
            currentId = getNextHarness(currentId);
        }

        if (currentId == ids[length - 1]) {
            return true;
        }
        return false;
    }
}
