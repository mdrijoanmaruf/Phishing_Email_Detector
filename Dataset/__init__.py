"""
Dataset package initialization.
Exports the Blueprint, Service, and Model.
"""

from Dataset.routes import dataset_bp
from Dataset.dataset_service import dataset_service, DatasetService
from Dataset.email_record import EmailRecord

__all__ = ["dataset_bp", "dataset_service", "DatasetService", "EmailRecord"]
