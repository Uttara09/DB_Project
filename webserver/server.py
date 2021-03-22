
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
# DATABASEURI = "postgresql://user:password@34.73.36.248/project1" # Modify this with your own credentials you received from Joseph!
DATABASEURI = "postgresql://aa4761:753658@34.73.36.248:5432/project1" # Modify this with your own credentials you received from Joseph!

#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. 
# This is only an example showing you how to run queries in your database using SQLAlchemy.
#

# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#

# @app.route('/')
# def index():
#   """
#   request is a special object that Flask provides to access web request information:

#   request.method:   "GET" or "POST"
#   request.form:     if the browser submitted a form, this contains the data in the form
#   request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

#   See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
#   """

#   # DEBUG: this is debugging code to see what request looks like
#   print(request.args)


#   #
#   # example of a database query
#   #
#   cursor = g.conn.execute("SELECT name FROM test")
#   names = []
#   for result in cursor:
#     names.append(result['name'])  # can also be accessed using result[0]
#   cursor.close()

#   #
#   # Flask uses Jinja templates, which is an extension to HTML where you can
#   # pass data to a template and dynamically generate HTML based on the data
#   # (you can think of it as simple PHP)
#   # documentation: https://realpython.com/primer-on-jinja-templating/
#   #
#   # You can see an example template in templates/index.html
#   #
#   # context are the variables that are passed to the template.
#   # for example, "data" key in the context variable defined below will be 
#   # accessible as a variable in index.html:
#   #
#   #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
#   #     <div>{{data}}</div>
#   #     
#   #     # creates a <div> tag for each element in data
#   #     # will print: 
#   #     #
#   #     #   <div>grace hopper</div>
#   #     #   <div>alan turing</div>
#   #     #   <div>ada lovelace</div>
#   #     #
#   #     {% for n in data %}
#   #     <div>{{n}}</div>
#   #     {% endfor %}
#   #
#   context = dict(data = names)


#   #
#   # render_template looks in the templates/ folder for files.
#   # for example, the below file reads template/index.html
#   #
#   return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
  return render_template("another.html")

def getFoodIdByName(foodName):
  QUERY = "SELECT foodid as id from food where foodname = 'foodAnchor'"
  QUERY = QUERY.replace('foodAnchor', foodName)
  print(QUERY)
  cursor = g.conn.execute(QUERY)
  ans = ""
  for result in cursor:
    ans = result['id']  
  cursor.close()
  print("food",ans)
  return ans

def getRestaurantIdByName(restName):
  QUERY = "SELECT restaurantid as id from restaurant where name = 'restAnchor'"
  QUERY = QUERY.replace('restAnchor', restName)
  print(QUERY)
  cursor = g.conn.execute(QUERY)
  ans = ""
  for result in cursor:
    ans = result['id']  
  cursor.close()
  print("restaurant",ans)
  return ans

def getCustomerIdByName(name):
  cursor = g.conn.execute("SELECT userid as id FROM users natural join customer WHERE username=%s", name)
  ans = ""
  for result in cursor:
    ans = result['id']  
  cursor.close()
  print("customer", name,ans)
  return ans

@app.route('/restaurant/add_review', methods=['POST'])
def add_review():
  print("Inside add_review!!!!!!!!")
  print('REVIEW : ', request.form['review'])
  print("RESTAURANT : ", RESTAURANT)
  print("si_customer_name : ", si_customer_name)

  ### get userid from name
  
  ### add entry in dinesat table
  g.conn.execute('INSERT INTO dinesat(userid,restaurantid) VALUES (%s, %s)', getCustomerIdByName(si_customer_name), getRestaurantIdByName(RESTAURANT))
  ### insert review to review table
  g.conn.execute('INSERT INTO review(userid,restaurantid,reviewtext) VALUES (%s, %s, %s)', getCustomerIdByName(si_customer_name), getRestaurantIdByName(RESTAURANT), request.form['review'])

  return restaurant()

@app.route('/owner/update', methods=['POST'])
def owner_update():
  restId = getRestaurantIdByName(request.form['rname'])
  foodId = getFoodIdByName(request.form['fname'])
  price = request.form['fprice']
  print(restId, foodId, price)
  QUERY = """
  UPDATE menuitem
  SET price=priceAnchor
  WHERE foodid=foodIdAnchor and restaurantId=restaurantIdAnchor;
  """
  QUERY = QUERY.replace('foodIdAnchor', str(foodId)).replace('restaurantIdAnchor',str(restId)).replace('priceAnchor', str(price)).replace('\n','')
  g.conn.execute(QUERY)
  print("Inside owner update")

  return owner()

@app.route('/owner/delete', methods=['POST'])
def owner_delete():
  print("Inside owner delete")
  fname = request.form['fname']
  rname = request.form['rname']
  fprice = request.form['fprice']
  print('fname : ', fname)

  return owner()

@app.route('/owner/add', methods=['POST'])
def owner_add():
  print("Inside owner add")
  return owner()

