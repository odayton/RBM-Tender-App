from typing import Dict, Any, List, Optional
from app.models.pumps.pump_model import Pump, PumpSeries
from app.models.pumps.pump_assembly import PumpAssembly
from app.core.core_errors import ValidationError
import pandas as pd
from datetime import datetime

class PumpSelector:
    """Helper class for pump selection logic"""
    
    @staticmethod
    def find_matching_pumps(flow_rate: float, head: float, 
                          series: Optional[PumpSeries] = None) -> List[Pump]:
        """
        Find pumps matching flow and head requirements
        Args:
            flow_rate: Required flow rate
            head: Required head
            series: Optional specific pump series to search
        Returns:
            List of matching pumps
        """
        query = Pump.query
        
        if series:
            query = query.filter(Pump.series == series)
            
        # Get all pumps first as we need to check their performance
        pumps = query.all()
        
        # Filter pumps based on requirements
        matching_pumps = [
            pump for pump in pumps 
            if pump.meets_requirements(flow_rate, head)
        ]
        
        return matching_pumps

    @staticmethod
    def calculate_efficiency(pump: Pump, flow_rate: float, head: float) -> float:
        """
        Calculate pump efficiency at given operating point
        Args:
            pump: Pump instance
            flow_rate: Operating flow rate
            head: Operating head
        Returns:
            float: Calculated efficiency
        """
        # This would be based on your pump curves and calculation method
        # For now, returning nominal efficiency if available
        return pump.efficiency if pump.efficiency else 0.0

class PumpDataProcessor:
    """Helper class for processing pump data"""
    
    @staticmethod
    def process_tech_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process technical data from uploaded file
        Args:
            data: Raw technical data
        Returns:
            Dict containing processed data
        """
        processed = {}
        
        # Extract relevant fields
        required_fields = ['sku', 'series', 'power_kw', 'efficiency']
        for field in required_fields:
            if field in data:
                processed[field] = data[field]
                
        return processed

    @staticmethod
    def extract_performance_data(data: Dict[str, Any]) -> List[Dict[str, float]]:
        """
        Extract performance curve data points
        Args:
            data: Raw performance data
        Returns:
            List of data points
        """
        points = []
        
        if 'performance_curves' in data:
            for point in data['performance_curves']:
                if 'flow_rate' in point and 'head' in point:
                    points.append({
                        'flow_rate': float(point['flow_rate']),
                        'head': float(point['head']),
                        'efficiency': float(point.get('efficiency', 0))
                    })
                    
        return points

class PumpHistoryTracker:
    """Helper class for tracking pump selection history"""
    
    @staticmethod
    def record_selection(pump: Pump, flow_rate: float, head: float) -> None:
        """
        Record a pump selection
        Args:
            pump: Selected pump
            flow_rate: Operating flow rate
            head: Operating head
        """
        # Implementation would depend on your history tracking model
        pass

    @staticmethod
    def get_similar_selections(flow_rate: float, head: float, 
                             tolerance: float = 0.1) -> List[Dict[str, Any]]:
        """
        Get similar historic selections
        Args:
            flow_rate: Target flow rate
            head: Target head
            tolerance: Matching tolerance (default 10%)
        Returns:
            List of similar selections
        """
        # Implementation would depend on your history tracking model
        return []

class PumpDataExporter:
    """Helper class for exporting pump data"""
    
    @staticmethod
    def export_selections_to_excel(selections: List[Dict[str, Any]], 
                                 filename: str) -> str:
        """
        Export pump selections to Excel
        Args:
            selections: List of pump selections
            filename: Output filename
        Returns:
            str: Path to exported file
        """
        df = pd.DataFrame(selections)
        filepath = f"exports/{filename}"
        df.to_excel(filepath, index=False)
        return filepath

    @staticmethod
    def generate_selection_report(pump: Pump, flow_rate: float, 
                                head: float) -> Dict[str, Any]:
        """
        Generate pump selection report
        Args:
            pump: Selected pump
            flow_rate: Operating flow rate
            head: Operating head
        Returns:
            Dict containing report data
        """
        return {
            'pump_details': pump.to_dict(),
            'operating_point': {
                'flow_rate': flow_rate,
                'head': head,
                'efficiency': PumpSelector.calculate_efficiency(pump, flow_rate, head)
            },
            'timestamp': datetime.now().isoformat()
        }