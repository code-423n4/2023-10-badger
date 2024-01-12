// SPDX-License-Identifier: MIT
pragma solidity 0.8.17;

import "../../packages/contracts/contracts/Dependencies/ICollateralToken.sol";
import "../../packages/contracts/contracts/Dependencies/Ownable.sol";

// This contract is a simple symbolic colletaral token contract with fixed ratio:
// 2 shares == 3 eth that is reflected in functions getSharesByPooledEth() and getPooledEthByShares()

contract CollateralTokenTester is ICollateralToken, Ownable {
    string public override name = "Collateral Token Tester in eBTC";
    string public override symbol = "CollTester";
    uint8 public override decimals = 18;

    event Transfer(address indexed src, address indexed dst, uint256 wad, uint256 _share);
    event Deposit(address indexed dst, uint256 wad, uint256 _share);
    event Withdrawal(address indexed src, uint256 wad, uint256 _share);

    mapping(address => uint256) private balances;
    mapping(address => mapping(address => uint256)) public override allowance;

    uint256 private _totalBalance;

    receive() external payable {
        deposit();
    }

    function deposit() public payable {
        uint256 _share = getSharesByPooledEth(msg.value);
        balances[msg.sender] += _share;
        _totalBalance += _share;
        emit Deposit(msg.sender, msg.value, _share);
    }

    function withdraw(uint256 wad) public {
        uint256 _share = getSharesByPooledEth(wad);
        require(balances[msg.sender] >= _share);
        balances[msg.sender] -= _share;
        _totalBalance -= _share;
        payable(msg.sender).transfer(wad);
        emit Withdrawal(msg.sender, wad, _share);
    }

    function totalSupply() public view override returns (uint) {
        return getPooledEthByShares(_totalBalance);
    }

    function balanceOf(address _usr) external view override returns (uint256) {
        return getPooledEthByShares(balances[_usr]);
    }

    function approve(address guy, uint256 wad) public override returns (bool) {
        allowance[msg.sender][guy] = wad;
        emit Approval(msg.sender, guy, wad);
        return true;
    }

    function transfer(address dst, uint256 wad) public override returns (bool) {
        return transferFrom(msg.sender, dst, wad);
    }

    function transferFrom(address src, address dst, uint256 wad) public override returns (bool) {
        uint256 _share = getSharesByPooledEth(wad);
        require(balances[src] >= _share, "ERC20: transfer amount exceeds balance");

        if (src != msg.sender && allowance[src][msg.sender] != type(uint256).max) {
            require(allowance[src][msg.sender] >= wad);
            allowance[src][msg.sender] -= wad;
        }

        balances[src] -= _share;
        balances[dst] += _share;

        emit Transfer(src, dst, wad, _share);

        return true;
    }

    function getSharesByPooledEth(uint256 _ethAmount) public view override returns (uint256) {
        return (_ethAmount * 2) / 3;
    }

    function getPooledEthByShares(uint256 _sharesAmount) public view override returns (uint256) {
        return (_sharesAmount * 3) / 2;
    }

    function transferShares(
        address _recipient,
        uint256 _sharesAmount
    ) public override returns (uint256) {
        uint256 _tknAmt = getPooledEthByShares(_sharesAmount);

        // NOTE: Changed here to transfer underlying shares without rounding
        balances[msg.sender] -= _sharesAmount;
        balances[_recipient] += _sharesAmount;

        emit Transfer(msg.sender, _recipient, _tknAmt, _sharesAmount);

        return _tknAmt;
    }

    function sharesOf(address _account) public view override returns (uint256) {
        return balances[_account];
    }

    function getOracle() external view override returns (address) {
        return address(this);
    }

    function decreaseAllowance(
        address spender,
        uint256 subtractedValue
    ) external override returns (bool) {
        approve(spender, allowance[msg.sender][spender] - subtractedValue);
        return true;
    }

    function increaseAllowance(
        address spender,
        uint256 addedValue
    ) external override returns (bool) {
        approve(spender, allowance[msg.sender][spender] + addedValue);
        return true;
    }
}