@app.route('/owner', methods=['POST'])
def owner():

  global si_owner_name
  if 'si_owner_name' in request.form:
    si_owner_name = request.form['si_owner_name']

  # get all food at this restaurant
  cursor = g.conn.execute("""SELECT restaurant.name as rname, food.foodname as fname, menuitem.price as price
  FROM restaurant
  natural join menuitem
  natural join food
  JOIN users on restaurant.userid = users.userid
  WHERE users.username = \'"""+si_owner_name+"""\';""")

  food = []
  for result in cursor:
    food.append([result['fname'],result['price'],result['rname']])  
  cursor.close()
  context = dict(food_data = food)
  return render_template("owner.html", **context)

@app.route('/order')
def order():
  print(request.form)
  for x in request.form:
    print(x)
  return render_template("order.html")

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')

def getFoodByCusine(cusine):
  CUSINE_SEARCH_QUERY = """SELECT food.foodname as fname, food.description as fdesc, restaurant.name as rname, menuitem.price as price
  FROM restaurant
  natural join menuitem
  natural join food
  join cuisine on food.cuisineid = cuisine.cuisineid
  WHERE cuisinename = \'cusineanchor\'"""
  return CUSINE_SEARCH_QUERY.replace("cusineanchor", cusine)

def getFoodByRestaurant(restaurant):
  RESTAURANT_SEARCH_QUERY = """SELECT food.foodname as fname, food.description as fdesc, restaurant.name as rname, menuitem.price as price
  FROM restaurant
  natural join menuitem
  natural join food
  WHERE restaurant.name LIKE \'%%restaurantAnchor%%\'"""
  return RESTAURANT_SEARCH_QUERY.replace("restaurantAnchor", restaurant)

def getFoodByName(foodName):
  FOOD_SEARCH_QUERY = """SELECT food.foodname as fname, food.description as fdesc, restaurant.name as rname, menuitem.price as price
  FROM restaurant
  natural join menuitem
  natural join food
  WHERE food.foodname LIKE \'%%foodAnchor%%\'"""
  return FOOD_SEARCH_QUERY.replace("foodAnchor", foodName)

def getGlutenFreeFood():
  QUERY = """
  SELECT food.foodname as fname, food.description as fdesc, restaurant.name as rname, menuitem.price as price
  FROM restaurant
  natural join menuitem
  natural join food
  WHERE food.foodid NOT IN (
  SELECT DISTINCT foodid
  FROM food
  natural join foodingredients
  join ingredient on foodingredients.ingredientid = ingredient.ingredientid
  WHERE ingredient.tagid IN (18)
  );
  """
  return QUERY

def getMeatFood():
  QUERY = """
  SELECT food.foodname as fname, food.description as fdesc, restaurant.name as rname, menuitem.price as price
  FROM restaurant
  natural join menuitem
  natural join food
  WHERE food.foodid IN (
  SELECT DISTINCT foodid
  FROM food
  natural join foodingredients
  join ingredient on foodingredients.ingredientid = ingredient.ingredientid
  WHERE ingredient.tagid IN (14, 16, 19, 20)  
  );
  """
  return QUERY

def getNutFreeFood():
  QUERY = """
  SELECT food.foodname as fname, food.description as fdesc, restaurant.name as rname, menuitem.price as price
  FROM restaurant
  natural join menuitem
  natural join food
  WHERE food.foodid NOT IN (
  SELECT DISTINCT foodid
  FROM food
  natural join foodingredients
  join ingredient on foodingredients.ingredientid = ingredient.ingredientid
  WHERE ingredient.tagid IN (17)  
  );
  """
  return QUERY

def getPescetarianFood():
  QUERY = """
  SELECT food.foodname as fname, food.description as fdesc, restaurant.name as rname, menuitem.price as price
  FROM restaurant
  natural join menuitem
  natural join food
  WHERE food.foodid NOT IN (
  SELECT DISTINCT foodid
  FROM food
  natural join foodingredients
  join ingredient on foodingredients.ingredientid = ingredient.ingredientid
  WHERE ingredient.tagid IN (14, 19, 16)   
  );
  """
  return QUERY

def getVegitarianFood():
  QUERY = """
  SELECT food.foodname as fname, food.description as fdesc, restaurant.name as rname, menuitem.price as price
  FROM restaurant
  natural join menuitem
  natural join food
  WHERE food.foodid NOT IN (
  SELECT DISTINCT foodid
  FROM food
  natural join foodingredients
  join ingredient on foodingredients.ingredientid = ingredient.ingredientid
  WHERE ingredient.tagid IN (14, 16, 19, 20)  
  );
  """
  return QUERY

def getVeganFood():
  QUERY = """
  SELECT food.foodname as fname, food.description as fdesc, restaurant.name as rname, menuitem.price as price
  FROM restaurant
  natural join menuitem
  natural join food
  WHERE food.foodid NOT IN (
  SELECT DISTINCT foodid
  FROM food
  natural join foodingredients
  join ingredient on foodingredients.ingredientid = ingredient.ingredientid
  WHERE ingredient.tagid IN (14, 15, 16, 19, 20)  
  );
  """
  return QUERY

