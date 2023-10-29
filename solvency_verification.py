from spyne import Application, rpc, ServiceBase, Unicode, String, Integer, Float
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted
from suds.client import Client
import json


stockageService = Client("http://127.0.0.1:8000/stockageService?wsdl")

class CreditBureauDatabase:
    data = {
        "001": (5000, 2, False),
        "002": (2000, 0, False),
        "003": (10000, 5, True)
    }

    @classmethod
    def get_client_credit_data(cls, client_id):
        """Retrieve credit data for a specific client."""
        return cls.data.get(client_id, (0, 0, False))

class ClientFinancialDatabase:
    data = {
        "001": {"name": "Marie Dupont", "address": "123 Main St", "monthly_income": 4000, "monthly_expenses": 300},
        "002": {"name": "Pierre Lauren", "address": "456 Elm St", "monthly_income": 3000, "monthly_expenses": 200},
        "003": {"name": "John Doe", "address": "789 Oak St", "monthly_income": 6000, "monthly_expenses": 500}
    }

    @classmethod
    def check_if_client_id_exists(cls, key):
        """Check if the specified key exists in the data dictionary."""
        return key in cls.data

    @classmethod
    def get_client_details(cls, client_id):
        """Retrieve client name and address based on client ID."""
        client_data = cls.data.get(client_id, {})
        name = client_data.get("name", "N/A")
        address = client_data.get("address", "N/A")
        return name, address

    @classmethod
    def get_client_financial_data(cls, client_id):
        """Retrieve client monthly income and expenses based on client ID."""
        client_data = cls.data.get(client_id, {})
        monthly_income = client_data.get("monthly_income", 0)
        monthly_expenses = client_data.get("monthly_expenses", 0)
        return monthly_income, monthly_expenses

class CreditScoring:
  @staticmethod
  def calculate_credit_score(debt, late_payments, has_bankruptcy):
    """Calculate credit score based on client's financial history."""
    score = 1000 - debt * 0.1 - late_payments * 50
    if has_bankruptcy:
      score -= 200
    return score

class SolvencyChecker:
  @staticmethod
  def check_solvency(monthly_income, monthly_expenses, credit_score):
    """Determine client's solvency status."""
    solvency = "solvent" if credit_score >= 700 and monthly_income > monthly_expenses else "not solvent"
    return solvency


class ExplanationGenerator:
    @staticmethod
    def generate_explanation(monthly_income, monthly_expenses, credit_score):
        # Checking solvency based on credit score and financial situation
        if credit_score >= 700:
            if monthly_income > monthly_expenses:
                explanation = "The client has a sufficient credit score and income over expenses."
            else:
                explanation = "The client has a sufficient credit score, but their monthly income does not cover their expenses."
        else:
            explanation = "The client has an insufficient credit score, potential high risks for a loan."

        return explanation


class SolvencyVerificationService(ServiceBase):
    @rpc(Unicode, _returns=Unicode)
    def check_client_solvency_status(ctx, client_id):
        # Retrieve client credit data
        debt, late_payments, has_bankruptcy = CreditBureauDatabase.get_client_credit_data(client_id)
        # Calculate credit score
        credit_score = CreditScoring.calculate_credit_score(debt, late_payments, has_bankruptcy)
        # Store client credit data
        client_data = {
            "Client_id": client_id,
            "Credit": credit_score
        }
        json_string = json.dumps(client_data, ensure_ascii=False, indent=4)
        stockageService.service.insert_credit_db(json_string)
        # Retrieve client financial data
        monthly_income, monthly_expenses = ClientFinancialDatabase.get_client_financial_data(client_id)
        # Check solvency
        solvency_status = SolvencyChecker.check_solvency(monthly_income, monthly_expenses, credit_score)
        # Generate explanation
        explanation = ExplanationGenerator.generate_explanation(monthly_income, monthly_expenses, credit_score)
        return solvency_status + ": " + explanation


application = Application([SolvencyVerificationService],
                          tns='spyne.examples.SolvencyVerificationService',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11()
                          )

if __name__ == '__main__':
    wsgi_app = WsgiApplication(application)
    twisted_apps = [
        (wsgi_app, b'SolvencyVerificationService'),
    ]

    run_twisted(twisted_apps, 8002)