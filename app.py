from flask import Flask, jsonify, render_template, request, redirect, session, url_for
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from flask_migrate import Migrate


app = Flask(__name__)

app.config['SECRET_KEY'] = 'proyecto_inventario'

USER_BD = 'postgres'
PASS_BD = 'admin'
SERVER_BD = 'localhost'
PORT_BD = '5432'
NAME_DB = 'inventario'

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{USER_BD}:{PASS_BD}@{SERVER_BD}:{PORT_BD}/{NAME_DB}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modelo de datos usuarios
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)   

    productos = db.relationship('Producto', backref='usuario', lazy=True)
    ventas = db.relationship('Venta', backref='usuario', lazy=True)    

    def __repr__(self):
        return (f"<Id : {self.id}, Nombre: {self.nombre}, Password: {self.password}>")


# Modelo de datos Producto
class Producto(db.Model):
    __tablename__ = 'productos'
    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(db.String(50), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(db.String(100), nullable=False)
    precio: Mapped[float] = mapped_column(nullable=False)
    categoria: Mapped[str] = mapped_column(db.String(50), nullable=False)
    cantidad: Mapped[int] = mapped_column(nullable=False)


    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    def __repr__(self):
        return (f"<Id : {self.id}, Nombre: {self.nombre}, Precio: {self.precio}, "
                f"Categoria: {self.categoria}, Cantidad: {self.cantidad}>")
    

# Modelo de Ventas
class Venta(db.Model):
    __tablename__ = 'ventas'
    id: Mapped[int] = mapped_column(primary_key=True)
    codigo_producto: Mapped[str] = mapped_column(db.String(50), nullable=False) 
    nombre_producto: Mapped[str] = mapped_column(db.String(100), nullable=False)
    cantidad_vendida: Mapped[int] = mapped_column(nullable=False)
    precio_producto : Mapped[float] = mapped_column(nullable=False)
    valor_total: Mapped[float] = mapped_column(nullable=False)
    precio_final: Mapped[float] = mapped_column(nullable=False)

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    def __repr__(self):
        return (f"<Id : {self.id}, Codigo_producto: {self.codigo_producto}, Nombre_producto: {self.nombre_producto}, "
                f"Cantidad_vendida: {self.cantidad_vendida}, Precio_producto: {self.precio_producto}, "
                f"Valor_total: {self.valor_total}, Precio_final: {self.precio_final}>")

    

# Modelo de Detalles de Venta
class DetalleVenta(db.Model):
    __tablename__ = 'detalle_ventas'
    id: Mapped[int] = mapped_column(primary_key=True)   
    venta_id: Mapped[int] = mapped_column(db.ForeignKey('ventas.id'), nullable=False)
    producto_codigo: Mapped[str] = mapped_column(db.String(50), nullable=False)
    cantidad: Mapped[int] = mapped_column(nullable=False)   
    precio_final: Mapped[float] = mapped_column(nullable=False)

    def __repr__(self):
        return (f"<Id : {self.id}, Venta_id: {self.venta_id}, Producto_codigo: {self.producto_codigo}, "
                f"Cantidad: {self.cantidad}, Precio_final: {self.precio_final}>")
    
#Modelo Historial de Ventas
class HistorialVenta(db.Model):
    __tablename__ = 'historial_ventas'
    id: Mapped[int] = mapped_column(primary_key=True)   
    total = db.Column(db.Float)
    efectivo = db.Column(db.Float)
    cambio = db.Column(db.Float)    
    fecha = db.Column(db.String(20))
    hora = db.Column(db.String(20))
    
    def __repr__(self):
        return (f"<Id : {self.id}, Venta_id: {self.venta_id}, Fecha: {self.fecha}, Hora: {self.hora}>")



with app.app_context():
    db.create_all()

app.secret_key = 'div'

@app.route('/')
@app.route('/registrarse', methods=['GET', 'POST'])
def registrarse():
    print("🔥 ESTE ES MI APP REAL")
    if request.method == 'POST':
        nombre = request.form['nombre']
        password = request.form['password']
        confirm = request.form['confirm']

        # Validación contraseñas
        if password != confirm:
            return render_template('registrarse.html', error="Las contraseñas no coinciden")
        else:
            # usuario ya existe?
            usuario_existente = Usuario.query.filter_by(nombre=nombre).first()
            if usuario_existente:
                return render_template('registrarse.html', error="El usuario ya existe")
       
        # Guardar usuario en la base de datos
        nuevo_usuario = Usuario(nombre=nombre, password=password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        print(f"Usuario registrado: {nombre}")

        return redirect(url_for('inicio'))
    
    return render_template('registrarse.html')

@app.route('/inicio', methods=['GET', 'POST'])
def inicio():
    if request.method == 'POST':
        nombre = request.form['nombre']
        password = request.form['password']

        usuario = Usuario.query.filter_by(nombre=nombre, password=password).first()
        if usuario:
            session['usuario'] = nombre
            session['usuario_id'] = usuario.id
            return redirect(url_for('bienvenida'))

        return render_template('inicio.html', error='Usuario o contraseña incorrectos')

    return render_template('inicio.html')


@app.route('/bienvenida')
def bienvenida():
    if 'usuario' in session:
        return render_template('bienvenida.html', nombre=session['usuario'])
    return redirect(url_for('inicio'))

@app.route('/inventario', methods=['GET', 'POST'])
def inventario():
    if 'usuario' not in session:
        return redirect(url_for('inicio'))
    
    session.setdefault('productos', [])
    
    if request.method == 'POST':
        codigo = request.form['codigo_producto']
        nombre = request.form['nombre_producto']
        precio = float(request.form['precio_producto'])
        categoria = request.form['categoria_producto'].strip().lower()
        cantidad = int(request.form['cantidad_producto'])
        
        nuevo_producto = Producto(codigo=codigo, nombre=nombre, precio=precio, categoria=categoria, cantidad=cantidad, usuario_id=session['usuario_id'])
        db.session.add(nuevo_producto)
        db.session.commit()
        
        return redirect(url_for('inventario'))

    productos = Producto.query.filter_by(usuario_id=session['usuario_id']).all()
    fecha = datetime.now().strftime("%d/%m/%Y")
    return render_template('Inventario.html', productos=productos, fecha=fecha, nombre=session['usuario'])
    
    return redirect(url_for('inicio'))

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if 'usuario' not in session:
        return redirect(url_for('inicio'))
    
    producto = Producto.query.get_or_404(id)
    
    if request.method == 'POST':
        # Manejo de JSON desde la modal
        if request.is_json:
            data = request.get_json()
            producto.codigo = data.get('codigo_producto')
            producto.nombre = data.get('nombre_producto')
            producto.precio = float(data.get('precio_producto'))
            producto.categoria = data.get('categoria_producto', '').strip().lower()
            producto.cantidad = int(data.get('cantidad_producto'))
            db.session.commit()
            return {'success': True, 'message': 'Producto actualizado'}
        # Manejo de form data tradicional
        else:
            producto.nombre = request.form['nombre_producto']
            producto.precio = float(request.form['precio_producto'])
            producto.categoria = request.form['categoria_producto'].strip().lower()
            producto.cantidad = int(request.form['cantidad_producto'])
            db.session.commit()
            return redirect(url_for('inventario'))
    
    fecha = datetime.now().strftime("%d/%m/%Y")
    return render_template('edit_product.html', producto=producto, fecha=fecha, nombre=session['usuario'])

@app.route('/get_product/<int:id>', methods=['GET'])
def get_product(id):
    if 'usuario' not in session:
        return {'error': 'No autorizado'}, 401
    
    producto = Producto.query.get_or_404(id)
    return {
        'id': producto.id,
        'codigo': producto.codigo,
        'nombre': producto.nombre,
        'precio': producto.precio,
        'categoria': producto.categoria,
        'cantidad': producto.cantidad
    }

@app.route('/delete_product/<int:id>', methods=['POST'])
def delete_product(id):
    if 'usuario' not in session:
        return redirect(url_for('inicio'))
    
    producto = Producto.query.get_or_404(id)
    try:
        db.session.delete(producto)
        db.session.commit()
        return redirect(url_for('inventario'))
    except Exception as e:
        db.session.rollback()
        # Podrías agregar un mensaje de error, pero por ahora redirigir
        return redirect(url_for('inventario'))
    
@app.route('/buscar_producto', methods=['GET'])
def buscar_producto():
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    search = request.args.get('search', '').strip()
    
    if not search:
        return jsonify({'productos': []})
    
    # Buscar por código o nombre
    productos = Producto.query.filter(
        Producto.usuario_id == session['usuario_id'],
        (
            Producto.codigo.ilike(f'%{search}%') | 
            Producto.nombre.ilike(f'%{search}%')
        )
    ).all()
    
    resultado = []
    for producto in productos:
        resultado.append({
            'id': producto.id,
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'precio': producto.precio,
            'categoria': producto.categoria,
            'cantidad': producto.cantidad
        })
    
    return jsonify({'productos': resultado})

@app.route('/venta_add', methods=['POST'])
def venta_add():
    
    if 'usuario' not in session:
        return jsonify({'success': False, 'error': 'No autorizado'}), 401

    try:
        data = request.get_json() or {}

        print("DATA:", data)

        codigo = str(data.get('codigo', '')).strip()
        cantidad_raw = data.get('cantidad')

        if not codigo:
            return jsonify({'success': False, 'error': 'Código requerido'}), 400

        try:
            cantidad = int(cantidad_raw)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Cantidad inválida'}), 400

        if cantidad <= 0:
            return jsonify({'success': False, 'error': 'Cantidad debe ser mayor a 0'}), 400

        producto = Producto.query.filter_by(codigo=codigo).first()

        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404

        if cantidad > producto.cantidad:
            return jsonify({
                'success': False,
                'error': f'Stock insuficiente. Disponible: {producto.cantidad}'
            }), 400

        producto.cantidad -= cantidad

        valor_total = cantidad * producto.precio

        nueva_venta = Venta(
            codigo_producto=producto.codigo,
            nombre_producto=producto.nombre,
            cantidad_vendida=cantidad,
            precio_producto=producto.precio,
            valor_total=valor_total,
            precio_final=valor_total,
            usuario_id=session['usuario_id']
        )

        db.session.add(nueva_venta)
        db.session.commit()

        low_stock = Producto.query.filter(Producto.cantidad <= 3).all()

        return jsonify({
            'success': True,
            'producto': {
                'codigo': producto.codigo,
                'nombre': producto.nombre,
                'cantidad': producto.cantidad,
                'precio': producto.precio
            },
            'low_stock': [
                {'codigo': p.codigo, 'nombre': p.nombre, 'cantidad': p.cantidad}
                for p in low_stock
            ]
        })

    except Exception as e:
        db.session.rollback()
        print("ERROR REAL:", e)
        import traceback
        traceback.print_exc()

        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500
    

@app.route('/venta', methods=['GET', 'POST'])
def venta():
    if 'usuario' not in session:
        return redirect(url_for('inicio'))
    
    fecha = datetime.now().strftime("%d/%m/%Y")
    hora = datetime.now().strftime("%H:%M:%S")
    try:
        low_stock_items = [
            {'codigo': prod.codigo, 'nombre': prod.nombre, 'cantidad': prod.cantidad}
            for prod in Producto.query.filter(Producto.cantidad <= 3).all()
        ]
    except Exception as e:
        print(f"Error al consultar productos de bajo stock: {e}")
        low_stock_items = []
    
    return render_template('Venta.html', fecha=fecha, hora=hora, nombre=session['usuario'], low_stock=low_stock_items)

@app.route('/test')
def test():
    return "TEST OK"
    
@app.route('/guardar_factura', methods=['POST', 'GET'])
def guardar_factura():

    data = request.get_json()

    total = data.get('total')
    efectivo = data.get('efectivo')
    cambio = data.get('cambio')

    nueva_factura = HistorialVenta(
        total=total,
        efectivo=efectivo,
        cambio=cambio,
        fecha=datetime.now().strftime("%d/%m/%Y"),
        hora=datetime.now().strftime("%H:%M:%S")
    )

    db.session.add(nueva_factura)
    db.session.commit()

    return jsonify({'success': True})

@app.route('/historial_ventas')
def historial_ventas():
    if 'usuario' not in session:
        return redirect(url_for('inicio'))
    
    fecha = datetime.now().strftime("%d/%m/%Y")
    hora = datetime.now().strftime("%H:%M:%S")
    ventas = HistorialVenta.query.all()

    return render_template('historial.html', ventas=ventas, fecha=fecha, hora=hora, nombre=session['usuario'])


if __name__ == '__main__':
    app.run(debug=True, port=5001)