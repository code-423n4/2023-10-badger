# Badger eBTC Audit + Certora Formal Verification details

- Total Audit + Formal Verification Prize Pool: $149,725 USDC

- Total Audit Prize Pool: $119,725 USDC
  - HM awards: $100,000 USDC
  - QA awards:  $2,112.50 USDC  
  - Gas awards:  $2,112.50 USDC
  - Judge awards: $9,000 USDC
  - Lookout awards: $6,000 USDC
  - Scout awards: $500 USDC
- Total FV Prize Pool: $30,000 USDC
  - Real Bug Rules: $7,500 USDC
  - Mutation Rules $19,500 USDC
  - Participation: $3,000 USDC
- Join [C4 Discord](https://discord.gg/code4rena) to register
- Submit findings [using the C4 form](https://code4rena.com/contests/2023-10-badger-ebtc-audit-certora-formal-verification-competition/submit)
- [Read our guidelines for more details](https://docs.code4rena.com/roles/wardens)
- Starts October 24, 2023 20:00 UTC
- Ends November 14, 2023 20:00 UTC

## Automated Findings / Publicly Known Issues

The 4naly3er report can be found [here](https://gist.github.com/JustDravee/086169a02a71f82beaf8a0ef8eff91ad).

[Badger provided 4 previous audit reports and known issues](https://gist.github.com/GalloDaSballo/a0f9766bf7bac391f49d2d167e947de0)

Automated findings output for the audit can be found [here](https://github.com/code-423n4/2023-10-badger/blob/main/bot-report.md) and within 24 hours of audit opening.

_Note for C4 wardens: Anything included in the 4naly3er **or** the automated findings output is considered a publicly known issue and is ineligible for awards._

# Overview

eBTC is a collateralized crypto asset soft pegged to the price of Bitcoin and built on the Ethereum network. It is backed exclusively by Staked Ether (stETH) and powered by immutable smart contracts with minimized counterparty reliance. It’s designed to be the most decentralized synthetic BTC in DeFi and offers the ability for anyone in the world to borrow BTC at no cost.

- See [Primary Readme](https://github.com/code-423n4/2023-10-badger/blob/main/README_EBTC.md).
- See [Intro Video](https://www.youtube.com/watch?v=QWIB4avTkt4).
- See the [eBTC Cheatsheet](https://gist.github.com/GalloDaSballo/7b060bb97de09c539ec64c533dd352c6) for additional videos and an up to date list of additional resources.

## Links

[Primary Readme](https://github.com/code-423n4/2023-10-badger/blob/main/README_EBTC.md) contains further links.

- **Previous audits:**
All findings contained in theses reports:
  - RiskDAO: <https://github.com/Risk-DAO/Reports/blob/main/eBTC.pdf>
  - Trust: <https://badger.com/images/uploads/trust-ebtc-audit-report.pdf>
  - Spearbit: <https://badger.com/images/uploads/ebtc-security-review-spearbit.pdf>
  - Cantina: <https://badger.com/images/uploads/ebtc-security-review-cantina.pdf>
  - Many additional links (cheatsheet): <https://gist.github.com/GalloDaSballo/7b060bb97de09c539ec64c533dd352c6>
- **Documentation:**
[Primary Readme](https://github.com/code-423n4/2023-10-badger/blob/main/README_EBTC.md)
- **Website:**
[ebtc.finance](https://www.ebtc.finance/)
- **Twitter:**
[eBTCProtocol](https://twitter.com/eBTCprotocol)

# Scope

*See [scope.txt](https://github.com/code-423n4/2023-10-badger/blob/main/scope.txt)*

**Legend:**

💰 Can Receive Funds
🖥 Uses Assembly 
📤 Transfers ETH 
👥 DelegateCall
🧮 Uses Hash Functions
🔖 ECRecover
🌀 New/Create/Create2
♻️ TryCatch
Σ Unchecked

**Scope Table:**

|File|SLOC|Description|
:-|:-:|:-|
|_Core Protocol Contracts (10)_|
|[/packages/contracts/contracts/ActivePool.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/ActivePool.sol) 📤Σ|221|Manages system-level internal accounting and stETH tokens.|
|[/packages/contracts/contracts/BorrowerOperations.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/BorrowerOperations.sol) 🧮🔖|751|Entry point to Open, Adjust, and Close Cdps as well as delegate positionManagers.|
|[/packages/contracts/contracts/CdpManager.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CdpManager.sol)|578|Cdp operations and entry point for non-borrower operations on Cdps (Liquidations, Redemptions).|
|[/packages/contracts/contracts/LiquidationLibrary.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/AAALiquidationLibrary.sol)|700|Contains liquidation-related functions. Split off due to maximum contract size, delegateCalled by CdpManager.|
|[/packages/contracts/contracts/CdpManagerStorage.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CdpManagerStorage.sol)|550|Shared storage variables between CdpManager and Liquidation Library, and common functions.|
|[/packages/contracts/contracts/CollSurplusPool.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CollSurplusPool.sol) Σ|83|Isolated storage of excess collateral owed to users from liquidations or redemptions. Not considered part of system for accounting.|
|[/packages/contracts/contracts/EBTCToken.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/EBTCToken.sol) 🧮🔖Σ|223|ERC20 EbtcToken, with permit approvals and extensible minting.|
|[/packages/contracts/contracts/Governor.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Governor.sol)|107|Roles-based authorization contract, adapted and expanded from solmate Authority. Expanded with more convenience view functions and ability to permanently burn capabilities.|
|[/packages/contracts/contracts/PriceFeed.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/PriceFeed.sol) ♻️|491|PriceFeed with primary and secondary oracles and state machine to switch between them and handle failure cases.|
|[/packages/contracts/contracts/SortedCdps.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/AAASortedCdps.sol)  
Σ|399|Data storage for the doubly-linked list of Cdps. Sorting of Cdps is used to enforce redemptions from lowest ICR to highest ICR.|
|_Lens / Helper Contracts (2)_|
|[/packages/contracts/contracts/HintHelpers.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/HintHelpers.sol) 🧮Σ|142|Generate approximate locations for proper linked list insertion locations for Cdps.|
|[/packages/contracts/contracts/CRLens.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/CRLens.sol) 🖥♻️|98|Simulate state changes and view results, to compare to expected results in testing env.|
|_Leverage Macros & Smart Wallets (5)_|
|[/packages/contracts/contracts/LeverageMacroBase.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroBase.sol) 🖥📤🧮Σ|353|Common base implementation of the LeverageMacro.|
|[/packages/contracts/contracts/LeverageMacroDelegateTarget.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroDelegateTarget.sol) 🔆|30|LeverageMacro variant for use with delegateCall with compatible smart wallets.|
|[/packages/contracts/contracts/LeverageMacroFactory.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroFactory.sol)  
🌀|46|Factory for deploying LeverageMacroReference|
|[/packages/contracts/contracts/LeverageMacroReference.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/LeverageMacroReference.sol)|38|LeverageMacro variant for use as a zap with an individual owner.|
|[/packages/contracts/contracts/SimplifiedDiamondLike.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/SimplifiedDiamondLike.sol)  
🖥💰👥🧮Σ|109|Smart wallet with custom callback handler support.|
|_Modified Dependencies (7)_|
|[/packages/contracts/contracts/Dependencies/Auth.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/Auth.sol)|33|Inherited by contracts consuming authorization rules of Governor.|
|[/packages/contracts/contracts/Dependencies/AuthNoOwner.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/AuthNoOwner.sol)|36|Inherited by contracts consuming authorization rules of Governor. Removes owner address that has global 'admin' permission from Auth.|
|[/packages/contracts/contracts/Dependencies/ERC3156FlashLender.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/ERC3156FlashLender.sol) 🧮|10|Base for standardized flash loans|
|[/packages/contracts/contracts/Dependencies/EbtcBase.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/EbtcBase.sol)|78|Common definition and base functions for system contracts.|
|[/packages/contracts/contracts/Dependencies/EbtcMath.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/EbtcMath.sol)|62|More common math functions for system contracts.|
|[/packages/contracts/contracts/Dependencies/ReentrancyGuard.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/ReentrancyGuard.sol)|12|Simple, optimized reentrancy guard.|
|[/packages/contracts/contracts/Dependencies/RolesAuthority.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Dependencies/RolesAuthority.sol)|102|Role-based authorization from solmate. Expanded functionality for use with Governor.|
|_Core Interface (17)_|
|[/packages/contracts/contracts/Interfaces/IActivePool.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IActivePool.sol)|28|ActivePool interface|
|[/packages/contracts/contracts/Interfaces/IBorrowerOperations.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IBorrowerOperations.sol)|68|BorrowerOperations primary interface|
|[/packages/contracts/contracts/Interfaces/ICdpManager.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/ICdpManager.sol)|52|CdpManager primary interface|
|[/packages/contracts/contracts/Interfaces/ICdpManagerData.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/ICdpManagerData.sol)|213|CdpManagerStorage interface. Contains structs, events, and common functions between CdpManager and LiquidationLibrary|
|[/packages/contracts/contracts/Interfaces/ICollSurplusPool.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/ICollSurplusPool.sol)|11|CollSurplusPool interface|
|[/packages/contracts/contracts/Interfaces/IEbtcBase.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IEbtcBase.sol)|5|EbtcBase interface.|
|[/packages/contracts/contracts/Interfaces/IEBTCToken.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IEBTCToken.sol)|7|EBTCToken interface, expands IERC20 and IERC2612|
|[/packages/contracts/contracts/Interfaces/IERC3156FlashBorrower.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IERC3156FlashBorrower.sol) 🔆|10|ERC3156FlashBorrower interface for recipients of flashLoans|
|[/packages/contracts/contracts/Interfaces/IERC3156FlashLender.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IERC3156FlashLender.sol)|15|ERC3156FlashLender interface for flash lenders, BorrowerOperations and ActivePool|
|[/packages/contracts/contracts/Interfaces/IFallbackCaller.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IFallbackCaller.sol)|7|Standardized interface for fallback oracles|
|[/packages/contracts/contracts/Interfaces/IPermitNonce.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IPermitNonce.sol)|5|Interface for managing permit nonces|
|[/packages/contracts/contracts/Interfaces/IPool.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IPool.sol)|10|Common interface for Pool contracts. Only consumed by IActivePool due to pool consolidation|
|[/packages/contracts/contracts/Interfaces/IPositionManagers.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IPositionManagers.sol)|35|Interface for PositionManager functions. Consumed by BorrowerOperations|
|[/packages/contracts/contracts/Interfaces/IPriceFeed.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IPriceFeed.sol)|31|PriceFeed interface|
|[/packages/contracts/contracts/Interfaces/IRecoveryModeGracePeriod.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/IRecoveryModeGracePeriod.sol)|9|Interface for GracePeriod functions. Consumed by CdpManager|
|[/packages/contracts/contracts/Interfaces/ISortedCdps.sol](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/contracts/Interfaces/ISortedCdps.sol)|54|SortedCdps interface|

## Out of scope

All other contracts in the repo.

Especially:

- Test Files
- /Proxy
- /TestContracts

- Echidna and Foundry Files
- Tellor related Files, Tellor will not be used

# Additional Context

- Describe any novel or unique curve logic or mathematical models implemented in the contracts.
  - None.
- Please list specific ERC20 that your protocol is anticipated to interact with. Could be "any" (literally anything, fee on transfer tokens, ERC777 tokens and so forth) or a list of tokens you envision using on launch.
  - ONLY stETH, eBTC token
- Please list specific ERC721 that your protocol is anticipated to interact with.
  - none
- Which blockchains will this code be deployed to, and are considered in scope for this audit?
  - Ethereum mainnet
- Please list all trusted roles (e.g. operators, slashers, pausers, etc.), the privileges they hold, and any conditions under which privilege escalation is expected/allowable

All governable permissions can be assumed to be managed by a multisig + timelock configuration by default.
Some functions will be callable my a smaller threshold of users with no timelocks to prioritize speed.

### Governable Function

#### ActivePool

```
claimFeeRecipientCollShares
sweepToken
setFeeRecipientAddress
setFeeBps
setFlashLoansPaused
```

#### CollSurplusPool

```
sweepToken
```

#### BorrowerOperations

```
setFeeRecipientAddress
setFeeBps
setFlashLoansPaused
```

#### CdpManager

```
setGracePeriod
setStakingRewardSplit
setRedemptionFeeFloor
setMinuteDecayFactor
setBeta
setRedemptionsPaused
```

#### EBTCToken

```
mint
burn
(both variants of each)
```

#### PriceFeed

```
setFallbackCaller
```

The following functions can be assumed to be exemptions from a timelock due to impact on operational efficiency and ability to respond to emergency scenarios.
See Known Issues for our stance on governance parameters.

#### ActivePool

```
claimFeeRecipientCollShares
sweepToken
setFlashLoansPaused
```

#### CollSurplusPool

```
sweepToken
```

#### BorrowerOperations

```
setFlashLoansPaused
```

#### CdpManager

```
setRedemptionsPaused
```

#### DOS Minimum Duration

- [ ] In the event of a DOS, could you outline a minimum duration after which you would consider a finding to be valid? This question is asked in the context of most systems' capacity to handle DoS attacks gracefully for a certain period.

#### EIP Compliance

- `ActivePool`: Should comply with `EIP3156`
- `BorrowerOperations`: Should comply with `EIP3156`
- `EBTCToken`: Should comply with `ERC20, ERC2612`

## Attack ideas (Where to look for bugs)

See [Known Issues](./README_EBTC.md#known-issues) section and previous audit reports.

## Main invariants

- [PROPERTIES.md](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/specs/PROPERTIES.md) file contains the main invariants.
- Also see [Price Feed](https://github.com/code-423n4/2023-10-badger/blob/main/packages/contracts/specs/PriceFeed.tree) state machine for reference.

## Scoping Details

```
- If you have a public code repo, please share it here:  https://github.com/ebtc-protocol/ebtc
- How many contracts are in scope?:   41
- Total SLoC for these contracts?:  5805
- How many separate interfaces and struct definitions are there for the contracts within scope?:  17 Interfaces, 16 Structs
- Does most of your code generally use composition or inheritance?:   Inheritance
- How many external calls?: 6 seperate calls (to stETH token and Chainlink)
- What is the overall line coverage percentage provided by your tests?: 99%
- Is this an upgrade of an existing system?:  False
- Check all that apply (e.g. timelock, NFT, AMM, ERC20, rollups, etc.): ERC-20
- Is there a need to understand a separate part of the codebase / get context in order to audit this part of the protocol?:  False 
- Please describe required context:   n/a
- Does it use an oracle?:  Chainlink with potential to connect an arbitrary backup oracle.
- Describe any novel or unique curve logic or mathematical models your code uses:  No
- Is this either a fork of or an alternate implementation of another project?:  Liquity
- Does it use a side-chain?: No
- Describe any specific areas you would like addressed: Accounting / yield accrural math
```

# Tests

Fresh build / run / test

```
yarn
cd packages/contracts
forge build 
forge test
yarn test
```

Gas report

```
forge test --gas-report
```
