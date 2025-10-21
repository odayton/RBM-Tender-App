"""
Performance tests for deal management
"""

import pytest
import time
from tests.factories import DealFactory, AdminUserFactory, CompanyFactory, ContactFactory


class TestDealPerformance:
    """Performance tests for deal operations."""
    
    def test_deal_creation_performance(self, db_session, benchmark):
        """Test performance of deal creation."""
        user = AdminUserFactory()
        company = CompanyFactory()
        contact = ContactFactory(company=company)
        
        db_session.add_all([user, company, contact])
        db_session.commit()
        
        def create_deal():
            deal = DealFactory(
                owner=user,
                companies=[company],
                contacts=[contact]
            )
            db_session.add(deal)
            db_session.commit()
            return deal
        
        # Benchmark deal creation
        result = benchmark(create_deal)
        assert result is not None
    
    def test_deal_list_performance(self, db_session, benchmark):
        """Test performance of deal listing."""
        user = AdminUserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Create multiple deals
        deals = []
        for i in range(100):
            deal = DealFactory(owner=user)
            deals.append(deal)
        
        db_session.add_all(deals)
        db_session.commit()
        
        def list_deals():
            return db_session.query(DealFactory._meta.model).filter_by(owner_id=user.id).all()
        
        # Benchmark deal listing
        result = benchmark(list_deals)
        assert len(result) == 100
    
    def test_deal_search_performance(self, db_session, benchmark):
        """Test performance of deal search."""
        user = AdminUserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Create deals with different names
        deals = []
        for i in range(100):
            deal = DealFactory(
                owner=user,
                project_name=f'Project {i} HVAC System'
            )
            deals.append(deal)
        
        db_session.add_all(deals)
        db_session.commit()
        
        def search_deals():
            return db_session.query(DealFactory._meta.model).filter(
                DealFactory._meta.model.project_name.like('%HVAC%')
            ).all()
        
        # Benchmark deal search
        result = benchmark(search_deals)
        assert len(result) == 100
    
    def test_deal_statistics_performance(self, db_session, benchmark):
        """Test performance of deal statistics calculation."""
        user = AdminUserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Create deals with different stages and amounts
        deals = []
        for i in range(50):
            deal = DealFactory(
                owner=user,
                total_amount=10000 + (i * 1000),
                probability=50 + (i % 50)
            )
            deals.append(deal)
        
        db_session.add_all(deals)
        db_session.commit()
        
        def calculate_statistics():
            from app.extensions import db
            total_deals = db_session.query(DealFactory._meta.model).filter_by(owner_id=user.id).count()
            total_value = db_session.query(
                db.func.sum(DealFactory._meta.model.total_amount)
            ).filter_by(owner_id=user.id).scalar()
            
            return {
                'total_deals': total_deals,
                'total_value': total_value or 0
            }
        
        # Benchmark statistics calculation
        result = benchmark(calculate_statistics)
        assert result['total_deals'] == 50
        assert result['total_value'] > 0
    
    def test_deal_bulk_operations_performance(self, db_session, benchmark):
        """Test performance of bulk deal operations."""
        user = AdminUserFactory()
        db_session.add(user)
        db_session.commit()
        
        def bulk_create_deals():
            deals = []
            for i in range(50):
                deal = DealFactory(owner=user)
                deals.append(deal)
            
            db_session.add_all(deals)
            db_session.commit()
            return len(deals)
        
        # Benchmark bulk creation
        result = benchmark(bulk_create_deals)
        assert result == 50
    
    def test_deal_filtering_performance(self, db_session, benchmark):
        """Test performance of deal filtering by stage."""
        user = AdminUserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Create deals with different stages
        from app.models import DealStage
        stages = [DealStage.SALES_LEAD, DealStage.PROPOSAL, DealStage.NEGOTIATION, DealStage.CLOSED_WON]
        
        deals = []
        for i in range(100):
            deal = DealFactory(
                owner=user,
                stage=stages[i % len(stages)]
            )
            deals.append(deal)
        
        db_session.add_all(deals)
        db_session.commit()
        
        def filter_by_stage():
            return db_session.query(DealFactory._meta.model).filter(
                DealFactory._meta.model.stage == DealStage.SALES_LEAD,
                DealFactory._meta.model.owner_id == user.id
            ).all()
        
        # Benchmark filtering
        result = benchmark(filter_by_stage)
        assert len(result) == 25  # 100 deals / 4 stages = 25 per stage
    
    def test_deal_pagination_performance(self, db_session, benchmark):
        """Test performance of deal pagination."""
        user = AdminUserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Create many deals
        deals = []
        for i in range(200):
            deal = DealFactory(owner=user)
            deals.append(deal)
        
        db_session.add_all(deals)
        db_session.commit()
        
        def paginate_deals():
            page = 1
            per_page = 20
            offset = (page - 1) * per_page
            
            return db_session.query(DealFactory._meta.model).filter_by(
                owner_id=user.id
            ).offset(offset).limit(per_page).all()
        
        # Benchmark pagination
        result = benchmark(paginate_deals)
        assert len(result) == 20
    
    def test_deal_relationship_loading_performance(self, db_session, benchmark):
        """Test performance of loading deal relationships."""
        user = AdminUserFactory()
        company = CompanyFactory()
        contact = ContactFactory(company=company)
        
        db_session.add_all([user, company, contact])
        db_session.commit()
        
        # Create deal with relationships
        deal = DealFactory(
            owner=user,
            companies=[company],
            contacts=[contact]
        )
        db_session.add(deal)
        db_session.commit()
        
        def load_relationships():
            deal = db_session.query(DealFactory._meta.model).first()
            # Access relationships to trigger lazy loading
            companies = deal.companies
            contacts = deal.contacts
            return len(companies), len(contacts)
        
        # Benchmark relationship loading
        result = benchmark(load_relationships)
        assert result[0] == 1  # One company
        assert result[1] == 1  # One contact

