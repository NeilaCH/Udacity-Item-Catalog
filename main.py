# - *- coding: utf- 8 - *-
from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash, make_response, session as login_session
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, HCategory, Item
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from pprint import pprint
import httplib2
import requests
import random
import string
import json

app = Flask(__name__)

# Load the Google Sign-in API Client ID.
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Create a database session.
engine = create_engine(
    'sqlite:///homecatalog.db', connect_args={'check_same_thread': False})

# Bind the above engine to a session.
Session = sessionmaker(bind=engine)

# Create a Session object.
session = Session()


# Redirect to login page.
@app.route('/')
@app.route('/catalog/')
@app.route('/catalog/items/')
def home():
    """Route to the homepage."""

    categories = session.query(HCategory).all()
    items = session.query(Item).all()
    return render_template(
        'main.html', categories=categories, items=items)


# Create anti-forgery state token
@app.route('/login/')
def login():
    """Route to the login page to create anti-forgery state token."""

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template("login.html", STATE=state)


# Connect to the Google Sign-in oAuth method.
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

# Verify that the access token is used for the intended user.
    google_id = credentials.id_token['sub']
    if result['user_id'] != google_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_google_id = login_session.get('google_id')
    if stored_access_token is not None and google_id == stored_google_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['google_id'] = google_id

    # Get user info.
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if the user exists. If it doesn't, make a new one.
    user_id = get_user_id(data["email"])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    # Show a welcome screen upon successful login.
    output = ''
    output += '<h3>Welcome, '
    output += login_session['username']
    output += ' to Home Decor Catalog!</h3>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 150px; height: 150px; '
    output += 'border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    flash("You are logged in as %s!" % login_session['username'])
    print("Done!")
    return output


# Google Account Disconnect.
def gdisconnect():
    """Disconnect the Google account of the current logged-in user."""

    # Disconnect tthe current logged-in user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Loging out the currently connected user.
@app.route('/logout')
def logout():
    """Loging out the currently connected user."""

    if 'username' in login_session:
        gdisconnect()
        del login_session['google_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        flash("You are successfully logged out!")
        return redirect(url_for('home'))
    else:
        flash("You were not logged in!")
        return redirect(url_for('home'))


# Create a new user.
def create_user(login_session):
    """Crate new user.

    Argument:
    login_session (dict): The login session.
    """

    new_user = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture']
    )
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def get_user_info(user_id):
    """Get user information by ID.

    Argument:
        user_id (int): The user ID.

    Returns:
        The user's details.
    """

    user = session.query(User).filter_by(id=user_id).one()
    return user


def get_user_id(email):
    """Get user ID by email.

    Argument:
        email (str) : the email of the user.
    """

    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Add new category.
@app.route("/catalog/category/new/", methods=['GET', 'POST'])
def add_category():
    """Add new category."""

    if 'username' not in login_session:
        flash("Please you have to log in first.")
        return redirect(url_for('login'))
    elif request.method == 'POST':
        if request.form['new-category-name'] == '':
            flash('This field is required.')
            return redirect(url_for('home'))

        category = session.query(HCategory).\
            filter_by(name=request.form['new-category-name']).first()
        if category is not None:
            flash('This category already exists.')
            return redirect(url_for('add_category'))

        new_category = HCategory(
            name=request.form['new-category-name'],
            user_id=login_session['user_id'])
        session.add(new_category)
        session.commit()
        flash('New category %s successfully created!' % new_category.name)
        return redirect(url_for('home'))
    else:
        return render_template('new-category.html')


