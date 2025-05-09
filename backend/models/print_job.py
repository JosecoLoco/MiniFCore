from datetime import datetime
from bson import ObjectId

class PrintJob:
    def __init__(self, name, description, file_url, status="pending", created_at=None, updated_at=None, _id=None):
        self._id = _id if _id else str(ObjectId())
        self.name = name
        self.description = description
        self.file_url = file_url
        self.status = status  # pending, printing, completed, failed
        self.created_at = created_at if created_at else datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.utcnow()

    @staticmethod
    def from_dict(data):
        return PrintJob(
            name=data.get('name'),
            description=data.get('description'),
            file_url=data.get('file_url'),
            status=data.get('status', 'pending'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            _id=data.get('_id')
        )

    def to_dict(self):
        return {
            '_id': self._id,
            'name': self.name,
            'description': self.description,
            'file_url': self.file_url,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        } 