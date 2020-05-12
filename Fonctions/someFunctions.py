import json
from web3 import Web3
import hashlib
from fpdf import FPDF

#To import adress and keys:
def import_log():

    with open('log_id.json') as json_data:
        data_dict = json.load(json_data)
        return data_dict

#Take the adress of the previous smart contract
def import_sm_adress():
    with open('smartContractAdress.txt','r') as data:
        data = data.read()
        return data

#Return the hash of a pdf
def getHashOf(path) : 
    with open(path, 'rb') as f:
        h1 = hashlib.sha256(f.read()).digest()
    return h1.hex()

#Fait un pdf à partir d'une liste d'element et d'image
def makePDF(listOfElement,listOfPictures,numero):
    #Intialization of the PDF file
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=20)
    #Write the title
    pdf.cell(200, 10, txt="Contract n°"+str(numero), ln=1, align="C")
    pdf.set_font("Arial", size=12)
    #We write all the informations
    for i in range(0, len(listOfElement)):
        pdf.cell(0, 10, listOfElement[i], 0, 1)
    #We write all the pictures
    pdf.add_page()
    for i in range(0, len(listOfPictures)):
        pdf.image(listOfPictures[i], x=10, y=8+200*i, w=100)

    #Let's create the pdf file
    pdf.output("contract"+str(numero)+".pdf","F")