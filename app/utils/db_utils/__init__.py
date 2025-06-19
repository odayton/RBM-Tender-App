# Root level: app/utils/db_utils/__init__.py
"""
Main database utilities package initialization.
Exposes all core functionality and managers from submodules.
"""

from ...core.core_database import DatabaseManager, DatabaseError
from .db_verify import DatabaseVerifier

# Import managers from submodules
from .pump import (
    PumpDatabaseManager,
    InertiaDatabaseManager,
    SeismicSpringDatabaseManager,
    RubberMountDatabaseManager,
    AdditionalPriceAdderManager,
    PumpAccessoryManager
)

from .deal import (
    DealDatabaseManager,
    LineItemDatabaseManager,
    RevisionDatabaseManager
)

from .organization import (
    ContactDatabaseManager,
    CompanyDatabaseManager,
    DealOwnerManager
)

from .bom import BOMDatabaseManager

from .export import ExcelExporter, PDFExporter, ReportGenerator
from .import_ import ExcelImporter, DataValidator, ImportProcessor
from .audit import DatabaseAuditor, ChangeTracker, AuditReporter
from .cache import QueryCache, CacheManager, CacheInvalidator
from .migration import SchemaManager, VersionControl, MigrationRunner

__all__ = [
    # Core
    'DatabaseManager',
    'DatabaseError',
    'DatabaseVerifier',
    
    # Pump Related
    'PumpDatabaseManager',
    'InertiaDatabaseManager',
    'SeismicSpringDatabaseManager',
    'RubberMountDatabaseManager',
    'AdditionalPriceAdderManager',
    'PumpAccessoryManager',
    
    # Deal Related
    'DealDatabaseManager',
    'LineItemDatabaseManager',
    'RevisionDatabaseManager',
    
    # Organization Related
    'ContactDatabaseManager',
    'CompanyDatabaseManager',
    'DealOwnerManager',
    
    # BOM Related
    'BOMDatabaseManager',
    
    # Export Related
    'ExcelExporter',
    'PDFExporter',
    'ReportGenerator',
    
    # Import Related
    'ExcelImporter',
    'DataValidator',
    'ImportProcessor',
    
    # Audit Related
    'DatabaseAuditor',
    'ChangeTracker',
    'AuditReporter',
    
    # Cache Related
    'QueryCache',
    'CacheManager',
    'CacheInvalidator',
    
    # Migration Related
    'SchemaManager',
    'VersionControl',
    'MigrationRunner',
]