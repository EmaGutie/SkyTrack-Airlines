from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_user, logout_user

# No importamos Usuario porque no existe en tus modelos
bp = Blueprint('auth', __name__)

# Creamos una clase simple "falsa" solo para que Flask-Login no de error
class UserSimulado:
    def __init__(self, id):
        self.id = id
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
    def get_id(self):
        return str(self.id)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Simulación: Si escribe algo, lo dejamos pasar
        if username == "admin" and password == "1234":
            user = UserSimulado(1)
            login_user(user)
            flash('¡Bienvenido al sistema SkyTrack!', 'success')
            return redirect(url_for('vuelos.listado_vuelos_frontend'))
        else:
            flash('Usuario o contraseña incorrectos (Prueba admin/1234)', 'danger')
            
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('auth.login'))