from backend.extensions import db
import json

class Item(db.Model):
    __tablename__ = 'items'
    
    url_name = db.Column(db.String, primary_key=True)
    item_name = db.Column(db.String)
    thumb = db.Column(db.String)
    tags = db.Column(db.String)  # Stored as JSON string
    last_updated = db.Column(db.String)
    
    # Relationships
    price_history = db.relationship('PriceHistory', backref='item', lazy=True)
    inventory = db.relationship('UserInventory', backref='item', lazy=True)

    def to_dict(self):
        return {
            'url_name': self.url_name,
            'item_name': self.item_name,
            'thumb': self.thumb,
            'tags': json.loads(self.tags) if self.tags else [],
            'last_updated': self.last_updated
        }

class PriceHistory(db.Model):
    __tablename__ = 'price_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url_name = db.Column(db.String, db.ForeignKey('items.url_name'), nullable=False)
    variant = db.Column(db.String, default='default')
    date = db.Column(db.String)
    avg_price = db.Column(db.Float)
    min_price = db.Column(db.Float)
    max_price = db.Column(db.Float)
    volume = db.Column(db.Integer)
    
    __table_args__ = (
        db.UniqueConstraint('url_name', 'variant', 'date', name='unique_price_history'),
    )

class UserInventory(db.Model):
    __tablename__ = 'user_inventory'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url_name = db.Column(db.String, db.ForeignKey('items.url_name'), nullable=False)
    buy_price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    purchase_date = db.Column(db.String)
    notes = db.Column(db.String)

class VoidTraderHistory(db.Model):
    __tablename__ = 'void_trader_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    arrival_date = db.Column(db.String)
    item_name = db.Column(db.String)
    url_name = db.Column(db.String)
    ducats = db.Column(db.Integer)
    credits = db.Column(db.Integer)
    market_price = db.Column(db.Float, default=0.0)
    
    __table_args__ = (
        db.UniqueConstraint('arrival_date', 'item_name', name='unique_void_trader_entry'),
    )
