pragma solidity ^0.5.0;

import "./openzeppelin-solidity/contracts/token/ERC20/ERC20.sol";
import "./openzeppelin-solidity/contracts/token/ERC20/ERC20Detailed.sol";

contract SuperToken is ERC20, ERC20Detailed {

  constructor () 
    ERC20Detailed("SuperToken", "SUP", 18)
    public {
      _mint(msg.sender, 10000 * (10 ** uint256(decimals())));
  }

}
