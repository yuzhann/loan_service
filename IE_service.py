from spyne import Application, rpc, ServiceBase, String, Unicode
from spyne.util.wsgi_wrapper import run_twisted
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from pymongo import MongoClient
from suds.client import Client
import twisted.web.server
import sys
import re
import json


def extract_info(pattern, text, default=""):
    match = pattern.search(text)
    return match.group() if match else default


class IDGenerator:
    def __init__(self, mongo_uri, db_name, collection_name):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.current_id = self.load_last_id()

    def load_last_id(self):
        id_record = self.collection.find_one({}, sort=[('_id', -1)])

        if id_record and 'last_id' in id_record:
            return id_record['last_id']
        else:
            return 0

    def get_new_id(self):
        # update id
        self.current_id += 1
        new_id = self.current_id

        # add new id to database
        self.collection.update_one({}, {'$set': {'last_id': new_id}}, upsert=True)

        return str(new_id).zfill(3)


def get_client_id():
    MONGO_URI = 'mongodb://localhost:27017/'
    DB_NAME = "client_info"
    COLLECTION_NAME = "id"

    id_generator = IDGenerator(mongo_uri=MONGO_URI, db_name=DB_NAME, collection_name=COLLECTION_NAME)

    new_id = id_generator.get_new_id()
    return new_id


class InfoExtractionService(ServiceBase):

    @rpc(Unicode, _returns=Unicode)
    def identify_entities(self, text):
        name_pattern = re.compile(r'Nom du client:\s*(.*)')
        address_pattern = re.compile(r'Adresse:\s*(.*)')
        code_postal_pattern = re.compile(r'Adresse:.*?(\d{5})')
        email_pattern = re.compile(r'Email:\s*([\w\.-]+@[\w\.-]+\.\w+)')
        phone_pattern = re.compile(r'Numéro de téléphone:\s*(\+\d{1,3}\s?\d{1,4}\s?\d{3}\s?\d{3})')
        montant_pattern = re.compile(r'Montant du Prêt Demandé:\s*([\d\s]+EUR)')
        duree_pattern = re.compile(r'Durée du Prêt:\s*(.*)')
        description_pattern = re.compile(r'Description de la Propriété:\s*(.*)')
        revenu_pattern = re.compile(r'Revenu Mensuel:\s*([\d\s]+EUR)')
        depenses_pattern = re.compile(r'Dépenses Mensuelles:\s*([\d\s]+EUR)')

        data = {}
        data['Client_id'] = get_client_id()
        data['Nom du client'] = name_pattern.search(text).group(1).strip()
        data['Adresse'] = address_pattern.search(text).group(1).strip()
        data['Code_Postal'] = code_postal_pattern.search(text).group(1).strip()
        data['Email'] = email_pattern.search(text).group(1).strip()
        data['Numéro de téléphone'] = phone_pattern.search(text).group(1).strip()
        data['Montant du Prêt Demandé'] = montant_pattern.search(text).group(1).strip()
        data['Durée du Prêt'] = duree_pattern.search(text).group(1).strip()
        data['Description de la Propriété'] = description_pattern.search(text).group(1).strip()
        data['Revenu Mensuel'] = revenu_pattern.search(text).group(1).strip()
        data['Dépenses Mensuelles'] = depenses_pattern.search(text).group(1).strip()

        json_string = json.dumps(data, ensure_ascii=False, indent=4)
        stockageService = Client("http://127.0.0.1:8000/stockageService?wsdl")
        stockageService.service.insert_info_db(json_string)
        return json_string


application = Application([InfoExtractionService],
                          tns='loanApproval.IEService',
                          in_protocol=Soap11(validator="lxml"),
                          out_protocol=Soap11()
                          )

if __name__ == '__main__':
    wsgi_app = WsgiApplication(application)

    twisted_apps = [
        (wsgi_app, b'IEService'),
    ]

    sys.exit(run_twisted(twisted_apps, 8080))