# Create new item by category.
@app.route("/catalog/item/new/", methods=['GET', 'POST'])
def add_item():
    """Create new item by category."""

    if 'username' not in login_session:
        flash("Please log in to continue.")
        return redirect(url_for('login'))
    elif request.method == 'POST':
        # Check if the item already exists in the database.
        item = session.query(Item).filter_by(name=request.form['name']).first()
        if item:
            if item.name == request.form['name']:
                flash('This item already exists!')
                return redirect(url_for("add_item"))
        new_item = Item(
            name=request.form['name'],
            category_id=request.form['category'],
            description=request.form['description'],
            user_id=login_session['user_id']
        )
        session.add(new_item)
        session.commit()
        flash('Item successfully created!')
        return redirect(url_for('home'))
    else:
        items = session.query(Item).\
                filter_by(user_id=login_session['user_id']).all()
        categories = session.query(HCategory).\
            filter_by(user_id=login_session['user_id']).all()
        return render_template(
            'new-item.html',
            items=items,
            categories=categories
        )


# Assign new item to Category ID.
@app.route("/catalog/category/<int:category_id>/item/new/",
           methods=['GET', 'POST'])
def add_item_by_category(category_id):
    """Assign new item to Category ID."""

    if 'username' not in login_session:
        flash("You have to login first !")
        return redirect(url_for('login'))
    elif request.method == 'POST':
        # Check if the item already exists.
        item = session.query(Item).filter_by(name=request.form['name']).first()
        if item:
            if item.name == request.form['name']:
                flash('This item already exists!')
                return redirect(url_for("add_item"))
        new_item = Item(
            name=request.form['name'],
            category_id=category_id,
            description=request.form['description'],
            user_id=login_session['user_id'])
        session.add(new_item)
        session.commit()
        flash('New item successfully created!')
        return redirect(url_for('show_items_in_category',
                                category_id=category_id))
    else:
        category = session.query(HCategory).filter_by(id=category_id).first()
        return render_template('new-item-2.html', category=category)


# Check if the category exists.
def exists_category(category_id):
    """Check if the category exists.

    It take as argument:
        category_id (int) : The Category ID.

    to return:
        A boolean vale to indicate if the category exists or not.
    """

    category = session.query(HCategory).filter_by(id=category_id).first()
    if category is not None:
        return True
    else:
        return False


# Check if the item exists.
def exists_item(item_id):
    """Check if the item exists in the database.
    It take as argument:
        item_id (int) : The item ID.
    to return:
        A boolean value to indicate if the item exists or not.
    """

    item = session.query(Item).filter_by(id=item_id).first()
    if item is not None:
        return True
    else:
        return False


# Show item by ID.
@app.route('/catalog/item/<int:item_id>/')
def view_item(item_id):
    """Show item by ID."""

    if exists_item(item_id):
        item = session.query(Item).filter_by(id=item_id).first()
        category = session.query(HCategory)\
            .filter_by(id=item.category_id).first()
        owner = session.query(User).filter_by(id=item.user_id).first()
        return render_template(
            "view-item.html",
            item=item,
            category=category,
            owner=owner
        )
    else:
        flash('We are sorry. We cannot process your request.')
        return redirect(url_for('home'))


# Edit existing items.
@app.route("/catalog/item/<int:item_id>/edit/", methods=['GET', 'POST'])
def edit_item(item_id):
    """Edit existing items."""

    if 'username' not in login_session:
        flash("Please you have to log in first.")
        return redirect(url_for('login'))

    if not exists_item(item_id):
        flash("We are sorry. We cannot process your request.")
        return redirect(url_for('home'))

    item = session.query(Item).filter_by(id=item_id).first()
    if login_session['user_id'] != item.user_id:
        flash("Please you have to log in first.")
        return redirect(url_for('home'))

    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['category']:
            item.category_id = request.form['category']
        session.add(item)
        session.commit()
        flash('Item successfully updated!')
        return redirect(url_for('edit_item', item_id=item_id))
    else:
        categories = session.query(HCategory).\
            filter_by(user_id=login_session['user_id']).all()
        return render_template(
            'update-item.html',
            item=item,
            categories=categories
        )


# Delete existing item.
@app.route("/catalog/item/<int:item_id>/delete/", methods=['GET', 'POST'])
def delete_item(item_id):
    """Delete existing item."""

    if 'username' not in login_session:
        flash("Please you have to log in first.")
        return redirect(url_for('login'))

    if not exists_item(item_id):
        flash("We are sorry. We cannot process your request.")
        return redirect(url_for('home'))

    item = session.query(Item).filter_by(id=item_id).first()
    if login_session['user_id'] != item.user_id:
        flash("Please you have to log in first.")
        return redirect(url_for('home'))

    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("Item successfully deleted!")
        return redirect(url_for('home'))
    else:
        return render_template('delete_item.html', item=item)


