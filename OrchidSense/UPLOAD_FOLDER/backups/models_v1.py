from extensions import db, mail
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash




class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Orquidea(db.Model):
    __tablename__ = 'orquideas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    temperatura_ideal = db.Column(db.String(50))
    humidade_ideal = db.Column(db.String(50))
    luz_ideal = db.Column(db.String(100))
    descricao = db.Column(db.Text)
    imagem = db.Column(db.String(255))

    def __repr__(self):
        return f'<Orquidea {self.nome}>'




class UserConfig(db.Model):
    __tablename__ = 'user_configs'  # Nome da tabela no banco de dados

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    orquidea_id = db.Column(db.Integer, db.ForeignKey('orquideas.id'), nullable=False)
    temp_min = db.Column(db.Float)
    temp_max = db.Column(db.Float)
    humidade_min = db.Column(db.Float)
    humidade_max = db.Column(db.Float)

