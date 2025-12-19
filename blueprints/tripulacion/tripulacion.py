from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Tripulante 

bp = Blueprint('tripulacion', __name__, template_folder='templates')

# Roles de la tripulación (Definición global)
ROLES_TRIPULACION = ['Piloto', 'Copiloto', 'Jefe de Cabina', 'Auxiliar de Vuelo', 'Técnico'] 

# ----------------- 1. LISTAR TRIPULANTES -----------------
@bp.route('/')
@login_required
def listado_tripulacion():
    tripulacion_db = Tripulante.query.filter_by(baja_logica=False).all()
    return render_template('tripulacion_listado.html', tripulacion=tripulacion_db)

# ----------------- 2. CREAR TRIPULANTE -----------------
@bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear_tripulante():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        rol = request.form.get('rol')

        nuevo_tripulante = Tripulante(
            nombre=nombre, 
            apellido=apellido, 
            rol=rol
        )

        try:
            db.session.add(nuevo_tripulante)
            db.session.commit()
            flash('Tripulante creado con éxito.', 'success')
            return redirect(url_for('tripulacion.listado_tripulacion'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el tripulante: {e}', 'danger')
            return render_template('form_staff.html', roles=ROLES_TRIPULACION)
    return render_template('form_staff.html', 
                           roles=ROLES_TRIPULACION, 
                           tripulante=None,
                           modo_edicion=False)

# ----------------- 3. EDITAR TRIPULANTE -----------------
@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_tripulante(id):
    tripulante = Tripulante.query.get_or_404(id)
    if request.method == 'POST':
        tripulante.nombre = request.form.get('nombre')
        tripulante.apellido = request.form.get('apellido')
        tripulante.rol = request.form.get('rol')
        db.session.commit()
        flash('Datos actualizados correctamente.', 'success')
        
        return redirect(url_for('tripulacion.listado_tripulacion'))
    
    return render_template('form_staff.html', tripulante=tripulante, roles=ROLES_TRIPULACION)


# ----------------- 4. BAJA LÓGICA TRIPULANTE -----------------
@bp.route('/baja/<int:id>', methods=['POST'])
@login_required
def baja_logica_tripulante(id):
    tripulante = Tripulante.query.get_or_404(id)
    tripulante.baja_logica = True 
    db.session.commit()
    flash(f'Tripulante {tripulante.nombre} dado de baja.', 'warning')
    
    return redirect(url_for('tripulacion.listado_tripulacion'))