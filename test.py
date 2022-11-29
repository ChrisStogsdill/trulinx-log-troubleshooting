
import pyodbc 
import pdb
import datetime
import random
import json
import os
import csv
import re
import sys

def getRecordsDict(rows, columns):
    records = []
    for row in rows:
        records.append(dict(zip(columns, row)))
    return(records)
    #print(records)

def getVendors(records):
    vendors = []
    for i in records:
        vendors.append(i["vend-Vendor"])
   
    vendors = list(set(vendors))
    vendors.sort()
    #print(vendors+"/n--EXIT FUNCTION/n")
    return vendors

def getVendorRecordNo(vendors_input, records_input):
    vendorRows = {}
    for vendor in vendors_input:
        vendorsRowNo = []
        ix = 0
        for record in records_input:
            if record["vend-Vendor"] == vendor:
                vendorsRowNo.append(ix)
                vendorRows[vendor] = vendorsRowNo
            ix += 1 
    return vendorRows

def getCheckNobyVendor(vendors_input, vendorsRecord_input, records_input):
    #import pdb; pdb.set_trace()
    checkNoDict = {}
    for vendor in vendors_input:
        #print("On Vendor:" + vendor) #For DEBUG/DEV
        checksNoList = []
        for x in vendorsRecord_input[vendor]:
            #print("Maybe Line No:" + str(x))
            checksNoList.append (records_input[x]["vp-CheckNumber"])
        checkNoList2 = list(set(checksNoList))
        checkNoDict[vendor] = checkNoList2
        #print("CheckNoDict: /n")
        #print(checkNoDict)
    return checkNoDict

