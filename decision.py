from spyne import Application, rpc, ServiceBase, Unicode, String, Integer, Float
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted
import json
from suds.client import Client

stockageService = Client("http://127.0.0.1:8000/stockageService?wsdl")


class DecisionApprobationService(ServiceBase):

    @rpc(Unicode, _returns=Unicode)
    def analyse_risques(self, client_id):
        client_data = stockageService.service.retrieve_client_data(client_id)
        client_data_dict = json.loads(client_data)
        credit_score = int(client_data_dict['Credit'])
        montant_pret = int(client_data_dict['Montant du Prêt Demandé'].split(' ')[0])
        propriete = int(client_data_dict['Property'])
        print(credit_score, montant_pret, propriete)

        if credit_score < 700:
            return False
        elif montant_pret > 0.8 * propriete:
            return False
        else:
            return True

    @rpc(Unicode, _returns=Unicode)
    def prise_decision(self, client_id):
        analyse = DecisionApprobationService.analyse_risques(self, client_id)

        if analyse:
            return "Votre demande de prêt est approuvée."
        else:
            return "Votre demande de prêt est refusée."


application = Application([DecisionApprobationService],
                          tns='spyne.examples.decision_approbation_service',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11()
                          )

if __name__ == '__main__':
    wsgi_app = WsgiApplication(application)
    twisted_apps = [
        (wsgi_app, b'DecisionApprobationService'),
    ]

    run_twisted(twisted_apps, 8003)
