from datetime import datetime
from app import db

class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    marital_status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with Child model
    children = db.relationship('Child', backref='family', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Family {self.name}>"

class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    marital_status = db.Column(db.String(20), nullable=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    
    def __repr__(self):
        return f"<Child {self.name}>"
    
    @property
    def age(self):
        today = datetime.now().date()
        born = self.date_of_birth
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
