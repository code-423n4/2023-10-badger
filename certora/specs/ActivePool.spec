import "./sanity.spec";
import "./erc20.spec";


methods {
    function _.increaseTotalSurplusCollShares(uint256) external => DISPATCHER(true);
    function _.onFlashLoan(address, address, uint256, uint256, bytes) external => DISPATCHER(true);
}


use rule sanity;


