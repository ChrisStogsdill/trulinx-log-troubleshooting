import invoiced
from invoiced import Invoice, Customer, CreditBalanceAdjustment, CreditNote
from pandas import Series
import requests
import hashlib
import json
import base64

def generate_idempotency_key(data):
    # Convert the data to a JSON string
    json_data = json.dumps(data, sort_keys=True)
    
    # Create a SHA-256 hash of the JSON string
    hash_object = hashlib.sha256(json_data.encode('utf-8'))
    
    # Get the hex digest of the hash
    hash_hex = hash_object.hexdigest()
    
    # Use the first 64 characters of the hash as the idempotency key
    idempotency_key = hash_hex[:64]
    
    return idempotency_key

def prepare_items(obj:dict) -> dict:

    key_mapping = {"Description": "description", 
            "Item": "name", 
            "UnitPrice": "unit_cost"}
     
    renamed_dict = {}
    meta_dict = {}
    for k, v in obj.items():
        if key_mapping.get(k, 0) and v:
            renamed_dict[key_mapping[k]] = v
        elif v:
            meta_dict[k] = v

    if meta_dict: renamed_dict["metadata"] = meta_dict
    return renamed_dict

def trim_dict(input_dict):
    max_length = 255
    current_dict = {}
    current_length = 0
    
    for key, value in input_dict.items():
        key_length = len(key)
        value_length = len(str(value))
        pair_length = key_length + value_length
        
        # Check if adding this pair would exceed the current dictionary's limit
        if current_length + pair_length > max_length:
            return current_dict
      
        current_dict[key] = value
        current_length += pair_length + 4

class InvoicedHandler:
    '''Supports operations to InvoicedAPI client and REST requests to Invoiced API Enpoints
    '''
    _api_key = "9IZVK0FVtiMw47if7v6qMpP0Zh9wJjm3" # Invoiced.JS publishable key: "fe027c1a460aa20ed9394d9a3c268fd2"
    _base_url_dev = 'https://app.sandbox.invoiced.com/'
    _base_url_prod = 'https://api.invoiced.com/'
    _handler = None
    _base_url = None

    def __init__(self):
        if self._handler is None:
            self._handler = invoiced.Client(self._api_key, True)
        self.base_url = self._base_url_dev

    def get_customer_id(self, customer_name:str) -> int:
        customers, _ = self._handler.Customer.list(per_page=10, filter={"name":customer_name})
        if not len(customers): return    
        customer = customers[0]
        return customer.id
   
    def get_customer_by_name(self, customer_name:str) -> Customer:
        customers, _ = self._handler.Customer.list(per_page=10, filter={"name":customer_name})
        if not len(customers): return    
        customer = customers[0]
        return customer
    
    def get_customer_by_id(self, customer_id:str) -> Customer:
        return self._handler.Customer.retrieve(customer_id)

    def get_invoice_by_id(self, invoice_id) -> Invoice:
        return self._handler.Invoice.retrieve(invoice_id)
    
    def get_invoice_id(self, invoice_number:str) -> int:
        invoices, _ = self._handler.Invoice.list(per_page=10, filter={"number":invoice_number})
        if not len(invoices): return -1
        invoice = invoices[0]
        return invoice.id

    def create_customer(self, serie:Series) -> Customer:
        serie.drop(["Name", "ShortName"], inplace=True) 
        serie.rename({"Customer":"given_name", "Email":"email", "AttentionTo":"attention_to", "Phone":"phone", "AddressLine1":"address1", "AddressLine2":"address2", "City":"city", 
                            "StateOrProvince":"state", "PostalCode":"postal_code"}, inplace=True)
        serie.dropna(inplace=True)
        serie["object"] = "Customer"
        customer = serie.to_dict()
        cust = self._handler.Customer.create(
                name=str(customer.get("name", None)),
                email=customer.get("email", None),
                number=customer.get("number", None),
                address1=customer.get("address1", None),
                address2=customer.get("address2", None),
                attention_to=customer.get("attention_to", None),
                city=customer.get("city", None),
                notes=customer.get("notes", None),
                # object=customer.get("object",  None),
                phone=customer.get("phone", None),
                postal_code=customer.get("postal_code", None),
                state=customer.get("state", None))
        return cust

    def update_customer(self, serie:Series, cust_id:str) -> bool:
        cust = self.get_customer_by_id(customer_id=cust_id)
        serie.dropna(inplace=True)
        cust.name = serie["Customer"]
        cust.email = serie["Email"]
        cust.attention_to = serie["AttentionTo"]
        cust.phone = serie["Phone"]
        cust.address1 = serie["AddressLine1"]
        if "AddressLine2" in serie.index :
            cust.address2 =serie["AddressLine2"]
        cust.city = serie["City"]
        cust.state = serie["StateOrProvince"]
        cust.postal_code = serie["PostalCode"]
        cust.notes = serie["notes"]
        
        response = cust.save()
        return response

    def delete_customer(self, name:str):
        customers, _ = self._handler.Customer.list(per_page=10, filter={"name":name})
        if not len(customers):
            return
        
        customer = customers[0]
        return customer.delete()

    def create_credit(self, amount:float, customer_id:int, credit_note_id:int) -> CreditBalanceAdjustment:
        transaction = self._handler.CreditBalanceAdjustment.create(amount=amount, customer=customer_id)
        return transaction
    
    def create_invoice(self, invoice_obj:dict) -> Invoice:
        meta = {}
        if invoice_obj.get("metadata", None): meta = trim_dict(input_dict=invoice_obj["metadata"])
        if invoice_obj.get("items", None): invoice_obj["items"] = [prepare_items(obj=item) for item in invoice_obj["items"]]

        inv = self._handler.Invoice.create(customer=invoice_obj.get("customer", 0),
                                           autopay=invoice_obj.get("autopay", False),
                                           date =invoice_obj.get("date", None),
                                           due_date=invoice_obj.get("due_date", None),
                                           items=invoice_obj.get("items", None),
                                           metadata=meta,
                                           notes=invoice_obj.get("notes", None),
                                           number=invoice_obj.get("number", None),
                                           payment_terms=invoice_obj.get("payment_terms", None),
                                           ship_to=invoice_obj["ship_to"])
        return inv

    def create_credit_note(self, credit_note) -> CreditNote:
        meta = {}
        if credit_note.get("metadata", None): meta = trim_dict(input_dict=credit_note["metadata"])
        if credit_note.get("items", None): credit_note["items"] = [prepare_items(obj=item) for item in credit_note["items"]]
        cust = self.get_customer_by_id(customer_id=credit_note.get("customer"))
        cnote = self._handler.CreditNote.create(
            customer = cust,
            name = credit_note.get("name", None), 
            date = credit_note.get("date", None),
            items = credit_note.get("items", None),
            notes = credit_note.get("notes", None),
            taxes = credit_note.get("taxes", []),
            metadata = meta
        )
        return cnote
    
    def list_credit_notes(self) -> tuple:
        credit_notes, metadata = self._handler.CreditNote.list(per_page=3)
        return credit_notes, metadata
    
    def create_transaction(self, invoice_id:int, transaction_type:str, amount:float, customer_id:int, notes:str):
        url = self.base_url + 'transactions'
        print(f"url: {url}")
        print(f"api key: {self._api_key}")
        # auth_header = {'Authorization': 'Basic ' + self._api_key,
        #                'Content-Type': 'application/json'}
        username = 'itambura@midwesthose.com'
        password = 
        # session = requests.Session()
        # session.auth = (username, password)
        # session.headers['X-API-Key'] = self._api_key
        # print("authorized")
        auth_header = {
            'Authorization': 'Basic ' + self._api_key,
            'Content-Type': 'application/json'
        }
        data = {"invoice": invoice_id,
                "type": transaction_type,
                "amount": amount,
                "customer": customer_id,
                "notes": notes}
        print(f"data: {data}")
        try:
            # response = requests.post(url=url, auth=(username, password), data=data)
            response = requests.post(url, headers=auth_header, json=data)
            
            if response.status_code == 200:
                print("POST request successful")
                return response.json()  
            else:
                print("POST request failed with status code:", response.status_code)
                return response.content
        except Exception as e:
            print("An error occurred:", e)
            return None

    def create_credit_transaction(self, amount:float, customer_id:int, credit_note_id:int):
        url = self.base_url + 'transactions'
        auth_header = {'Authorization': 'Basic ' + self._api_key}
        data = { "amount": amount,
                "type": "adjustment",
                "method": "balance",
                "customer": customer_id
                }
        if credit_note_id > -1:
            data["credit_note"] = credit_note_id

        try:
            response = requests.post(url, headers=auth_header, json=data)
            
            if response.status_code == 200:
                print("POST request successful")
                return response.json()  
            else:
                print("POST request failed with status code:", response.status_code)
                return None
        except Exception as e:
            print("An error occurred:", e)
            return None
    
