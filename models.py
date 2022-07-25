from flask import Response
from werkzeug.wrappers.response import Response as WZResponse
from main import db, bcrypt, login_manager
from functools import wraps
import datetime

class User(db.Model):
    # Identification
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    lastip = db.Column(db.String, nullable=False)
    lastlogin = db.Column(db.DateTime, nullable=False)

    # Personaliation
    profile_picture = db.Column(db.String, nullable=False, default='default.jpg')
    colour = db.Column(db.String, nullable=False, default='#ffffff')
    banner = db.Column(db.String, nullable=False, default='default.jpg')

    # Moderation
    account_level = db.Column(db.Integer, nullable=False, default=0)
    banned = db.Column(db.Boolean, nullable=False, default=False)
    ban_reason = db.Column(db.String, nullable=True, default='')

    # Flask-Bcrypt
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    # Flask-Login
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def is_admin(self):
        return self.account_level >= 1

    def is_moderator(self):
        return self.account_level >= 2

    def set_moderator(self):
        self.account_level = 2
        db.session.commit()
    
    def __repr__(self):
        return '<User %r>' % self.username

class Server(db.Model):
    # Identification
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(80), nullable=False)
    hostname = db.Column(db.String(100), nullable=False)
    owner = db.Column(db.Integer)

    # Personaliation
    colour = db.Column(db.String, nullable=False, default='#ffffff')
    banner = db.Column(db.String, nullable=False, default='default.jpg')
    image = db.Column(db.String, nullable=False, default='default.jpg')

    # Moderation
    approved = db.Column(db.Boolean, nullable=False, default=False)
    approved_by = db.Column(db.Integer, nullable=True)
    approved_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return '<Server %r>' % self.name

class Utility:
    @staticmethod
    def get_approved_servers():
        return Server.query.filter_by(approved=True).all()

    @staticmethod
    def get_unapproved_servers():
        return Server.query.filter_by(approved=False).all()

    @staticmethod
    def get_server_by_id(id):
        return Server.query.filter_by(id=id).first()

    @staticmethod
    def randomColour():
        import random
        return '#%06x' % random.randint(0, 0xFFFFFF)

    @staticmethod
    def create_fake_servers(count=100):
        from faker import Faker
        fake = Faker()
        for i in range(count):
            server = Server(
                name=fake.company(),
                description=fake.text(),
                hostname=fake.domain_name(),
                owner=1,
                colour=Utility.randomColour(),
                banner='default.jpg',
                image='default.jpg',
                approved=True
            )
            db.session.add(server)
        db.session.commit()

    @staticmethod
    def getServers(page, per_page, approved=True):
        if approved:
            return Server.query.filter_by(approved=True).paginate(page, per_page, False)
        else:
            return Server.query.filter_by(approved=False).paginate(page, per_page, False)

db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))