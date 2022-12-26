from flask import Flask, request, render_template, url_for, flash, redirect, session, send_from_directory
import sqlite3
from flask_session import Session
from forms import RegistrationForm, LoginForm, DeliveryRange, ItemDetails, TransporterForm
from werkzeug.utils import secure_filename
from flask_paginate import Pagination, get_page_parameter
import os

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app = Flask('g')
app.config['SECRET_KEY'] = 'flask303'

app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, r'media\profile_pics')
app.config['STATIC_IMAGES'] = 'C:\\Users\\rg22060\\Desktop\\Django\\flask_basics\\flask_quickport365\\static\\'
Session(app)

print(app.root_path)
# connection = sqlite3.connect('database.db')
# connection.execute('create table users (username text, email text,
# password text)') connection.close()
# con.execute('create table itemdetails ( id INTEGER PRIMARY KEY AUTOINCREMENT ,
# name text, weight text, ' 'date text, ' 'receiver text, receiver_phone text)')
# con.execute('create table orderdetails
# (id INTEGER PRIMARY KEY AUTOINCREMENT, user text, itemname text, itemweight text,' 'date text,
# receiver text, receiver_phone text, service text, price text, delivery_address text)')
# con.commit()
# with sqlite3.connect('database.db') as con:
#   con.execute('alter table orderdetails add destinationpin text')
#   con.commit()
# with sqlite3.connect('database.db') as con:
#   data = con.execute('select * from orderdetails')
#   print(data.description)

'creating super user'
# with sqlite3.connect('database.db') as con:
#     # con.execute('alter table users add superuser int default 0')
#     con.execute('insert into users (username,email,password,superuser) values(?,?,?,?)', ('ravi', 'r@gmail.com',
#     '1234', True))

'creating transporter table'
# with sqlite3.connect('database.db') as con:
#     con.execute('create table transporter (id INTEGER PRIMARY KEY AUTOINCREMENT, username text, email text, '
#                 'phoneno text, vehiclename text, vehicleno text, drivinglicense text )')


@app.route('/base', methods=['GET', 'POST'])
def base():
    user = None
    superuser = None
    if session.get('user'):
        user = session['user']
    if session.get('superuser'):
        session['superuser'] = True
        superuser = session['superuser']
    return render_template('base.html', user=user, superuser=superuser)


@app.route('/bookings')
def user_bookings():
    superuser = False
    if session.get('user'):
        user = session['user']
    else:
        flash('Login to continue')
        return redirect('/login')
    with sqlite3.connect('database.db') as con:
        con.row_factory = sqlite3.Row
        cur = con.execute('select * from orderdetails where user=?', (user,))
        rows = cur.fetchall()
    return render_template('bookings.html', rows=rows, total=len(rows), superuser=superuser)


@app.route('/', methods=['GET', 'POST'])
def home():
    form = DeliveryRange()
    if request.method == 'POST':
        if session.get('user'):
            if form.validate_on_submit():
                session['pincodes'] = request.form
                return redirect('/item_details')
        else:
            flash('Please login to continue')
            return redirect('/login')
    if request.method == 'GET':
        book = request.args.get('book')
        user = session.get('user')
        superuser = session.get('superuser')
        return render_template('home.html', form=form, user=user, superuser=superuser, book=book)


@app.route('/item_details', methods=['GET', 'POST'])
def item_details():
    form = ItemDetails()
    if request.method == "POST":
        name = request.form['name']
        weight = request.form['weight']
        date = request.form['date']
        receiver = request.form['receiver']
        receiver_phone = request.form['receiver_phone']
        session['item_details'] = request.form
        with sqlite3.connect('database.db') as con:
            con.execute('insert into itemdetails (name,weight,date,receiver,receiver_phone) values (?,?,?,?,?)',
                        (name, weight, date, receiver, receiver_phone))
        return redirect('/services')
    return render_template('item_details.html', form=form)


@app.route('/services')
def services():
    if request.method == 'GET':
        service = request.args.get('service')
        session['service'] = service
        if service == 'Standard':
            session['price'] = 300
            return render_template('services.html', price=300, days=3)
        elif service == 'Premium':
            session['price'] = 800
            return render_template('services.html', price=800, days=1)
        else:
            return render_template('services.html')


@app.route('/address', methods=['POST', 'GET'])
def address():
    if request.method == 'POST':
        session['daddress'] = request.form
        return redirect('/summary')
    return render_template('address.html')


@app.route('/summary')
def summary():
    price = 300
    item_details = session['item_details']
    service = session['service']
    daddress = session.get('daddress')
    return render_template('summary.html', price=price, item_details=item_details, service=service, daddress=daddress)


@app.route('/success')
def success():
    user = session.get('user')
    name = session['item_details']['name']
    weight = session['item_details']['weight']
    date = session['item_details']['date']
    receiver = session['item_details']['receiver']
    receiver_phone = session['item_details']['receiver_phone']
    service = session['service']
    price = session['price']
    opin = session['pincodes']['origin_pincode']
    dpin = session['pincodes']['destination_pincode']
    daddress = ''

    for i in session['daddress']:
        daddress += session['daddress'][i] + ','

    with sqlite3.connect('database.db') as con:
        con.execute('insert into orderdetails (user, itemname, itemweight, date, receiver, receiver_phone, service, '
                    'price, '
                    'delivery_address,originpin,destinationpin) values(?,?,?,?,?,?,?,?,?,?,?)',
                    (user, name, weight, date, receiver, receiver_phone, service, price, daddress, opin, dpin))
    return render_template('success.html')


