from . import db

class VisitLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45))
    url = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

