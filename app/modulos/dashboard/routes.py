from flask import Blueprint, render_template, jsonify, abort
from flask_login import login_required
from sqlalchemy import func
from app.models import db, Propiedad, TipoPropiedad, EstadoPropiedad, Contrato
from app.modulos.auth.routes import roles_permitidos

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def index():
    # 1. Total de propiedades (Cálculo directo en BD)
    total_propiedades = db.session.query(func.count(Propiedad.id)).scalar() or 0
    
    # 2. Total de propiedades vendidas (Cálculo directo en BD)
    vendido_estado = db.session.query(EstadoPropiedad.id).filter(EstadoPropiedad.nombre_estado == 'Vendida').scalar()
    total_vendidas = db.session.query(func.count(Propiedad.id)).filter(Propiedad.estado_id == vendido_estado).scalar() if vendido_estado else 0
    
    # 3. Suma total de montos de contratos (Cálculo directo en BD)
    suma_transacciones = db.session.query(func.sum(Contrato.monto_final)).scalar() or 0
    
    # 4. Promedio de precio de propiedades (Cálculo directo en BD)
    precio_promedio = db.session.query(func.avg(Propiedad.precio)).scalar() or 0

    return render_template(
        'dashboard/index.html',
        total_propiedades=total_propiedades,
        total_vendidas=total_vendidas,
        suma_transacciones=float(suma_transacciones),
        precio_promedio=float(precio_promedio)
    )

@bp.route('/api/metrics')
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def api_metrics():
    """
    Retorna métricas agregadas de la base de datos en formato JSON
    para los gráficos de Chart.js utilizando el nuevo esquema.
    """
    # Distribución por Tipo de Propiedad
    tipos_data = db.session.query(
        TipoPropiedad.nombre_tipo,
        func.count(Propiedad.id)
    ).join(Propiedad, Propiedad.tipo_id == TipoPropiedad.id)\
     .group_by(TipoPropiedad.nombre_tipo).all()
     
    distribucion_tipos = {nombre: count for nombre, count in tipos_data}

    # Distribución por Estado
    estados_data = db.session.query(
        EstadoPropiedad.nombre_estado,
        func.count(Propiedad.id)
    ).join(Propiedad, Propiedad.estado_id == EstadoPropiedad.id)\
     .group_by(EstadoPropiedad.nombre_estado).all()
     
    distribucion_estados = {nombre: count for nombre, count in estados_data}

    # Contratos por Tipo (Compraventa vs Arrendamiento)
    contratos_data = db.session.query(
        Contrato.tipo_contrato,
        func.sum(Contrato.monto_final)
    ).group_by(Contrato.tipo_contrato).all()
    
    monto_contratos = {tipo: float(monto) for tipo, monto in contratos_data if monto is not None}

    return jsonify({
        'tipos': distribucion_tipos,
        'estados': distribucion_estados,
        'transacciones': monto_contratos
    })
