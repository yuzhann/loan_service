from spyne import Application, rpc, ServiceBase, Unicode, String, Integer, Float
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted
from suds.client import Client
import json

solvencyVerificationService = Client('http://127.0.0.1:8002/SolvencyVerificationService?wsdl')
property_evaluation_service = Client('http://127.0.0.1:8088/propertyEvaluationService?wsdl')
ie_client = Client('http://127.0.0.1:8080/IEService?wsdl')
stockageService = Client("http://127.0.0.1:8000/stockageService?wsdl")
decisionService = Client("http://127.0.0.1:8003/DecisionApprobationService?wsdl")


class LoanApprovalService(ServiceBase):
    @rpc(Unicode, _returns=Unicode)
    def loan_request(ctx, data):
        processed_data_str = ie_client.service.identify_entities(data)
        processed_data_dict = {}
        try:
            processed_data_dict = json.loads(processed_data_str)
        except json.JSONDecodeError:
            print("The response is not a valid JSON string.")
        solvencyVerificationService.service.check_client_solvency_status(processed_data_dict.get('Client_id'))
        property_evaluation_service.service.evaluate_property_value(processed_data_dict.get('Code_Postal'))
        result = decisionService.service.prise_decision(processed_data_dict.get('Client_id'))

        return result


application = Application([LoanApprovalService],
                          tns='spyne.examples.LoanApprovalService',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11()
                          )

if __name__ == '__main__':
    wsgi_app = WsgiApplication(application)
    twisted_apps = [
        (wsgi_app, b'loanApprovalService'),
    ]

    run_twisted(twisted_apps, 8010)
