import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


DATABASEURI = "postgresql://aa4761:753658@34.73.36.248:5432/project1" # Modify this with your own credentials you received from Joseph!
engine = create_engine(DATABASEURI)

# Global Variables
customer_preferences = None
RESTAURANT = ""
restaurant_preferences = None
si_customer_name = ""
su_customer_name = ""
su_billing_info = ""
su_customer_address = ""
su_customer_ph = ""

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

@app.route('/another')
def another():
  return render_template("another.html")

def getCaloriesByFoodName(foodName):
  return getCaloriesByFoodId(getFoodIdByName(foodName))

def getCaloriesByFoodId(foodId):
  QUERY = """
  SELECT SUM(ingredient.calories * foodingredients.quantity) as calories
  FROM foodingredients
  natural join ingredient
  where foodingredients.foodid = foodIdAnchor
  group by foodingredients.foodid;
  """
  QUERY = QUERY.replace('foodIdAnchor', str(foodId)).replace('\n','')
  cursor = g.conn.execute(QUERY)
  ans = ""
  for result in cursor:
    ans = result['calories']  
  cursor.close()
  print("calories",ans)
  return ans  


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

def getOwnerIdByName(name):
  cursor = g.conn.execute("SELECT userid as id FROM users natural join owner WHERE username=%s", name)
  ans = ""
  for result in cursor:
    ans = result['id']  
  cursor.close()
  print("owner", name,ans)
  return ans

def getUserIdByName(name):
  cursor = g.conn.execute("SELECT userid as id FROM users WHERE username=%s", name)
  ans = ""
  for result in cursor:
    ans = result['id']  
  cursor.close()
  print("customer", name,ans)
  return ans

@app.errorhandler(500)
def special_exception_handler(error):
  context = dict(error_message = "Error Occoured")
  return render_template("error.html", **context)

@app.errorhandler(400)
def special_exception_handlers(error):
  context = dict(error_message = "Error Occoured")
  return render_template("error.html", **context)

@app.errorhandler(404)
def special_exception_handlerx(error):
  context = dict(error_message = "Error Occoured")
  return render_template("error.html", **context)

@app.route('/restaurant/add_review', methods=['POST'])
def add_review():
  g.conn.execute('INSERT INTO dinesat(userid,restaurantid) VALUES (%s, %s)', getCustomerIdByName(si_customer_name), getRestaurantIdByName(RESTAURANT))
  g.conn.execute('INSERT INTO review(userid,restaurantid,reviewtext) VALUES (%s, %s, %s)', getCustomerIdByName(si_customer_name), getRestaurantIdByName(RESTAURANT), request.form['review'])
  return restaurant()

@app.route('/restaurant/add_reservation', methods=['POST'])
def create_reservation():
  DATE = request.form['reservation_date']
  TIME = request.form['reservation_time']
  date_time = request.form['reservation_date'] + request.form['reservation_time']
  custId = getCustomerIdByName(si_customer_name)
  restId = getRestaurantIdByName(RESTAURANT)
  guests = request.form['guests']
  g.conn.execute('INSERT INTO reservation(userid, restaurantid, reservationtime, guests) VALUES (%s, %s, %s, %s)', custId, restId, date_time, guests)
  
  reservation_details = [si_customer_name, RESTAURANT, DATE, TIME]
  context = dict(reservation_data = reservation_details)
  return render_template("reservation.html", **context)


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
  restId = getRestaurantIdByName(request.form['rname'])
  foodId = getFoodIdByName(request.form['fname'])
  price = request.form['fprice']
  print(restId, foodId, price)
  QUERY = "DELETE FROM menuitem WHERE foodid=foodIdAnchor and restaurantId=restaurantIdAnchor"
  QUERY = QUERY.replace('foodIdAnchor', str(foodId)).replace('restaurantIdAnchor',str(restId)).replace('\n','')
  g.conn.execute(QUERY)
  print("Inside owner delete")
  return owner()

@app.route('/owner/add', methods=['POST'])
def owner_add():
  print("Inside owner add")
  restId = getRestaurantIdByName(request.form['rname'])
  foodId = getFoodIdByName(request.form['fname'])
  price = request.form['fprice']
  print(restId, foodId, price)
  QUERY = "INSERT INTO menuitem(foodid, restaurantId, price) VALUES (foodIdAnchor, restaurantIdAnchor, priceAnchor)"
  QUERY = QUERY.replace('foodIdAnchor', str(foodId)).replace('restaurantIdAnchor',str(restId)).replace('priceAnchor', str(price)).replace('\n','')
  g.conn.execute(QUERY)
  print("Inside owner add")
  return owner()

@app.route('/owner', methods=['POST'])
def owner():
  global si_owner_name
  login_message = ""
  if 'si_owner_name' in request.form:
    si_owner_name = request.form['si_owner_name']
    if not getOwnerIdByName(si_owner_name):
      print("There is no such user")
      login_message = "Invalid user, please login with correct username"
      context = dict(login_message = login_message)
      return render_template("login.html", **context)

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
  context = dict(food_data = food, login_message = login_message)
  return render_template("owner.html", **context)

def deleteOrdersByUserId(userId):
  orderId = getOrdersByUserId(userId)
  g.conn.execute("DELETE FROM orders WHERE orderid = %s", orderId)
  print("Deleted")
  return getOrdersByUserId(userId)  