def getFoodByTag(tag):
  if tag == 'vegan':
    return getVeganFood()
  if tag == 'vegetarian':
    return getVegitarianFood()
  if tag == 'gluten-free':
    return getGlutenFreeFood()
  if tag == 'nut-free':
    return getNutFreeFood()
  if tag == 'contains-meat':
    return getMeatFood()
  if tag == 'pescetarian':
    return getPescetarianFood()




def buidSearchQuery(cusine, restaurant, foodName, tag):
  queryList = []
  if cusine:
    queryList.append(getFoodByCusine(cusine)) 
  if restaurant:
    queryList.append(getFoodByRestaurant(restaurant))
  if foodName:
    queryList.append(getFoodByName(foodName))
  if tag:
    queryList.append(getFoodByTag(tag))
  return " INTERSECT ".join(queryList)

@app.route('/food', methods=['POST'])
def food():
  print(buidSearchQuery(request.form['cuisine'], request.form['rname'], request.form['dname'], request.form['dietTag']).replace('\n',''))
  cursor = g.conn.execute(buidSearchQuery(request.form['cuisine'], request.form['rname'], request.form['dname'], request.form['dietTag']).replace('\n','')) ## TODO: Add new query here!
  # cursor = g.conn.execute()
  foods = []
  for result in cursor:
    foods.append([result['fname'], result['fdesc'],result['price'],result['rname']])  
  cursor.close()

  context = dict(food_data = foods)
  return render_template("food.html", **context)


RESTAURANT = ""
@app.route('/restaurant', methods=['POST'])
def restaurant():
  global RESTAURANT
  if 'submit_restaurant_button' in request.form:    
    RESTAURANT = request.form['submit_restaurant_button']
  ## TODO: Add new block of code here with appropriate lists etc
  # print("HELLO")
  # print("RESTAURANT : ", RESTAURANT)

  cursor = g.conn.execute("""SELECT food.foodname as fname, food.description as fdesc, menuitem.price as price
                            FROM restaurant
                            natural join menuitem
                            natural join food
                            WHERE restaurant.name LIKE \'"""+RESTAURANT+"""\';""")
  restaurant_items = []
  for result in cursor:
    restaurant_items.append([result['fname'], result['fdesc'],result['price']])  # can also be accessed using result[0]
  cursor.close()

  cursor = g.conn.execute("""SELECT reviewtext
                            FROM review
                            join restaurant on review.restaurantid = restaurant.restaurantid
                            WHERE name = \'"""+RESTAURANT+"""\';""")
  restaurant_reviews = []
  for result in cursor:
    restaurant_reviews.append(result['reviewtext'])  # can also be accessed using result[0]
  cursor.close()
  print("HELLO")
  print(restaurant_reviews)

  context = dict(restaurant_items_data = restaurant_items, restaurant_reviews_data = restaurant_reviews)
  return render_template("restaurant.html", **context)
si_customer_name = ""
su_customer_name = ""
su_billing_info = ""
su_customer_address = ""
su_customer_ph = ""

@app.route('/customer', methods=['POST'])
def customer():
  
  global si_customer_name
  global su_customer_name
  global su_billing_info
  global su_customer_address
  global su_customer_ph

  if 'si_customer_name' in request.form:
    print("Trying to Sign in")
    si_customer_name = request.form['si_customer_name']
    ### TODO: Check if this customer doesn't exist
    ### TODO: Create an alert saying invalid customer name
    ### TODO: Redirect back to login page


  if 'su_customer_name' in request.form:
    print("Trying to Sign up")
    su_customer_name = request.form['su_customer_name']
    su_billing_info = request.form['su_billing_info']
    su_customer_address = request.form['su_customer_address']
    su_customer_ph = request.form['su_customer_ph']

    ### TODO: Add this customer to customer table

    ### render the login page again so customer can login manually
    return render_template("login.html")
    

  cursor = g.conn.execute("SELECT cuisinename FROM cuisine")
  cuisinenames = []
  for result in cursor:
    cuisinenames.append(result['cuisinename'])  # can also be accessed using result[0]
  cursor.close()

  cursor = g.conn.execute("SELECT tagname FROM tag")
  tagnames = []
  for result in cursor:
    tagnames.append(result['tagname'])  # can also be accessed using result[0]
  cursor.close()

  cursor = g.conn.execute("SELECT name FROM restaurant")
  restaurantnames = []
  for result in cursor:
    restaurantnames.append(result['name'])  # can also be accessed using result[0]
  cursor.close()


  context = dict(tag_data = tagnames, cuisine_data = cuisinenames, restaurant_data = restaurantnames, si_customer_name = si_customer_name)

  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("customer.html", **context)


@app.route('/')
def login():
  return render_template("login.html")

    

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
