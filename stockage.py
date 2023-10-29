import logging

logging.basicConfig(level=logging.DEBUG)
import sys
from spyne import Application, rpc, ServiceBase, \
    Integer, Unicode, AnyDict, Iterable
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted
from pymongo import MongoClient
from suds.xsd.doctor import Import, ImportDoctor
from spyne.protocol.json import JsonDocument
import json
from suds.client import Client
import pymongo


class stockageService(ServiceBase):
    @rpc(Unicode, _returns=Integer)
    def insert_info_db(ctx, client_info):
        info = json.loads(client_info)
        mongodb_client = MongoClient('localhost', 27017)
        db = mongodb_client['client_info']
        coll = db["info"]
        coll.insert_one(info)
        return 1

    @rpc(Unicode, _returns=Integer)
    def insert_credit_db(ctx, client_credit):
        credit = json.loads(client_credit)
        mongodb_client = MongoClient('localhost', 27017)
        db = mongodb_client['client_info']
        coll = db["credit"]
        coll.insert_one(credit)
        return 1

    @rpc(Unicode, _returns=Integer)
    def insert_property_db(ctx, client_property):
        property = json.loads(client_property)
        mongodb_client = MongoClient('localhost', 27017)
        db = mongodb_client['client_info']
        coll = db["property"]
        coll.insert_one(property)
        return 1

    @rpc(Unicode, _returns=Integer)
    def insert_client_data_db(ctx, data):
        client_data = json.loads(data)
        mongodb_client = MongoClient('localhost', 27017)
        db = mongodb_client['client_info']
        coll = db["client_data"]
        coll.insert_one(client_data)
        return 1


    @rpc(Unicode, _returns=Unicode)
    def retrieve_client_data(ctx, client_id):
        client = MongoClient('localhost', 27017)
        db = client['client_info']
        credit_collection = db['credit']
        property_collection = db['property']
        info_collection = db['info']
        credit_data = credit_collection.find_one({'Client_id': client_id})
        property_data = property_collection.find_one({'Client_id': client_id})
        info_data = info_collection.find_one({'Client_id': client_id})

        credit = credit_data['Credit'] if credit_data is not None else 0
        property_value = property_data['Property'] if property_data is not None else 0
        loan_amount_requested = info_data['Montant du Prêt Demandé'] if info_data is not None else 0
        client_data = {
            'Client_id': client_id,
            'Credit': credit,
            'Property': property_value,
            'Montant du Prêt Demandé': loan_amount_requested
        }
        json_string = json.dumps(client_data, ensure_ascii=False, indent=4)
        return json_string


    @rpc(_returns=Unicode)
    def retrieve_credit_db(ctx):
        mongodb_client = MongoClient('mongodb://localhost:27017/')
        db = mongodb_client["client_info"]
        col = db["credit"]
        x = col.find()
        credit = []
        for data in x:
            credit.append(data)
        return json.dumps(credit)


application = Application([stockageService],
                          tns='loanApproval.stokageService',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11()
                          )

if __name__ == '__main__':
    wsgi_app = WsgiApplication(application)

    twisted_apps = [
        (wsgi_app, b'stockageService'),
    ]

    sys.exit(run_twisted(twisted_apps, 8000))