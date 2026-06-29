from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
# pyrefly: ignore [missing-import]
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Rol(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(50), unique=True, nullable=False)  # Admin, Agente, Cliente, Propietario
    descripcion = db.Column(db.String(200), nullable=True)
    
    # Relationships
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

    def __init__(self, nombre_rol, descripcion=None):
        self.nombre_rol = nombre_rol
        self.descripcion = descripcion

    def __repr__(self):
        return f'<Rol {self.nombre_rol}>'

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='RESTRICT'), nullable=False)
    
    # Relationships
    propiedades = db.relationship('Propiedad', backref='agente', lazy=True, foreign_keys='Propiedad.agente_id')
    visitas = db.relationship('Visita', backref='cliente', lazy=True, foreign_keys='Visita.cliente_id')
    contratos = db.relationship('Contrato', backref='cliente', lazy=True, foreign_keys='Contrato.cliente_id')

    def __init__(self, username, nombre_completo, correo, rol_id):
        self.username = username
        self.nombre_completo = nombre_completo
        self.correo = correo
        self.rol_id = rol_id

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<Usuario {self.username}>'

class TipoPropiedad(db.Model):
    __tablename__ = 'tipos_propiedad'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_tipo = db.Column(db.String(50), unique=True, nullable=False)  # Casa, Departamento, Terreno, Local Comercial
    
    # Relationships
    propiedades = db.relationship('Propiedad', backref='tipo_propiedad', lazy=True)

    def __init__(self, nombre_tipo):
        self.nombre_tipo = nombre_tipo

    def __repr__(self):
        return f'<TipoPropiedad {self.nombre_tipo}>'

class EstadoPropiedad(db.Model):
    __tablename__ = 'estados_propiedad'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_estado = db.Column(db.String(50), unique=True, nullable=False)  # Disponible, Reservada, Alquilada, Vendida
    
    # Relationships
    propiedades = db.relationship('Propiedad', backref='estado', lazy=True)

    def __init__(self, nombre_estado):
        self.nombre_estado = nombre_estado

    def __repr__(self):
        return f'<EstadoPropiedad {self.nombre_estado}>'

class Propietario(db.Model):
    __tablename__ = 'propietarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    correo = db.Column(db.String(100), nullable=True)
    ci_nit = db.Column(db.String(20), unique=True, nullable=False)
    
    # Relationships
    propiedades = db.relationship('Propiedad', backref='propietario', lazy=True)

    def __init__(self, nombre, telefono, ci_nit, correo=None):
        self.nombre = nombre
        self.telefono = telefono
        self.ci_nit = ci_nit
        self.correo = correo

    def __repr__(self):
        return f'<Propietario {self.nombre}>'

class Propiedad(db.Model):
    __tablename__ = 'propiedades'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    precio = db.Column(db.Float, nullable=False)
    direccion = db.Column(db.String(255), nullable=False)
    accion = db.Column(db.String(20), nullable=False)  # Alquiler o Venta
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    imagen_url = db.Column(db.String(255), nullable=True)
    
    # Foreign Keys
    tipo_id = db.Column(db.Integer, db.ForeignKey('tipos_propiedad.id', ondelete='RESTRICT'), nullable=False)
    estado_id = db.Column(db.Integer, db.ForeignKey('estados_propiedad.id', ondelete='RESTRICT'), nullable=False)
    propietario_id = db.Column(db.Integer, db.ForeignKey('propietarios.id', ondelete='RESTRICT'), nullable=False)
    agente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='RESTRICT'), nullable=False)
    
    # Relationships
    visitas = db.relationship('Visita', backref='propiedad', lazy=True, cascade='all, delete-orphan')
    contratos = db.relationship('Contrato', backref='propiedad', lazy=True, cascade='all, delete-orphan')

    def __init__(self, titulo, precio, direccion, accion, tipo_id, propietario_id, agente_id, estado_id, descripcion=None, imagen_url=None):
        self.titulo = titulo
        self.precio = precio
        self.direccion = direccion
        self.accion = accion
        self.tipo_id = tipo_id
        self.propietario_id = propietario_id
        self.agente_id = agente_id
        self.estado_id = estado_id
        self.descripcion = descripcion
        self.imagen_url = imagen_url

    def __repr__(self):
        return f'<Propiedad {self.titulo}>'

class Visita(db.Model):
    __tablename__ = 'visitas'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    estado_visita = db.Column(db.String(50), default='Programada')  # Programada, Realizada, Cancelada
    observaciones = db.Column(db.Text, nullable=True)
    
    # Foreign Keys
    propiedad_id = db.Column(db.Integer, db.ForeignKey('propiedades.id', ondelete='CASCADE'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, fecha_hora, propiedad_id, cliente_id, estado_visita='Programada', observaciones=None):
        self.fecha_hora = fecha_hora
        self.propiedad_id = propiedad_id
        self.cliente_id = cliente_id
        self.estado_visita = estado_visita
        self.observaciones = observaciones

    def __repr__(self):
        return f'<Visita {self.fecha_hora} - Propiedad {self.propiedad_id}>'

class Contrato(db.Model):
    __tablename__ = 'contratos'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_firma = db.Column(db.DateTime, default=datetime.utcnow)
    monto_final = db.Column(db.Float, nullable=False)
    clausulas = db.Column(db.Text, nullable=True)
    tipo_contrato = db.Column(db.String(50), nullable=False)  # Compraventa o Arrendamiento
    
    # Foreign Keys
    propiedad_id = db.Column(db.Integer, db.ForeignKey('propiedades.id', ondelete='CASCADE'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, monto_final, tipo_contrato, propiedad_id, cliente_id, clausulas=None):
        self.monto_final = monto_final
        self.tipo_contrato = tipo_contrato
        self.propiedad_id = propiedad_id
        self.cliente_id = cliente_id
        self.clausulas = clausulas

    def __repr__(self):
        return f'<Contrato {self.tipo_contrato} - Propiedad {self.propiedad_id}>'
