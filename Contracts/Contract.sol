pragma solidity ^0.5.12;


//Ceth contract is an abstract contract that is needed to use compoundCommunication contract
contract CEth 
{
  function mint() external payable;
  function balanceOf(address owner) external view returns (uint256);
  function redeem(uint redeemTokens) external returns (uint);
  
}

//########################################################
//####   Compound communication Functions           ######
//########################################################
//This contract has all the compound communication functions
contract compoundCommunication
{
  //master will be able to call every functions
  //It is a kind of security but could be delete
  address payable internal master = address(0x2ae25A44DA2B14E12c4eD4C441E2B9189cE260dC);
  //  -- ! Address for ropsten ! --
  address payable public ethCompound = address(0x1d70B01A2C3e3B2e56FcdcEfe50d5c5d70109a5D);
    //Send all Eth own by the contract to Compound
  function sendToCompound() internal returns (bool check){
      CEth(ethCompound).mint.value(address(this).balance).gas(250000)();
      return true;
  }
  // Get Back all money from Compound: 
  function getBackFromCompound() internal returns (bool check){
      CEth(ethCompound).redeem.gas(250000)(getBalance_cToken());
      return true;
  }
  //See how much cEth we own 
  function getBalance_cToken() public view returns (uint){
      require(msg.sender==master,"Only for the master");
      return CEth(ethCompound).balanceOf(address(this));
      
  }
  //Able me to see how much eth the contract own
  function getBalance_Token()public view returns (uint){
      require(msg.sender==master,"Only for the master");
      return address(this).balance;
      
  }
}
//########################################################
//####   MAIN CONTRACT                              ######
//########################################################
//This is the main contract that will contain the main functions 
contract smartCaution is compoundCommunication
{
    //Set all the variables

    //This is the tenant address, He is supposed to create the contract
    address payable private tenantAddress;
    //This is the landlord adress, it is supposed to be initializate in the constructor by the tenant 
    address payable private landLordAddress;
    //Stock the value of the starting amount 
    uint private amountAtStart = 0;
    //That is the part that the landlord have to pay to be part of this contract
    uint private landLordPart = 1000;
    //Does the contract has been launch 
    bool private launched = false;
    bool private closed = false;
    //The hash of the document containing all the informations of the contract, ex: address, name, date, pictures...
    bytes32  private hashOfDocument;
    //Validation table
    mapping(address => bool) private validationOf;
    //Amount paid by each
    mapping(address => uint) private amountPaidBy;
    //Let set the main modifier :
    modifier onlyUsers () {
        //allow users 
        require(
            (msg.sender == landLordAddress ||msg.sender == tenantAddress || msg.sender == master ),
            "Only users can call this function"
        );
        _;
    }
    modifier onlyMaster (){
        //allow only the master 
        require (
            msg.sender == master,
            "You are not the moderator of this contract"
        );
        _;
    }
    modifier contractNotLaunched () {
        //require that the contract has been already launched
        require(
            (!launched || msg.sender == master),
            "This function will be available when the contract will be launch"
        );
        _;
    }
    modifier bothValidation () {
        //require that the both part have validate the contract or it's called by the master 
        require(
            (msg.sender == master ||(validationOf[tenantAddress]&&validationOf[landLordAddress])),
            "Both parts need to validate in order to apply this function"
        );
        _;
    }
    
    //The constructor of the function will initialize all we need
    constructor(address payable _landLordAddress , bytes32  _hashDoc) public payable{
        //We don't want to deploy empty contract
        require(msg.value>0);
        //We intialize the first values
        amountAtStart = msg.value;
        tenantAddress = msg.sender;
        //We initialize the paramters of the contract
        landLordAddress = _landLordAddress;
        hashOfDocument = _hashDoc;
        //We initialize the amount paid by the tenant
        //Not necessary but we want to ensure that it's initializate at 0
        amountPaidBy[tenantAddress]= msg.value;
        amountPaidBy[landLordAddress]=0;
        //Of course the tenant agree with what he just Set
        validationOf[tenantAddress]=true;
        
    }
    //fallback function
    function () external payable {

    }
    //This function will launch the contract if everything is ok
    function launchContract() public onlyUsers contractNotLaunched bothValidation returns(bool check){
        //First we check that every one paid his part
        require(amountPaidBy[landLordAddress]>=landLordPart,"The landlord didn't paid his part");
        //We send the money to Compound
        sendToCompound();
        //We unvalidate both part
        validationOf[landLordAddress] = false;
        validationOf[tenantAddress] = false;
        //The contract is now launched
        launched = true;
        return true;
    }
    //This function will close the contract if everybody is ok
    function closeContract() public onlyUsers bothValidation returns(bool check){
        //Doesn't have to be used after the contract has been closed
        require(!closed,"The contract is closed now !");
        //We check that the contract has been launched
        require(launched,"The contract hasn't been launched yet");
        //We get back the money from compound
        getBackFromCompound();
        //The contract is now closed 
        closed = true;
        return true;
    }
    //Return the money to the user
    function returnMoneyToUsers() public onlyUsers bothValidation returns(bool check){
        //We check that the contract has been closed
        require(closed,"The contract hasn't been closed yet");
        //We transfer the landlord the amount he has paid 
        landLordAddress.transfer(amountPaidBy[landLordAddress]);
        //We transfer the rest of the amount to the tenant 
        tenantAddress.transfer(address(this).balance);
        return true;
    }
    //This function allow each user to validate the contract and change the hash if they don't agree
    function userValidateBegin(bytes32 hash) public payable onlyUsers contractNotLaunched returns (bool change){
        //we increment the register of people who have paid something
        amountPaidBy[msg.sender] += msg.value; 
        if(hash == hashOfDocument)
        {
            //if both agreed the user validate
            validationOf[msg.sender] = true;
            return false;
        }
        else
        {
            //if one doesn't agree, we change the state of the other 
            if(msg.sender == tenantAddress)
            {
                validationOf[tenantAddress] = true;
                validationOf[landLordAddress] = false;
                hashOfDocument = hash;
            }
            if(msg.sender == landLordAddress)
            {
                validationOf[landLordAddress] = true;
                validationOf[tenantAddress] = false;
                hashOfDocument = hash;
            }
            return true;
        }
    }
    //This function allow users to validate the end of the contract
    function userValidateEnd() public onlyUsers  returns (bool change){
        //Doesn't have to be used after the contract has been closed
        require(!closed,"The contract is closed now !");
        //We check that the contract has been launched
        require(launched,"The contract hasn't been launched yet");
        validationOf[msg.sender] = true;
        return true;
    }
    //This function allow the tenant to cancel the contract if no agreement has been found
    function contractDestruction() public returns(bool check){
        //Only the tenant can call the function
        require(msg.sender==tenantAddress|| msg.sender == master);
        //The contract can't be launch or closed
        require(!launched && !closed);
        //We transfer the landlord the amount he has paid first
        landLordAddress.transfer(amountPaidBy[landLordAddress]);
        //We transfer the rest of the amount to the tenant 
        tenantAddress.transfer(address(this).balance);
        //We block the contract
        launched = true;
        closed = true;
        return true;
    }
    
    //Send Back money to master
    function giveBackToMaster() public onlyMaster returns (bool check){master.transfer(address(this).balance);return true;}
    //View the hash
    function viewHashOfDocument()public view onlyUsers returns(bytes32 hash){return hashOfDocument;}
    //View the state of the contract
    function viewState()public view onlyUsers returns(bool state){return launched;}
    //view the amount of the caution 
    function viewAmount()public view onlyUsers returns(uint amount){return amountAtStart;}
    //view the validation of somebody
    function validationof(address toLookAt)public view onlyUsers returns(bool validate){return validationOf[toLookAt];}
}

//Created by Tfrx1er & rletilly
//Special Thanks to 5fiftyseven7 on the Compound discord that helped me