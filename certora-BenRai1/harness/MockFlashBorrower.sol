// SPDX-License-Identifier: MIT
pragma solidity 0.8.17;

import {IERC3156FlashBorrower} from "../../packages/contracts/contracts/Interfaces/IERC3156FlashBorrower.sol";
import {IERC3156FlashLender} from "../../packages/contracts/contracts/Interfaces/IERC3156FlashLender.sol";
import {IEBTCToken} from "../../packages/contracts/contracts/Interfaces/IEBTCToken.sol";

contract MockFlashBorrower is IERC3156FlashBorrower {
  enum Action {
    MINT,
    BURN,
    APPROVE,
    TRANSFER,
    TRANSFER_FROM,
    INCREASE_ALLOWANCE,
    DECREASE_ALLOWANCE,
    OTHER
  }

  Action public action;
  uint8 public counter;
  uint8 public repeat_on_count;
  IEBTCToken public EBTC_Token;
  address public _transferTo;

  IERC3156FlashLender private _lender;

  bool allowRepayment;

  constructor(IERC3156FlashLender lender) {
    _lender = lender;
    allowRepayment = true;
  }

  /// @dev ERC-3156 Flash loan callback
  function onFlashLoan(
    address initiator,
    address token,
    uint256 amount,
    uint256 fee,
    bytes calldata data
  ) external override returns (bytes32) {
    require(msg.sender == address(_lender), 'FlashBorrower: Untrusted lender');
    require(initiator == address(this), 'FlashBorrower: Untrusted loan initiator');
    counter++;
    if (action == Action.APPROVE) {
        address spender;
        uint256 amt;
        EBTC_Token.approve(spender, amt);
    } else if (action == Action.TRANSFER) {
        uint256 amt;
        EBTC_Token.transfer(_transferTo, amt);
    } else if (action == Action.MINT) {
        address account;
        uint256 amt;
        EBTC_Token.mint(account, amt);
    } else if (action == Action.BURN) {
        address account;
        uint256 amt;
        EBTC_Token.burn(account, amt);
    } else if (action == Action.TRANSFER_FROM) {
        address from;
        uint256 amt;
        EBTC_Token.transferFrom(from, _transferTo, amt);
    } else if (action == Action.INCREASE_ALLOWANCE) {
        address spender;
        uint256 addedAmt;
        EBTC_Token.increaseAllowance(spender, addedAmt);
    } else if (action == Action.DECREASE_ALLOWANCE) {
        address spender;
        uint256 decreasedAmt;
        EBTC_Token.decreaseAllowance(spender, decreasedAmt);
    }   else if (action == Action.OTHER) {
        require(true);
    }
    return keccak256('ERC3156FlashBorrower.onFlashLoan');
  }
}
