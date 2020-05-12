import json , os , hashlib
from Fonctions.someFunctions import *
from web3 import Web3
os.system("clear")

#Connection to infura Provider:
my_provider = Web3.HTTPProvider('https://ropsten.infura.io/v3/3767a0f190b84ac38727a50508c19f4b')
w3 = Web3(my_provider)

#We set the contract parameters :
SmartCautionAbi = json.loads('[{"constant": false,"inputs": [],"name": "getBackFromCompound","outputs": [{"internalType": "bool","name": "check","type": "bool"}],"payable": false,"stateMutability": "nonpayable","type": "function"},{"constant": false,"inputs": [],"name": "giveBackToYou","outputs": [{"internalType": "bool","name": "check","type": "bool"}],"payable": false,"stateMutability": "nonpayable","type": "function"},{"constant": false,"inputs": [],"name": "sendToCompound","outputs": [{"internalType": "bool","name": "check","type": "bool"}],"payable": false,"stateMutability": "nonpayable","type": "function"},{"inputs": [],"payable": true,"stateMutability": "payable","type": "constructor"},{"payable": true,"stateMutability": "payable","type": "fallback"},{"constant": true,"inputs": [],"name": "ethCompound","outputs": [{"internalType": "address payable","name": "","type": "address"}],"payable": false,"stateMutability": "view","type": "function"},{"constant": true,"inputs": [],"name": "getBalance_cToken","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"payable": false,"stateMutability": "view","type": "function"},{"constant": true,"inputs": [],"name": "getBalance_Token","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"payable": false,"stateMutability": "view","type": "function"}]')
SmartCautionBin = '6080604052731d70b01a2c3e3b2e56fcdcefe50d5c5d70109a5d6000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055506104be806100676000396000f3fe6080604052600436106100555760003560e01c8063076ff0f6146100575780631227c5ea146100865780631d10b0ab146100b55780632e531beb146100e0578063a58e08be14610137578063de59bac414610166575b005b34801561006357600080fd5b5061006c610191565b604051808215151515815260200191505060405180910390f35b34801561009257600080fd5b5061009b610256565b604051808215151515815260200191505060405180910390f35b3480156100c157600080fd5b506100ca6102bd565b6040518082815260200191505060405180910390f35b3480156100ec57600080fd5b506100f561039d565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b34801561014357600080fd5b5061014c6103c2565b604051808215151515815260200191505060405180910390f35b34801561017257600080fd5b5061017b61046a565b6040518082815260200191505060405180910390f35b60008060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1663db006a756203d0906101dc6102bd565b6040518363ffffffff1660e01b815260040180828152602001915050602060405180830381600088803b15801561021257600080fd5b5087f1158015610226573d6000803e3d6000fd5b50505050506040513d602081101561023d57600080fd5b8101908080519060200190929190505050506001905090565b60003373ffffffffffffffffffffffffffffffffffffffff166108fc3073ffffffffffffffffffffffffffffffffffffffff16319081150290604051600060405180830381858888f193505050501580156102b5573d6000803e3d6000fd5b506001905090565b60008060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff166370a08231306040518263ffffffff1660e01b8152600401808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060206040518083038186803b15801561035d57600080fd5b505afa158015610371573d6000803e3d6000fd5b505050506040513d602081101561038757600080fd5b8101908080519060200190929190505050905090565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b60008060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16631249c58b3073ffffffffffffffffffffffffffffffffffffffff16316203d090906040518363ffffffff1660e01b81526004016000604051808303818589803b15801561044957600080fd5b5088f115801561045d573d6000803e3d6000fd5b5050505050506001905090565b60003073ffffffffffffffffffffffffffffffffffffffff163190509056fea265627a7a72315820e7fda0f2a6baafc40288ece227c25789d114a1f18a14de97276e61ad0cdfe06264736f6c634300050c0032'
SmartCautionAdress = ''
try : 
    SmartCautionAdress = import_sm_adress()
except:
    #Empty file
    print("There is not smart contract created yet ! ")

SmartCaution = w3.eth.contract(address = SmartCautionAdress , abi = SmartCautionAbi)

#We define the customer account:
user = import_log()['adresseLocataire']
user_private = import_log()['privateKeyLocataire']
w3.eth.defaultAccount = user

#Check if we are connected to the server
assert (w3.isConnected())

#Let set the sign transaction function : 
def sign_transaction(txn,value):
    #Flesh out the transaction for local signing
    next_nonce = w3.eth.getTransactionCount(str(w3.eth.defaultAccount))
    signable_transaction = dict(
        txn,
        value = value,
        nonce = next_nonce,
        gasPrice = w3.toWei(4,'gwei'),
    )
    #Sign Transaction
    private_key = user_private
    signature_info = w3.eth.account.signTransaction(signable_transaction,private_key)
    #Broadcast transaction
    txn_hash = w3.eth.sendRawTransaction(signature_info.rawTransaction)
    #Wait to be mined
    receipt = w3.eth.waitForTransactionReceipt(txn_hash)

    return receipt
#This function deploy a new smart contract
def deploy_new_smartCaution(value):
    # That is an exemple of use : 
    # deploy_new_smartCaution(100000000000000000)
    # don't forget that the adress is write in a file 
    SmartCaution_to_deploy = w3.eth.contract(abi = SmartCautionAbi,bytecode = SmartCautionBin)
    init = SmartCaution_to_deploy.constructor() 
    txn = init.buildTransaction({'gas':1000000})
    receipt = sign_transaction(txn,value)#100000000000000000 = 0.01 eth
    if (receipt !=0):
        with open('smartContractAdress.txt','w') as data:
            data.write(receipt.contractAddress)
    else :
        return False
    print(receipt.contractAddress)

#
#print(contract.functions.getBalance_Token().call())
#txn = contract.functions.getBackFromCompound().buildTransaction({'gas':1000000})
#receipt  = sign_transaction(txn)
#print(receipt.status)


print(SmartCaution.functions.getBalance_Token().call())


