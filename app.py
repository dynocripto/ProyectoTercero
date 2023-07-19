# , {{ current_user.Firstname }}
from flask import Flask, render_template, request, redirect, url_for, flash, Response, send_file
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required
from fpdf import FPDF

from config import config

# Models:
from models.ModelUser import ModelUser

# Entities:
from models.entities.User import User

app = Flask(__name__)

csrf = CSRFProtect()
db = MySQL(app)
login_manager_app = LoginManager(app)


@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # print(request.form['username'])
        # print(request.form['password'])
        user = User(0, request.form['username'], request.form['password'])
        logged_user = ModelUser.login(db, user)
        if logged_user != None:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for('home'))
            else:
                flash("Invalid password...")
                return render_template('auth/login.html')
        else:
            flash("User not found...")
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        cur = db.connection.cursor()
        # user_exist = cur.execute('SELECT username FROM user')
        # # if user_exist != username:
        cur.execute('INSERT INTO UserTable (UserName, Password, Firstname) VALUES (%s, %s, %s)', 
        (username, password, fullname))
        db.connection.commit()
        flash('Usuario creado con éxito')
        redirect(url_for('register'))
        # else:
        #     flash('Usuario ya existente')    
    return render_template('./auth/register.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    cur = db.connection.cursor()
    cur.execute('SELECT Firstname FROM UserTable')
    data = cur.fetchall()
    return render_template('./home.html', user = data)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/products', methods=['GET', 'POST'])
def products():
    cur = db.connection.cursor()
    cur.execute('SELECT * FROM DoctorTable')
    data = cur.fetchall()

    if request.method == 'POST':
        name = request.form['name']
        stock = request.form['stock']
        value = request.form['value']
        cur = db.connection.cursor()
        cur.execute('INSERT INTO products (name, stock, value) VALUES (%s, %s, %s)', 
        (name, stock, value))
        db.connection.commit()
        flash('Producto registrado con éxito')
        redirect(url_for('products'))

    return render_template('products.html', product = data)



def status_401(error):
    return redirect(url_for('login'))


def status_404(error):
    return render_template('404.html'), 404

# @app.route('/download/report/pdf')
# def download_report():
#     conn = None
#     cursor = None
#     try:
#         conn = db.connect()
	    
#         cursor = conn.cursor(db.cursors.DictCursor)
		
		
#         cursor.execute("SELECT * FROM products")
		
#         result = cursor.fetchall()
		
# 	    pdf = FPDF()
# 		pdf.add_page()
		
# 		page_width = pdf.w - 2 * pdf.l_margin
		
# 		pdf.set_font('Times','B',14.0) 
# 		pdf.cell(page_width, 0.0, 'Products Data', align='C')
# 		pdf.ln(10)

# 		pdf.set_font('Courier', '', 12)
		
# 		col_width = page_width/4
		
# 		pdf.ln(1)
		
# 		th = pdf.font_size
		
# 		for row in result:
# 			pdf.cell(col_width, th, str(row['prod_code']), border=1)
# 			pdf.cell(col_width, th, row['name'], border=1)
# 			pdf.cell(col_width, th, row['stock'], border=1)
# 			pdf.cell(col_width, th, row['value'], border=1)
# 			pdf.ln(th)
		
# 		pdf.ln(10)
		
# 		pdf.set_font('Times','',10.0) 
# 		pdf.cell(page_width, 0.0, '- end of report -', align='C')

# 	except Exception as e:
# 		print(e)
# 	finally:
# 		cursor.close() 
# 		conn.close()
#     return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition':'attachment;filename=products_report.pdf'})

if __name__ == '__main__':
    app.config.from_object(config['development'])
    #csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run()
