# =========
# Imports
# =========
from flask import Flask, render_template, request, redirect, url_for, flash,\
    jsonify, make_response, session as login_session, abort, g
from functools import wraps
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from catalog_db_user import Base, Catalog, Items, User
import random, string, httplib2, json, requests, os
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from flask_httpauth import HTTPBasicAuth
from config import ProductionConfig
auth = HTTPBasicAuth()

# ================
# Flask instance
# ================
app = Flask(__name__)

# config
app.config.from_object('config.ProductionConfig')


# ==========================================
# GConnect CLIENT_ID and Facebook App ID
# ==========================================
CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
fb_app_id = json.loads(
    open('fb_client_secrets.json', 'r').read())['web']['app_id']


# connect to database
if os.environ.get('APP_LOCATION') == 'heroku':
    engine = create_engine(os.environ['DATABASE_URL'])
else:
    engine = create_engine('sqlite:///catalogappwithuserslogin.db')

Base.metadata.bind = engine
# create session
DBSession = sessionmaker(bind=engine)
session = DBSession()


# login decorator 
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'username' in login_session:
           return f(*args, **kwargs)     
        else:    
            flash('You need to login in first!')
            return redirect(url_for('showLogin'))
    return wrap        


# login route
@app.route('/login', methods=['GET', 'POST'])
def showLogin():

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state

    if request.method == 'POST':
        user = verify_password(request.form['email'], request.form['password'])
        if user == "user not found":
            flash('User account doesnt exist please register or use third \
                                                party authentication!')
            return render_template('login.html', STATE=state,
                                   CLIENT_ID=CLIENT_ID, APP_ID=fb_app_id)
        if user == "wrong password":
            flash('Incorrect password')
            return render_template('login.html', STATE=state,
                                   CLIENT_ID=CLIENT_ID, APP_ID=fb_app_id)
        login_session['email'] = user.email
        login_session['username'] = user.username
        login_session['user_id'] = user.id
        login_session['provider'] = 'catalogApp'

        flash("You are logged in as {0}!".format(login_session['username']))
        return redirect(url_for('showCatalog'))
    else:
        return render_template('login.html', STATE=state,
                               CLIENT_ID=CLIENT_ID, APP_ID=fb_app_id)


# register a new user
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        login_session['email'] = request.form['email']
        login_session['username'] = request.form['username']
        user_id = getUserID(login_session['email'])
        print(user_id,"780987989807770797970979797979709")
        login_session['user_id'] = user_id
        if (user_id) is None:
            new_user = User(username=login_session['username'],
                            email=login_session['email'])
            new_user.hash_password(request.form['password'])
            session.add(new_user)
            session.commit()
            user = (session.query(User).filter_by(email=login_session['email'])
                    .one())
            login_session['user_id'] = user.id
            login_session['provider'] = 'catalogApp'
            flash("You are now logged in as {0}!".
                  format(login_session['username']))
            return redirect(url_for('showCatalog'))
        else:
            flash("{0} is already registered, plesae login!".
                  format(login_session['email']))
            return redirect(url_for('showLogin'))
    return render_template('registration.html')


# verify password
@auth.verify_password
def verify_password(email, password):
    print("Looking for user %s" % email)
    user = session.query(User).filter_by(email=email).first()
    if not user:
        print("User not found")
        return "user not found"
    elif not user.verify_password(password):
        print("Unable to verify password")
        return "wrong password"
    else:
        g.user = user
        return user


# login via google authentication
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

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
    gplus_id = credentials.id_token['sub']

    if result['user_id'] != gplus_id:
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

    # check if the user is already logged into the system
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')

    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user '
                                 'is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Use google+ API to more Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # check if the user exists if not create a new one.
    user_id = getUserID(login_session['email'])
    if (user_id) is None:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h2>Welcome, '
    output += login_session['username']+' '
    output += '!</h2>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 100px; height: 100px;border-radius: '\
        '50px;-webkit-border-radius: 50px;-moz-border-radius: 50px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")

    return output


