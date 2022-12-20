from flask import Flask, request, render_template, url_for, flash, redirect, sessions
import sqlite3
from flask_session import Session
from forms import RegistrationForm, LoginForm, DeliveryRange, ItemDetails

app = Flask(__name__)
app.config['SECRET_KEY'] = 'flask303'

# connection = sqlite3.connect('database.db')
# connection.execute('create table users (username text, email text, password text)')
# connection.close()
# con.execute('create table itemdetails ( id INTEGER PRIMARY KEY AUTOINCREMENT ,name text, weight text, '
#             'date text, '
#             'receiver text, receiver_phone text)')
# con.commit()


@app.route('/', methods=['GET', 'POST'])
def home():
    form = DeliveryRange()
    if request.method == 'POST':
        print(request.form)
        if form.validate_on_submit():
            return redirect('/item_details')
    return render_template('home.html', form=form)


@app.route('/item_details', methods=['GET', 'POST'])
def item_details():
    form = ItemDetails()
    if request.method == "POST":
        print(request.form)
        name = request.form['name']
        weight = request.form['weight']
        date = request.form['date']
        receiver = request.form['receiver']
        receiver_phone = request.form['receiver_phone']
        with sqlite3.connect('database.db') as con:
            con.execute('insert into itemdetails (name,weight,date,receiver,receiver_phone) values (?,?,?,?,?)',
                        (name, weight, date, receiver, receiver_phone))
        return redirect('/services')
    return render_template('item_details.html', form=form)


@app.route('/services')
def services():
    if request.method == 'GET':
        service = request.args.get('service')
        if service == 'Standard':
            return render_template('services.html', price=300, days=3)
        elif service == 'Premium':
            return render_template('services.html', price=800, days=1)
        else:
            return render_template('services.html')


@app.route('/address')
def address():
    return render_template('address.html')


@app.route('/list_items')
def list_items():
    with sqlite3.connect('database.db') as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute('select * from itemdetails')
        row = cur.fetchall()
    print(row)
    return render_template('list_items.html', row=row)


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
                cur.execute('insert into users (username,email,password) values (?,?,?)',(un,email,paswd))
                con.commit()
            flash('signup successful')
            return redirect('/')
    return render_template('register.html', form=form)


@app.route('/login', methods=(['POST', 'GET']))
def login():
    form = LoginForm()
    print('yes')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        con = sqlite3.connect('database.db')
        users = con.execute('select * from users')
        for i in users.fetchall():
            if i[0] == username and i[2] == password:
                flash('logged in successfully')
                return redirect('/')
        else:
            flash('wrong credentials')
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)


@app.route('/users')
def user_list():
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute('select * from users')

    rows = cur.fetchall()
    print(rows)
    return render_template('users.html', rows=rows)


if __name__ == '__main__':
    app.run(debug=True)
