from flask import Flask, render_template, request, redirect, url_for,flash
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['UPLOAD_FOLDER'] = 'static/image'

conn = sqlite3.connect('database.db', check_same_thread=False)

product_list = [
    {
        'id': '1',
        'title': 'night cream',
        'price': '20',
        'description': "Some quick example text to build on the card title and make up the bulk of the card's content.",
        'image': 'product1.jpg'
    },
    {
        'id': '2',
        'title': 'day cream',
        'price': '25',
        'description': "Some quick example text to build on the card title and make up the bulk of the card's content.",
        'image': 'product2.jpg'
    }
]


@app.route('/')
@app.route('/home')
def home():
    student_list = [
        {
            'id': '001',
            'name': 'dara',
            'gender': 'male',
            'GPA': '4.0',
        },
        {
            'id': '002',
            'name': 'rithy',
            'gender': 'male',
            'GPA': '3.0',
        }
    ]
    return render_template("index.html", student_list=student_list, module='home')


@app.get('/product')
def product():
    row = conn.execute("""SELECT * FROM product""")
    product = []
    for item in row:
        image = ''
        if item[6] == None:
            image = 'no_image'
        else:
            image = item[6]
        product.append(
            {
                'id': item[0],
                'title': item[1],
                'price': item[3],
                'category': item[4],
                'description': item[5],
                'image': image,
            }
        )
    return render_template('product.html', data=product, module='product')


@app.get('/product_detail')
def product_detail():
    product_id = request.args.get('id')
    current_product = []
    for item in product_list:
        if item['id'] == product_id:
            current_product = item

    return render_template('product_detail.html', current_product=current_product)


@app.get('/checkout')
def checkout():
    product_id = request.args.get('id')
    current_product = []
    for item in product_list:
        if item['id'] == product_id:
            current_product = item

    return render_template('checkout.html', current_product=current_product)


@app.post('/submit_order')
def submit_order():
    product_id = request.form.get('product_id')
    current_product = []
    for item in product_list:
        if item['id'] == product_id:
            current_product = item

    name = request.form.get('fullname')
    phone = request.form.get('phone')
    email = request.form.get('email')

    return current_product


@app.get('/about')
def about():
    return render_template("about.html", module='about')


@app.get('/contact')
def contact():
    return render_template("contact.html",  module='contact')


@app.get('/jinja')
def jinja():
    return render_template('jinja.html',  module='jinja')


@app.get('/add_product')
def add_product():
    return render_template('add_product.html',  module='add_product')


@app.post('/submit_new_product')
def submit_new_product():
    title = request.form.get('title')
    price = request.form.get('price')
    category = request.form.get('category')
    description = request.form.get('description')
    file = request.files['compress_file']
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    filename = timestamp + '.' + file.filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'product', filename))

    cropped_image_name = None
    if 'cropped_image' in request.files:
        cropped_image = request.files['cropped_image']
        cropped_image_name = timestamp + '.' + cropped_image.filename
        cropped_image.save(os.path.join(app.config['UPLOAD_FOLDER'], 'crop', cropped_image_name))
    else:
        flash('Cropped image upload failed', 'error')

    # Use parameterized query to prevent SQL injection
    cursor = conn.cursor()
    cursor.execute("INSERT INTO `product` (title, cost, price, category, description, image) VALUES (?, ?, ?, ?, ?, ?)",
                   (title, 0, price, category, description, filename))
    conn.commit()
    flash("Product created successfully", "success")
    return redirect(url_for('product'))


@app.get('/redirect_with_success')
def redirect_with_success():
    flash(f"Product created successfully", "success")
    return redirect(url_for('product'))


@app.get('/edit_product')
def edit_product():
    product_id = request.args.get('id')
    row = conn.execute("""SELECT * FROM product where id =?""", (product_id,))
    product = {}
    for item in row:
        image = ''
        if item[6] == None:
            image = 'no_image'
        else:
            image = item[6]
        product ={
                'id': item[0],
                'title': item[1],
                'cost': item[2],
                'price': item[3],
                'category': item[4],
                'description': item[5],
                'image': image,
            }
    return render_template('edit_product.html', product=product, module='add_product')


@app.post('/update')
def update():
    product_id = request.form.get('product_id')
    image_name = ''

    title = request.form.get('title')
    price = request.form.get('price')
    category = request.form.get('category')
    description = request.form.get('description')

    file = request.files['file']
    if file != "":
        file_path = os.path.join(app.config['UPLOAD_FOLDER'] + '/product/', file.filename)

    if not os.path.exists(file_path):
        file.save(file_path)
    file = conn.execute("""SELECT image FROM product where id =?""", (product_id,))
    for item in file:
        if item[0] is not None:
            image_name = item[0]
            file_path = os.path.join(app.config['UPLOAD_FOLDER'] + '/product/', image_name)
            if os.path.exists(file_path):
                os.remove(file_path)

    res = conn.execute(
        f"""UPDATE `product` SET title = '{title}', price = {price}, category = '{category}
            ', description = '{description}', image= '{file.filename}' where id ={product_id}""")
    conn.commit()
    flash(f"Product created successfully", "success")
    return redirect(url_for('product'))


@app.get('/product_destroy')
def product_destroy():
    product_id = request.args.get('id')
    image_name=''
    file = conn.execute("""SELECT image FROM product where id =?""", (product_id,))
    for item in file:
        image_name = item[0]
    file_path = os.path.join(app.config['UPLOAD_FOLDER'] + '/product/', image_name)
    if os.path.exists(file_path):
        os.remove(file_path)
    conn.execute("DELETE FROM product WHERE id = ?", (product_id,))
    conn.commit()
    flash(f"Product with id {product_id} has been deleted successfully", "success")
    return redirect(url_for('product'))


if __name__ == '__main__':
    app.run()
