from app.extensions import db
from app.models import Company

class CompanyManager:
    @staticmethod
    def get_all_companies():
        return db.session.query(Company).all()

    @staticmethod
    def get_company_by_id(company_id):
        return db.session.query(Company).get(company_id)