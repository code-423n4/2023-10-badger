# Report

## Gas Optimizations

| |Issue|Instances|
|-|:-|:-:|
| [GAS-1](#GAS-1) | Use assembly to check for `address(0)` | 29 |
| [GAS-2](#GAS-2) | `array[index] += amount` is cheaper than `array[index] = array[index] + amount` (or related variants) | 2 |
| [GAS-3](#GAS-3) | Using bools for storage incurs overhead | 4 |
| [GAS-4](#GAS-4) | Cache array length outside of loop | 5 |
| [GAS-5](#GAS-5) | State variables should be cached in stack variables rather than re-reading them from storage | 2 |
| [GAS-6](#GAS-6) | Use calldata instead of memory for function arguments that do not get mutated | 6 |
| [GAS-7](#GAS-7) | For Operations that will not overflow, you could use unchecked | 709 |
| [GAS-8](#GAS-8) | Use Custom Errors | 88 |
| [GAS-9](#GAS-9) | Don't initialize variables with default value | 19 |
| [GAS-10](#GAS-10) | Long revert strings | 55 |
| [GAS-11](#GAS-11) | `++i` costs less gas than `i++`, especially when it's used in `for`-loops (`--i`/`i--` too) | 13 |
| [GAS-12](#GAS-12) | Using `private` rather than `public` for constants, saves gas | 31 |
| [GAS-13](#GAS-13) | Use shift Right/Left instead of division/multiplication if possible | 3 |
| [GAS-14](#GAS-14) | Use != 0 instead of > 0 for unsigned integer comparison | 53 |
| [GAS-15](#GAS-15) | `internal` functions not called by the contract should be removed | 8 |

### <a name="GAS-1"></a>[GAS-1] Use assembly to check for `address(0)`

*Saves 6 gas per instance*

*Instances (29)*:

```solidity
File: packages/contracts/contracts/ActivePool.sol

61:         if (_authorityAddress != address(0)) {

394:             _feeRecipientAddress != address(0),

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/ActivePool.sol)

```solidity
File: packages/contracts/contracts/BorrowerOperations.sol

124:         if (_authorityAddress != address(0)) {

735:             recoveredAddress != address(0) && recoveredAddress == _borrower,

1142:             _feeRecipientAddress != address(0),

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/BorrowerOperations.sol)

```solidity
File: packages/contracts/contracts/CdpManager.sol

369:             while (currentBorrower != address(0) && getSyncedICR(_cId, totals.price) < MCR) {

389:             currentBorrower != address(0) && totals.remainingDebtToRedeem > 0 && _maxIterations > 0

497:         while (_cnt > 0 && _id != bytes32(0)) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CdpManager.sol)

```solidity
File: packages/contracts/contracts/CollSurplusPool.sol

55:         if (_authorityAddress != address(0)) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CollSurplusPool.sol)

```solidity
File: packages/contracts/contracts/Dependencies/Auth.sol

38:             (address(auth) != address(0) && auth.canCall(user, address(this), functionSig)) ||

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/Auth.sol)

```solidity
File: packages/contracts/contracts/Dependencies/AuthNoOwner.sol

35:         return (address(auth) != address(0) && auth.canCall(user, address(this), functionSig));

56:         require(address(_authority) == address(0), "Auth: authority is non-zero");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/AuthNoOwner.sol)

```solidity
File: packages/contracts/contracts/Dependencies/RolesAuthority.sol

75:             return bytes32(0) != getUserRoles[user] & getRolesWithCapability[target][functionSig];

158:             if (getUserRoles[user] == bytes32(0)) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/RolesAuthority.sol)

```solidity
File: packages/contracts/contracts/EBTCToken.sol

247:         require(sender != address(0), "EBTCToken: zero sender!");

248:         require(recipient != address(0), "EBTCToken: zero recipient!");

263:         require(account != address(0), "EBTCToken: mint to zero recipient!");

271:         require(account != address(0), "EBTCToken: burn from zero account!");

286:         require(owner != address(0), "EBTCToken: zero approve owner!");

287:         require(spender != address(0), "EBTCToken: zero approve spender!");

297:             _recipient != address(0) && _recipient != address(this),

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/EBTCToken.sol)

```solidity
File: packages/contracts/contracts/HintHelpers.sol

69:                 vars.currentCdpUser != address(0) &&

85:                 vars.currentCdpUser != address(0) &&

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/HintHelpers.sol)

```solidity
File: packages/contracts/contracts/LiquidationLibrary.sol

756:             if (vars.cdpId != bytes32(0) && Cdps[vars.cdpId].status == Status.active) {

819:             if (vars.cdpId != bytes32(0) && Cdps[vars.cdpId].status == Status.active) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LiquidationLibrary.sol)

```solidity
File: packages/contracts/contracts/PriceFeed.sol

224:             if (address(fallbackCaller) == address(0)) {

363:         if (_fallbackCaller != address(0)) {

587:         if (address(fallbackCaller) != address(0)) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/PriceFeed.sol)

```solidity
File: packages/contracts/contracts/SimplifiedDiamondLike.sol

187:         require(facet != address(0), "Diamond: Function does not exist");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/SimplifiedDiamondLike.sol)

### <a name="GAS-2"></a>[GAS-2] `array[index] += amount` is cheaper than `array[index] = array[index] + amount` (or related variants)

When updating a value in an array with arithmetic, using `array[index] += amount` is cheaper than `array[index] = array[index] + amount`.
This is because you avoid an additonal `mload` when the array is stored in memory, and an `sload` when the array is stored in storage.
This can be applied for any arithmetic operation including `+=`, `-=`,`/=`,`*=`,`^=`,`&=`, `%=`, `<<=`,`>>=`, and `>>>=`.
This optimization can be particularly significant if the pattern occurs during a loop.

*Saves 28 gas for a storage array, 38 for a memory array*

*Instances (2)*:

```solidity
File: packages/contracts/contracts/EBTCToken.sol

258:         _balances[recipient] = _balances[recipient] + amount;

266:         _balances[account] = _balances[account] + amount;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/EBTCToken.sol)

### <a name="GAS-3"></a>[GAS-3] Using bools for storage incurs overhead

Use uint256(1) and uint256(2) for true/false to avoid a Gwarmaccess (100 gas), and to avoid Gsset (20000 gas) when changing from ‘false’ to ‘true’, after having been ‘true’ in the past. See [source](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/58f635312aa21f947cae5f8578638a85aa2519f5/contracts/security/ReentrancyGuard.sol#L23-L27).

*Instances (4)*:

```solidity
File: packages/contracts/contracts/CdpManagerStorage.sol

143:     bool public redemptionsPaused;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CdpManagerStorage.sol)

```solidity
File: packages/contracts/contracts/Dependencies/AuthNoOwner.sol

14:     bool private _authorityInitialized;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/AuthNoOwner.sol)

```solidity
File: packages/contracts/contracts/Dependencies/ERC3156FlashLender.sol

15:     bool public flashLoansPaused;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/ERC3156FlashLender.sol)

```solidity
File: packages/contracts/contracts/LeverageMacroBase.sol

35:     bool internal immutable willSweep;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroBase.sol)

### <a name="GAS-4"></a>[GAS-4] Cache array length outside of loop

If not cached, the solidity compiler will always read the length of the array during each iteration. That is, if it is a storage array, this is an extra sload operation (100 additional extra gas for each iteration except for the first) and if it is a memory array, this is an extra mload operation (3 additional gas for each iteration except for the first).

*Instances (5)*:

```solidity
File: packages/contracts/contracts/Governor.sol

46:         for (uint256 i = 0; i < users.length(); i++) {

57:             for (uint256 i = 0; i < _usrs.length; i++) {

122:         for (uint8 i = 0; i < roleIds.length; i++) {

137:             for (uint256 i = 0; i < _sigs.length; ++i) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Governor.sol)

```solidity
File: packages/contracts/contracts/LeverageMacroBase.sol

292:         uint256 beforeSwapsLength = operation.swapsBefore.length;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroBase.sol)

### <a name="GAS-5"></a>[GAS-5] State variables should be cached in stack variables rather than re-reading them from storage

The instances below point to the second+ access of a state variable within a function. Caching of a state variable replaces each Gwarmaccess (100 gas) with a much cheaper stack read. Other less obvious fixes/optimizations include having local memory caches of state variable structs, or having local caches of state variable contracts/addresses.

*Saves 100 gas per instance*

*Instances (2)*:

```solidity
File: packages/contracts/contracts/BorrowerOperations.sol

1103:         ebtcToken.burn(feeRecipientAddress, amount);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/BorrowerOperations.sol)

```solidity
File: packages/contracts/contracts/PriceFeed.sol

384:             address oldFallbackCaller = address(fallbackCaller);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/PriceFeed.sol)

### <a name="GAS-6"></a>[GAS-6] Use calldata instead of memory for function arguments that do not get mutated

Mark data types as `calldata` instead of `memory` where possible. This makes it so that the data is not automatically loaded into memory. If the data passed into the function does not need to be changed (like updating values in an array), it can be passed in as `calldata`. The one exception to this is if the argument must later be passed into another function that takes an argument that specifies `memory` storage.

*Instances (6)*:

```solidity
File: packages/contracts/contracts/CdpManager.sol

126:     function batchLiquidateCdps(bytes32[] memory _cdpArray) external override {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CdpManager.sol)

```solidity
File: packages/contracts/contracts/Governor.sol

120:     function getByteMapFromRoles(uint8[] memory roleIds) public pure returns (bytes32) {

154:     function setRoleName(uint8 role, string memory roleName) external requiresAuth {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Governor.sol)

```solidity
File: packages/contracts/contracts/Interfaces/ISortedCdps.sol

16:     function batchRemove(bytes32[] memory _ids) external;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/ISortedCdps.sol)

```solidity
File: packages/contracts/contracts/LiquidationLibrary.sol

679:     function batchLiquidateCdps(bytes32[] memory _cdpArray) external nonReentrantSelfAndBOps {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LiquidationLibrary.sol)

```solidity
File: packages/contracts/contracts/SortedCdps.sol

419:     function batchRemove(bytes32[] memory _ids) external override {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/SortedCdps.sol)

### <a name="GAS-7"></a>[GAS-7] For Operations that will not overflow, you could use unchecked

*Instances (709)*:

```solidity
File: packages/contracts/contracts/ActivePool.sol

5: import "./Interfaces/IActivePool.sol";

5: import "./Interfaces/IActivePool.sol";

6: import "./Interfaces/ICollSurplusPool.sol";

6: import "./Interfaces/ICollSurplusPool.sol";

7: import "./Dependencies/ICollateralToken.sol";

7: import "./Dependencies/ICollateralToken.sol";

8: import "./Interfaces/ICdpManagerData.sol";

8: import "./Interfaces/ICdpManagerData.sol";

9: import "./Dependencies/ERC3156FlashLender.sol";

9: import "./Dependencies/ERC3156FlashLender.sol";

10: import "./Dependencies/SafeERC20.sol";

10: import "./Dependencies/SafeERC20.sol";

11: import "./Dependencies/ReentrancyGuard.sol";

11: import "./Dependencies/ReentrancyGuard.sol";

12: import "./Dependencies/AuthNoOwner.sol";

12: import "./Dependencies/AuthNoOwner.sol";

13: import "./Dependencies/BaseMath.sol";

13: import "./Dependencies/BaseMath.sol";

31:     uint256 internal systemCollShares; // deposited collateral tracker

31:     uint256 internal systemCollShares; // deposited collateral tracker

33:     uint256 internal feeRecipientCollShares; // coll shares claimable by fee recipient

33:     uint256 internal feeRecipientCollShares; // coll shares claimable by fee recipient

107:             cachedSystemCollShares -= _shares; // Updating here avoids an SLOAD

107:             cachedSystemCollShares -= _shares; // Updating here avoids an SLOAD

107:             cachedSystemCollShares -= _shares; // Updating here avoids an SLOAD

138:         uint256 totalShares = _shares + _liquidatorRewardShares;

141:             cachedSystemCollShares -= _shares;

165:             cachedSystemCollShares -= _shares;

170:         uint256 cachedFeeRecipientCollShares = feeRecipientCollShares + _shares;

197:         uint256 cachedSystemDebt = systemDebt + _amount;

210:         uint256 cachedSystemDebt = systemDebt - _amount;

245:         uint256 cachedSystemCollShares = systemCollShares + _value;

268:         uint256 fee = flashFee(token, amount); // NOTE: Check for `token` is implicit in the requires above // also checks for paused

268:         uint256 fee = flashFee(token, amount); // NOTE: Check for `token` is implicit in the requires above // also checks for paused

268:         uint256 fee = flashFee(token, amount); // NOTE: Check for `token` is implicit in the requires above // also checks for paused

268:         uint256 fee = flashFee(token, amount); // NOTE: Check for `token` is implicit in the requires above // also checks for paused

271:         uint256 amountWithFee = amount + fee;

321:         return (amount * feeBps) / MAX_BPS;

321:         return (amount * feeBps) / MAX_BPS;

347:         ICdpManagerData(cdpManagerAddress).syncGlobalAccountingAndGracePeriod(); // Calling this increases shares so do it first

347:         ICdpManagerData(cdpManagerAddress).syncGlobalAccountingAndGracePeriod(); // Calling this increases shares so do it first

356:             cachedFeeRecipientCollShares -= _shares;

372:         ICdpManagerData(cdpManagerAddress).syncGlobalAccountingAndGracePeriod(); // Accrue State First

372:         ICdpManagerData(cdpManagerAddress).syncGlobalAccountingAndGracePeriod(); // Accrue State First

379:         address cachedFeeRecipientAddress = feeRecipientAddress; // Saves an SLOAD

379:         address cachedFeeRecipientAddress = feeRecipientAddress; // Saves an SLOAD

391:         ICdpManagerData(cdpManagerAddress).syncGlobalAccountingAndGracePeriod(); // Accrue State First

391:         ICdpManagerData(cdpManagerAddress).syncGlobalAccountingAndGracePeriod(); // Accrue State First

405:         ICdpManagerData(cdpManagerAddress).syncGlobalAccountingAndGracePeriod(); // Accrue State First

405:         ICdpManagerData(cdpManagerAddress).syncGlobalAccountingAndGracePeriod(); // Accrue State First

418:         ICdpManagerData(cdpManagerAddress).syncGlobalAccountingAndGracePeriod(); // Accrue State First

418:         ICdpManagerData(cdpManagerAddress).syncGlobalAccountingAndGracePeriod(); // Accrue State First

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/ActivePool.sol)

```solidity
File: packages/contracts/contracts/BorrowerOperations.sol

5: import "./Interfaces/IBorrowerOperations.sol";

5: import "./Interfaces/IBorrowerOperations.sol";

6: import "./Interfaces/ICdpManager.sol";

6: import "./Interfaces/ICdpManager.sol";

7: import "./Interfaces/ICdpManagerData.sol";

7: import "./Interfaces/ICdpManagerData.sol";

8: import "./Interfaces/IEBTCToken.sol";

8: import "./Interfaces/IEBTCToken.sol";

9: import "./Interfaces/ICollSurplusPool.sol";

9: import "./Interfaces/ICollSurplusPool.sol";

10: import "./Interfaces/ISortedCdps.sol";

10: import "./Interfaces/ISortedCdps.sol";

11: import "./Dependencies/EbtcBase.sol";

11: import "./Dependencies/EbtcBase.sol";

12: import "./Dependencies/ReentrancyGuard.sol";

12: import "./Dependencies/ReentrancyGuard.sol";

13: import "./Dependencies/Ownable.sol";

13: import "./Dependencies/Ownable.sol";

14: import "./Dependencies/AuthNoOwner.sol";

14: import "./Dependencies/AuthNoOwner.sol";

15: import "./Dependencies/ERC3156FlashLender.sol";

15: import "./Dependencies/ERC3156FlashLender.sol";

16: import "./Dependencies/PermitNonce.sol";

16: import "./Dependencies/PermitNonce.sol";

70:     "CompilerError: Stack too deep". */

70:     "CompilerError: Stack too deep". */

100:         uint256 collAddUnderlying; // ONLY for isCollIncrease=true

100:         uint256 collAddUnderlying; // ONLY for isCollIncrease=true

142:         @dev Prevents multi-contract reentrancy between these two contracts

396:             _requireNonZeroDebt(vars.debt - vars.netDebtChange);

533:             The static liqudiation incentive is stored in the gas pool and can be considered a deposit / voucher to be returned upon Cdp close, to the closer.

542:             vars.netStEthBalance + LIQUIDATOR_REWARD == _stEthBalance,

727:                         _nonces[_borrower]++,

727:                         _nonces[_borrower]++,

758:         @notice Handles the cases of a debt increase / decrease, and/or a collateral increase / decrease.

758:         @notice Handles the cases of a debt increase / decrease, and/or a collateral increase / decrease.

758:         @notice Handles the cases of a debt increase / decrease, and/or a collateral increase / decrease.

835:         require(_debtChange > 0, "BorrowerOperations: Debt increase requires non-zero debtChange");

936:         require(_debt > 0, "BorrowerOperations: Debt must be non-zero");

965:             return; // Early return, no delegation

965:             return; // Early return, no delegation

1042:             ? _collShares + _collSharesChange

1043:             : _collShares - _collSharesChange;

1044:         newDebt = _isDebtIncrease ? _debt + _debtChange : _debt - _debtChange;

1044:         newDebt = _isDebtIncrease ? _debt + _debtChange : _debt - _debtChange;

1061:             ? systemStEthBalance + _stEthBalanceChange

1062:             : systemStEthBalance - _stEthBalanceChange;

1063:         systemDebt = _isDebtIncrease ? systemDebt + _debtChange : systemDebt - _debtChange;

1063:         systemDebt = _isDebtIncrease ? systemDebt + _debtChange : systemDebt - _debtChange;

1084:         uint256 fee = flashFee(token, amount); // NOTE: Check for `eBTCToken` is implicit here // NOTE: Pause check is here

1084:         uint256 fee = flashFee(token, amount); // NOTE: Check for `eBTCToken` is implicit here // NOTE: Pause check is here

1084:         uint256 fee = flashFee(token, amount); // NOTE: Check for `eBTCToken` is implicit here // NOTE: Pause check is here

1084:         uint256 fee = flashFee(token, amount); // NOTE: Check for `eBTCToken` is implicit here // NOTE: Pause check is here

1100:         ebtcToken.transferFrom(address(receiver), feeRecipientAddress, fee + amount);

1118:         return (amount * feeBps) / MAX_BPS;

1118:         return (amount * feeBps) / MAX_BPS;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/BorrowerOperations.sol)

```solidity
File: packages/contracts/contracts/CRLens.sol

5: import "./Interfaces/IPriceFeed.sol";

5: import "./Interfaces/IPriceFeed.sol";

6: import "./Interfaces/ICdpManager.sol";

6: import "./Interfaces/ICdpManager.sol";

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CRLens.sol)

```solidity
File: packages/contracts/contracts/CdpManager.sol

5: import "./Interfaces/ICdpManager.sol";

5: import "./Interfaces/ICdpManager.sol";

6: import "./Interfaces/ICollSurplusPool.sol";

6: import "./Interfaces/ICollSurplusPool.sol";

7: import "./Interfaces/IEBTCToken.sol";

7: import "./Interfaces/IEBTCToken.sol";

8: import "./Interfaces/ISortedCdps.sol";

8: import "./Interfaces/ISortedCdps.sol";

9: import "./Dependencies/ICollateralTokenOracle.sol";

9: import "./Dependencies/ICollateralTokenOracle.sol";

10: import "./CdpManagerStorage.sol";

11: import "./Dependencies/Proxy.sol";

11: import "./Dependencies/Proxy.sol";

142:             Cdps[_redeemColFromCdp.cdpId].debt /// @audit Redeem everything

142:             Cdps[_redeemColFromCdp.cdpId].debt /// @audit Redeem everything

142:             Cdps[_redeemColFromCdp.cdpId].debt /// @audit Redeem everything

146:             (singleRedemption.debtToRedeem * DECIMAL_PRECISION) / _redeemColFromCdp.price

146:             (singleRedemption.debtToRedeem * DECIMAL_PRECISION) / _redeemColFromCdp.price

156:         uint256 newDebt = _oldDebtAndColl.debt - singleRedemption.debtToRedeem;

157:         uint256 newColl = _oldDebtAndColl.collShares - singleRedemption.collSharesDrawn;

167:                 singleRedemption.collSurplus = newColl; // Collateral surplus processed on full redemption

167:                 singleRedemption.collSurplus = newColl; // Collateral surplus processed on full redemption

257:         collSurplusPool.increaseSurplusCollShares(_borrower, _collSurplus + _liquidatorRewardShares);

336:         _syncGlobalAccounting(); // Apply state, we will syncGracePeriod at end of function

336:         _syncGlobalAccounting(); // Apply state, we will syncGracePeriod at end of function

393:                 _syncAccounting(_cId); /// @audit This happens even if the re-insertion doesn't

393:                 _syncAccounting(_cId); /// @audit This happens even if the re-insertion doesn't

393:                 _syncAccounting(_cId); /// @audit This happens even if the re-insertion doesn't

393:                 _syncAccounting(_cId); /// @audit This happens even if the re-insertion doesn't

410:                 totals.debtToRedeem = totals.debtToRedeem + singleRedemption.debtToRedeem;

411:                 totals.collSharesDrawn = totals.collSharesDrawn + singleRedemption.collSharesDrawn;

413:                     totals.remainingDebtToRedeem -

416:                     totals.totalCollSharesSurplus +

421:                     _numCdpsFullyRedeemed = _numCdpsFullyRedeemed + 1;

429:             _maxIterations--;

429:             _maxIterations--;

458:         totals.collSharesToRedeemer = totals.collSharesDrawn - totals.feeCollShares;

461:             totals.systemCollSharesAtStart - totals.collSharesDrawn - totals.totalCollSharesSurplus,

461:             totals.systemCollSharesAtStart - totals.collSharesDrawn - totals.totalCollSharesSurplus,

462:             totals.systemDebtAtStart - totals.debtToRedeem,

498:             _toRemoveIds[_total - _cnt] = _id;

499:             _cnt = _cnt - 1;

504:             _toRemoveIds[_total - 1] == _end,

553:         3e30 EBTC dwarfs the value of all wealth in the world ( which is < 1e15 USD). */

553:         3e30 EBTC dwarfs the value of all wealth in the world ( which is < 1e15 USD). */

559:         index = uint128(CdpIds.length - 1);

621:         uint256 redeemedEBTCFraction = (collateral.getPooledEthByShares(_ETHDrawn) * _price) /

621:         uint256 redeemedEBTCFraction = (collateral.getPooledEthByShares(_ETHDrawn) * _price) /

624:         uint256 newBaseRate = decayedBaseRate + (redeemedEBTCFraction / beta);

624:         uint256 newBaseRate = decayedBaseRate + (redeemedEBTCFraction / beta);

625:         newBaseRate = EbtcMath._min(newBaseRate, DECIMAL_PRECISION); // cap baseRate at a maximum of 100%

625:         newBaseRate = EbtcMath._min(newBaseRate, DECIMAL_PRECISION); // cap baseRate at a maximum of 100%

626:         require(newBaseRate > 0, "CdpManager: new baseRate is zero!"); // Base rate is always non-zero after redemption

626:         require(newBaseRate > 0, "CdpManager: new baseRate is zero!"); // Base rate is always non-zero after redemption

626:         require(newBaseRate > 0, "CdpManager: new baseRate is zero!"); // Base rate is always non-zero after redemption

650:                 redemptionFeeFloor + _baseRate,

651:                 DECIMAL_PRECISION // cap at a maximum of 100%

651:                 DECIMAL_PRECISION // cap at a maximum of 100%

671:         uint256 redemptionFee = (_redemptionRate * _ETHDrawn) / DECIMAL_PRECISION;

671:         uint256 redemptionFee = (_redemptionRate * _ETHDrawn) / DECIMAL_PRECISION;

678:         require(decayedBaseRate <= DECIMAL_PRECISION, "CdpManager: baseRate too large!"); // The baseRate can decay to 0

678:         require(decayedBaseRate <= DECIMAL_PRECISION, "CdpManager: baseRate too large!"); // The baseRate can decay to 0

691:             ? block.timestamp - lastRedemptionTimestamp

697:             lastRedemptionTimestamp += _minutesPassedSinceLastRedemption() * SECONDS_IN_ONE_MINUTE;

697:             lastRedemptionTimestamp += _minutesPassedSinceLastRedemption() * SECONDS_IN_ONE_MINUTE;

706:         return (baseRate * decayFactor) / DECIMAL_PRECISION;

706:         return (baseRate * decayFactor) / DECIMAL_PRECISION;

712:                 ? ((block.timestamp - lastRedemptionTimestamp) / SECONDS_IN_ONE_MINUTE)

712:                 ? ((block.timestamp - lastRedemptionTimestamp) / SECONDS_IN_ONE_MINUTE)

919:         cdpStEthFeePerUnitIndex[_cdpId] = systemStEthFeePerUnitIndex; /// @audit We critically assume global accounting is synced here

919:         cdpStEthFeePerUnitIndex[_cdpId] = systemStEthFeePerUnitIndex; /// @audit We critically assume global accounting is synced here

919:         cdpStEthFeePerUnitIndex[_cdpId] = systemStEthFeePerUnitIndex; /// @audit We critically assume global accounting is synced here

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CdpManager.sol)

```solidity
File: packages/contracts/contracts/CdpManagerStorage.sol

5: import "./Interfaces/ICdpManager.sol";

5: import "./Interfaces/ICdpManager.sol";

6: import "./Interfaces/ICollSurplusPool.sol";

6: import "./Interfaces/ICollSurplusPool.sol";

7: import "./Interfaces/IEBTCToken.sol";

7: import "./Interfaces/IEBTCToken.sol";

8: import "./Interfaces/ISortedCdps.sol";

8: import "./Interfaces/ISortedCdps.sol";

9: import "./Dependencies/EbtcBase.sol";

9: import "./Dependencies/EbtcBase.sol";

10: import "./Dependencies/ReentrancyGuard.sol";

10: import "./Dependencies/ReentrancyGuard.sol";

11: import "./Dependencies/ICollateralTokenOracle.sol";

11: import "./Dependencies/ICollateralTokenOracle.sol";

12: import "./Dependencies/AuthNoOwner.sol";

12: import "./Dependencies/AuthNoOwner.sol";

24:     uint128 public lastGracePeriodStartTimestamp = UNSET_TIMESTAMP; // use max to signify

24:     uint128 public lastGracePeriodStartTimestamp = UNSET_TIMESTAMP; // use max to signify

141:     uint256 public constant MIN_REDEMPTION_FEE_FLOOR = (DECIMAL_PRECISION * 5) / 1000; // 0.5%

141:     uint256 public constant MIN_REDEMPTION_FEE_FLOOR = (DECIMAL_PRECISION * 5) / 1000; // 0.5%

141:     uint256 public constant MIN_REDEMPTION_FEE_FLOOR = (DECIMAL_PRECISION * 5) / 1000; // 0.5%

141:     uint256 public constant MIN_REDEMPTION_FEE_FLOOR = (DECIMAL_PRECISION * 5) / 1000; // 0.5%

149:     uint256 public constant MIN_MINUTE_DECAY_FACTOR = 1; // Non-zero

149:     uint256 public constant MIN_MINUTE_DECAY_FACTOR = 1; // Non-zero

149:     uint256 public constant MIN_MINUTE_DECAY_FACTOR = 1; // Non-zero

150:     uint256 public constant MAX_MINUTE_DECAY_FACTOR = 999999999999999999; // Corresponds to a very fast decay rate, but not too extreme

150:     uint256 public constant MAX_MINUTE_DECAY_FACTOR = 999999999999999999; // Corresponds to a very fast decay rate, but not too extreme

263:             "CdpManagerStorage: close non-exist or non-active CDP!"

263:             "CdpManagerStorage: close non-exist or non-active CDP!"

297:         uint256 _totalCollateralSnapshot = activePool.getSystemCollShares() - _collRemainder;

313:         _debtIndexDiff = systemDebtRedistributionIndex - cdpDebtRedistributionIndex[_cdpId];

316:             pendingEBTCDebtReward = (cdp.stake * _debtIndexDiff) / DECIMAL_PRECISION;

316:             pendingEBTCDebtReward = (cdp.stake * _debtIndexDiff) / DECIMAL_PRECISION;

411:         uint256 _newTotalStakes = totalStakes - Cdps[_cdpId].stake;

422:         uint256 _newTotalStakes = totalStakes + newStake - oldStake;

422:         uint256 _newTotalStakes = totalStakes + newStake - oldStake;

454:             stake = (_coll * totalStakesSnapshot) / totalCollateralSnapshot;

454:             stake = (_coll * totalStakesSnapshot) / totalCollateralSnapshot;

468:             "CdpManagerStorage: remove non-exist or non-active CDP!"

468:             "CdpManagerStorage: remove non-exist or non-active CDP!"

473:         uint256 idxLast = length - 1;

528:         _syncGlobalAccounting(); // Apply // Could trigger RM

528:         _syncGlobalAccounting(); // Apply // Could trigger RM

528:         _syncGlobalAccounting(); // Apply // Could trigger RM

528:         _syncGlobalAccounting(); // Apply // Could trigger RM

529:         _syncGracePeriod(); // Synch Grace Period

529:         _syncGracePeriod(); // Synch Grace Period

557:         uint256 deltaIndex = _newIndex - _prevIndex;

558:         uint256 deltaIndexFees = (deltaIndex * stakingRewardSplit) / MAX_REWARD_SPLIT;

558:         uint256 deltaIndexFees = (deltaIndex * stakingRewardSplit) / MAX_REWARD_SPLIT;

561:         uint256 _deltaFeeSplit = deltaIndexFees * getSystemCollShares();

564:         uint256 _feeTaken = collateral.getSharesByPooledEth(_deltaFeeSplit) / DECIMAL_PRECISION;

565:         uint256 _deltaFeeSplitShare = (_feeTaken * DECIMAL_PRECISION) +

565:         uint256 _deltaFeeSplitShare = (_feeTaken * DECIMAL_PRECISION) +

567:         uint256 _deltaFeePerUnit = _deltaFeeSplitShare / _cachedAllStakes;

568:         uint256 _perUnitError = _deltaFeeSplitShare - (_deltaFeePerUnit * _cachedAllStakes);

568:         uint256 _perUnitError = _deltaFeeSplitShare - (_deltaFeePerUnit * _cachedAllStakes);

631:         uint256 _feeSplitDistributed = Cdps[_cdpId].stake *

632:             (_systemStEthFeePerUnitIndex - _cdpStEthFeePerUnitIndex);

634:         uint256 _scaledCdpColl = _cdpCol * DECIMAL_PRECISION;

639:                 (_scaledCdpColl - _feeSplitDistributed) / DECIMAL_PRECISION

639:                 (_scaledCdpColl - _feeSplitDistributed) / DECIMAL_PRECISION

690:             _newGlobalSplitIdx /// NOTE: This is latest index

690:             _newGlobalSplitIdx /// NOTE: This is latest index

690:             _newGlobalSplitIdx /// NOTE: This is latest index

774:             uint256 _newPerUnit = systemStEthFeePerUnitIndex + _deltaFeePerUnit;

830:             _newDebt = _newDebt + pendingDebtRedistributed;

880:             _systemCollShare = _systemCollShare - _feeTaken;

900:             block.timestamp > cachedLastGracePeriodStartTimestamp + recoveryModeGracePeriodDuration;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CdpManagerStorage.sol)

```solidity
File: packages/contracts/contracts/CollSurplusPool.sol

5: import "./Interfaces/ICollSurplusPool.sol";

5: import "./Interfaces/ICollSurplusPool.sol";

6: import "./Dependencies/ICollateralToken.sol";

6: import "./Dependencies/ICollateralToken.sol";

7: import "./Dependencies/SafeERC20.sol";

7: import "./Dependencies/SafeERC20.sol";

8: import "./Dependencies/ReentrancyGuard.sol";

8: import "./Dependencies/ReentrancyGuard.sol";

9: import "./Dependencies/AuthNoOwner.sol";

9: import "./Dependencies/AuthNoOwner.sol";

10: import "./Interfaces/IActivePool.sol";

10: import "./Interfaces/IActivePool.sol";

80:         uint256 newAmount = balances[_account] + _amount;

102:             totalSurplusCollShares = cachedTotalSurplusCollShares - claimableColl;

132:         totalSurplusCollShares = totalSurplusCollShares + _value;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CollSurplusPool.sol)

```solidity
File: packages/contracts/contracts/Dependencies/Auth.sol

4: import {Authority} from "./Authority.sol";

33:         Authority auth = authority; // Memoizing authority saves us a warm SLOAD, around 100 gas.

33:         Authority auth = authority; // Memoizing authority saves us a warm SLOAD, around 100 gas.

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/Auth.sol)

```solidity
File: packages/contracts/contracts/Dependencies/AuthNoOwner.sol

4: import {Authority} from "./Authority.sol";

31:         Authority auth = _authority; // Memoizing authority saves us a warm SLOAD, around 100 gas.

31:         Authority auth = _authority; // Memoizing authority saves us a warm SLOAD, around 100 gas.

56:         require(address(_authority) == address(0), "Auth: authority is non-zero");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/AuthNoOwner.sol)

```solidity
File: packages/contracts/contracts/Dependencies/ERC3156FlashLender.sol

5: import "../Interfaces/IERC3156FlashLender.sol";

5: import "../Interfaces/IERC3156FlashLender.sol";

6: import "../Interfaces/IWETH.sol";

6: import "../Interfaces/IWETH.sol";

10:     uint256 public constant MAX_FEE_BPS = 1_000; // 10%

10:     uint256 public constant MAX_FEE_BPS = 1_000; // 10%

14:     uint16 public feeBps = 3; // may be subject to future adjustments through protocol governance

14:     uint16 public feeBps = 3; // may be subject to future adjustments through protocol governance

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/ERC3156FlashLender.sol)

```solidity
File: packages/contracts/contracts/Dependencies/EbtcBase.sol

5: import "./BaseMath.sol";

6: import "./EbtcMath.sol";

7: import "../Interfaces/IActivePool.sol";

7: import "../Interfaces/IActivePool.sol";

8: import "../Interfaces/IPriceFeed.sol";

8: import "../Interfaces/IPriceFeed.sol";

9: import "../Interfaces/IEbtcBase.sol";

9: import "../Interfaces/IEbtcBase.sol";

10: import "../Dependencies/ICollateralToken.sol";

10: import "../Dependencies/ICollateralToken.sol";

19:     uint256 public constant LICR = 1030000000000000000; // 103%

19:     uint256 public constant LICR = 1030000000000000000; // 103%

22:     uint256 public constant MCR = 1100000000000000000; // 110%

22:     uint256 public constant MCR = 1100000000000000000; // 110%

25:     uint256 public constant CCR = 1250000000000000000; // 125%

25:     uint256 public constant CCR = 1250000000000000000; // 125%

33:     uint256 public constant PERCENT_DIVISOR = 200; // dividing by 200 yields 0.5%

33:     uint256 public constant PERCENT_DIVISOR = 200; // dividing by 200 yields 0.5%

35:     uint256 public constant BORROWING_FEE_FLOOR = 0; // 0.5%

35:     uint256 public constant BORROWING_FEE_FLOOR = 0; // 0.5%

37:     uint256 public constant STAKING_REWARD_SPLIT = 5_000; // taking 50% cut from staking reward

37:     uint256 public constant STAKING_REWARD_SPLIT = 5_000; // taking 50% cut from staking reward

61:         return _stEthBalance - LIQUIDATOR_REWARD;

108:         uint256 feePercentage = (_fee * DECIMAL_PRECISION) / _amount;

108:         uint256 feePercentage = (_fee * DECIMAL_PRECISION) / _amount;

119:         return (_debt * _price) / DECIMAL_PRECISION;

119:         return (_debt * _price) / DECIMAL_PRECISION;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/EbtcBase.sol)

```solidity
File: packages/contracts/contracts/Dependencies/EbtcMath.sol

36:         uint256 prod_xy = x * y;

38:         decProd = (prod_xy + (DECIMAL_PRECISION / 2)) / DECIMAL_PRECISION;

38:         decProd = (prod_xy + (DECIMAL_PRECISION / 2)) / DECIMAL_PRECISION;

38:         decProd = (prod_xy + (DECIMAL_PRECISION / 2)) / DECIMAL_PRECISION;

62:         } // cap to avoid overflow

62:         } // cap to avoid overflow

76:                 n = n / 2;

81:                 n = (n - 1) / 2;

81:                 n = (n - 1) / 2;

89:         return (_a >= _b) ? (_a - _b) : (_b - _a);

89:         return (_a >= _b) ? (_a - _b) : (_b - _a);

94:             return (_collShares * NICR_PRECISION) / _debt;

94:             return (_collShares * NICR_PRECISION) / _debt;

110:             uint256 newCollRatio = (_stEthBalance * _price) / _debt;

110:             uint256 newCollRatio = (_stEthBalance * _price) / _debt;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/EbtcMath.sol)

```solidity
File: packages/contracts/contracts/Dependencies/RolesAuthority.sol

4: import {IRolesAuthority} from "./IRolesAuthority.sol";

5: import {Auth, Authority} from "./Auth.sol";

6: import "./EnumerableSet.sol";

23:                             ROLE/USER STORAGE

60:             - The capability has not been burned

61:             - That capability is public, or the user has a role that has been granted the capability to call the function

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/RolesAuthority.sol)

```solidity
File: packages/contracts/contracts/EBTCToken.sol

5: import "./Interfaces/IEBTCToken.sol";

5: import "./Interfaces/IEBTCToken.sol";

7: import "./Dependencies/AuthNoOwner.sol";

7: import "./Dependencies/AuthNoOwner.sol";

8: import "./Dependencies/PermitNonce.sol";

8: import "./Dependencies/PermitNonce.sol";

146:                 _approve(sender, msg.sender, cachedAllowance - amount);

156:         _approve(msg.sender, spender, _allowances[msg.sender][spender] + addedValue);

167:             _approve(msg.sender, spender, cachedAllowances - subtractedValue);

214:                     abi.encode(_PERMIT_TYPEHASH, owner, spender, amount, _nonces[owner]++, deadline)

214:                     abi.encode(_PERMIT_TYPEHASH, owner, spender, amount, _nonces[owner]++, deadline)

255:             _balances[sender] = cachedSenderBalances - amount;

258:         _balances[recipient] = _balances[recipient] + amount;

265:         _totalSupply = _totalSupply + amount;

266:         _balances[account] = _balances[account] + amount;

278:             _balances[account] = cachedBalance - amount;

281:         _totalSupply = _totalSupply - amount;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/EBTCToken.sol)

```solidity
File: packages/contracts/contracts/Governor.sol

4: import {EnumerableSet} from "./Dependencies/EnumerableSet.sol";

4: import {EnumerableSet} from "./Dependencies/EnumerableSet.sol";

5: import {Authority} from "./Dependencies/Auth.sol";

5: import {Authority} from "./Dependencies/Auth.sol";

6: import {RolesAuthority} from "./Dependencies/RolesAuthority.sol";

6: import {RolesAuthority} from "./Dependencies/RolesAuthority.sol";

46:         for (uint256 i = 0; i < users.length(); i++) {

46:         for (uint256 i = 0; i < users.length(); i++) {

50:                 count += 1;

57:             for (uint256 i = 0; i < _usrs.length; i++) {

57:             for (uint256 i = 0; i < _usrs.length; i++) {

62:                     j++;

62:                     j++;

76:         for (uint8 i = 0; i < type(uint8).max; i++) {

76:         for (uint8 i = 0; i < type(uint8).max; i++) {

78:                 count += 1;

84:             for (uint8 i = 0; i < type(uint8).max; i++) {

84:             for (uint8 i = 0; i < type(uint8).max; i++) {

87:                     j++;

87:                     j++;

98:         for (uint8 i = 0; i < type(uint8).max; i++) {

98:         for (uint8 i = 0; i < type(uint8).max; i++) {

101:                 count += 1;

107:             for (uint8 i = 0; i < type(uint8).max; i++) {

107:             for (uint8 i = 0; i < type(uint8).max; i++) {

111:                     j++;

111:                     j++;

122:         for (uint8 i = 0; i < roleIds.length; i++) {

122:         for (uint8 i = 0; i < roleIds.length; i++) {

137:             for (uint256 i = 0; i < _sigs.length; ++i) {

137:             for (uint256 i = 0; i < _sigs.length; ++i) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Governor.sol)

```solidity
File: packages/contracts/contracts/HintHelpers.sol

5: import "./Interfaces/ICdpManager.sol";

5: import "./Interfaces/ICdpManager.sol";

6: import "./Interfaces/ISortedCdps.sol";

6: import "./Interfaces/ISortedCdps.sol";

7: import "./Dependencies/EbtcBase.sol";

7: import "./Dependencies/EbtcBase.sol";

87:                 _maxIterations-- > 0

87:                 _maxIterations-- > 0

105:                         partialRedemptionHintNICR = 0; //reset to 0 as there is no partial redemption in this case

105:                         partialRedemptionHintNICR = 0; //reset to 0 as there is no partial redemption in this case

113:                     vars.remainingEbtcToRedeem = vars.remainingEbtcToRedeem - currentCdpDebt;

121:         truncatedEBTCamount = _EBTCamount - vars.remainingEbtcToRedeem;

143:         vars.remainingEbtcToRedeem = vars.remainingEbtcToRedeem - maxRedeemableEBTC;

145:             (maxRedeemableEBTC * DECIMAL_PRECISION) / _price

145:             (maxRedeemableEBTC * DECIMAL_PRECISION) / _price

148:         uint256 _newCollShareAfter = newCollShare - collShareToReceive;

151:             EbtcMath._computeNominalCR(_newCollShareAfter, currentCdpDebt - maxRedeemableEBTC)

158:     Note: The output address is worst-case O(n) positions away from the correct insert position, however, the function 

161:     Submitting numTrials = k * sqrt(length), with k = 15 makes it very, very likely that the ouput address will 

195:             i++;

195:             i++;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/HintHelpers.sol)

```solidity
File: packages/contracts/contracts/Interfaces/IActivePool.sol

5: import "./IPool.sol";

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IActivePool.sol)

```solidity
File: packages/contracts/contracts/Interfaces/IBorrowerOperations.sol

4: import "./IPositionManagers.sol";

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IBorrowerOperations.sol)

```solidity
File: packages/contracts/contracts/Interfaces/ICdpManager.sol

5: import "./IEbtcBase.sol";

6: import "./ICdpManagerData.sol";

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/ICdpManager.sol)

```solidity
File: packages/contracts/contracts/Interfaces/ICdpManagerData.sol

5: import "./ICollSurplusPool.sol";

6: import "./IEBTCToken.sol";

7: import "./ISortedCdps.sol";

8: import "./IActivePool.sol";

9: import "./IRecoveryModeGracePeriod.sol";

10: import "../Dependencies/ICollateralTokenOracle.sol";

10: import "../Dependencies/ICollateralTokenOracle.sol";

120:         uint256 partialAmount; // used only for partial liquidation, default 0 means full liquidation

120:         uint256 partialAmount; // used only for partial liquidation, default 0 means full liquidation

232:     function syncGlobalAccounting() external; // Accrues StEthFeeSplit without influencing Grace Period

232:     function syncGlobalAccounting() external; // Accrues StEthFeeSplit without influencing Grace Period

234:     function syncGlobalAccountingAndGracePeriod() external; // Accrues StEthFeeSplit and influences Grace Period

234:     function syncGlobalAccountingAndGracePeriod() external; // Accrues StEthFeeSplit and influences Grace Period

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/ICdpManagerData.sol)

```solidity
File: packages/contracts/contracts/Interfaces/IEBTCToken.sol

5: import "../Dependencies/IERC20.sol";

5: import "../Dependencies/IERC20.sol";

6: import "../Dependencies/IERC2612.sol";

6: import "../Dependencies/IERC2612.sol";

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IEBTCToken.sol)

```solidity
File: packages/contracts/contracts/Interfaces/IERC3156FlashLender.sol

5: import "./IERC3156FlashBorrower.sol";

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IERC3156FlashLender.sol)

```solidity
File: packages/contracts/contracts/Interfaces/IEbtcBase.sol

5: import "./IPriceFeed.sol";

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IEbtcBase.sol)

```solidity
File: packages/contracts/contracts/Interfaces/IRecoveryModeGracePeriod.sol

6:     event TCRNotified(uint256 TCR); /// NOTE: Mostly for debugging to ensure synch

6:     event TCRNotified(uint256 TCR); /// NOTE: Mostly for debugging to ensure synch

6:     event TCRNotified(uint256 TCR); /// NOTE: Mostly for debugging to ensure synch

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IRecoveryModeGracePeriod.sol)

```solidity
File: packages/contracts/contracts/LeverageMacroBase.sol

4: import "./Interfaces/IBorrowerOperations.sol";

4: import "./Interfaces/IBorrowerOperations.sol";

5: import "./Interfaces/IERC3156FlashLender.sol";

5: import "./Interfaces/IERC3156FlashLender.sol";

6: import "./Interfaces/IEBTCToken.sol";

6: import "./Interfaces/IEBTCToken.sol";

7: import "./Interfaces/ICdpManager.sol";

7: import "./Interfaces/ICdpManager.sol";

8: import "./Interfaces/ISortedCdps.sol";

8: import "./Interfaces/ISortedCdps.sol";

9: import "./Interfaces/IPriceFeed.sol";

9: import "./Interfaces/IPriceFeed.sol";

10: import "./Dependencies/ICollateralToken.sol";

10: import "./Dependencies/ICollateralToken.sol";

11: import {ICdpManagerData} from "./Interfaces/ICdpManagerData.sol";

11: import {ICdpManagerData} from "./Interfaces/ICdpManagerData.sol";

12: import "./Dependencies/SafeERC20.sol";

12: import "./Dependencies/SafeERC20.sol";

73:         noFlashloan // Use this to not perform a FL and just `doOperation`

73:         noFlashloan // Use this to not perform a FL and just `doOperation`

100:         ICdpManagerData.Status expectedStatus; // NOTE: THIS IS SUPERFLUOUS

100:         ICdpManagerData.Status expectedStatus; // NOTE: THIS IS SUPERFLUOUS

262:         SwapOperation[] swapsBefore; // Empty to skip

262:         SwapOperation[] swapsBefore; // Empty to skip

263:         SwapOperation[] swapsAfter; // Empty to skip

263:         SwapOperation[] swapsAfter; // Empty to skip

264:         OperationType operationType; // Open, Close, etc..

264:         OperationType operationType; // Open, Close, etc..

265:         bytes OperationData; // Generic Operation Data, which we'll decode to use

265:         bytes OperationData; // Generic Operation Data, which we'll decode to use

275:         SwapCheck[] swapChecks; // Empty to skip

275:         SwapCheck[] swapChecks; // Empty to skip

388:                 ++i;

388:                 ++i;

438:             for (uint256 i; i < length; ++i) {

438:             for (uint256 i; i < length; ++i) {

456:         require(addy != address(this)); // If it could call this it could fake the forwarded caller

456:         require(addy != address(this)); // If it could call this it could fake the forwarded caller

515:                 _gas, // gas

515:                 _gas, // gas

516:                 _target, // recipient

516:                 _target, // recipient

517:                 _value, // ether value

517:                 _value, // ether value

518:                 add(_calldata, 0x20), // inloc

518:                 add(_calldata, 0x20), // inloc

519:                 mload(_calldata), // inlen

519:                 mload(_calldata), // inlen

520:                 0, // outloc

520:                 0, // outloc

521:                 0 // outlen

521:                 0 // outlen

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroBase.sol)

```solidity
File: packages/contracts/contracts/LeverageMacroDelegateTarget.sol

4: import {LeverageMacroBase} from "./LeverageMacroBase.sol";

56:             false // Do not sweep to caller

56:             false // Do not sweep to caller

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroDelegateTarget.sol)

```solidity
File: packages/contracts/contracts/LeverageMacroFactory.sol

4: import {LeverageMacroReference} from "./LeverageMacroReference.sol";

5: import "./Dependencies/ICollateralToken.sol";

5: import "./Dependencies/ICollateralToken.sol";

6: import "./Interfaces/IEBTCToken.sol";

6: import "./Interfaces/IEBTCToken.sol";

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroFactory.sol)

```solidity
File: packages/contracts/contracts/LeverageMacroReference.sol

4: import {LeverageMacroBase} from "./LeverageMacroBase.sol";

33:             true // Sweep to caller since this is not supposed to hold funds

33:             true // Sweep to caller since this is not supposed to hold funds

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroReference.sol)

```solidity
File: packages/contracts/contracts/LiquidationLibrary.sol

4: import "./Interfaces/ICdpManagerData.sol";

4: import "./Interfaces/ICdpManagerData.sol";

5: import "./Interfaces/ICollSurplusPool.sol";

5: import "./Interfaces/ICollSurplusPool.sol";

6: import "./Interfaces/IEBTCToken.sol";

6: import "./Interfaces/IEBTCToken.sol";

7: import "./Interfaces/ISortedCdps.sol";

7: import "./Interfaces/ISortedCdps.sol";

8: import "./Dependencies/ICollateralTokenOracle.sol";

8: import "./Dependencies/ICollateralTokenOracle.sol";

9: import "./CdpManagerStorage.sol";

74:         uint256 _ICR = getCachedICR(_cdpId, _price); // @audit syncAccounting already called, guarenteed to be synced

74:         uint256 _ICR = getCachedICR(_cdpId, _price); // @audit syncAccounting already called, guarenteed to be synced

95:                     cachedLastGracePeriodStartTimestamp + recoveryModeGracePeriodDuration,

98:         } // Implicit Else Case, Implies ICR < MRC, meaning the CDP is liquidatable

98:         } // Implicit Else Case, Implies ICR < MRC, meaning the CDP is liquidatable

263:                 _cappedColPortion = _cappedColPortion + _collSurplus;

267:                 _totalDebtToBurn = _totalDebtToBurn - _debtToRedistribute;

270:         _liqState.totalDebtToBurn = _liqState.totalDebtToBurn + _totalDebtToBurn;

271:         _liqState.totalCollSharesToSend = _liqState.totalCollSharesToSend + _cappedColPortion;

272:         _liqState.totalDebtToRedistribute = _liqState.totalDebtToRedistribute + _debtToRedistribute;

274:             _liqState.totalLiquidatorRewardCollShares +

278:         uint _debtToColl = (_totalDebtToBurn * DECIMAL_PRECISION) / _liqState.price;

278:         uint _debtToColl = (_totalDebtToBurn * DECIMAL_PRECISION) / _liqState.price;

279:         uint _cappedColl = collateral.getPooledEthByShares(_cappedColPortion + _liquidatorReward);

289:             _cappedColl > _debtToColl ? (_cappedColl - _debtToColl) : 0

339:                     _recoveryState.totalSurplusCollShares +

343:                 _totalDebtToBurn = _totalDebtToBurn - _debtToRedistribute;

346:         _recoveryState.totalDebtToBurn = _recoveryState.totalDebtToBurn + _totalDebtToBurn;

348:             _recoveryState.totalCollSharesToSend +

351:             _recoveryState.totalDebtToRedistribute +

354:             _recoveryState.totalLiquidatorRewardCollShares +

359:             ? _recoveryState.entireSystemDebt - _totalDebtToBurn

362:             ? _recoveryState.entireSystemColl - _totalColToSend

365:         uint _debtToColl = (_totalDebtToBurn * DECIMAL_PRECISION) / _recoveryState.price;

365:         uint _debtToColl = (_totalDebtToBurn * DECIMAL_PRECISION) / _recoveryState.price;

366:         uint _cappedColl = collateral.getPooledEthByShares(_cappedColPortion + _liquidatorReward);

375:             _cappedColl > _debtToColl ? (_cappedColl - _debtToColl) : 0

406:         uint256 newDebt = _debtAndColl.debt - _partialDebt;

435:             uint _debtToColl = (_partialDebt * DECIMAL_PRECISION) / _partialState.price;

435:             uint _debtToColl = (_partialDebt * DECIMAL_PRECISION) / _partialState.price;

444:                 _cappedColl > _debtToColl ? (_cappedColl - _debtToColl) : 0

460:         _cdp.coll = _coll - _partialColl;

461:         _cdp.debt = _debt - _partialDebt;

519:             systemInitialCollShares - totalCollSharesToSend - totalSurplusCollShares,

519:             systemInitialCollShares - totalCollSharesToSend - totalSurplusCollShares,

520:             systemInitialDebt - totalDebtToBurn,

555:             _incentiveColl = (_totalDebtToBurn * (_ICR > MCR ? MCR : _ICR)) / _price;

555:             _incentiveColl = (_totalDebtToBurn * (_ICR > MCR ? MCR : _ICR)) / _price;

558:             _incentiveColl = (_totalDebtToBurn * LICR) / _price;

558:             _incentiveColl = (_totalDebtToBurn * LICR) / _price;

564:         assert(toLiquidator < _totalColToSend); // Assert is correct here for Echidna

564:         assert(toLiquidator < _totalColToSend); // Assert is correct here for Echidna

567:         collSurplus = _totalColToSend - toLiquidator; // Can use unchecked but w/e

567:         collSurplus = _totalColToSend - toLiquidator; // Can use unchecked but w/e

567:         collSurplus = _totalColToSend - toLiquidator; // Can use unchecked but w/e

567:         collSurplus = _totalColToSend - toLiquidator; // Can use unchecked but w/e

579:             _incentiveColl = (_totalDebtToBurn * (_ICR > MCR ? MCR : _ICR)) / _price;

579:             _incentiveColl = (_totalDebtToBurn * (_ICR > MCR ? MCR : _ICR)) / _price;

592:             uint256 _debtToRepay = (_incentiveColl * _price) / LICR;

592:             uint256 _debtToRepay = (_incentiveColl * _price) / LICR;

595:                 ? _totalDebtToBurn - _debtToRepay //  Bad Debt (to be redistributed) is (CdpDebt - Repaid)

595:                 ? _totalDebtToBurn - _debtToRepay //  Bad Debt (to be redistributed) is (CdpDebt - Repaid)

595:                 ? _totalDebtToBurn - _debtToRepay //  Bad Debt (to be redistributed) is (CdpDebt - Repaid)

595:                 ? _totalDebtToBurn - _debtToRepay //  Bad Debt (to be redistributed) is (CdpDebt - Repaid)

596:                 : 0; // Else 0 (note we may underpay per the comment above, althought that may be imaginary)

596:                 : 0; // Else 0 (note we may underpay per the comment above, althought that may be imaginary)

603:         collSurplus = (toLiquidator == _totalColToSend) ? 0 : _totalColToSend - toLiquidator;

774:                     vars.entireSystemDebt = vars.entireSystemDebt - singleLiquidation.debtToBurn;

776:                         vars.entireSystemColl -

777:                         singleLiquidation.totalCollToSendToLiquidator -

800:             ++vars.i;

800:             ++vars.i;

830:             ++vars.i;

830:             ++vars.i;

845:             oldTotals.totalDebtInSequence +

847:         newTotals.totalDebtToBurn = oldTotals.totalDebtToBurn + singleLiquidation.debtToBurn;

849:             oldTotals.totalCollToSendToLiquidator +

852:             oldTotals.totalDebtToRedistribute +

854:         newTotals.totalCollSurplus = oldTotals.totalCollSurplus + singleLiquidation.collSurplus;

856:             oldTotals.totalCollReward +

878:         uint256 EBTCDebtNumerator = (_debt * DECIMAL_PRECISION) + lastEBTCDebtErrorRedistribution;

878:         uint256 EBTCDebtNumerator = (_debt * DECIMAL_PRECISION) + lastEBTCDebtErrorRedistribution;

882:         uint256 EBTCDebtRewardPerUnitStaked = EBTCDebtNumerator / _totalStakes;

885:             EBTCDebtNumerator -

886:             (EBTCDebtRewardPerUnitStaked * _totalStakes);

889:         systemDebtRedistributionIndex = systemDebtRedistributionIndex + EBTCDebtRewardPerUnitStaked;

902:             (_partialDebt + _convertDebtDenominationToBtc(MIN_NET_STETH_BALANCE, _price)) <=

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LiquidationLibrary.sol)

```solidity
File: packages/contracts/contracts/PriceFeed.sol

5: import "./Interfaces/IPriceFeed.sol";

5: import "./Interfaces/IPriceFeed.sol";

6: import "./Interfaces/IFallbackCaller.sol";

6: import "./Interfaces/IFallbackCaller.sol";

7: import "./Dependencies/AggregatorV3Interface.sol";

7: import "./Dependencies/AggregatorV3Interface.sol";

8: import "./Dependencies/BaseMath.sol";

8: import "./Dependencies/BaseMath.sol";

9: import "./Dependencies/EbtcMath.sol";

9: import "./Dependencies/EbtcMath.sol";

10: import "./Dependencies/AuthNoOwner.sol";

10: import "./Dependencies/AuthNoOwner.sol";

29:     IFallbackCaller public fallbackCaller; // Wrapper contract that calls the fallback system

29:     IFallbackCaller public fallbackCaller; // Wrapper contract that calls the fallback system

32:     uint256 public constant TIMEOUT_ETH_BTC_FEED = 4800; // 1 hours & 20min: 60 * 80

32:     uint256 public constant TIMEOUT_ETH_BTC_FEED = 4800; // 1 hours & 20min: 60 * 80

32:     uint256 public constant TIMEOUT_ETH_BTC_FEED = 4800; // 1 hours & 20min: 60 * 80

33:     uint256 public constant TIMEOUT_STETH_ETH_FEED = 90000; // 25 hours: 60 * 60 * 25

33:     uint256 public constant TIMEOUT_STETH_ETH_FEED = 90000; // 25 hours: 60 * 60 * 25

33:     uint256 public constant TIMEOUT_STETH_ETH_FEED = 90000; // 25 hours: 60 * 60 * 25

33:     uint256 public constant TIMEOUT_STETH_ETH_FEED = 90000; // 25 hours: 60 * 60 * 25

36:     uint256 public constant MAX_PRICE_DEVIATION_FROM_PREVIOUS_ROUND = 5e17; // 50%

36:     uint256 public constant MAX_PRICE_DEVIATION_FROM_PREVIOUS_ROUND = 5e17; // 50%

42:     uint256 public constant MAX_PRICE_DIFFERENCE_BETWEEN_ORACLES = 5e16; // 5%

42:     uint256 public constant MAX_PRICE_DIFFERENCE_BETWEEN_ORACLES = 5e16; // 5%

458:             ? ((maxPrice - minPrice) * EbtcMath.DECIMAL_PRECISION) / maxPrice

458:             ? ((maxPrice - minPrice) * EbtcMath.DECIMAL_PRECISION) / maxPrice

458:             ? ((maxPrice - minPrice) * EbtcMath.DECIMAL_PRECISION) / maxPrice

494:         return block.timestamp - _timestamp > _timeout;

534:         uint256 percentPriceDifference = ((maxPrice - minPrice) * EbtcMath.DECIMAL_PRECISION) /

534:         uint256 percentPriceDifference = ((maxPrice - minPrice) * EbtcMath.DECIMAL_PRECISION) /

534:         uint256 percentPriceDifference = ((maxPrice - minPrice) * EbtcMath.DECIMAL_PRECISION) /

599:         } // If unset we return a zero response with success = false

599:         } // If unset we return a zero response with success = false

640:             uint80 /* answeredInRound */

640:             uint80 /* answeredInRound */

640:             uint80 /* answeredInRound */

640:             uint80 /* answeredInRound */

656:             uint80 /* answeredInRound */

656:             uint80 /* answeredInRound */

656:             uint80 /* answeredInRound */

656:             uint80 /* answeredInRound */

722:         try ETH_BTC_CL_FEED.getRoundData(_currentRoundEthBtcId - 1) returns (

728:             uint80 /* answeredInRound */

728:             uint80 /* answeredInRound */

728:             uint80 /* answeredInRound */

728:             uint80 /* answeredInRound */

738:         try STETH_ETH_CL_FEED.getRoundData(_currentRoundStEthEthId - 1) returns (

744:             uint80 /* answeredInRound */

744:             uint80 /* answeredInRound */

744:             uint80 /* answeredInRound */

744:             uint80 /* answeredInRound */

798:             ? 10 ** (_stEthEthDecimals - _ethBtcDecimals)

798:             ? 10 ** (_stEthEthDecimals - _ethBtcDecimals)

798:             ? 10 ** (_stEthEthDecimals - _ethBtcDecimals)

799:             : 10 ** (_ethBtcDecimals - _stEthEthDecimals);

799:             : 10 ** (_ethBtcDecimals - _stEthEthDecimals);

799:             : 10 ** (_ethBtcDecimals - _stEthEthDecimals);

801:             (_scaledDecimal *

802:                 uint256(_ethBtcAnswer) *

803:                 uint256(_stEthEthAnswer) *

804:                 EbtcMath.DECIMAL_PRECISION) / 10 ** (_decimalDenominator * 2);

804:                 EbtcMath.DECIMAL_PRECISION) / 10 ** (_decimalDenominator * 2);

804:                 EbtcMath.DECIMAL_PRECISION) / 10 ** (_decimalDenominator * 2);

804:                 EbtcMath.DECIMAL_PRECISION) / 10 ** (_decimalDenominator * 2);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/PriceFeed.sol)

```solidity
File: packages/contracts/contracts/SimplifiedDiamondLike.sol

35:         OurSettings settings; // add to these to allow more fields

35:         OurSettings settings; // add to these to allow more fields

77:         require(msg.sender == address(this)); // Must call this via `execute` to explicitly set the flag

77:         require(msg.sender == address(this)); // Must call this via `execute` to explicitly set the flag

100:         address to; // Target to call

100:         address to; // Target to call

101:         bool checkSuccess; // If false we will ignore a revert

101:         bool checkSuccess; // If false we will ignore a revert

102:         uint128 value; // How much ETH to send

102:         uint128 value; // How much ETH to send

103:         uint128 gas; // How much gas to send

103:         uint128 gas; // How much gas to send

104:         bool capGas; // true to use above "gas" setting or we send gasleft()

104:         bool capGas; // true to use above "gas" setting or we send gasleft()

105:         OperationType opType; // See `OperationType`

105:         OperationType opType; // See `OperationType`

106:         bytes data; // Calldata to send (funsig + data)

106:         bytes data; // Calldata to send (funsig + data)

106:         bytes data; // Calldata to send (funsig + data)

118:                 ++i;

118:                 ++i;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/SimplifiedDiamondLike.sol)

```solidity
File: packages/contracts/contracts/SortedCdps.sol

5: import "./Interfaces/ISortedCdps.sol";

5: import "./Interfaces/ISortedCdps.sol";

6: import "./Interfaces/ICdpManager.sol";

6: import "./Interfaces/ICdpManager.sol";

7: import "./Interfaces/IBorrowerOperations.sol";

7: import "./Interfaces/IBorrowerOperations.sol";

60:     uint256 constant ADDRESS_SHIFT = 96; // 8 * 12; Puts the address at leftmost bytes32 position

60:     uint256 constant ADDRESS_SHIFT = 96; // 8 * 12; Puts the address at leftmost bytes32 position

60:     uint256 constant ADDRESS_SHIFT = 96; // 8 * 12; Puts the address at leftmost bytes32 position

61:     uint256 constant BLOCK_SHIFT = 64; // 8 * 8; Puts the block value after the address

61:     uint256 constant BLOCK_SHIFT = 64; // 8 * 8; Puts the block value after the address

61:     uint256 constant BLOCK_SHIFT = 64; // 8 * 8; Puts the block value after the address

65:         bytes32 nextId; // Id of next node (smaller NICR) in the list

65:         bytes32 nextId; // Id of next node (smaller NICR) in the list

66:         bytes32 prevId; // Id of previous node (larger NICR) in the list

66:         bytes32 prevId; // Id of previous node (larger NICR) in the list

71:         bytes32 head; // Head of the list. Also the node in the list with the largest NICR

71:         bytes32 head; // Head of the list. Also the node in the list with the largest NICR

72:         bytes32 tail; // Tail of the list. Also the node in the list with the smallest NICR

72:         bytes32 tail; // Tail of the list. Also the node in the list with the smallest NICR

73:         uint256 size; // Current size of the list

73:         uint256 size; // Current size of the list

74:         mapping(bytes32 => Node) nodes; // Track the corresponding ids for each node in the list

74:         mapping(bytes32 => Node) nodes; // Track the corresponding ids for each node in the list

113:         serialized |= bytes32(blockHeight) << BLOCK_SHIFT; // to accommendate more than 4.2 billion blocks

113:         serialized |= bytes32(blockHeight) << BLOCK_SHIFT; // to accommendate more than 4.2 billion blocks

193:                     _currentIndex = _currentIndex + 1;

196:             ++i;

196:             ++i;

251:                 _ownedCount = _ownedCount + 1;

253:             ++i;

253:             ++i;

322:                 ++_cdpRetrieved;

322:                 ++_cdpRetrieved;

324:             ++i;

324:             ++i;

357:             ++nextCdpNonce;

357:             ++nextCdpNonce;

404:         data.size = data.size + 1;

425:         bytes32 _lastNext = data.nodes[_ids[_len - 1]].nextId;

432:         for (uint256 i = 0; i < _len; ++i) {

432:         for (uint256 i = 0; i < _len; ++i) {

449:         for (uint i = 0; i < _len; ++i) {

449:         for (uint i = 0; i < _len; ++i) {

453:         data.size = data.size - _len;

489:         data.size = data.size - 1;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/SortedCdps.sol)

### <a name="GAS-8"></a>[GAS-8] Use Custom Errors

[Source](https://blog.soliditylang.org/2021/04/21/custom-errors/)
Instead of using error strings, to reduce deployment and runtime cost, you should use Custom Errors. This would save both deployment and runtime cost.

*Instances (88)*:

```solidity
File: packages/contracts/contracts/ActivePool.sol

104:         require(cachedSystemCollShares >= _shares, "!ActivePoolBal");

137:         require(cachedSystemCollShares >= _shares, "ActivePool: Insufficient collateral shares");

162:         require(cachedSystemCollShares >= _shares, "ActivePool: Insufficient collateral shares");

236:         require(msg.sender == cdpManagerAddress, "ActivePool: Caller is not CdpManager");

267:         require(amount > 0, "ActivePool: 0 Amount");

269:         require(amount <= maxFlashLoan(token), "ActivePool: Too much");

318:         require(token == address(collateral), "ActivePool: collateral Only");

319:         require(!flashLoansPaused, "ActivePool: Flash Loans Paused");

374:         require(token != address(collateral), "ActivePool: Cannot Sweep Collateral");

377:         require(amount <= balance, "ActivePool: Attempt to sweep more than balance");

407:         require(_newFee <= MAX_FEE_BPS, "ERC3156FlashLender: _newFee should <= MAX_FEE_BPS");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/ActivePool.sol)

```solidity
File: packages/contracts/contracts/BorrowerOperations.sol

145:         require(locked == OPEN, "BorrowerOperations: Reentrancy in nonReentrant call");

463:         require(vars.netStEthBalance > 0, "BorrowerOperations: zero collateral for openCdp()!");

715:         require(_deadline >= block.timestamp, "BorrowerOperations: Position manager permit expired");

826:         require(status == 1, "BorrowerOperations: Cdp does not exist or is closed");

831:         require(status == 0, "BorrowerOperations: Cdp is active or has been previously closed");

835:         require(_debtChange > 0, "BorrowerOperations: Debt increase requires non-zero debtChange");

918:         require(_newICR >= CCR, "BorrowerOperations: Operation must leave cdp with ICR >= CCR");

936:         require(_debt > 0, "BorrowerOperations: Debt must be non-zero");

1083:         require(amount > 0, "BorrowerOperations: 0 Amount");

1085:         require(amount <= maxFlashLoan(token), "BorrowerOperations: Too much");

1115:         require(token == address(ebtcToken), "BorrowerOperations: EBTC Only");

1116:         require(!flashLoansPaused, "BorrowerOperations: Flash Loans Paused");

1155:         require(_newFee <= MAX_FEE_BPS, "ERC3156FlashLender: _newFee should <= MAX_FEE_BPS");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/BorrowerOperations.sol)

```solidity
File: packages/contracts/contracts/CRLens.sol

104:             if (reason.length < 68) revert("Unexpected error");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CRLens.sol)

```solidity
File: packages/contracts/contracts/CdpManager.sol

332:         require(redemptionsPaused == false, "CdpManager: Redemptions Paused");

431:         require(totals.collSharesDrawn > 0, "CdpManager: Unable to redeem any amount");

502:         require(_toRemoveIds[0] == _start, "CdpManager: batchRemoveSortedCdpIds check start error");

626:         require(newBaseRate > 0, "CdpManager: new baseRate is zero!"); // Base rate is always non-zero after redemption

672:         require(redemptionFee < _ETHDrawn, "CdpManager: Fee would eat up all returned collateral");

678:         require(decayedBaseRate <= DECIMAL_PRECISION, "CdpManager: baseRate too large!"); // The baseRate can decay to 0

754:         require(_amount > 0, "CdpManager: Amount must be greater than zero");

758:         require(_TCR >= MCR, "CdpManager: Cannot redeem when TCR < MCR");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CdpManager.sol)

```solidity
File: packages/contracts/contracts/CdpManagerStorage.sol

242:         require(locked == OPEN, "CdpManager: Reentrancy in nonReentrant call");

453:             require(totalStakesSnapshot > 0, "CdpManagerStorage: zero totalStakesSnapshot!");

475:         require(index <= idxLast, "CdpManagerStorage: CDP indexing overflow!");

556:         require(_newIndex > _prevIndex, "CDPManager: only take fee with bigger new index");

584:         require(activePool.getSystemCollShares() > _feeTaken, "CDPManager: fee split is too big");

649:         require(Cdps[_cdpId].status == Status.active, "CdpManager: Cdp does not exist or is closed");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CdpManagerStorage.sol)

```solidity
File: packages/contracts/contracts/CollSurplusPool.sol

92:         require(claimableColl > 0, "CollSurplusPool: No collateral available to claim");

99:         require(cachedTotalSurplusCollShares >= claimableColl, "!CollSurplusPoolBal");

120:         require(msg.sender == cdpManagerAddress, "CollSurplusPool: Caller is not CdpManager");

124:         require(msg.sender == activePoolAddress, "CollSurplusPool: Caller is not Active Pool");

143:         require(token != address(collateral), "CollSurplusPool: Cannot Sweep Collateral");

146:         require(amount <= balance, "CollSurplusPool: Attempt to sweep more than balance");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CollSurplusPool.sol)

```solidity
File: packages/contracts/contracts/Dependencies/Auth.sol

27:         require(isAuthorized(msg.sender, msg.sig), "Auth: UNAUTHORIZED");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/Auth.sol)

```solidity
File: packages/contracts/contracts/Dependencies/AuthNoOwner.sol

17:         require(isAuthorized(msg.sender, msg.sig), "Auth: UNAUTHORIZED");

56:         require(address(_authority) == address(0), "Auth: authority is non-zero");

57:         require(!_authorityInitialized, "Auth: authority already initialized");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/AuthNoOwner.sol)

```solidity
File: packages/contracts/contracts/Dependencies/EbtcBase.sol

109:         require(feePercentage <= _maxFeePercentage, "Fee exceeded provided maximum");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/EbtcBase.sol)

```solidity
File: packages/contracts/contracts/Dependencies/ReentrancyGuard.sol

14:         require(locked == OPEN, "ReentrancyGuard: Reentrancy in nonReentrant call");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/ReentrancyGuard.sol)

```solidity
File: packages/contracts/contracts/EBTCToken.sol

144:             require(cachedAllowance >= amount, "ERC20: transfer amount exceeds allowance");

165:         require(cachedAllowances >= subtractedValue, "ERC20: decreased allowance below zero");

208:         require(deadline >= block.timestamp, "EBTC: expired deadline");

219:         require(recoveredAddress == owner, "EBTC: invalid signature");

247:         require(sender != address(0), "EBTCToken: zero sender!");

248:         require(recipient != address(0), "EBTCToken: zero recipient!");

251:         require(cachedSenderBalances >= amount, "ERC20: transfer amount exceeds balance");

263:         require(account != address(0), "EBTCToken: mint to zero recipient!");

271:         require(account != address(0), "EBTCToken: burn from zero account!");

274:         require(cachedBalance >= amount, "ERC20: burn amount exceeds balance");

286:         require(owner != address(0), "EBTCToken: zero approve owner!");

287:         require(spender != address(0), "EBTCToken: zero approve spender!");

324:         require(msg.sender == cdpManagerAddress, "EBTC: Caller is not CdpManager");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/EBTCToken.sol)

```solidity
File: packages/contracts/contracts/LeverageMacroBase.sol

40:         revert("Must be overridden");

45:         require(owner() == msg.sender, "Must be owner");

249:             require(check.value >= valueToCheck, "!LeverageMacroReference: gte post check");

251:             require(check.value <= valueToCheck, "!LeverageMacroReference: let post check");

253:             require(check.value == valueToCheck, "!LeverageMacroReference: equal post check");

255:             revert("Operator not found");

352:         require(initiator == address(this), "LeverageMacroReference: wrong initiator for flashloan");

421:         require(success, "Call has failed");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroBase.sol)

```solidity
File: packages/contracts/contracts/LiquidationLibrary.sol

56:         require(_partialAmount != 0, "LiquidationLibrary: use `liquidate` for 100%");

710:         require(totals.totalDebtInSequence > 0, "LiquidationLibrary: nothing to liquidate");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LiquidationLibrary.sol)

```solidity
File: packages/contracts/contracts/SimplifiedDiamondLike.sol

111:         require(msg.sender == owner, "Must be owner");

179:             require(ds.settings.callbackEnabledForCall, "Only Enabled Callbacks");

187:         require(facet != address(0), "Diamond: Function does not exist");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/SimplifiedDiamondLike.sol)

```solidity
File: packages/contracts/contracts/SortedCdps.sol

352:         require(cdpManager.getCdpStatus(_id) == 0, "SortedCdps: new id is NOT nonExistent!");

365:         require(!isFull(), "SortedCdps: List is full");

367:         require(!contains(_id), "SortedCdps: List already contains the node");

369:         require(_id != dummyId, "SortedCdps: Id cannot be zero");

371:         require(_NICR > 0, "SortedCdps: NICR must be positive");

422:         require(_len > 1, "SortedCdps: batchRemove() only apply to multiple cdpIds!");

433:             require(contains(_ids[i]), "SortedCdps: List does not contain the id");

458:         require(contains(_id), "SortedCdps: List does not contain the id");

506:         require(contains(_id), "SortedCdps: List does not contain the id");

508:         require(_newNICR > 0, "SortedCdps: NICR must be positive");

715:         require(msg.sender == address(cdpManager), "SortedCdps: Caller is not the CdpManager");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/SortedCdps.sol)

### <a name="GAS-9"></a>[GAS-9] Don't initialize variables with default value

*Instances (19)*:

```solidity
File: packages/contracts/contracts/Dependencies/EbtcBase.sol

35:     uint256 public constant BORROWING_FEE_FLOOR = 0; // 0.5%

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/EbtcBase.sol)

```solidity
File: packages/contracts/contracts/Governor.sol

46:         for (uint256 i = 0; i < users.length(); i++) {

54:             uint256 j = 0;

57:             for (uint256 i = 0; i < _usrs.length; i++) {

76:         for (uint8 i = 0; i < type(uint8).max; i++) {

82:             uint256 j = 0;

84:             for (uint8 i = 0; i < type(uint8).max; i++) {

98:         for (uint8 i = 0; i < type(uint8).max; i++) {

105:             uint256 j = 0;

107:             for (uint8 i = 0; i < type(uint8).max; i++) {

122:         for (uint8 i = 0; i < roleIds.length; i++) {

137:             for (uint256 i = 0; i < _sigs.length; ++i) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Governor.sol)

```solidity
File: packages/contracts/contracts/HintHelpers.sol

105:                         partialRedemptionHintNICR = 0; //reset to 0 as there is no partial redemption in this case

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/HintHelpers.sol)

```solidity
File: packages/contracts/contracts/SortedCdps.sol

182:         uint _currentIndex = 0;

245:         uint _ownedCount = 0;

246:         uint i = 0;

311:         uint i = 0;

432:         for (uint256 i = 0; i < _len; ++i) {

449:         for (uint i = 0; i < _len; ++i) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/SortedCdps.sol)

### <a name="GAS-10"></a>[GAS-10] Long revert strings

*Instances (55)*:

```solidity
File: packages/contracts/contracts/ActivePool.sol

137:         require(cachedSystemCollShares >= _shares, "ActivePool: Insufficient collateral shares");

162:         require(cachedSystemCollShares >= _shares, "ActivePool: Insufficient collateral shares");

236:         require(msg.sender == cdpManagerAddress, "ActivePool: Caller is not CdpManager");

374:         require(token != address(collateral), "ActivePool: Cannot Sweep Collateral");

377:         require(amount <= balance, "ActivePool: Attempt to sweep more than balance");

407:         require(_newFee <= MAX_FEE_BPS, "ERC3156FlashLender: _newFee should <= MAX_FEE_BPS");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/ActivePool.sol)

```solidity
File: packages/contracts/contracts/BorrowerOperations.sol

145:         require(locked == OPEN, "BorrowerOperations: Reentrancy in nonReentrant call");

463:         require(vars.netStEthBalance > 0, "BorrowerOperations: zero collateral for openCdp()!");

715:         require(_deadline >= block.timestamp, "BorrowerOperations: Position manager permit expired");

826:         require(status == 1, "BorrowerOperations: Cdp does not exist or is closed");

831:         require(status == 0, "BorrowerOperations: Cdp is active or has been previously closed");

835:         require(_debtChange > 0, "BorrowerOperations: Debt increase requires non-zero debtChange");

918:         require(_newICR >= CCR, "BorrowerOperations: Operation must leave cdp with ICR >= CCR");

936:         require(_debt > 0, "BorrowerOperations: Debt must be non-zero");

1116:         require(!flashLoansPaused, "BorrowerOperations: Flash Loans Paused");

1155:         require(_newFee <= MAX_FEE_BPS, "ERC3156FlashLender: _newFee should <= MAX_FEE_BPS");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/BorrowerOperations.sol)

```solidity
File: packages/contracts/contracts/CdpManager.sol

431:         require(totals.collSharesDrawn > 0, "CdpManager: Unable to redeem any amount");

502:         require(_toRemoveIds[0] == _start, "CdpManager: batchRemoveSortedCdpIds check start error");

626:         require(newBaseRate > 0, "CdpManager: new baseRate is zero!"); // Base rate is always non-zero after redemption

672:         require(redemptionFee < _ETHDrawn, "CdpManager: Fee would eat up all returned collateral");

754:         require(_amount > 0, "CdpManager: Amount must be greater than zero");

758:         require(_TCR >= MCR, "CdpManager: Cannot redeem when TCR < MCR");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CdpManager.sol)

```solidity
File: packages/contracts/contracts/CdpManagerStorage.sol

242:         require(locked == OPEN, "CdpManager: Reentrancy in nonReentrant call");

453:             require(totalStakesSnapshot > 0, "CdpManagerStorage: zero totalStakesSnapshot!");

475:         require(index <= idxLast, "CdpManagerStorage: CDP indexing overflow!");

556:         require(_newIndex > _prevIndex, "CDPManager: only take fee with bigger new index");

649:         require(Cdps[_cdpId].status == Status.active, "CdpManager: Cdp does not exist or is closed");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CdpManagerStorage.sol)

```solidity
File: packages/contracts/contracts/CollSurplusPool.sol

92:         require(claimableColl > 0, "CollSurplusPool: No collateral available to claim");

120:         require(msg.sender == cdpManagerAddress, "CollSurplusPool: Caller is not CdpManager");

124:         require(msg.sender == activePoolAddress, "CollSurplusPool: Caller is not Active Pool");

143:         require(token != address(collateral), "CollSurplusPool: Cannot Sweep Collateral");

146:         require(amount <= balance, "CollSurplusPool: Attempt to sweep more than balance");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CollSurplusPool.sol)

```solidity
File: packages/contracts/contracts/Dependencies/AuthNoOwner.sol

57:         require(!_authorityInitialized, "Auth: authority already initialized");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/AuthNoOwner.sol)

```solidity
File: packages/contracts/contracts/Dependencies/ReentrancyGuard.sol

14:         require(locked == OPEN, "ReentrancyGuard: Reentrancy in nonReentrant call");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/ReentrancyGuard.sol)

```solidity
File: packages/contracts/contracts/EBTCToken.sol

144:             require(cachedAllowance >= amount, "ERC20: transfer amount exceeds allowance");

165:         require(cachedAllowances >= subtractedValue, "ERC20: decreased allowance below zero");

251:         require(cachedSenderBalances >= amount, "ERC20: transfer amount exceeds balance");

263:         require(account != address(0), "EBTCToken: mint to zero recipient!");

271:         require(account != address(0), "EBTCToken: burn from zero account!");

274:         require(cachedBalance >= amount, "ERC20: burn amount exceeds balance");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/EBTCToken.sol)

```solidity
File: packages/contracts/contracts/LeverageMacroBase.sol

249:             require(check.value >= valueToCheck, "!LeverageMacroReference: gte post check");

251:             require(check.value <= valueToCheck, "!LeverageMacroReference: let post check");

253:             require(check.value == valueToCheck, "!LeverageMacroReference: equal post check");

352:         require(initiator == address(this), "LeverageMacroReference: wrong initiator for flashloan");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroBase.sol)

```solidity
File: packages/contracts/contracts/LiquidationLibrary.sol

56:         require(_partialAmount != 0, "LiquidationLibrary: use `liquidate` for 100%");

710:         require(totals.totalDebtInSequence > 0, "LiquidationLibrary: nothing to liquidate");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LiquidationLibrary.sol)

```solidity
File: packages/contracts/contracts/SortedCdps.sol

352:         require(cdpManager.getCdpStatus(_id) == 0, "SortedCdps: new id is NOT nonExistent!");

367:         require(!contains(_id), "SortedCdps: List already contains the node");

371:         require(_NICR > 0, "SortedCdps: NICR must be positive");

422:         require(_len > 1, "SortedCdps: batchRemove() only apply to multiple cdpIds!");

433:             require(contains(_ids[i]), "SortedCdps: List does not contain the id");

458:         require(contains(_id), "SortedCdps: List does not contain the id");

506:         require(contains(_id), "SortedCdps: List does not contain the id");

508:         require(_newNICR > 0, "SortedCdps: NICR must be positive");

715:         require(msg.sender == address(cdpManager), "SortedCdps: Caller is not the CdpManager");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/SortedCdps.sol)

### <a name="GAS-11"></a>[GAS-11] `++i` costs less gas than `i++`, especially when it's used in `for`-loops (`--i`/`i--` too)

*Saves 5 gas per loop*

*Instances (13)*:

```solidity
File: packages/contracts/contracts/BorrowerOperations.sol

727:                         _nonces[_borrower]++,

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/BorrowerOperations.sol)

```solidity
File: packages/contracts/contracts/EBTCToken.sol

214:                     abi.encode(_PERMIT_TYPEHASH, owner, spender, amount, _nonces[owner]++, deadline)

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/EBTCToken.sol)

```solidity
File: packages/contracts/contracts/Governor.sol

46:         for (uint256 i = 0; i < users.length(); i++) {

57:             for (uint256 i = 0; i < _usrs.length; i++) {

62:                     j++;

76:         for (uint8 i = 0; i < type(uint8).max; i++) {

84:             for (uint8 i = 0; i < type(uint8).max; i++) {

87:                     j++;

98:         for (uint8 i = 0; i < type(uint8).max; i++) {

107:             for (uint8 i = 0; i < type(uint8).max; i++) {

111:                     j++;

122:         for (uint8 i = 0; i < roleIds.length; i++) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Governor.sol)

```solidity
File: packages/contracts/contracts/HintHelpers.sol

195:             i++;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/HintHelpers.sol)

### <a name="GAS-12"></a>[GAS-12] Using `private` rather than `public` for constants, saves gas

If needed, the values can be read from the verified contract source code, or if there are multiple values there can be a single getter function that [returns a tuple](https://github.com/code-423n4/2022-08-frax/blob/90f55a9ce4e25bceed3a74290b854341d8de6afa/src/contracts/FraxlendPair.sol#L156-L178) of the values of all currently-public constants. Saves **3406-3606 gas** in deployment gas due to the compiler not having to create non-payable getter functions for deployment calldata, not having to store the bytes of the value outside of where it's used, and not adding another entry to the method ID table

*Instances (31)*:

```solidity
File: packages/contracts/contracts/ActivePool.sol

24:     string public constant NAME = "ActivePool";

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/ActivePool.sol)

```solidity
File: packages/contracts/contracts/BorrowerOperations.sol

29:     string public constant NAME = "BorrowerOperations";

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/BorrowerOperations.sol)

```solidity
File: packages/contracts/contracts/CdpManagerStorage.sol

21:     uint128 public constant UNSET_TIMESTAMP = type(uint128).max;

22:     uint128 public constant MINIMUM_GRACE_PERIOD = 15 minutes;

122:     string public constant NAME = "CdpManager";

139:     uint256 public constant SECONDS_IN_ONE_MINUTE = 60;

141:     uint256 public constant MIN_REDEMPTION_FEE_FLOOR = (DECIMAL_PRECISION * 5) / 1000; // 0.5%

149:     uint256 public constant MIN_MINUTE_DECAY_FACTOR = 1; // Non-zero

150:     uint256 public constant MAX_MINUTE_DECAY_FACTOR = 999999999999999999; // Corresponds to a very fast decay rate, but not too extreme

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CdpManagerStorage.sol)

```solidity
File: packages/contracts/contracts/CollSurplusPool.sol

19:     string public constant NAME = "CollSurplusPool";

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CollSurplusPool.sol)

```solidity
File: packages/contracts/contracts/Dependencies/ERC3156FlashLender.sol

9:     uint256 public constant MAX_BPS = 10_000;

10:     uint256 public constant MAX_FEE_BPS = 1_000; // 10%

11:     bytes32 public constant FLASH_SUCCESS_VALUE = keccak256("ERC3156FlashBorrower.onFlashLoan");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/ERC3156FlashLender.sol)

```solidity
File: packages/contracts/contracts/Dependencies/EbtcBase.sol

19:     uint256 public constant LICR = 1030000000000000000; // 103%

22:     uint256 public constant MCR = 1100000000000000000; // 110%

25:     uint256 public constant CCR = 1250000000000000000; // 125%

28:     uint256 public constant LIQUIDATOR_REWARD = 2e17;

31:     uint256 public constant MIN_NET_STETH_BALANCE = 2e18;

33:     uint256 public constant PERCENT_DIVISOR = 200; // dividing by 200 yields 0.5%

35:     uint256 public constant BORROWING_FEE_FLOOR = 0; // 0.5%

37:     uint256 public constant STAKING_REWARD_SPLIT = 5_000; // taking 50% cut from staking reward

39:     uint256 public constant MAX_REWARD_SPLIT = 10_000;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/EbtcBase.sol)

```solidity
File: packages/contracts/contracts/Dependencies/EbtcMath.sol

7:     uint256 public constant MAX_TCR = type(uint256).max;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/EbtcMath.sol)

```solidity
File: packages/contracts/contracts/HintHelpers.sol

12:     string public constant NAME = "HintHelpers";

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/HintHelpers.sol)

```solidity
File: packages/contracts/contracts/PriceFeed.sol

22:     string public constant NAME = "PriceFeed";

32:     uint256 public constant TIMEOUT_ETH_BTC_FEED = 4800; // 1 hours & 20min: 60 * 80

33:     uint256 public constant TIMEOUT_STETH_ETH_FEED = 90000; // 25 hours: 60 * 60 * 25

36:     uint256 public constant MAX_PRICE_DEVIATION_FROM_PREVIOUS_ROUND = 5e17; // 50%

42:     uint256 public constant MAX_PRICE_DIFFERENCE_BETWEEN_ORACLES = 5e16; // 5%

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/PriceFeed.sol)

```solidity
File: packages/contracts/contracts/SortedCdps.sol

52:     string public constant NAME = "SortedCdps";

80:     bytes32 public constant dummyId =

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/SortedCdps.sol)

### <a name="GAS-13"></a>[GAS-13] Use shift Right/Left instead of division/multiplication if possible

*Instances (3)*:

```solidity
File: packages/contracts/contracts/Dependencies/EbtcMath.sol

38:         decProd = (prod_xy + (DECIMAL_PRECISION / 2)) / DECIMAL_PRECISION;

76:                 n = n / 2;

81:                 n = (n - 1) / 2;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/EbtcMath.sol)