# Show item in its associated category.
@app.route('/catalog/category/<int:category_id>/items/')
def show_items_in_category(category_id):
    """Show item in its associated category"""

    if not exists_category(category_id):
        flash("We are sorry. We cannot process your request.")
        return redirect(url_for('home'))

    category = session.query(HCategory).filter_by(id=category_id).first()
    items = session.query(Item).filter_by(category_id=category.id).all()
    total = session.query(Item).filter_by(category_id=category.id).count()
    return render_template(
        'in_category.html',
        category=category,
        items=items,
        total=total)


# Edit categories.
@app.route('/catalog/category/<int:category_id>/edit/',
           methods=['GET', 'POST'])
def edit_category(category_id):

    category = session.query(HCategory).filter_by(id=category_id).first()

    if 'username' not in login_session:
        flash("Please you have to log in first.")
        return redirect(url_for('login'))

    if not exists_category(category_id):
        flash("We are sorry. This category dose not exist.")
        return redirect(url_for('home'))

    # If the  user does not have authorisation to edit the category.
    if login_session['user_id'] != category.user_id:
        flash("We are sorry. We cannot process your request.")
        return redirect(url_for('home'))

    if request.method == 'POST':
        if request.form['name']:
            category.name = request.form['name']
            session.add(category)
            session.commit()
            flash('Category successfully updated!')
            return redirect(url_for('show_items_in_category',
                                    category_id=category.id))
    else:
        return render_template('edit_category.html', category=category)


# Delete category.
@app.route('/catalog/category/<int:category_id>/delete/',
           methods=['GET', 'POST'])
def delete_category(category_id):
    """Delete category."""

    category = session.query(HCategory).filter_by(id=category_id).first()

    if 'username' not in login_session:
        flash("Please you have to log in first.")
        return redirect(url_for('login'))

    if not exists_category(category_id):
        flash("We are sorry.This category dose not exist.")
        return redirect(url_for('home'))

    # If the logged in user does not have authorisation to
    # edit the category, redirect to homepage.
    if login_session['user_id'] != category.user_id:
        flash("We are sorry. We cannot process your request.")
        return redirect(url_for('home'))

    if request.method == 'POST':
        session.delete(category)
        session.commit()
        flash("Category successfully deleted!")
        return redirect(url_for('home'))
    else:
        return render_template("delete_category.html", category=category)


# JSON Endpoints


# Return JSON of all the items in the Home Catalog.
@app.route('/api/v1/catalog.json')
def show_catalog_json():
    """Return JSON of all the items in the Home Catalog."""

    items = session.query(Item).order_by(Item.id.desc())
    return jsonify(catalog=[i.serialize for i in items])


# Return JSON of a requested item in the catalog.
@app.route(
    '/api/v1/categories/<int:category_id>/item/<int:item_id>/JSON')
def catalog_item_json(category_id, item_id):
    """Return JSON of a requested item in the catalog."""

    if exists_category(category_id) and exists_item(item_id):
        item = session.query(Item)\
               .filter_by(id=item_id, category_id=category_id).first()
        if item is not None:
            return jsonify(item=item.serialize)
        else:
            return jsonify(
                error='The requested item {} is not in the category {}.'
                .format(item_id, category_id))
    else:
        return jsonify(
            error='We are sorry. Item or category does not exist.')


# Return JSON of all the categories in the catalog.
@app.route('/api/v1/categories/JSON')
def categories_json():
    """Returns JSON of all the categories in the catalog."""

    categories = session.query(HCategory).all()
    return jsonify(categories=[i.serialize for i in categories])


if __name__ == "__main__":
    app.secret_key = '-??ȞGqJ??b=S??'
    app.run(host="0.0.0.0", port=8080, debug=True)