@app.route('/order', methods=['POST'])
def order():
  
  custId = str(getCustomerIdByName(si_customer_name))
  cursor = g.conn.execute("""SELECT foodname, price, name as restaurantname, quantity
                    FROM orderitem
                    natural join orders
                    natural join menuitem
                    natural join food
                    join restaurant on restaurant.restaurantid = menuitem.restaurantid
                    WHERE orders.userid = \'"""+custId+"""\';""")
  orderitems = []
  for result in cursor:
    orderitems.append([result['foodname'],str(result['price']),result['restaurantname'],str(result['quantity'])])  
  cursor.close()
  
  cursor = g.conn.execute("""SELECT price*quantity as amount
                    FROM orderitem
                    natural join orders
                    natural join menuitem
                    natural join food
                    join restaurant on restaurant.restaurantid = menuitem.restaurantid
                    WHERE orders.userid = \'"""+custId+"""\';""")

  total_bill = sum([result['amount'] for result in cursor])
  cursor.close()

  context = dict(order_data = orderitems, total_bill = total_bill)
  deleteOrdersByUserId(custId)
  return render_template("order.html", **context)

def getOrdersByUserId(userid):
  cursor = g.conn.execute("SELECT orderid as id FROM orders where userid=%s", userid)
  ans = None
  for result in cursor:
    ans = result['id']  
  cursor.close()
  print("orders", ans)
  return ans

def createOrderForUser(userId):
  g.conn.execute("INSERT INTO orders(userid) VALUES (%s)", userId)
  print("Inserted")
  return getOrdersByUserId(userId)

def createOrderItem(foodId, orderId, restaurantId, qty):
  print("Inserted orderItem ", foodId, orderId, restaurantId, qty)
  g.conn.execute("INSERT INTO orderitem(foodid, orderid, restaurantid, quantity) VALUES (%s,%s,%s,%s)", foodId, orderId, restaurantId, qty)
  print("Inserted orderItem")
  return

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  global customer_preferences
  global restaurant_preferences
  user_id = getCustomerIdByName(si_customer_name)
  orderId = getOrdersByUserId(user_id)
  if not orderId:
    orderId = createOrderForUser(user_id)
  qty = request.form['quantity']
  print('qty : ', qty)
  if not qty:
    qty = 1
  values = request.form['add_action_button']
  print('add_action_button = ', request.form['add_action_button'])
  split_values = values.split("$")
  print(split_values)
  foodId = getFoodIdByName(split_values[0])
  restaurantId = getRestaurantIdByName(split_values[1])
  if not restaurantId:
    restaurantId = getRestaurantIdByName(RESTAURANT)
    createOrderItem(foodId, orderId, restaurantId, qty)
    context = restaurant_preferences 
    return render_template("restaurant.html", **context)


  createOrderItem(foodId, orderId, restaurantId, qty)
  return render_template("food.html", **customer_preferences)


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
  )
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
  )
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
  )
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
  )
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
  )
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


def buidSearchQuery(cusine, restaurant, foodName, tag, tag1, tag2):
  queryList = []
  if cusine:
    queryList.append(getFoodByCusine(cusine)) 
  if restaurant:
    queryList.append(getFoodByRestaurant(restaurant))
  if foodName:
    queryList.append(getFoodByName(foodName))
  if tag:
    queryList.append(getFoodByTag(tag))
  if tag1:
    queryList.append(getFoodByTag(tag1))
  if tag2:
    queryList.append(getFoodByTag(tag2))        
  return " INTERSECT ".join(queryList)

@app.route('/food', methods=['POST'])
def food():
  global customer_preferences
  if request.form:
    #print(buidSearchQuery(request.form['cuisine'], request.form['rname'], request.form['dname'], request.form['dietTag']).replace('\n',''))
    cursor = g.conn.execute(buidSearchQuery(request.form['cuisine'], request.form['rname'], request.form['dname'], request.form['dietTag'], request.form['dietTag1'], request.form['dietTag2']).replace('\n','')) ## TODO: Add new query here!
    # cursor = g.conn.execute()
    foods = []
    for result in cursor:
      foods.append([result['fname'], result['fdesc'],result['price'],result['rname'],getCaloriesByFoodName(result['fname'])])
    cursor.close()

    context = dict(food_data = foods)
    customer_preferences = context
    return render_template("food.html", **context)
  return render_template("food.html", **customer_preferences)

@app.route('/restaurant', methods=['POST'])
def restaurant():
  global RESTAURANT
  global restaurant_preferences
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
  restaurant_preferences = context
  return render_template("restaurant.html", **context)

@app.route('/customer', methods=['POST'])
def customer():
  login_message = ""
  global si_customer_name
  global su_customer_name
  global su_billing_info
  global su_customer_address
  global su_customer_ph

  if 'si_customer_name' in request.form:
    print("Trying to Sign in")
    si_customer_name = request.form['si_customer_name']

    if not getCustomerIdByName(si_customer_name):
      print("There is no such user")
      login_message = "Invalid user, please login with correct username"
      context = dict(login_message = login_message)
      return render_template("login.html", **context)
    

  if 'su_customer_name' in request.form:
    print("Trying to Sign up")
    su_customer_name = request.form['su_customer_name']
    su_billing_info = request.form['su_billing_info']
    su_customer_address = request.form['su_customer_address']
    su_customer_ph = request.form['su_customer_ph']

    g.conn.execute('INSERT INTO users(username,address, phonenumber) VALUES (%s, %s, %s)', su_customer_name, su_customer_address, su_customer_ph)
    g.conn.execute('INSERT INTO customer(userid, billinginfo) VALUES (%s,%s)', getUserIdByName(su_customer_name), su_billing_info)

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

  context = dict(tag_data = tagnames, cuisine_data = cuisinenames, restaurant_data = restaurantnames, si_customer_name = si_customer_name, login_message = login_message)

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
