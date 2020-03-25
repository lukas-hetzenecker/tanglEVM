pragma solidity ^0.5.0;

contract Hash {

    function myhash(bytes memory data) public pure returns (bytes32, bytes32)  {
        bytes32 a = keccak256(data);
        bytes32 b = "";
        
        return (a, b);
    }
}

