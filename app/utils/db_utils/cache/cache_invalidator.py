# app/utils/db_utils/cache/cache_invalidator.py

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Set, Union
from datetime import datetime
from functools import wraps
from app.core.core_database import DatabaseManager, DatabaseError
from .query_cache import QueryCache

logger = logging.getLogger(__name__)

class CacheInvalidator:
    """
    Handles cache invalidation strategies and dependencies.
    Provides automatic and manual cache invalidation with dependency tracking.
    """

    def __init__(self, query_cache: QueryCache):
        self.query_cache = query_cache
        self.dependencies: Dict[str, Set[str]] = {}
        self._initialize_invalidation_tables()
        self._load_dependencies()

    def _initialize_invalidation_tables(self) -> None:
        """Initialize tables for invalidation tracking"""
        try:
            queries = [
                # Cache dependencies table
                """
                CREATE TABLE IF NOT EXISTS cache_dependencies (
                    id SERIAL PRIMARY KEY,
                    cache_key TEXT NOT NULL UNIQUE,
                    dependencies JSONB NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """,
                # Invalidation history table
                """
                CREATE TABLE IF NOT EXISTS invalidation_history (
                    id SERIAL PRIMARY KEY,
                    table_name TEXT NOT NULL,
                    record_id TEXT,
                    action TEXT NOT NULL,
                    patterns TEXT[],
                    invalidated_keys INTEGER,
                    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    details JSONB
                );
                """
            ]

            for query in queries:
                DatabaseManager.execute_query(query)

        except Exception as e:
            logger.error(f"Error initializing invalidation tables: {str(e)}")
            raise DatabaseError(f"Failed to initialize invalidation tables: {str(e)}")

    def _load_dependencies(self) -> None:
        """Load cache dependencies from database"""
        try:
            query = "SELECT cache_key, dependencies FROM cache_dependencies"
            results = DatabaseManager.execute_query(query)
            
            for result in results:
                key = result['cache_key']
                deps = json.loads(result['dependencies'])
                self.dependencies[key] = set(deps)

        except Exception as e:
            logger.error(f"Error loading cache dependencies: {str(e)}")
            raise DatabaseError(f"Failed to load cache dependencies: {str(e)}")

    def invalidate_on_change(
        self,
        table_names: Union[str, List[str]],
        track_dependencies: bool = True
    ):
        """
        Decorator to automatically invalidate cache on data changes
        
        Args:
            table_names: Table(s) that trigger invalidation
            track_dependencies: Whether to track and invalidate dependencies
        """
        if isinstance(table_names, str):
            table_names = [table_names]

        def decorator(func):
            if asyncio.iscoroutinefunction(func):
                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    try:
                        # Execute the async function
                        result = await func(*args, **kwargs)
                        
                        # Perform invalidation after the function completes
                        record_id = kwargs.get('id') or kwargs.get('record_id')
                        action = self._determine_action(kwargs)
                        
                        for table_name in table_names:
                            self._invalidate_table_cache(
                                table_name,
                                record_id,
                                action,
                                track_dependencies
                            )
                        return result
                    except Exception as e:
                        logger.error(f"Error in async invalidation: {str(e)}")
                        raise
                return async_wrapper
            else:
                @wraps(func)
                def sync_wrapper(*args, **kwargs):
                    try:
                        # Execute the sync function
                        result = func(*args, **kwargs)
                        
                        # Perform invalidation after the function completes
                        record_id = kwargs.get('id') or kwargs.get('record_id')
                        action = self._determine_action(kwargs)
                        
                        for table_name in table_names:
                            self._invalidate_table_cache(
                                table_name,
                                record_id,
                                action,
                                track_dependencies
                            )
                        return result
                    except Exception as e:
                        logger.error(f"Error in sync invalidation: {str(e)}")
                        raise
                return sync_wrapper
            
        return decorator

    def _determine_action(self, kwargs: Dict) -> str:
        """Determine the type of database action"""
        if 'delete' in kwargs or kwargs.get('action') == 'DELETE':
            return 'DELETE'
        if any(key in kwargs for key in ['id', 'record_id']):
            return 'UPDATE'
        return 'INSERT'

    def _invalidate_table_cache(
        self,
        table_name: str,
        record_id: Optional[Any],
        action: str,
        track_dependencies: bool
    ) -> None:
        """Invalidate cache for a specific table"""
        try:
            # Get invalidation patterns
            patterns = self._get_invalidation_patterns(table_name)
            invalidated_keys = 0

            # Process each pattern
            for pattern in patterns:
                # Replace placeholders
                if record_id and '{id}' in pattern:
                    actual_pattern = pattern.format(id=record_id)
                else:
                    actual_pattern = pattern

                # Invalidate matching keys
                keys = self.query_cache.redis.keys(actual_pattern)
                if keys:
                    self.query_cache.redis.delete(*keys)
                    invalidated_keys += len(keys)

                    # Track dependencies if enabled
                    if track_dependencies:
                        self._invalidate_dependencies(actual_pattern)

            # Log invalidation
            self._log_invalidation(
                table_name,
                record_id,
                action,
                patterns,
                invalidated_keys
            )

        except Exception as e:
            logger.error(f"Error invalidating table cache: {str(e)}")
            raise DatabaseError(f"Failed to invalidate table cache: {str(e)}")

    def _get_invalidation_patterns(self, table_name: str) -> List[str]:
        """Get invalidation patterns for a table"""
        try:
            query = """
                SELECT invalidation_patterns 
                FROM cache_rules 
                WHERE table_name = %s 
                AND enabled = true
            """
            result = DatabaseManager.execute_query(query, (table_name,))
            
            if result:
                return json.loads(result[0]['invalidation_patterns'])
            return []

        except Exception as e:
            logger.error(f"Error getting invalidation patterns: {str(e)}")
            raise DatabaseError(f"Failed to get invalidation patterns: {str(e)}")

    def _invalidate_dependencies(self, pattern: str) -> None:
        """Invalidate dependent cache keys"""
        try:
            # Get direct dependencies
            direct_deps = self.dependencies.get(pattern, set())
            
            # Track processed patterns to avoid cycles
            processed = {pattern}
            to_process = direct_deps.copy()

            # Process dependencies breadth-first
            while to_process:
                current_pattern = to_process.pop()
                if current_pattern in processed:
                    continue

                processed.add(current_pattern)
                
                # Invalidate current pattern
                keys = self.query_cache.redis.keys(current_pattern)
                if keys:
                    self.query_cache.redis.delete(*keys)

                # Add its dependencies to process
                pattern_deps = self.dependencies.get(current_pattern, set())
                to_process.update(pattern_deps - processed)

        except Exception as e:
            logger.error(f"Error invalidating dependencies: {str(e)}")
            logger.exception("Dependency invalidation failed but continuing")

    def _log_invalidation(
        self,
        table_name: str,
        record_id: Optional[Any],
        action: str,
        patterns: List[str],
        invalidated_keys: int
    ) -> None:
        """Log cache invalidation details"""
        try:
            query = """
                INSERT INTO invalidation_history (
                    table_name, record_id, action, patterns,
                    invalidated_keys, details
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            details = {
                'timestamp': datetime.now().isoformat(),
                'patterns': patterns,
                'invalidated_keys': invalidated_keys
            }
            
            DatabaseManager.execute_query(
                query,
                (
                    table_name,
                    str(record_id) if record_id else None,
                    action,
                    patterns,
                    invalidated_keys,
                    json.dumps(details)
                )
            )

        except Exception as e:
            logger.error(f"Error logging invalidation: {str(e)}")
            logger.exception("Invalidation logging failed but continuing")

    def add_dependency(
        self,
        cache_key: str,
        dependent_keys: List[str]
    ) -> None:
        """Add cache key dependencies"""
        try:
            self.dependencies[cache_key] = set(dependent_keys)
            
            query = """
                INSERT INTO cache_dependencies (
                    cache_key, dependencies, created_at
                ) VALUES (%s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (cache_key) DO UPDATE SET
                    dependencies = EXCLUDED.dependencies,
                    updated_at = CURRENT_TIMESTAMP
            """
            
            DatabaseManager.execute_query(
                query,
                (cache_key, json.dumps(list(dependent_keys)))
            )

        except Exception as e:
            logger.error(f"Error adding cache dependency: {str(e)}")
            raise DatabaseError(f"Failed to add cache dependency: {str(e)}")

    def remove_dependency(self, cache_key: str) -> None:
        """Remove cache key dependencies"""
        try:
            self.dependencies.pop(cache_key, None)
            
            query = "DELETE FROM cache_dependencies WHERE cache_key = %s"
            DatabaseManager.execute_query(query, (cache_key,))

        except Exception as e:
            logger.error(f"Error removing cache dependency: {str(e)}")
            raise DatabaseError(f"Failed to remove cache dependency: {str(e)}")

    def get_invalidation_history(
        self,
        table_name: Optional[str] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get cache invalidation history with filters"""
        try:
            query = "SELECT * FROM invalidation_history WHERE 1=1"
            params = []

            if table_name:
                query += " AND table_name = %s"
                params.append(table_name)

            if action:
                query += " AND action = %s"
                params.append(action)

            if start_date:
                query += " AND timestamp >= %s"
                params.append(start_date)

            if end_date:
                query += " AND timestamp <= %s"
                params.append(end_date)

            query += " ORDER BY timestamp DESC LIMIT %s"
            params.append(limit)

            return DatabaseManager.execute_query(query, tuple(params))

        except Exception as e:
            logger.error(f"Error getting invalidation history: {str(e)}")
            raise DatabaseError(f"Failed to get invalidation history: {str(e)}")

    def get_dependency_graph(self) -> Dict[str, Any]:
        """Get cache dependency graph"""
        try:
            nodes = []
            edges = []
            
            for key, deps in self.dependencies.items():
                nodes.append({
                    'id': key,
                    'type': 'pattern',
                    'keys': len(self.query_cache.redis.keys(key))
                })
                
                for dep in deps:
                    edges.append({
                        'source': key,
                        'target': dep
                    })
            
            return {
                'nodes': nodes,
                'edges': edges
            }

        except Exception as e:
            logger.error(f"Error getting dependency graph: {str(e)}")
            raise DatabaseError(f"Failed to get dependency graph: {str(e)}")