'''


    def create_credit_balance_adjustment(self, customer_id:int, amount:int) -> str:

        response = self._handler.CreditBalanceAdjustment.create(customer = customer_id, amount=amount, currency = 'USD')
        return response
    
    def create_credit_invoice(self, credit_note:dict): # type: ignore
        # Creates a credit note on Invoiced API

        response = self._handler.CreditNote.create(credit_note)

        return response

    
    def create_credit_note(self, credit_note_obj):
        url = self.base_url + 'credit_notes'
        idempotency_key = generate_idempotency_key(credit_note_obj)
        auth_header = {'Authorization': 'Basic ' + self._api_key,
                       'Content-Type': 'application/json',
                       'Idempotency-Key': idempotency_key}
        if credit_note_obj.get("items", 0):
            credit_note_obj["items"] = [prepare_items(obj=item) for item in credit_note_obj["items"]]
        
        try:
            response = requests.post(url, headers=auth_header, json=json.dumps(credit_note_obj))
            
            if response.status_code == 200:
                print("POST request successful")
                return response.json()  
            else:
                print("POST request failed with status code:", response.status_code)
                return None
        except Exception as e:
            print("An error occurred:", e)
            return None
    
    
    def create_credit_POST(self, amount:float, customer_id:int, credit_note_id:int):   
        url = self.base_url + 'transactions'
        auth_header = {'Authorization': 'Basic ' + self._api_key,
                       'Content-Type': 'application/json'}
        
        data = {"amount": amount,
                "type": "adjustment",
                "method": "balance",
                "customer": customer_id,
                }
        if credit_note_id > -1: data["credit_note"] = credit_note_id
        try:
            response = requests.post(url, headers=auth_header, json=data)
            
            if response.status_code == 200:
                print("POST request successful")
                return response.json()  
            else:
                print("POST request failed with status code:", response.status_code)
                return None
        except Exception as e:
            print("An error occurred:", e)
            return None

    def create_invoice_POST(self, invoice_obj:dict):
        url = self._base_url + '/transactions'
        auth_header = {'Authorization': 'Basic ' + self._api_key}
        try:
            response = requests.post(url, headers=auth_header, json=invoice_obj)
            
            if response.status_code == 200:
                print("POST request successful")
                return response.json()  
            else:
                print("POST request failed with status code:", response.status_code)
                return None
        except Exception as e:
            print("An error occurred:", e)
            return None

    def create_invoice_with_client_api(self, invoice_obj):
        return self._handler.Invoice.create(invoice_obj)



'''
