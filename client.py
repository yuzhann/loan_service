from suds.client import Client
import json

from suds.client import Client

loanApprovalService = Client("http://127.0.0.1:8010/loanApprovalService?wsdl")


def upload_information(client_info):
    result = loanApprovalService.service.loan_request(client_info)
    print(result)


if __name__ == '__main__':
    text = """
        Nom du client: John Doe
        Adresse: 123 Rue de la Liberté, 75001 Paris, France
        Email: john.doe@email.com
        Numéro de téléphone: +33 123 456 789
        Montant du Prêt Demandé: 200000 EUR
        Durée du Prêt: 20 ans
        Description de la Propriété: Maison à deux étages avec jardin, située dans un quartier résidentiel calme.
        Revenu Mensuel: 5000 EUR
        Dépenses Mensuelles: 3000 EUR
        """
    upload_information(text)