def getDistributionRecords(vendors_input, vendorsRecord_input, records_input, batchno, accountsList, classList, config_dict):
    #import pdb; pdb.set_trace()
    #checkNoDict_input = {}
    errored_spm = ["Bad Check List"]
    checkNoDict_input = getCheckNobyVendor(vendors_input, vendorsRecord_input, records_input)
    full_iff_file = ""
    bad_trns_file = ""
    final_void_print = ""
    full_iff_file += ("""!TRNS\tTRNSID\tTRNSTYPE\tDATE\tACCNT\tNAME\tCLASS\tAMOUNT\tDOCNUM\tCLEAR\tTOPRINT\tADDR1\n!SPL\tSPLID\tTRNSTYPE\tDATE\tACCNT\tNAME\tCLASS\tAMOUNT\tDOCNUM\n!ENDTRNS\n""")
    for vendor in vendors_input:
        #print("vendor "+str(vendor))
        trnsid = 1
        recordno = vendorsRecord_input[vendor][0]
        #print("recordno", recordno)
        row = records_input[recordno]
        #print("row", row)
        #print("")
        tx_line_check_amount = row["cr-Amount"]
        spm_line_check_amount = []
        final_tx_print = ""
        final_void_print = ""
        transaction_line= "TRNS\t{txID}\tCHECK\t{date}\t{account}\t{payee}\t{check_class}\t{check_amnt:.2f}\t{checkno}\tY\tN\t{vendor_address}\n"
        if check_IfVoid(row) == False:
            vendor_address_config = (str(row["vend-AddressLine1"]))+" "+(str(row["vend-AddressLine2"]))
            print((transaction_line.format(txID=str(random.randint(100000,999999)), \
                date=str((row["cr-CheckDate"]).strftime("%-m/%-d/%Y" )), \
                account=str(searchShortCodes(accountsList, "1001")).strip(), \
                payee=str(row["cr-Payee"]), \
                check_class="", \
                check_amnt=row["cr-Amount"], \
                checkno= str(row["cr-CheckNumber"]), \
                vendor_address=str(row["vend-AddressLine1"])+" "+str(row["vend-AddressLine2"]\
                    )))) # For Debug
            final_tx_print += (transaction_line.format(txID=str(random.randint(100000,999999)), \
                date=str((row["cr-CheckDate"]).strftime("%-m/%-d/%Y" )), \
                account=(str(1001).strip()), \
                payee=str(row["cr-Payee"]), \
                check_class="", \
                check_amnt=row["cr-Amount"], \
                checkno= int(row["cr-CheckNumber"]), \
                vendor_address= vendor_address_config[:40]
                ))
            for row2 in vendorsRecord_input[vendor]:
                trnsid = random.randint(100000,999999) 
                #spl_class_breakdown = 
                spm_line = "SPL\t{SPLID}\t{SPL_TRNSTYPE}\t{SPL_DATE}\t{SPL_ACCNT}\t{SPL_NAME}\t{SPL_CLASS}\t{SPL_AMOUNT:.2f}\t{SPL_DOCNUM}\n"
                spm_line_check_amount.append(records_input[row2]["th-TxAmount"])
                if str(records_input[row2]["cr-CheckNumber"]) == str(row["cr-CheckNumber"]):
                    """print(spm_line.format(
                        SPLID = str(trnsid), \
                        SPL_TRNSTYPE = "CHECK", \
                        SPL_DATE = ((records_input[row2]["cr-CheckDate"]).strftime("%-m/%-d/%Y" )), \
                        SPL_ACCNT =  str(records_input[row2]["th-QBClass"]), \
                        SPL_NAME = "",\
                        SPL_CLASS =  str(searchShortCodes(classList,str(classSplit(".", records_input[row2]["th-QBClass"])))).strip(), \
                        SPL_AMOUNT = records_input[row2]["th-TxAmount"], \
                        SPL_DOCNUM = str(records_input[row2]["th-VoucherNumber"])
                        #SPL_REIMBEXP = "NONEED"
                        ))"""

                    #write Error/Exceptions for .strip() functions. 

                    class_output = ""
                    #If Class is empty then fall back on original output class
                    if (records_input[row2]["th-QBClass"] == None) or (records_input[row2]["th-QBClass"] == ""):
                        account_output = records_input[row2]["th-Class"]
                        account_output = classCheckandCorrect(account_output, str(records_input[row2]["th-Location"]), config_dict)
                    else:
                        account_output = records_input[row2]["th-QBClass"] 
                        account_output = classCheckandCorrect(account_output, str(records_input[row2]["th-Location"]), config_dict)

                    final_tx_print += (spm_line.format(
                        SPLID = str(trnsid), \
                        SPL_TRNSTYPE = "CHECK", \
                        SPL_DATE = ((records_input[row2]["cr-CheckDate"]).strftime("%-m/%-d/%Y" )), \
                        SPL_ACCNT =  str(searchShortCodes(accountsList, str(account_output))).strip(), \
                        SPL_NAME = "",\
                        SPL_CLASS =  str(searchShortCodes(classList,str(classSplit(".", account_output)))).strip(), \
                        SPL_AMOUNT = records_input[row2]["th-TxAmount"], \
                        SPL_DOCNUM = str(records_input[row2]["th-VoucherNumber"])
                        #SPL_REIMBEXP = "NONEED"
                        ))
                    #print(str(classSplit(".", class_output)))
                else:
                    errored_spm.append(str(records_input[row2]["th-VoucherNumber"])
                        )
            final_tx_print += "ENDTRNS\n"
            if checkCheckSum(tx_line_check_amount, spm_line_check_amount) == True:
                full_iff_file += final_tx_print
            else:
                bad_trns_file += row["cr-CheckNumber"] +"\n"
                print(str(row["cr-CheckNumber"]), "did not match see bad iff file for more info")
        
        else:
            bad_trns_file += "Voided Checks:\n" +\
                            "!TRNS\tTRNSID\tTRNSTYPE\tDATE\tACCNT\tNAME\tCLASS\tAMOUNT\tDOCNUM\tCLEAR\tADDR1\tADDR2\n"
            bad_trns_file += (transaction_line.format(txID=str(random.randint(100000,999999)), \
                date=str((row["cr-CheckDate"]).strftime("%-m/%-d/%Y" )), \
                account=str(searchShortCodes(accountsList, "1001")).strip(), \
                payee=str(row["cr-Payee"]), \
                check_class="", \
                check_amnt=row["cr-Amount"], \
                checkno= str(row["cr-CheckNumber"]), \
                vendor_address=str(row["vend-AddressLine1"])+" "+str(row["vend-AddressLine2"]\
                    )))
            print(bad_trns_file)
    print("end of vendors")
    if bad_trns_file != "":
        writeToFile(bad_trns_file, config_dict['PATHS']['finalPath']+"voidChecks_"+batchno+".csv")    
    return full_iff_file, bad_trns_file

def classSplit(delimiter, string):
    x = string.split(delimiter)
    print("x is", x)
    if len(x) >= 2:
        if x[0] == "6681" and x[1] != 99:
            return str(int(x[1])-10).zfill(2)
        if x[0] == "6681" and x[1] == 99:
            return str("95")
        else:
            return x[1]
    else:
        print("Failed Class Number is:", string)
        print("Split Failed")
        return string

