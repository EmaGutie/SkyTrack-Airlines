from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_user, logout_user, current_user
from models import db, Usuario

# Creamos el Blueprint
bp = Blueprint('auth', __name__, template_folder='templates')

@bp.route('/register', methods=['GET', 'POST'])
def registro():
    """Endpoint para registrar nuevos usuarios (admin/operador)."""
    # NOTA: En un sistema real, solo el admin podría registrar usuarios.
    # Aquí lo hacemos accesible por POST para crear los usuarios de prueba.
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        rol = request.form.get('rol') # Debe ser 'admin' o 'operador'

        if not username or not password or rol not in ['admin', 'operador']:
            flash('Datos incompletos o rol inválido.', 'danger')
            return redirect(url_for('auth.register'))

        if Usuario.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe.', 'danger')
            return redirect(url_for('auth.register'))

        new_user = Usuario(username=username, rol=rol)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        flash(f'Usuario {username} ({rol}) registrado con éxito!', 'success')
        
        # Redirigir al login
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Endpoint para iniciar sesión."""
    if current_user.is_authenticated:
        return redirect(url_for('vuelos.listado_vuelos_frontend')) # Cambiar a la ruta principal
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Usuario.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user) # Inicia la sesión del usuario
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('vuelos.listado_vuelos_frontend')) # Redirige al listado principal
        else:
            flash('Usuario o contraseña inválidos.', 'danger')
            
    return render_template('login.html')

@bp.route('/logout')
def logout():
    """Endpoint para cerrar sesión."""
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('auth.login'))