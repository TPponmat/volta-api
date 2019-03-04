from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app
from flask_migrate import Migrate

POSTGRES = {
    'user': 'postgres',
    'pw': 'admin',
    'db': 'peavoltadb',
    'host': 'localhost',
    'port': '5432',
}
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
# app.config['JWT_TOKEN_LOCATION'] = ['json']
#app.config['JWT_SECRET_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'# Change this!
# app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Config for non expiration token
db = SQLAlchemy(app)
# migrate = Migrate(app, db)

class Customer(db.Model):
    id = db.Column(db.Integer, db.Sequence('Seq_customer_id', start=10001, increment=1), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(30), nullable=False, unique=True)
    mobile = db.Column(db.String(30), nullable=False, unique=True)
    login = db.Column(db.String(30), nullable=False, unique=True)
    passwd = db.Column(db.String(30), nullable=False)
    avatar = db.Column(db.String(50))

    def __init__(self, data):
        self.name = data.get('name')
        self.email = data.get('email')
        self.mobile = data.get('mobile')
        self.login = data.get('login')
        self.passwd = data.get('password')
        self.avatar = data.get('avatar_path')
        
    def __repr__(self):
        return '{"cus_id": %r, "cus_login": %r}' % (self.id, self.login)