# disconnect google authentication
@app.route('/gdisconnect')
def gdisconnect():

    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % access_token)

    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':

        response = make_response(json.dumps('Successfully disconnected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke '
                                            'token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# login via facebook authentication
@app.route('/fbconnect', methods=['POST'])
def fbconnect():

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?grant_type='
           'fb_exchange_token&client_id=%s&client_secret=%s'
           '&fb_exchange_token=%s' % (app_id, app_secret, access_token))

    h = httplib2.Http()
    result = h.request(url, 'GET')[1].decode('utf-8')
  
    data = json.loads(result)

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.9/me"
    '''
        Due to the formatting for the result from the server token
        exchange we have to split the token first on commas and select the
        first index which gives us the key : value for the server
        access token then we split it on colons to pull out the actual
        token value and replace the remaining quotes with nothing so
        that it can be used directly in the graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = ('https://graph.facebook.com/v2.9/me?access_token=%s'
           '&fields=name,id,email' % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1].decode('utf-8')

    data = json.loads(result)

    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = ('https://graph.facebook.com/v2.8/me/picture?access_token=%s'
           '&redirect=0&height=200&width=200' % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h2>Welcome, '
    output += login_session['username']

    output += '!</h2>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 100px; height: 100px;border-radius:' \
              ' 50px;-webkit-border-radius: 50px;-moz-border-radius: 50px;">'

    flash("Now logged in as %s" % login_session['username'])
    return output


# disconnect facebook authentication
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = ('https://graph.facebook.com/%s/permissions?access_token=%s % '
           '(facebook_id, access_token)')
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():

    if 'provider' in login_session:
        if login_session['provider'] == 'catalogApp':
            del login_session['username']
            del login_session['email']
            del login_session['provider']
            flash("You have successfully been logged out.")
            return redirect(url_for('showCatalog'))

        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']

        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']

        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalog'))


# create new user
@app.route('/createuser')
def createUser(login_session):
    new_user = User(username=login_session['username'],
                    picture=login_session['picture'],
                    email=login_session['email'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# get userinfo
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# get user id
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# show catalog and latest items
@app.route('/')
@app.route('/catalog')
def showCatalog():

    catalogs = session.query(Catalog).all()
    items = session.query(Items).order_by(desc(Items.create_date))[0:6]

    if 'username' not in login_session:
        return render_template('publiccatalogs.html',
                               catalog=catalogs, item=items)
    else:
        return render_template('catalogs.html',
                               catalog=catalogs, item=items)


# show items belonging to catalog
@app.route('/catalog/<string:catalog>/items')
def showCatalogItems(catalog):

    catalogs = session.query(Catalog).filter_by(name=catalog).first()
    catalogall = session.query(Catalog).all()
    items = session.query(Items).filter_by(catalog_id=catalogs.id)
    return render_template('catalogsItem.html', catalogall=catalogall,
                           catalogs=catalogs, item=items)


# show description of the item
@app.route('/catalog/<string:catalog>/<string:item>')
def showItemDescription(catalog, item):

    items = session.query(Items).filter_by(name=item).first()
    if 'username' in login_session:
        creatorID = getUserID(login_session['email'])

    if 'username' not in login_session or creatorID != items.user_id:
        return render_template('publicitemdescription.html', item=items)
    else:
        return render_template('itemdescription.html', item=items)


# add item to the catalog
@app.route('/catalog/item/new', methods=['GET', 'POST'])
@login_required
def addItem():
    '''if 'username' not in login_session:
        flash('please login to add item!')
        return redirect(url_for('showLogin'))'''

    if request.method == 'POST':

        user_id = getUserID(login_session['email'])
        print(user_id)
        catalogs = session.query(Catalog).filter_by(
                                    name=request.form['category']).one()
        newItem = Items(name=request.form['name'],
                        description=request.form['description'],
                        catalog_id=catalogs.id,
                        user_id=user_id)
        session.add(newItem)
        session.commit()

        flash('{0} item added!'.format(newItem.name))
        return redirect(url_for('showCatalog'))
    else:
        return render_template('additem.html')


# edit a catalog item
@app.route('/catalog/<string:item>/edit', methods=['GET', 'POST'])
@login_required
def editItem(item):

    edititem = session.query(Items).filter_by(name=item).first()

    catalogs = (session.query(Catalog).filter_by(id=edititem.catalog_id).
                first())

    '''if 'username' not in login_session:
        flash('Please login to edit item!')
        return redirect(url_for('showLogin'))'''

    if login_session['user_id'] != edititem.user_id:
        return "<script>function myFunction(){alert('you ae not authorized" \
               " to edit this item')}</script><body onload='myFunction()'>"

    if request.method == 'POST':

        catalogs = session.query(Catalog).filter_by(
                        name=request.form['category']).one()

        edititem.name = request.form['name']
        edititem.description = request.form['description']
        edititem.catalog_id = catalogs.id
        session.add(edititem)
        session.commit()
        flash('{0} Item edited!'.format(edititem.name)) 

        return redirect(url_for('showCatalog'))
    else:
        return render_template('editItem.html',
                               item=edititem, catalog=catalogs)


# delete a catalog item
@app.route('/catalog/<string:item>/delete', methods=['GET', 'POST'])
@login_required
def deleteItem(item):

    deleteitem = session.query(Items).filter_by(name=item).first()

    '''if 'username' not in login_session:
        flash('Please login to delete item!')
        return redirect(url_for('showLogin'))'''

    if login_session['user_id'] != deleteitem.user_id:
        return "<script>function myFunction(){alert('you ae not authorized " \
               "to delete this item')}</script><body onload='myFunction()'>"

    if request.method == 'POST':
        session.delete(deleteitem)
        session.commit()
        flash('{} item deleted!'.format(deleteitem.name))
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deleteitem.html', deleteitem=deleteitem)


# JSON APIs to view catalog Information
@app.route('/catalog/<string:catalog>/items/JSON')
def catalogItemJSON(catalog):
    catalogs = session.query(Catalog).filter_by(name=catalog).one()
    items = session.query(Items).filter_by(catalog_id=catalogs.id).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/catalog/<string:catalog>/items/<string:item>/JSON')
def ItemJSON(catalog, item):
    Item = session.query(Items).filter_by(name=item).first()
    return jsonify(Items=Item.serialize)


@app.route('/catalog/JSON')
def catalogJSON():
    catalog = session.query(Catalog).all()
    return jsonify(catalogs=[c.serialize for c in catalog])


@app.route('/items/JSON')
def itemsJSON():
    item = session.query(Items).all()
    return jsonify(Items=[i.serialize for i in item])


if __name__ == '__main__':
    if os.environ.get('APP_LOCATION') == 'heroku':
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    else:
        app.run(host='0.0.0.0', port=8001)