### <a name="GAS-14"></a>[GAS-14] Use != 0 instead of > 0 for unsigned integer comparison

*Instances (53)*:

```solidity
File: packages/contracts/contracts/ActivePool.sol

267:         require(amount > 0, "ActivePool: 0 Amount");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/ActivePool.sol)

```solidity
File: packages/contracts/contracts/BorrowerOperations.sol

393:         if (!_isDebtIncrease && _debtChange > 0) {

463:         require(vars.netStEthBalance > 0, "BorrowerOperations: zero collateral for openCdp()!");

835:         require(_debtChange > 0, "BorrowerOperations: Debt increase requires non-zero debtChange");

936:         require(_debt > 0, "BorrowerOperations: Debt must be non-zero");

1083:         require(amount > 0, "BorrowerOperations: 0 Amount");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/BorrowerOperations.sol)

```solidity
File: packages/contracts/contracts/CdpManager.sol

389:             currentBorrower != address(0) && totals.remainingDebtToRedeem > 0 && _maxIterations > 0

389:             currentBorrower != address(0) && totals.remainingDebtToRedeem > 0 && _maxIterations > 0

431:         require(totals.collSharesDrawn > 0, "CdpManager: Unable to redeem any amount");

497:         while (_cnt > 0 && _id != bytes32(0)) {

626:         require(newBaseRate > 0, "CdpManager: new baseRate is zero!"); // Base rate is always non-zero after redemption

754:         require(_amount > 0, "CdpManager: Amount must be greater than zero");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CdpManager.sol)

```solidity
File: packages/contracts/contracts/CdpManagerStorage.sol