def checkCheckSum(checksum, distline_list):
    if checksum == sum(distline_list):
        return True
        print("diff: ", checksum , "-", sum(distline_list),"=", str(checksum - sum(distline_list)))
        print("True", "Vouchers does match the Check!")
    else:
        print("diff: ", checksum , "-", sum(distline_list),"=", str(checksum - sum(distline_list)))
        print("False", "Vouchers does not match the Check! The Check May be Void?")
        #full_iff_file += ("False"+ " Vouchers does not match the Check! The Check May be Void?")
        return False

def writeToFile(string, filename):
    file1 = open(filename,"w")#write mode
    file1.write(string)
    file1.close()

def check_IfVoid(row):
    if row["cr-Void"] == 1:
        return True
    else:
        return False

def csvToListofDict(filepath):
    table = []
    with open(filepath, 'r') as f:
        csv_reader = csv.DictReader(f, delimiter='\t')
        next(csv_reader)
        for line in csv_reader:
            table.append(dict(line))
    return table

def getConfig(filePath):
    #PASSED, MC, 2JUN2021
    with open(filePath, "r") as read_file:
        data = json.load(read_file)
        config = data
    return config

def searchShortCodes(listofDict, shortcode):
    shortcode_small = ""
    acctname = ""
   # print("shortcode is", shortcode)
    if "." in shortcode:
        codesplit = shortcode.split(".")
        shortcode_small = codesplit[0]
    for line in listofDict:
        if line['shortCode'].strip() == shortcode.strip():
            acctname = line['name']
            break
        if (shortcode_small != "") and (line['shortCode'].strip() == shortcode_small):
                acctname = line['name']
    return acctname

def classCheckandCorrect(class_input, location, config):
    x = ""
    if location != None:
     location = location.strip()
     #import pdb; pdb.set_trace()
    else:
        #print("location is empty, for some reason")
        return class_input

    if "." in class_input:
        #print("classC&C:", "Starting if period IS found")
        x = class_input.split(".")
        if len(x) >= 2:
            x = x[0]

    else:
       # print("classC&C:", "Starting if period IS NOT found")

        x = class_input
        #print("classC&C:", "x is", str(x), type(x))

    #print("what is config output",type(config['CUSTOM']['CLASS CHANGE']['Accounts']))
    if x in config['CUSTOM']['CLASS CHANGE']['Accounts']: 
        #print("classC&C:", "X is in config")
        for i in config['CUSTOM']['CLASS CHANGE']['Accounts']:
            if x == i:
                return str(x +"."+config['CUSTOM']['CLASS CHANGE'][i][location])
    else:
        #print("classC&C:", "X is NOT in config")
        return class_input

"""
def searchShortCodes(listofDict, shortcode):
    shortcode_small = ""
    acctname = ""
    if "." in shortcode:
        codesplit = shortcode.split(".")
        shortcode_small = codesplit[0]
    for line in listofDict:
        if line['shortCode'].strip() == shortcode.strip():
            acctname = line['name']
            if acctname == None or acctname == "":
                if (shortcode_small != "") and (line['shortCode'].strip() == shortcode_small):
                    acctname = line['name']
    return acctname
"""
                

def main(x):
    x = x.strip()
    config = getConfig('/datadrive_01/SQLtoIIF/src/config.json')
    batchno = x
    server = config['DBCONNECTIONS']['server']
    database = config['DBCONNECTIONS']['database'] 
    username = config['DBCONNECTIONS']['username']
    password = config['DBCONNECTIONS']['password'] 

    #Load QB Accounts and Classes
    accountsList = csvToListofDict(config['PATHS']['QB Accounts File'])
    classList = csvToListofDict(config['PATHS']['QB Class File'])

    
    inputcheck = re.match(r"^\d{4,8}$", x)
    if (bool(inputcheck) == True):
        cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
        cursor = cnxn.cursor()
        rows = cursor.execute("exec MWH_QB_spGetChecksFromRegisterNumber " + batchno).fetchall()
        columns = [column[0] for column in cursor.description]
        records = getRecordsDict(rows, columns)
        #print(records)
        vendors = getVendors(records)
        print("This is Vendors",vendors)
        vendorRecords = getVendorRecordNo(vendors, records)
        #print(vendorRecords)
        getCheckNobyVendor(vendors, vendorRecords, records)
        final_iif_file, final_void_print = getDistributionRecords(vendors, vendorRecords, records, batchno, accountsList, classList, config)
        writeToFile(final_iif_file, config['PATHS']['finalPath']+"iif_import_"+batchno+"_"+str(random.randint(100000,999999))+".iif")  
    else:
        print("Input may be wrong, please make sure it has between 4 and 8 digits and the batch no exists.")

if __name__ == "__main__":
    main(sys.argv[1])