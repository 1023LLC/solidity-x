from solcx import compile_standard
import json
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()


with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    # print(simple_storage_file)
    

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)
    
# Get Bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

# Get ABI
abi =  compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# For connecting to ganache
w3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/c2d79fce338845f1993a5f41fd151587"))
chain_id = 11155111
my_address = "0x23322c357e08396a77BC00739230413472D94dAB"
private_key = os.getenv("PRIVATE_KEY")
# print(private_key)

# Create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# print(SimpleStorage)

# Get the latest transaction
nonce = w3.eth.get_transaction_count(my_address)
# print(nonce)

# 1. Build a transaction
# 2. Sign a transaction
# 3. Send a transaction
transaction = SimpleStorage.constructor().build_transaction({
    "chainId":chain_id, "from":my_address, "nonce":nonce
})
# print(transaction)

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# print(signed_txn)

# Send this signed transaction
print("Deploying contract..")
tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")


# Working with the contract, you'll always need
# Contract Address
# Contract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# This is our initial value of stored number
print(simple_storage.functions.retrieve().call())
# print(simple_storage.functions.store(1023).call())
# print(simple_storage.functions.retrieve().call())

print("Updating contract..")
store_transaction = simple_storage.functions.store(23).build_transaction({
    "chainId":chain_id, "from": my_address, "nonce": nonce + 1
})

signed_store_txn = w3.eth.account.sign_transaction( store_transaction, private_key=private_key)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.raw_transaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Updated!")
print(simple_storage.functions.retrieve().call())