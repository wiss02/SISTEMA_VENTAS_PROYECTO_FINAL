from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from sqlalchemy import func, extract
from app.models import db, Propiedad, TipoPropiedad, EstadoPropiedad, Contrato, Visita, Usuario, Rol
from app.modulos.auth.routes import roles_permitidos

bp = Blueprint('dashboard', __name__)


@bp.route('/')
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def index():
    # KPIs principales
    total_propiedades = db.session.query(func.count(Propiedad.id)).scalar() or 0

    vendido_estado = db.session.query(EstadoPropiedad.id).filter(
        EstadoPropiedad.nombre_estado == 'Vendida').scalar()
    total_vendidas = db.session.query(func.count(Propiedad.id)).filter(
        Propiedad.estado_id == vendido_estado).scalar() if vendido_estado else 0

    suma_transacciones = db.session.query(func.sum(Contrato.monto_final)).scalar() or 0
    precio_promedio = db.session.query(func.avg(Propiedad.precio)).scalar() or 0

    # KPIs adicionales
    total_visitas = db.session.query(func.count(Visita.id)).scalar() or 0
    total_contratos = db.session.query(func.count(Contrato.id)).scalar() or 0

    # Últimas 5 visitas
    ultimas_visitas = Visita.query.order_by(Visita.fecha_hora.desc()).limit(5).all()

    # Últimos 5 contratos
    ultimos_contratos = Contrato.query.order_by(Contrato.fecha_firma.desc()).limit(5).all()

    return render_template(
        'dashboard/index.html',
        total_propiedades=total_propiedades,
        total_vendidas=total_vendidas,
        suma_transacciones=float(suma_transacciones),
        precio_promedio=float(precio_promedio),
        total_visitas=total_visitas,
        total_contratos=total_contratos,
        ultimas_visitas=ultimas_visitas,
        ultimos_contratos=ultimos_contratos
    )


@bp.route('/api/metrics')
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def api_metrics():
    """
    Retorna métricas agregadas de la base de datos en formato JSON
    para los gráficos de Chart.js.
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

    # Contratos por Tipo
    contratos_data = db.session.query(
        Contrato.tipo_contrato,
        func.sum(Contrato.monto_final)
    ).group_by(Contrato.tipo_contrato).all()

    monto_contratos = {tipo: float(monto) for tipo, monto in contratos_data if monto is not None}

    # Propiedades por Agente
    agente_rol = Rol.query.filter_by(nombre_rol='Agente').first()
    admin_rol = Rol.query.filter_by(nombre_rol='Administrador').first()

    agentes_data = db.session.query(
        Usuario.nombre_completo,
        func.count(Propiedad.id)
    ).join(Propiedad, Propiedad.agente_id == Usuario.id)\
     .group_by(Usuario.nombre_completo).all()

    propiedades_por_agente = {nombre: count for nombre, count in agentes_data}

    # Visitas por estado
    visitas_estado_data = db.session.query(
        Visita.estado_visita,
        func.count(Visita.id)
    ).group_by(Visita.estado_visita).all()

    visitas_por_estado = {estado: count for estado, count in visitas_estado_data}

    return jsonify({
        'tipos': distribucion_tipos,
        'estados': distribucion_estados,
        'transacciones': monto_contratos,
        'agentes': propiedades_por_agente,
        'visitas_estado': visitas_por_estado
    })