@app.route('/orders_list')
def orders_list():
    with sqlite3.connect('database.db') as con:
        con.row_factory = sqlite3.Row
        cur = con.execute('select * from orderdetails')
        rows = cur.fetchall()
        page = request.args.get(get_page_parameter(), type=int, default=1)
        pagination = Pagination(page=page, total=len(rows), record_name=rows)
        for i in rows:
            print(i)
    superuser = session.get('superuser')
    return render_template('orders_list.html', rows=rows, total=len(rows), superuser=superuser, pagination=pagination)


@app.route('/cancel/<int:id>', methods=('GET', 'POST'))
def cancel_order(id):
    if request.method == 'POST':
        with sqlite3.connect('database.db') as con:
            con.execute('delete from orderdetails where id=?', (id,))
            con.commit()
            return redirect('/bookings')
    else:
        return render_template('cancel_order.html', id=id)


@app.route('/contact')
def contact():
    superuser = False
    return render_template('contact.html', superuser=superuser)


@app.route('/about')
def about_us():
    return render_template('about.html')


@app.route('/complaints')
def complaints():
    superuser = session.get('superuser')
    return render_template('complaints.html', superuser=superuser)


@app.route('/profile', methods=(['GET', 'POST']))
def profile():
    user = session.get('user')
    pic = 0
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files.get('file')
            print(file.filename)
            file.filename = f'{user}_pic.jpg'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            pic = 1
    with sqlite3.connect('database.db') as con:
        cur = con.execute('select * from users where username=?', (user,))
        orders = con.execute('select * from orderdetails where user=?', (user,))
        row = cur.fetchone()
    return render_template('profile.html', user=user, pic=pic, row=row, orders=len(orders.fetchall()))


@app.route('/media/<path:filename>')
def media(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename+'_pic.jpg',
        as_attachment=True
    )


@app.route('/list_items')
def list_items():
    with sqlite3.connect('database.db') as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute('select * from itemdetails')
        row = cur.fetchall()
    print(row)
    return render_template('list_items.html', row=row)


@app.route('/edit_item/<int:id>', methods=(['GET', 'POST']))
def edit_item(id):
    if request.method == 'POST':
        name = request.form.get('name')
        weight = request.form.get('weight')
        date = request.form.get('date')
        receiver_ph = request.form.get('receiver_ph')
        with sqlite3.connect('database.db') as con:
            con.execute('update itemdetails set name=?,weight=?,date=?,receiver_phone=? where id=?',
                        (name, weight, date, receiver_ph, id))
            con.commit()
            return redirect('/list_items')
    with sqlite3.connect('database.db') as con:
        var = con.execute('select * from itemdetails where id=?', (id,))
        for i in var:
            record = i
    name, weight, date, receiver_ph = record[1], record[2], record[3], record[5]
    return render_template('edit_item.html', record=record, name=name, weight=weight, date=date,
                           receiver_ph=receiver_ph)


@app.route('/delete_item/<int:id>')
def delete_item(id):
    with sqlite3.connect('database.db') as con:
        con.execute('delete from itemdetails where id=?', (id,))
        con.commit()
    return redirect('/list_items')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            print(request.form['username'])
            print(request.form)
            un = request.form['username']
            email = request.form['email']
            paswd = request.form['password']
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute('insert into users (username,email,password) values (?,?,?)', (un, email, paswd))
                con.commit()
            flash('signup successful')
            return redirect('/')
    return render_template('register.html', form=form)


@app.route('/login', methods=(['POST', 'GET']))
def login():
    form = LoginForm()
    user = session.get('user')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        con = sqlite3.connect('database.db')
        users = con.execute('select * from users')
        for i in users.fetchall():
            if i[0] == username and i[3] == 1:
                print(i)
                session['superuser'] = True
            if i[0] == username and i[2] == password:
                flash('logged in successfully')
                session['user'] = username
                return redirect('/')
        else:
            flash('wrong credentials')
            return render_template('login.html', form=form)
    return render_template('login.html', form=form, user=user)


@app.route('/logout')
def logout():
    if session.get('user'):
        session['user'] = None
        session['superuser'] = False
        flash('logged out successfully')
        return redirect('/')
    else:
        flash('not login yet')
        return redirect('/')


@app.route('/users')
def user_list():
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute('select * from users')

    rows = cur.fetchall()
    print(rows)
    return render_template('users.html', rows=rows)


@app.route('/transporters')
def transporters():
    superuser = session.get('superuser')
    with sqlite3.connect('database.db') as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute('select * from transporter')
        row = cur.fetchall()
    return render_template('transporters.html', row=row, superuser=superuser)


@app.route('/addtransporter', methods=(['POST', 'GET']))
def add_transporter():
    form = TransporterForm()
    superuser = session.get('superuser')
    if request.method == 'POST':
        user = request.form['username']
        email = request.form['email']
        ph = request.form['phone_no']
        with sqlite3.connect('database.db') as con:
            con.execute('insert into transporter(username,email,phoneno) values(?,?,?)', (user, email, ph))
    return render_template('add_transporter.html', form=form, superuser=superuser)


if __name__ == '__main__':
    app.run(debug=True)
