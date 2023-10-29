from spyne import Application, rpc, ServiceBase, Unicode, ComplexModel
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted
import json
from suds.client import Client
from IE_service import get_client_id

stockageService = Client("http://127.0.0.1:8000/stockageService?wsdl")

# Define a complex type for property details
class PropertyDetails(ComplexModel):
    address = Unicode
    property_type = Unicode  # e.g., apartment, house
    area = Unicode  # e.g., square meters
    images_or_links = Unicode


class PropertyEvaluationDatabase:
    data = {
        "Appt-001": {"codePostal": 75001, "prix": 500000},  # Estimated market price in EUR based on the address
        "Appt-002": {"codePostal": 75001, "prix": 600000},
        "Appt-003": {"codePostal": 75001, "prix": 550000}
    }

    @classmethod
    def get_prices_by_code_postal(cls, code_postal):
        """Find property prices of the given code postal"""
        prices = [info["prix"] for info in cls.data.values() if info["codePostal"] == code_postal]
        return prices


class MarketDataAnalysis:
    @staticmethod
    def analyse_property_market_data(prices):
        """Estimate the value of the property based on recent sales of similar properties."""
        average_price = sum(prices) / len(prices) if prices else 0

        return average_price


class VirtualInspection:
    @staticmethod
    def conduct_virtual_inspection(property_details):
        """Conduct a virtual inspection using satellite images, photos or virtual tours."""
        # For now, this returns a dummy string, but in a real application, this would return more detailed results
        return "Property is in good condition based on virtual inspection."


class LegalComplianceChecker:
    @staticmethod
    def check_legal_compliance(property_details):
        """Check if the property adheres to legal and regulatory standards."""
        # For now, this returns a dummy string, but in a real application, this would check a database or perform other operations
        return "Property is compliant with all legal and regulatory standards."


class PropertyEvaluationService(ServiceBase):
    @rpc(Unicode, _returns=Unicode)
    def evaluate_property_value(self, codePostal):
        prices = PropertyEvaluationDatabase.get_prices_by_code_postal(codePostal)
        market_value = MarketDataAnalysis.analyse_property_market_data(prices)

        client_data = {
            "Client_id": get_client_id(),
            "Property": market_value

        }
        json_string = json.dumps(client_data, ensure_ascii=False, indent=4)
        stockageService.service.insert_property_db(json_string)

        return f"{market_value} EUR"



application = Application([PropertyEvaluationService],
                          tns='spyne.examples.property_evaluation',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11()
                          )

if __name__ == '__main__':
    wsgi_app = WsgiApplication(application)
    twisted_apps = [
        (wsgi_app, b'propertyEvaluationService'),
    ]

    run_twisted(twisted_apps, 8088)