315:         if (_debtIndexDiff > 0) {

362:         if (_feeSplitDistributed > 0 || _debtIndexDelta > 0) {

362:         if (_feeSplitDistributed > 0 || _debtIndexDelta > 0) {

369:             if (_feeSplitDistributed > 0) {

380:             if (_debtIndexDelta > 0) {

453:             require(totalStakesSnapshot > 0, "CdpManagerStorage: zero totalStakesSnapshot!");

512:         if (_newIndex > _oldIndex && totalStakes > 0) {

765:         if (_newIndex > _oldIndex && totalStakes > 0) {

796:         if (_cdpPerUnitIdx != _systemStEthFeePerUnitIndex && _cdpPerUnitIdx > 0) {

829:         if (pendingDebtRedistributed > 0) {

879:         if (_feeTaken > 0) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CdpManagerStorage.sol)

```solidity
File: packages/contracts/contracts/CollSurplusPool.sol

92:         require(claimableColl > 0, "CollSurplusPool: No collateral available to claim");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CollSurplusPool.sol)

```solidity
File: packages/contracts/contracts/Dependencies/EbtcMath.sol

93:         if (_debt > 0) {

109:         if (_debt > 0) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/EbtcMath.sol)

```solidity
File: packages/contracts/contracts/Governor.sol

53:         if (count > 0) {

81:         if (count > 0) {

104:         if (count > 0) {

135:         if (_sigs.length > 0) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Governor.sol)

```solidity
File: packages/contracts/contracts/HintHelpers.sol

86:                 vars.remainingEbtcToRedeem > 0 &&

87:                 _maxIterations-- > 0

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/HintHelpers.sol)

```solidity
File: packages/contracts/contracts/LeverageMacroBase.sol

128:         if (operation.amountToTransferIn > 0) {

223:         if (ebtcBal > 0) {

227:         if (collateralBal > 0) {

293:         if (beforeSwapsLength > 0) {

307:         if (afterSwapsLength > 0) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroBase.sol)

```solidity
File: packages/contracts/contracts/LiquidationLibrary.sol

195:             if (_outputState.totalSurplusCollShares > 0) {

261:             if (_collSurplus > 0) {

266:             if (_debtToRedistribute > 0) {

336:             if (_collSurplus > 0) {

342:             if (_debtToRedistribute > 0) {

525:         if (totalDebtToRedistribute > 0) {

710:         require(totals.totalDebtInSequence > 0, "LiquidationLibrary: nothing to liquidate");

713:         if (totals.totalCollSurplus > 0) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LiquidationLibrary.sol)

```solidity
File: packages/contracts/contracts/PriceFeed.sol

457:         uint256 percentDeviation = maxPrice > 0

489:             _fallbackResponse.timestamp > 0 &&

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/PriceFeed.sol)

```solidity
File: packages/contracts/contracts/SortedCdps.sol

202:             if (maxNodes > 0 && i >= maxNodes) {

259:             if (maxNodes > 0 && i >= maxNodes) {

274:         if (_ownedCount > 0) {

330:             if (maxNodes > 0 && i >= maxNodes) {

371:         require(_NICR > 0, "SortedCdps: NICR must be positive");

508:         require(_newNICR > 0, "SortedCdps: NICR must be positive");

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/SortedCdps.sol)

### <a name="GAS-15"></a>[GAS-15] `internal` functions not called by the contract should be removed

If the functions are required by an interface, the contract should inherit from that interface and use the `override` keyword

*Instances (8)*:

```solidity
File: packages/contracts/contracts/Dependencies/EbtcMath.sol

20:     function _min(uint256 _a, uint256 _b) internal pure returns (uint256) {

24:     function _max(uint256 _a, uint256 _b) internal pure returns (uint256) {

59:     function _decPow(uint256 _base, uint256 _minutes) internal pure returns (uint256) {

88:     function _getAbsoluteDifference(uint256 _a, uint256 _b) internal pure returns (uint256) {

92:     function _computeNominalCR(uint256 _collShares, uint256 _debt) internal pure returns (uint256) {

104:     function _computeCR(

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/EbtcMath.sol)

```solidity
File: packages/contracts/contracts/EBTCToken.sol

306:     function _requireCallerIsBorrowerOperations() internal view {

323:     function _requireCallerIsCdpM() internal view {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/EBTCToken.sol)

## Non Critical Issues

| |Issue|Instances|
|-|:-|:-:|
| [NC-1](#NC-1) | Missing checks for `address(0)` when assigning values to address state variables | 4 |
| [NC-2](#NC-2) |  `require()` / `revert()` statements should have descriptive reason strings | 12 |
| [NC-3](#NC-3) | Return values of `approve()` not checked | 12 |
| [NC-4](#NC-4) | Event is missing `indexed` fields | 42 |
| [NC-5](#NC-5) | Constants should be defined rather than using magic numbers | 1 |
| [NC-6](#NC-6) | Functions not used internally could be marked external | 21 |

### <a name="NC-1"></a>[NC-1] Missing checks for `address(0)` when assigning values to address state variables

*Instances (4)*:

```solidity
File: packages/contracts/contracts/ActivePool.sol

57:         feeRecipientAddress = _feeRecipientAddress;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/ActivePool.sol)

```solidity
File: packages/contracts/contracts/BorrowerOperations.sol

121:         feeRecipientAddress = _feeRecipientAddress;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/BorrowerOperations.sol)

```solidity
File: packages/contracts/contracts/Dependencies/Auth.sol

19:         owner = _owner;

53:         owner = newOwner;

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/Auth.sol)

### <a name="NC-2"></a>[NC-2]  `require()` / `revert()` statements should have descriptive reason strings

*Instances (12)*:

```solidity
File: packages/contracts/contracts/Dependencies/Auth.sol

45:         require(msg.sender == owner || authority.canCall(msg.sender, address(this), msg.sig));

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/Auth.sol)

```solidity
File: packages/contracts/contracts/Dependencies/AuthNoOwner.sol

41:         require(_authority.canCall(msg.sender, address(this), msg.sig));

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/AuthNoOwner.sol)

```solidity
File: packages/contracts/contracts/LeverageMacroBase.sol

452:         require(addy != address(borrowerOperations));

453:         require(addy != address(sortedCdps));

454:         require(addy != address(activePool));

455:         require(addy != address(cdpManager));

456:         require(addy != address(this)); // If it could call this it could fake the forwarded caller

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroBase.sol)

```solidity
File: packages/contracts/contracts/SimplifiedDiamondLike.sol

52:         require(msg.sender == owner);

56:         require(sig != 0x94b24d09);

67:         require(msg.sender == owner);

77:         require(msg.sender == address(this)); // Must call this via `execute` to explicitly set the flag

154:             require(success);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/SimplifiedDiamondLike.sol)

### <a name="NC-3"></a>[NC-3] Return values of `approve()` not checked

Not all IERC20 implementations `revert()` when there's a failure in `approve()`. The function signature has a boolean return value and they indicate errors that way instead. By not checking the return value, operations that should have marked as failed, may potentially go through without actually approving anything

*Instances (12)*:

```solidity
File: packages/contracts/contracts/EBTCToken.sol

130:         _approve(msg.sender, spender, amount);

146:                 _approve(sender, msg.sender, cachedAllowance - amount);

156:         _approve(msg.sender, spender, _allowances[msg.sender][spender] + addedValue);

167:             _approve(msg.sender, spender, cachedAllowances - subtractedValue);

220:         _approve(owner, spender, amount);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/EBTCToken.sol)

```solidity
File: packages/contracts/contracts/LeverageMacroDelegateTarget.sol

22:     stETH.approve(_borrowerOperationsAddress, type(uint256).max);

23:     stETH.approve(_activePool, type(uint256).max);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroDelegateTarget.sol)

```solidity
File: packages/contracts/contracts/LeverageMacroReference.sol

40:         stETH.approve(_borrowerOperationsAddress, type(uint256).max);

41:         stETH.approve(_activePool, type(uint256).max);

53:         ebtcToken.approve(address(borrowerOperations), type(uint256).max);

54:         stETH.approve(address(borrowerOperations), type(uint256).max);

55:         stETH.approve(address(activePool), type(uint256).max);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroReference.sol)

### <a name="NC-4"></a>[NC-4] Event is missing `indexed` fields

Index event fields make the field more quickly accessible to off-chain tools that parse events. However, note that each index field costs extra gas during emission, so it's not necessarily best to index the maximum allowed per event (three fields). Each event should use three indexed fields if there are three or more fields, and gas usage is not particularly of concern for the events in question. If there are fewer than three fields, all of the fields should be indexed.

*Instances (42)*:

```solidity
File: packages/contracts/contracts/Interfaces/IActivePool.sol

9:     event ActivePoolEBTCDebtUpdated(uint256 _EBTCDebt);

10:     event SystemCollSharesUpdated(uint256 _coll);

12:     event FeeRecipientClaimableCollSharesIncreased(uint256 _coll, uint256 _fee);

13:     event FeeRecipientClaimableCollSharesDecreased(uint256 _coll, uint256 _fee);

14:     event FlashLoanSuccess(

20:     event SweepTokenSuccess(address indexed _token, uint256 _amount, address indexed _recipient);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IActivePool.sol)

```solidity
File: packages/contracts/contracts/Interfaces/IBorrowerOperations.sol

11:     event FlashLoanSuccess(

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IBorrowerOperations.sol)

```solidity
File: packages/contracts/contracts/Interfaces/ICdpManagerData.sol

17:     event StakingRewardSplitSet(uint256 _stakingRewardSplit);

18:     event RedemptionFeeFloorSet(uint256 _redemptionFeeFloor);

19:     event MinuteDecayFactorSet(uint256 _minuteDecayFactor);

20:     event BetaSet(uint256 _beta);

21:     event RedemptionsPaused(bool _paused);

23:     event Liquidation(uint256 _liquidatedDebt, uint256 _liquidatedColl, uint256 _liqReward);

24:     event Redemption(

60:     event BaseRateUpdated(uint256 _baseRate);

61:     event LastRedemptionTimestampUpdated(uint256 _lastFeeOpTime);

62:     event TotalStakesUpdated(uint256 _newTotalStakes);

63:     event SystemSnapshotsUpdated(uint256 _totalStakesSnapshot, uint256 _totalCollateralSnapshot);

64:     event SystemDebtRedistributionIndexUpdated(uint256 _systemDebtRedistributionIndex);

65:     event CdpDebtRedistributionIndexUpdated(bytes32 _cdpId, uint256 _cdpDebtRedistributionIndex);

66:     event CdpArrayIndexUpdated(bytes32 _cdpId, uint256 _newIndex);

67:     event StEthIndexUpdated(uint256 _oldIndex, uint256 _newIndex, uint256 _updTimestamp);

68:     event CollateralFeePerUnitUpdated(uint256 _oldPerUnit, uint256 _newPerUnit, uint256 _feeTaken);

69:     event CdpFeeSplitApplied(

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/ICdpManagerData.sol)

```solidity
File: packages/contracts/contracts/Interfaces/ICollSurplusPool.sol

8:     event SurplusCollSharesUpdated(address indexed _account, uint256 _newBalance);

9:     event CollSharesTransferred(address indexed _to, uint256 _amount);

11:     event SweepTokenSuccess(address indexed _token, uint256 _amount, address indexed _recipient);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/ICollSurplusPool.sol)

```solidity
File: packages/contracts/contracts/Interfaces/IERC3156FlashLender.sol

8:     event FlashFeeSet(address indexed _setter, uint256 _oldFee, uint256 _newFee);

9:     event MaxFlashFeeSet(address indexed _setter, uint256 _oldMaxFee, uint256 _newMaxFee);

10:     event FlashLoansPaused(address indexed _setter, bool _paused);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IERC3156FlashLender.sol)

```solidity
File: packages/contracts/contracts/Interfaces/IFallbackCaller.sol

7:     event FallbackTimeOutChanged(uint256 _oldTimeOut, uint256 _newTimeOut);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IFallbackCaller.sol)

```solidity
File: packages/contracts/contracts/Interfaces/IPool.sol

9:     event ETHBalanceUpdated(uint256 _newBalance);

10:     event EBTCBalanceUpdated(uint256 _newBalance);

11:     event CollSharesTransferred(address indexed _to, uint256 _amount);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IPool.sol)

```solidity
File: packages/contracts/contracts/Interfaces/IPositionManagers.sol

12:     event PositionManagerApprovalSet(

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IPositionManagers.sol)

```solidity
File: packages/contracts/contracts/Interfaces/IPriceFeed.sol

7:     event LastGoodPriceUpdated(uint256 _lastGoodPrice);

8:     event PriceFeedStatusChanged(Status newStatus);

13:     event UnhealthyFallbackCaller(address indexed _fallbackCaller, uint256 timestamp);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IPriceFeed.sol)

```solidity
File: packages/contracts/contracts/Interfaces/IRecoveryModeGracePeriod.sol

6:     event TCRNotified(uint256 TCR); /// NOTE: Mostly for debugging to ensure synch

11:     event GracePeriodDurationSet(uint256 _recoveryModeGracePeriodDuration);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IRecoveryModeGracePeriod.sol)

```solidity
File: packages/contracts/contracts/Interfaces/ISortedCdps.sol

9:     event NodeAdded(bytes32 _id, uint _NICR);

10:     event NodeRemoved(bytes32 _id);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/ISortedCdps.sol)

### <a name="NC-5"></a>[NC-5] Constants should be defined rather than using magic numbers

*Instances (1)*:

```solidity
File: packages/contracts/contracts/BorrowerOperations.sol

476:             CCR > MCR (125% vs 110%)

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/BorrowerOperations.sol)

### <a name="NC-6"></a>[NC-6] Functions not used internally could be marked external

*Instances (21)*:

```solidity
File: packages/contracts/contracts/ActivePool.sol

100:     function transferSystemCollShares(address _account, uint256 _shares) public override {

371:     function sweepToken(address token, uint256 amount) public nonReentrant requiresAuth {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/ActivePool.sol)

```solidity
File: packages/contracts/contracts/CdpManager.sol

570:     function getSystemDebt() public view returns (uint256 entireSystemDebt) {

717:     function getDeploymentStartTime() public view returns (uint256) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CdpManager.sol)

```solidity
File: packages/contracts/contracts/CdpManagerStorage.sol

701:     function getCachedICR(bytes32 _cdpId, uint256 _price) public view returns (uint256) {

719:     function getPendingRedistributedDebt(

728:     function hasPendingRedistributedDebt(bytes32 _cdpId) public view returns (bool) {

864:     function getSyncedICR(bytes32 _cdpId, uint256 _price) public view returns (uint256) {

874:     function getSyncedTCR(uint256 _price) public view returns (uint256) {

890:     function canLiquidateRecoveryMode(uint256 icr, uint256 tcr) public view returns (bool) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CdpManagerStorage.sol)

```solidity
File: packages/contracts/contracts/CollSurplusPool.sol

142:     function sweepToken(address token, uint256 amount) public nonReentrant requiresAuth {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CollSurplusPool.sol)

```solidity
File: packages/contracts/contracts/Dependencies/AuthNoOwner.sol

22:     function authority() public view returns (Authority) {

26:     function authorityInitialized() public view returns (bool) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/AuthNoOwner.sol)

```solidity
File: packages/contracts/contracts/Dependencies/RolesAuthority.sol

50:     function isPublicCapability(address target, bytes4 functionSig) public view returns (bool) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/RolesAuthority.sol)

```solidity
File: packages/contracts/contracts/Governor.sol

96:     function getRolesFromByteMap(bytes32 byteMap) public pure returns (uint8[] memory roleIds) {

120:     function getByteMapFromRoles(uint8[] memory roleIds) public pure returns (bytes32) {

131:     function getEnabledFunctionsInTarget(

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Governor.sol)

```solidity
File: packages/contracts/contracts/LeverageMacroBase.sol

234:     function sweepToken(address token, uint256 amount) public {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroBase.sol)

```solidity
File: packages/contracts/contracts/LeverageMacroDelegateTarget.sol

63:     function owner() public override returns (address) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroDelegateTarget.sol)

```solidity
File: packages/contracts/contracts/LeverageMacroReference.sol

44:     function owner() public override returns (address) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroReference.sol)

```solidity
File: packages/contracts/contracts/SortedCdps.sol

130:     function nonExistId() public pure override returns (bytes32) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/SortedCdps.sol)

## Low Issues

| |Issue|Instances|
|-|:-|:-:|
| [L-1](#L-1) |  `abi.encodePacked()` should not be used with dynamic types when passing the result to a hash function such as `keccak256()` | 1 |
| [L-2](#L-2) | Do not use deprecated library functions | 2 |
| [L-3](#L-3) | Empty Function Body - Consider commenting why | 8 |
| [L-4](#L-4) | Unsafe ERC20 operation(s) | 15 |
| [L-5](#L-5) | Use of ecrecover is susceptible to signature malleability | 2 |

### <a name="L-1"></a>[L-1]  `abi.encodePacked()` should not be used with dynamic types when passing the result to a hash function such as `keccak256()`

Use `abi.encode()` instead which will pad items to 32 bytes, which will [prevent hash collisions](https://docs.soliditylang.org/en/v0.8.13/abi-spec.html#non-standard-packed-mode) (e.g. `abi.encodePacked(0x123,0x456)` => `0x123456` => `abi.encodePacked(0x1,0x23456)`, but `abi.encode(0x123,0x456)` => `0x0...1230...456`). "Unless there is a compelling reason, `abi.encode` should be preferred". If there is only one argument to `abi.encodePacked()` it can often be cast to `bytes()` or `bytes32()` [instead](https://ethereum.stackexchange.com/questions/30912/how-to-compare-strings-in-solidity#answer-82739).
If all arguments are strings and or bytes, `bytes.concat()` should be used instead

*Instances (1)*:

```solidity
File: packages/contracts/contracts/HintHelpers.sol

182:             latestRandomSeed = uint256(keccak256(abi.encodePacked(latestRandomSeed)));

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/HintHelpers.sol)

### <a name="L-2"></a>[L-2] Do not use deprecated library functions

*Instances (2)*:

```solidity
File: packages/contracts/contracts/LeverageMacroBase.sol

405:         IERC20(swapData.tokenForSwap).safeApprove(

427:         IERC20(swapData.tokenForSwap).safeApprove(swapData.addressForApprove, 0);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroBase.sol)

### <a name="L-3"></a>[L-3] Empty Function Body - Consider commenting why

*Instances (8)*:

```solidity
File: packages/contracts/contracts/CRLens.sol

117:         try this.getRealTCR(true) {} catch (bytes memory reason) {

126:         try this.getRealICR(cdpId, true) {} catch (bytes memory reason) {

135:         try this.getRealNICR(cdpId, true) {} catch (bytes memory reason) {

144:         try this.getCheckRecoveryMode(true) {} catch (bytes memory reason) {

150:         try anything() {} catch (bytes memory reason) {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CRLens.sol)

```solidity
File: packages/contracts/contracts/Dependencies/RolesAuthority.sol

20:     constructor(address _owner, Authority _authority) Auth(_owner, _authority) {}

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/RolesAuthority.sol)

```solidity
File: packages/contracts/contracts/Governor.sol

36:     constructor(address _owner) RolesAuthority(_owner, Authority(address(this))) {}

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Governor.sol)

```solidity
File: packages/contracts/contracts/LiquidationLibrary.sol

34:     {}

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LiquidationLibrary.sol)

### <a name="L-4"></a>[L-4] Unsafe ERC20 operation(s)

*Instances (15)*:

```solidity
File: packages/contracts/contracts/ActivePool.sol

274:         collateral.transfer(address(receiver), amount);

283:         collateral.transferFrom(address(receiver), address(this), amountWithFee);

286:         collateral.transfer(feeRecipientAddress, fee);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/ActivePool.sol)

```solidity
File: packages/contracts/contracts/BorrowerOperations.sol

785:         collateral.transferFrom(msg.sender, address(activePool), _stEthBalance);

1100:         ebtcToken.transferFrom(address(receiver), feeRecipientAddress, fee + amount);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/BorrowerOperations.sol)

```solidity
File: packages/contracts/contracts/LeverageMacroBase.sol

224:             ebtcToken.transfer(msg.sender, ebtcBal);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroBase.sol)

```solidity
File: packages/contracts/contracts/LeverageMacroDelegateTarget.sol

21:     ebtcToken.approve(_borrowerOperationsAddress, type(uint256).max);

22:     stETH.approve(_borrowerOperationsAddress, type(uint256).max);

23:     stETH.approve(_activePool, type(uint256).max);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroDelegateTarget.sol)

```solidity
File: packages/contracts/contracts/LeverageMacroReference.sol

39:         ebtcToken.approve(_borrowerOperationsAddress, type(uint256).max);

40:         stETH.approve(_borrowerOperationsAddress, type(uint256).max);

41:         stETH.approve(_activePool, type(uint256).max);

53:         ebtcToken.approve(address(borrowerOperations), type(uint256).max);

54:         stETH.approve(address(borrowerOperations), type(uint256).max);

55:         stETH.approve(address(activePool), type(uint256).max);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroReference.sol)

### <a name="L-5"></a>[L-5] Use of ecrecover is susceptible to signature malleability

The built-in EVM precompile ecrecover is susceptible to signature malleability, which could lead to replay attacks.Consider using OpenZeppelin’s ECDSA library instead of the built-in function.

*Instances (2)*:

```solidity
File: packages/contracts/contracts/BorrowerOperations.sol

733:         address recoveredAddress = ecrecover(digest, v, r, s);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/BorrowerOperations.sol)

```solidity
File: packages/contracts/contracts/EBTCToken.sol

218:         address recoveredAddress = ecrecover(digest, v, r, s);

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/EBTCToken.sol)

## Medium Issues

| |Issue|Instances|
|-|:-|:-:|
| [M-1](#M-1) | Centralization Risk for trusted owners | 36 |

### <a name="M-1"></a>[M-1] Centralization Risk for trusted owners

#### Impact

Contracts have owners with privileged rights to perform admin tasks and need to be trusted to not perform malicious updates or drain funds.

*Instances (36)*:

```solidity
File: packages/contracts/contracts/ActivePool.sol

346:     function claimFeeRecipientCollShares(uint256 _shares) external override requiresAuth {

371:     function sweepToken(address token, uint256 amount) public nonReentrant requiresAuth {

390:     function setFeeRecipientAddress(address _feeRecipientAddress) external requiresAuth {

404:     function setFeeBps(uint256 _newFee) external requiresAuth {

417:     function setFlashLoansPaused(bool _paused) external requiresAuth {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/ActivePool.sol)

```solidity
File: packages/contracts/contracts/BorrowerOperations.sol

1140:     function setFeeRecipientAddress(address _feeRecipientAddress) external requiresAuth {

1154:     function setFeeBps(uint256 _newFee) external requiresAuth {

1167:     function setFlashLoansPaused(bool _paused) external requiresAuth {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/BorrowerOperations.sol)

```solidity
File: packages/contracts/contracts/CdpManager.sol

773:     function setStakingRewardSplit(uint256 _stakingRewardSplit) external requiresAuth {

788:     function setRedemptionFeeFloor(uint256 _redemptionFeeFloor) external requiresAuth {

807:     function setMinuteDecayFactor(uint256 _minuteDecayFactor) external requiresAuth {

830:     function setBeta(uint256 _beta) external requiresAuth {

843:     function setRedemptionsPaused(bool _paused) external requiresAuth {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CdpManager.sol)

```solidity
File: packages/contracts/contracts/CdpManagerStorage.sol

111:     function setGracePeriod(uint128 _gracePeriod) external requiresAuth {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CdpManagerStorage.sol)

```solidity
File: packages/contracts/contracts/CollSurplusPool.sol

142:     function sweepToken(address token, uint256 amount) public nonReentrant requiresAuth {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CollSurplusPool.sol)

```solidity
File: packages/contracts/contracts/Dependencies/Auth.sol

9: abstract contract Auth {

26:     modifier requiresAuth() virtual {

52:     function transferOwnership(address newOwner) public virtual requiresAuth {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/Auth.sol)

```solidity
File: packages/contracts/contracts/Dependencies/AuthNoOwner.sol

16:     modifier requiresAuth() virtual {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/AuthNoOwner.sol)

```solidity
File: packages/contracts/contracts/Dependencies/RolesAuthority.sol

5: import {Auth, Authority} from "./Auth.sol";

12: contract RolesAuthority is IRolesAuthority, Auth, Authority {

12: contract RolesAuthority is IRolesAuthority, Auth, Authority {

12: contract RolesAuthority is IRolesAuthority, Auth, Authority {

20:     constructor(address _owner, Authority _authority) Auth(_owner, _authority) {}

89:     ) public virtual requiresAuth {

111:     ) public virtual requiresAuth {

133:     function burnCapability(address target, bytes4 functionSig) public virtual requiresAuth {

147:     function setUserRole(address user, uint8 role, bool enabled) public virtual requiresAuth {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/RolesAuthority.sol)

```solidity
File: packages/contracts/contracts/EBTCToken.sol

86:         _requireCallerIsBOorCdpMOrAuth();

96:         _requireCallerIsBOorCdpMOrAuth();

105:         _requireCallerIsBOorCdpMOrAuth();

314:     function _requireCallerIsBOorCdpMOrAuth() internal view {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/EBTCToken.sol)

```solidity
File: packages/contracts/contracts/Governor.sol

13: contract Governor is RolesAuthority {

36:     constructor(address _owner) RolesAuthority(_owner, Authority(address(this))) {}

154:     function setRoleName(uint8 role, string memory roleName) external requiresAuth {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Governor.sol)

```solidity
File: packages/contracts/contracts/PriceFeed.sol

358:     function setFallbackCaller(address _fallbackCaller) external requiresAuth {

```

[Link to code](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/PriceFeed.sol)
