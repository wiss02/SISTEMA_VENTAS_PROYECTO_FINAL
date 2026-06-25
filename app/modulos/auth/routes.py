from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, Usuario, Rol
from functools import wraps

bp = Blueprint('auth', __name__)

def roles_permitidos(roles):
    """
    Decorador para restringir el acceso a vistas según el rol del usuario (nombre_rol).
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debes iniciar sesión para acceder a esta página.', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.rol.nombre_rol not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('propiedades.list_propiedades'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        contrasena = request.form.get('contrasena')
        
        usuario = Usuario.query.filter_by(username=username).first()
        if usuario and usuario.check_password(contrasena):
            login_user(usuario)
            flash(f'¡Bienvenido de nuevo, {usuario.nombre_completo}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('propiedades.list_propiedades'))
        else:
            flash('Nombre de usuario o contraseña incorrectos.', 'danger')
            
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('propiedades.list_propiedades'))
        
    roles = Rol.query.all()
    
    if request.method == 'POST':
        username = request.form.get('username')
        nombre_completo = request.form.get('nombre_completo')
        correo = request.form.get('correo')
        contrasena = request.form.get('contrasena')
        rol_id = request.form.get('rol_id')
        
        if not username or not nombre_completo or not correo or not contrasena or not rol_id:
            flash('Todos los campos son obligatorios.', 'danger')
            return redirect(url_for('auth.register'))
            
        usuario_existente = Usuario.query.filter((Usuario.username == username) | (Usuario.correo == correo)).first()
        if usuario_existente:
            flash('El nombre de usuario o el correo ya están registrados.', 'danger')
            return redirect(url_for('auth.register'))
            
        nuevo_usuario = Usuario(
            username=username, 
            nombre_completo=nombre_completo,
            correo=correo, 
            rol_id=int(rol_id)
        )
        nuevo_usuario.set_password(contrasena)
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash('Registro completado con éxito. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', roles=roles)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('auth.login'))
