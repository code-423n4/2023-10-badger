// SPDX-License-Identifier: MIT

pragma solidity 0.8.17;

import "../../packages/contracts/contracts/SortedCdps.sol";

contract SortedCdpsHarness is SortedCdps { 
    
    mapping(bytes32 => uint256) cachedNominalICR;

    constructor(
        uint256 _size, 
        address _cdpManagerAddress, 
        address _borrowerOperationsAddress
    ) SortedCdps(_size, _cdpManagerAddress, _borrowerOperationsAddress) { }

    // Set correct initial list structure
    function isListStructureValid() external view returns (bool) {        
        if(data.size == 0) {
            require(data.head == dummyId 
                && data.tail == dummyId 
                && data.nodes[dummyId].nextId == dummyId 
                && data.nodes[dummyId].prevId == dummyId
            );
            return true;
        } else if(data.size == 1) {
            require(data.head != dummyId && data.head == data.tail
                && data.nodes[data.head].nextId == dummyId
                && data.nodes[data.head].prevId == dummyId
            );
            return true;
        } else if(data.size > 1 && data.size <= maxSize) {
            require(data.head != dummyId && data.tail != dummyId && data.head != data.tail
                && data.nodes[data.head].prevId == dummyId
                && data.nodes[data.tail].nextId == dummyId
            );

            uint256 count = 1;
            bytes32 currentId = data.head;
            do {
                require(data.nodes[data.nodes[currentId].nextId].prevId == currentId);

                currentId = data.nodes[currentId].nextId;
                count++;

            } while(currentId != data.tail);

            require(count == data.size);

            return true;
        } else {
            return false;
        }
    }

    // Use to prove cdpCountOf()
    function countOwnerIds(address owner) external view returns (uint256 count) {
        if (data.size == 1) {
            count = getOwnerAddress(data.head) == owner ? 1 : 0;
        } else if (data.size > 1 && data.size <= maxSize) {
            bytes32 currentId = data.head;
            do {
                if (getOwnerAddress(currentId) == owner) {
                    count++;
                }

                if (currentId == data.tail) {
                    break;
                }

                currentId = data.nodes[currentId].nextId;

            } while (true);
        }
    }

    // Use to prove contains()
    function isNodeInList(bytes32 _id) public view returns (bool) {
        if (data.size == 0 || _id == dummyId) {
            // Early return if the list is empty or _id is null.
            return false;
        }

        bytes32 currentId = data.head;
        while (currentId != dummyId) {
            if (currentId == _id) {
                // Node found.
                return true;
            }
            // Move to the next node.
            currentId = data.nodes[currentId].nextId;
        }

        // Node not found after traversing the whole list.
        return false;
    }

    // Use to prove toCdpId()
    function toCdpIdHarness(address owner, uint256 blockHeight, uint256 nonce) external view returns (bytes32) {
        return this.toCdpId(owner, blockHeight, nonce);
    }

    function toCdpIdFunc(address owner, uint256 blockHeight, uint256 nonce) external pure returns (bytes32) {
        bytes32 serialized;

        serialized |= bytes32(nonce);
        serialized |= bytes32(blockHeight) << BLOCK_SHIFT;
        serialized |= bytes32(uint256(uint160(owner))) << ADDRESS_SHIFT;

        return serialized;
    }

    // Prove address formated correctly in bytes32
    function verifyAddressFormatting(bytes32 cdpId, address expectedAddress) external pure returns (bool) {
        uint256 _tmp = uint256(cdpId) >> 96;
        address convertedAddress = address(uint160(_tmp));
        return convertedAddress == expectedAddress;
    }

    // Helper function from CdpManager
    function _getCdpIdsToRemove(
        bytes32 _start,
        uint256 _total,
        bytes32 _end
    ) internal view returns (bytes32[] memory) {
        uint256 _cnt = _total;
        bytes32 _id = _start;
        bytes32[] memory _toRemoveIds = new bytes32[](_total);
        while (_cnt > 0 && _id != bytes32(0)) {
            _toRemoveIds[_total - _cnt] = _id;
            _cnt = _cnt - 1;
            _id = this.getNext(_id);
        }
        require(_toRemoveIds[0] == _start, "CdpManager: batchRemoveSortedCdpIds check start error");
        require(
            _toRemoveIds[_total - 1] == _end,
            "CdpManager: batchRemoveSortedCdpIds check end error"
        );
        return _toRemoveIds;
    }

    function _isStartBeforeEnd(bytes32 _start, bytes32 _end) private view returns (bool) {
        require(_start != _end, "Start and end nodes cannot be the same");
        require(_start != dummyId && _end != dummyId, "Invalid node IDs");

        bytes32 currentNodeId = _start;

        while (currentNodeId != dummyId && currentNodeId != _end) {
            currentNodeId = data.nodes[currentNodeId].nextId;
        }

        // If currentNodeId is _end, it means we've found _end after _start
        return currentNodeId == _end;
    }

    function _calculateTotal(bytes32 _start, bytes32 _end) private view returns (uint256) {
        require(_start != bytes32(0) && _end != bytes32(0), "Invalid node IDs");
        require(_start != _end, "Start and end nodes cannot be the same");
        
        bytes32 currentNodeId = _start;
        uint256 total = 1; // Start at 1 to include the `_start` node itself

        // Traverse the list until we reach `_end` or the end of the list
        while (currentNodeId != _end) {
            currentNodeId = data.nodes[currentNodeId].nextId;
            require(currentNodeId != bytes32(0), "Reached end of list without finding `_end`");
            total++;
        }

        return total;
    }

    // Use instead of batchRemove(), it prepaires an array of id's in the correct order (like it CdpManager do)
    function batchRemoveHarness(bytes32 _start, bytes32 _end) external {
        
        require(isNodeInList(_start) 
            && isNodeInList(_end) 
            && _isStartBeforeEnd(_start, _end)
        );

        uint256 _total = _calculateTotal(_start, _end);

        bytes32[] memory _toRemoveIds = _getCdpIdsToRemove(
            _start,
            _total,
            _end
        );

        // Strong trust assumption that the specified nodes are sorted in the same order as in the input array
        this.batchRemove(_toRemoveIds);
    }

    // Use instead of insert(), it syncs id and it's NICR
    function insertHarness(address owner, uint256 _NICR, bytes32 _prevId, bytes32 _nextId) external returns (bytes32) {
        bytes32 _id = toCdpId(owner, block.number, nextCdpNonce);
        cachedNominalICR[_id] = _NICR;
        return this.insert(owner, _NICR, _prevId, _nextId);
    }

    // Use instead of reInsert(), it syncs id and it's NICR
    function reInsertHarness(bytes32 _id, uint256 _newNICR, bytes32 _prevId, bytes32 _nextId) external {
        cachedNominalICR[_id] = _newNICR;
        this.reInsert(_id, _newNICR, _prevId, _nextId);
    }
}
