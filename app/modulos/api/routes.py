from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required
from sqlalchemy import func
from app.models import db, Propiedad, TipoPropiedad, EstadoPropiedad, Propietario, Contrato, Visita, Usuario
from app.modulos.auth.routes import roles_permitidos

bp = Blueprint('api', __name__)


@bp.route('/')
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def api_docs():
    """Página de documentación de la API REST."""
    return render_template('api/docs.html')


@bp.route('/propiedades')
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def api_propiedades():
    """Endpoint GET: Lista de propiedades en JSON con filtros opcionales."""
    tipo_id = request.args.get('tipo_id', type=int)
    estado_id = request.args.get('estado_id', type=int)
    accion = request.args.get('accion', type=str)

    query = Propiedad.query

    if tipo_id:
        query = query.filter(Propiedad.tipo_id == tipo_id)
    if estado_id:
        query = query.filter(Propiedad.estado_id == estado_id)
    if accion:
        query = query.filter(Propiedad.accion == accion)

    propiedades = query.order_by(Propiedad.fecha_registro.desc()).all()

    resultado = []
    for p in propiedades:
        resultado.append({
            'id': p.id,
            'titulo': p.titulo,
            'descripcion': p.descripcion,
            'precio': p.precio,
            'direccion': p.direccion,
            'accion': p.accion,
            'tipo': p.tipo_propiedad.nombre_tipo,
            'estado': p.estado.nombre_estado,
            'propietario': p.propietario.nombre,
            'agente': p.agente.nombre_completo,
            'fecha_registro': p.fecha_registro.isoformat()
        })

    return jsonify({
        'total': len(resultado),
        'propiedades': resultado
    })


@bp.route('/propiedades/<int:id>')
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def api_propiedad_detalle(id):
    """Endpoint GET: Detalle de una propiedad específica en JSON."""
    p = Propiedad.query.get_or_404(id)

    return jsonify({
        'id': p.id,
        'titulo': p.titulo,
        'descripcion': p.descripcion,
        'precio': p.precio,
        'direccion': p.direccion,
        'accion': p.accion,
        'tipo': p.tipo_propiedad.nombre_tipo,
        'estado': p.estado.nombre_estado,
        'propietario': {
            'nombre': p.propietario.nombre,
            'telefono': p.propietario.telefono,
            'correo': p.propietario.correo,
            'ci_nit': p.propietario.ci_nit
        },
        'agente': {
            'nombre': p.agente.nombre_completo,
            'correo': p.agente.correo
        },
        'fecha_registro': p.fecha_registro.isoformat(),
        'total_visitas': len(p.visitas),
        'total_contratos': len(p.contratos)
    })


@bp.route('/estadisticas')
@login_required
@roles_permitidos(['Administrador', 'Agente'])
def api_estadisticas():
    """Endpoint GET: Resumen estadístico completo del sistema."""
    total_propiedades = db.session.query(func.count(Propiedad.id)).scalar() or 0
    total_contratos = db.session.query(func.count(Contrato.id)).scalar() or 0
    total_visitas = db.session.query(func.count(Visita.id)).scalar() or 0
    total_propietarios = db.session.query(func.count(Propietario.id)).scalar() or 0
    suma_contratos = db.session.query(func.sum(Contrato.monto_final)).scalar() or 0
    precio_promedio = db.session.query(func.avg(Propiedad.precio)).scalar() or 0

    return jsonify({
        'resumen': {
            'total_propiedades': total_propiedades,
            'total_contratos': total_contratos,
            'total_visitas': total_visitas,
            'total_propietarios': total_propietarios,
            'suma_contratos': float(suma_contratos),
            'precio_promedio': round(float(precio_promedio), 2)
        }
    })
