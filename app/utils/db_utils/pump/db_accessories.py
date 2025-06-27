from app.extensions import db
from app.models import Pump, InertiaBase, SeismicSpring, RubberMount

class AccessoryManager:
    @staticmethod
    def get_all_accessories():
        """
        Retrieves all accessories from the database.
        Returns a dictionary with keys 'inertia_bases', 'seismic_springs', 'rubber_mounts'.
        """
        return {
            'inertia_bases': db.session.query(InertiaBase).all(),
            'seismic_springs': db.session.query(SeismicSpring).all(),
            'rubber_mounts': db.session.query(RubberMount).all()
        }