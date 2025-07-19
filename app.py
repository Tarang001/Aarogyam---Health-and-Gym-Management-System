# IMPORTING LIBRARIES AND MODULES FROM PYTHON
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request,jsonify, redirect, url_for,session
import bcrypt
import mysql.connector
from datetime import datetime
from flask_cors import CORS
from mysql.connector import Error


# Daily Progress Picture configuring folder and filetype
UPLOAD_FOLDER = 'static/progress_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

#  IMPORTING FUNCTIONS FROM OTHER FILES
from connection import connection
from youtubeApi import fetch_video
from sql_queries import target_muscles


# CREATING AN INSTANCE OF FLASK AND Youtube api
app = Flask(__name__)
app.secret_key = "samar_e_muqaatil"

# Daily Progress picture folder configuration
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# declaring the functions to be used after
def get_current_day():
  current_day = datetime.now().strftime('%A')
  return current_day

def joinDate():
  email = session.get('email')
  query = "Select Date_format(join_date, '%M %D, %Y') from person where email=%s"
  conn =connection()
  cursor = conn.cursor()
  cursor.execute(query,(email,))
  join_date = cursor.fetchone()[0]
  query = "Select Datediff(CURDATE(),join_date) from person where email=%s"
  cursor.execute(query,(email,))
  total_days = cursor.fetchone()[0]
  query ="select count(check_in_time) as total_present_days from user_attendance where member_id =%s"
  cursor.execute(query,(email,))
  present_days = cursor.fetchone()[0]
  query = 'select dob from person where email= %s'
  cursor.execute(query,(email,))
  dob = cursor.fetchone()[0]
  query = 'select disease from person where email= %s'
  cursor.execute(query,(email,))
  disease = cursor.fetchone()[0]
  
  return [join_date,total_days,present_days,dob,disease]

# Preparing my first function of pushing data from form to backend database of aiven
@app.route("/")
def landing_page():
    return render_template("index.html")

# SHOWING THE PLANS PAGE
@app.route("/plans")
def plans():
  return render_template("plans.html")

#SHOWING THE TAEKWONDO PAGE
@app.route("/taekwondo",methods = ["GET"])
def render_taekwondo():
  return render_template("taekwondo.html")

# Showing the success corner page comprising of the successfull people who excel their field through exercising
@app.route("/success_corner", methods=["GET"])
def render_page():
  return render_template("success_corner.html")

#Showing the meals page which would be having the diets for the users
@app.route("/meals", methods=["GET"])
def render_meals():
  return render_template("meals.html")

# Rendering the form page and taking the submissions and storing them into the table
@app.route("/forms", methods = ["POST","GET"])
def form_render():
  if(request.method == "GET"):
    if 'email' in session:
      return render_template("forms.html")
    else :
      return redirect(url_for('login'))
  elif(request.method=="POST"):
    name = request.form['name']
    email = request.form['email']
    mobile = request.form['mobile']
    dob = request.form['dob']
    height = request.form['height']
    weight = request.form['weight']
    address = request.form['address']
    plan = request.form['plan']
    disease = request.form['disease']

    try:
      conn = connection()
      cursor = conn.cursor()

      #Creating Table users if it don't exist
      cursor.execute("""CREATE TABLE IF NOT EXISTS person (
    name VARCHAR(100) NOT NULL,           -- Compulsory Name
    email VARCHAR(100) UNIQUE ,            -- Unique Email
    mobile VARCHAR(14) NOT NULL,   -- Compulsory Mobile Number (Assuming 15-digit max for international format)
    dob DATE NOT NULL,          -- Compulsory Date of Birth
    height DECIMAL(5,2),                  -- Height in cm (can handle up to 999.99 cm)
    weight DECIMAL(5,2),                  -- Weight in kg (can handle up to 999.99 kg)
    address TEXT NOT NULL,                -- Compulsory Address
    plan ENUM('Monthly', 'Quarterly', 'Yearly') NOT NULL, -- Plan (Dropdown options)
    disease VARCHAR(255) DEFAULT 'NA', -- Any chronic disease (NA if not)
    trainer varchar(32) NOT NULL, -- Trainer's Name
    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Automatic current join date
    FOREIGN KEY (email) REFERENCES users(email)
    ON UPDATE CASCADE
);
""")
      
      #CREATING QUERY FOR INSERTION
      query_insert = 'INSERT INTO person(name,email,mobile,dob,height,weight,address,plan,disease) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
      cursor.execute(query_insert,(name,email,mobile,dob,height,weight,address,plan,disease))
      conn.commit()
      cursor.close()
      conn.close()
      print('One insert query has been successfully executed')
      return redirect(url_for("payment"))
    
    except Error as e:
      return jsonify({'error': str(e)})
    
   
    
    
# SIGNUP FOR USERS/TRAINERS AND STORING DATA IN USERS TABLE IN THE DATABASE
@app.route("/signup", methods = ["POST","GET"])
def signup():
  if(request.method=="GET"):
    return render_template("signup.html")
  elif(request.method == "POST"):
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    hash_password = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
    hash_pass_str = hash_password.decode('utf-8')
    role = request.form['role']

    try:
      conn = connection()
      cursor = conn.cursor()

      cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        role varchar(15) NOT NULL DEFAULT 'user',
        created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
      )
      query_insert = 'INSERT INTO users(username, email, password, role) VALUES (%s,%s,%s,%s);'
      cursor.execute(query_insert,(username,email,hash_pass_str,role))
      
      for i in range(7):
        query = "INSERT INTO routine(member_id,week_day,gym_day)"
        cursor.execute(query,(email,i,i+1))
      conn.commit()
      cursor.close()
      conn.close()
      print('One insert query has been successfully executed')
      return render_template("login.html")
    
    except Error as e:
      return jsonify({'error': str(e)})


# LOGIN FOR USERS/TRAINERS/ADMIN AND VERIFYING DATA FROM THE DATA IN DATABASE
@app.route("/login", methods = ["POST","GET"])
def login():
  if (request.method== "GET"):
    return render_template("login.html")
  
  elif(request.method == "POST"):
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    conn = connection()
    cursor = conn.cursor()

    query = 'SELECT email, password, role FROM users WHERE email = %s AND role = %s '
    cursor.execute(query,(email,role))
    login_data = cursor.fetchone()
    if login_data:
      password_get= login_data[1]
      pass_final = password_get.encode('utf-8')
      if(bcrypt.checkpw(password.encode('utf-8'),pass_final)):
        session['email'] = email
        session['role'] = role
        if(session['role']=='user'):
          return render_template("user_after_login.html")
        elif session['role']=='admin':
          return redirect(url_for("admin_main_page"))
        elif session['role']=='trainer':
          return ("Ye trainer wala page hai")
      else:
        return(f'Incorrect password for {email}')
    else:
      return ("NO USER FOUND!!!")



# @app.route("/user_after_login",methods = ["POST","GET"])
# def user_after_login():
#   if(request.method=="GET"):
#     profile = get_user_profile()
#     weekly_plan = get_weekly_plan()
#     attendance_data = get_attendance_data()

#     # Render template and pass data to the frontend
#     return render_template('user_after_login.html',profile,weekly_plan,attendance_data)

@app.route("/logged_in_home")
def logged_in_home_render():
  return render_template("user_after_login.html")
@app.route("/logged_in_plans")
def logged_in_plans_render():
  return render_template("logged_in_plans.html")
@app.route("/logged_in_about")
def logged_in_about_render():
  return render_template("logged_in_about.html")

# ADMIN MAIN PAGE RENDERING AND FUNCTIONALITY
@app.route("/admin")
def admin_main_page():
  if session['role']=='admin':
    return render_template("admin_login.html")
  else:
    return ("You are not athorised for this page")
@app.route("/inventory")
def inventory():
  return ("bana raha hu")


@app.route("/logout")
def logout():
  session.clear()
  return render_template("index.html")
@app.route("/payment")
def payment():
  return("This is the place where you need to pay!!!")

@app.route("/exercises")
def exercise():
  conn = connection()
  cursor = conn.cursor()
  query1 = "select * from exercise"
  cursor.execute(query1)
  exercises = cursor.fetchall()
  url_got = [urls[3] for urls in exercises]  
  exercise_name = [name[1] for name in exercises]
  exercises = [exercise + (fetch_video(str(url)),) +(target_muscles(str(ex_name)),)  for exercise, url, ex_name in zip(exercises, url_got, exercise_name)]
  print(exercises[0])

  return render_template("exercise_corner.html", exercises = exercises)

@app.route("/admin/inventory")
def show_inventory():
  return render_template("admin_inventory.html")

@app.route('/member_id')
def get_current_member_id():
  memberId = session.get('email')
  return jsonify({'member_id':memberId})

@app.route('/user/profile/workout-day', methods=["GET"])
def workout_day():
    member_id = request.args.get('memberId')
    week_day = request.args.get('weekDay')
    if not member_id or not week_day:
        return jsonify({'error': 'missing parameters'})

    conn = connection()
    cursor = conn.cursor()
    query = 'select gym_days.name from gym_days join routine on gym_days.gym_day_id = routine.gym_day where routine.member_id=%s AND routine.week_day = %s'
    cursor.execute(query, (member_id, week_day))
    result = cursor.fetchall()

    if not result:
        return jsonify({'error': 'no workout day found'}), 404

    return jsonify({'gymDayName': result[0][0]})

@app.route('/user/profile/member-info',methods = ['GET'])
def fetch_join_date():
  member_id = request.args.get('memberId')
  if not member_id:
    return jsonify({'error':"Missing parameters"}), 400
  conn = connection()
  cursor = conn.cursor()
  query = "select Date(join_date),height,weight from person where email=%s"
  cursor.execute(query,(member_id,))
  response = cursor.fetchall()
  print(response)
  return jsonify({'joinDate':response[0][0],
                  'height':float(response[0][1]),
                  'weight':float(response[0][2])                  
                  })

@app.route("/profile")
def view_profile():
  if 'email' in session:
    email = session['email']
    try:
      conn = connection()
      cursor = conn.cursor()
      query = "select username from users where email = %s"
      cursor.execute(query, (email,))
      name = cursor.fetchone()
      query_check ="Select * from person where email=%s"
      cursor.execute(query_check,(email,))
      if(name and cursor.fetchone()):
        session['name']=name[0]
        Dates_info = joinDate()
        if Dates_info[1]==0:
          Dates_info[1]=1
        join_date = Dates_info[0]
        total_days = Dates_info[1]
        present_days = Dates_info[2]
        dob = Dates_info[3]
        disease = Dates_info[4]
        print(join_date)
        return render_template("logged_in_user_profile.html",name=session['name'],email=session['email'],join_date=join_date,total_days=total_days,present_days=present_days,disease=disease,dob=dob)
      else:
        return render_template("forms.html")
    except Error as e:
      return jsonify({'error': str(e)})
  else:
    return "You are not authorised to access the page!"
  
@app.route('/user/profile/exercises',methods=['GET'])
def fetch_exercises():
  muscle = request.args.get('target_muscle')
  query = 'select exercise.exercise_name, exercise.exercise_description, difficulty_level, exercise_url from exercise join exercise_muscle_group on exercise.exercise_id = exercise_muscle_group.exercise_id join muscle_group on exercise_muscle_group.muscle_group_id = muscle_group.muscle_group_id where muscle_group_name =%s limit 5'
  conn = connection()
  cursor = conn.cursor()
  cursor.execute(query,(muscle,))
  response = cursor.fetchall()
  return response

@app.route('/user/profile/attendance',methods = ['GET'])
def fetch_dates():
  memberId = request.args.get('memberId')
  query = 'select distinct extract(day from check_in_time) as attendance_days from user_attendance where member_id=%s and date(check_in_time) between date(now()) - interval day(now()) +1 day and last_day(now()) order by attendance_days'
  conn = connection()
  cursor = conn.cursor()
  cursor.execute(query,(memberId,))
  result = cursor.fetchall()
  attendance_data = [dates[0] for dates in result]
  print(attendance_data)
  return jsonify({'attendance_data':attendance_data})

@app.route("/user/markAttendance", methods = ["POST"])
def markAttendance():
  member_id = session.get('email')
  conn =  connection()
  cursor = conn.cursor()
  query = 'Insert into user_attendance(member_id) values (%s)'
  cursor.execute(query,(member_id,))
  conn.commit()
  cursor.close()
  conn.close()
  return jsonify({'message': 'Attendance was marked successfully!'})

@app.route('/user/update_routine',methods = ["POST"])
def update_schedule():
  gym_days = {
    'Biceps Day':1,
    'Triceps Day':2,
    'Legs Day':3,
    'Core Day':4,
    'Shoulders Day':5,
    'Chest Day':7,
    'Back Day':8,
    'Rest Day':9
  }
  monday_ex = request.form['monday']
  tuesday_ex = request.form['tuesday']
  wednesday_ex = request.form['wednesday']
  thursday_ex = request.form['thursday']
  friday_ex = request.form['friday']
  saturday_ex = request.form['saturday']
  sunday_ex = request.form['sunday']
  conn = connection()
  cursor = conn.cursor()
  for i in [sunday_ex,monday_ex,tuesday_ex,wednesday_ex,thursday_ex,friday_ex,saturday_ex]:
    j=0
    query = 'Update routine set gym_day=%s where week_day=%s'
    cursor.execute(query,(gym_days[i],j))
    j+=1
  conn.commit()
  cursor.close()
  conn.close()
  return render_template("logged_in_user_profile.html")

# Daily progress Pics
@app.route('/user/upload_prog_pics', methods=['POST'])
def upload_progress_pic():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    description = request.form.get('description', '')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Create unique filename using timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f"{timestamp}_{file.filename}")
        
        # Ensure upload directory exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        # Save file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Save to database
        try:
            db = connection()
            cursor = db.cursor()
            query = 'Insert into prog_pics(member_id, image_path, description) values (%s,%s,%s)'
            cursor.execute(query,(session.get('email'),filename, description))
            db.commit()
            
            return jsonify({
                'success': True,
                'message': 'Image uploaded successfully',
                'image_path': filename
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/user/get_prog_pics', methods=['GET'])
def get_progress_pics():
    try:
        db = connection()
        cursor = db.cursor()
        cursor.execute('''
            SELECT image_path, description, upload_date 
            FROM prog_pics 
            WHERE member_id = ? 
            ORDER BY upload_date DESC 
            LIMIT 1
        ''', (session['email'],))
        
        result = cursor.fetchone()
        
        if result:
            return jsonify({
                'success': True,
                'image_path': result[0],
                'description': result[1],
                'upload_date': result[2]
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No progress pictures found'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
  
  


@app.route('/admin/add_staff', methods=['POST'])
def add_staff():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    phone = request.form['phone']
    join_date = request.form['hire_date']
    salary = request.form['salary']
    department= request.form['department']
    conn = connection()
    cursor = conn.cursor()
    
    query = """
    INSERT INTO staff 
    (first_name, last_name, email, phone, 
    hire_date, salary, department) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    values = (
        first_name,last_name,email, phone,join_date,salary,department
    )
    
    try:
        cursor.execute(query, values)
        conn.commit()
        return jsonify({"status": "success", "message": "Staff added successfully"})
    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": str(err)})
    finally:
        cursor.close()
        conn.close()
      
# Search Staff
@app.route('/search_staff', methods=['GET'])
def search_staff():
    query = request.args.get('query', '')
    department = request.args.get('department', '')
    
    conn = connection()
    cursor = conn.cursor(dictionary=True)
    
    sql_query = """
    SELECT * FROM staff 
    WHERE (first_name LIKE %s OR last_name LIKE %s OR email LIKE %s)
    AND (department = %s OR %s = '')
    """
    
    search_param = f'%{query}%'
    params = (search_param, search_param, search_param, department, department)
    
    cursor.execute(sql_query, params)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(results)

@app.route('/delete_staff/<int:staff_id>', methods=['DELETE'])
def delete_staff(staff_id):
    conn = connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM staff WHERE id = %s", (staff_id,))
        conn.commit()
        return jsonify({"status": "success", "message": "Staff deleted successfully"})
    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": str(err)})
    finally:
        cursor.close()
        conn.close()

@app.route("/admin/staff", methods = ["GET"])
def render_admin_staff():
   return render_template("staff.html")
   

@app.route("/admin/membership", methods = ["GET"])
def render_membershi():
   return render_template("membership.html")
# Add Membership
@app.route('/admin/add_membership', methods=['POST'])
def add_membership():
    member_id = request.form['member_id']
    plan = request.form['plan']
    amount = request.form['amount']
    conn = connection()
    cursor = conn.cursor()
    
    try:
        query = """
        INSERT INTO memberships 
        (member_id, plan, purchase_date, amount, status) 
        VALUES (%s, %s, %s, %s, %s)
        """
        
        purchase_date = datetime.now().date()
        values = (
            member_id,
            plan,
            purchase_date,
            amount,
            'Active'
        )
        
        cursor.execute(query, values)
        conn.commit()
        
        return jsonify({
            "status": "success", 
            "message": "Membership added successfully",
            "membership_id": cursor.lastrowid
        })
    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": str(err)})
    finally:
        cursor.close()
        conn.close()

# Search Memberships
@app.route('/admin/search_memberships', methods=['GET'])
def search_memberships():
    plan = request.args.get('plan', '')
    status = request.args.get('status', '')
    member_id = request.args.get('member_id', '')
    
    conn = connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT * FROM memberships 
    WHERE 1=1
    """
    params = []
    
    if plan:
        query += " AND plan LIKE %s"
        params.append(f'%{plan}%')
    
    if status:
        query += " AND status = %s"
        params.append(status)
    
    if member_id:
        query += " AND member_id = %s"
        params.append(member_id)
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(results)

# Delete Membership
@app.route('/delete_membership/<int:membership_id>', methods=['DELETE'])
def delete_membership(membership_id):
    conn = connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM memberships WHERE membership_id = %s", (membership_id,))
        conn.commit()
        return jsonify({"status": "success", "message": "Membership deleted successfully"})
    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": str(err)})
    finally:
        cursor.close()
        conn.close()

@app.route('/update_membership/<int:membership_id>', methods=['PUT'])
def update_membership(membership_id):
    data = request.json
    conn = connection()
    cursor = conn.cursor()
    
    try:
        # Determine new purchase date and renewal date
        current_date = datetime.now().date()
        
        query = """
        UPDATE memberships 
        SET plan = %s, 
            purchase_date = %s, 
            renewal_date = %s, 
            amount = %s 
        WHERE membership_id = %s
        """
        
        values = (
            data.get('plan'),
            current_date,
            current_date,
            data.get('amount'),
            membership_id
        )
        
        cursor.execute(query, values)
        conn.commit()
        
        return jsonify({
            "status": "success", 
            "message": "Membership updated successfully"
        })
    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": str(err)})
    finally:
        cursor.close()
        conn.close()

@app.route('/get_suppliers')
def get_suppliers():
    conn = connection()
    cur = conn.cursor()
    cur.execute('''SELECT supplier_id, name, company_name FROM suppliers''')
    suppliers = cur.fetchall()
    cur.close()
    return jsonify([{'id': s[0], 'name': s[1], 'company': s[2]} for s in suppliers])

@app.route('/get_locations')
def get_locations():
    conn = connection()
    cur = conn.cursor()
    cur.execute('''SELECT location_id, location_name FROM product_location''')
    locations = cur.fetchall()
    cur.close()
    return jsonify([{'id': l[0], 'name': l[1]} for l in locations])

@app.route('/get_categories')
def get_categories():
    conn = connection()
    cur = conn.cursor()
    cur.execute('''SELECT category_id, category_name FROM product_categories''')
    categories = cur.fetchall()
    cur.close()
    return jsonify([{'id': c[0], 'name': c[1]} for c in categories])

@app.route('/get_products')
def get_products():
    conn = connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT p.product_id, p.product_name, p.description, p.quantity, 
               p.min_threshold, p.manufacture_date, p.expiry_date,
               s.Name as supplier_name, l.location_name, pc.category_name,
               date(p.purchased_at), p.price
        FROM products p 
        JOIN suppliers s ON p.supplier_id = s.supplier_id
        JOIN product_location l ON p.location_id = l.location_id
        JOIN product_categories pc ON p.category_id = pc.category_id
    ''')
    products = cur.fetchall()
    cur.close()
    
    return jsonify([{
        'id': p[0],
        'name': p[1],
        'description': p[2],
        'quantity': p[3],
        'min_threshold': p[4],
        'manufacture_date': p[5].strftime('%Y-%m-%d') if p[5] else None,
        'expiry_date': p[6].strftime('%Y-%m-%d') if p[6] else None,
        'supplier': p[7],
        'location': p[8],
        'category': p[9],
        'purchased_at': p[10],
        'price':p[11]
    } for p in products])

@app.route('/add_product', methods=['POST'])
def add_product():
    try:
        data = request.json
        conn = connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO products (
                location_id, supplier_id, category_id, product_name,
                description, manufacture_date, expiry_date,
                min_threshold, quantity,price
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            data['location_id'], data['supplier_id'], data['category_id'],
            data['product_name'], data['description'], data['manufacture_date'],
            data['expiry_date'], data['min_threshold'], data['quantity'],
            data['purchased_at']
        ))
        conn.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/delete_product/<int:pid>', methods=['DELETE'])
def delete_product(pid):
    try:
        conn = connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM products WHERE product_id = %s', (pid,))
        conn.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
@app.route('/update_product/<int:pid>', methods = ['PUT'])
def update_product(pid):
   data = request.json
   conn = connection()
   cursor = conn.cursor()
   print(pid)
   query = """
   UPDATE products
   set quantity=%s, min_threshold = %s,price= %s
   where product_id = %s
   """
   values = (int(data['quantity']),int(data['min_threshold']),int(data['price'],pid))
   print(values)
   cursor.execute(query,values)
   return jsonify({'status': "success"})   
   




if __name__ == "__main__":
  app.run(debug=True , host='0.0.0.0',port=9000)
# IMPORTING LIBRARIES AND MODULES FROM PYTHON
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request,jsonify, redirect, url_for,session
import bcrypt
import mysql.connector
from datetime import datetime
from flask_cors import CORS
from mysql.connector import Error


# Daily Progress Picture configuring folder and filetype
UPLOAD_FOLDER = 'static/progress_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

#  IMPORTING FUNCTIONS FROM OTHER FILES
from connection import connection
from youtubeApi import fetch_video
from sql_queries import target_muscles


# CREATING AN INSTANCE OF FLASK AND Youtube api
app = Flask(__name__)
app.secret_key = "samar_e_muqaatil"

# Daily Progress picture folder configuration
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# declaring the functions to be used after
def get_current_day():
  current_day = datetime.now().strftime('%A')
  return current_day

def joinDate():
  email = session.get('email')
  query = "Select Date_format(join_date, '%M %D, %Y') from person where email=%s"
  conn =connection()
  cursor = conn.cursor()
  cursor.execute(query,(email,))
  join_date = cursor.fetchone()[0]
  query = "Select Datediff(CURDATE(),join_date) from person where email=%s"
  cursor.execute(query,(email,))
  total_days = cursor.fetchone()[0]
  query ="select count(check_in_time) as total_present_days from user_attendance where member_id =%s"
  cursor.execute(query,(email,))
  present_days = cursor.fetchone()[0]
  query = 'select dob from person where email= %s'
  cursor.execute(query,(email,))
  dob = cursor.fetchone()[0]
  query = 'select disease from person where email= %s'
  cursor.execute(query,(email,))
  disease = cursor.fetchone()[0]
  
  return [join_date,total_days,present_days,dob,disease]

# Preparing my first function of pushing data from form to backend database of aiven
@app.route("/")
def landing_page():
    return render_template("index.html")

# SHOWING THE PLANS PAGE
@app.route("/plans")
def plans():
  return render_template("plans.html")

#SHOWING THE TAEKWONDO PAGE
@app.route("/taekwondo",methods = ["GET"])
def render_taekwondo():
  return render_template("taekwondo.html")

# Showing the success corner page comprising of the successfull people who excel their field through exercising
@app.route("/success_corner", methods=["GET"])
def render_page():
  return render_template("success_corner.html")

#Showing the meals page which would be having the diets for the users
@app.route("/meals", methods=["GET"])
def render_meals():
  return render_template("meals.html")

# Rendering the form page and taking the submissions and storing them into the table
@app.route("/forms", methods = ["POST","GET"])
def form_render():
  if(request.method == "GET"):
    if 'email' in session:
      return render_template("forms.html")
    else :
      return redirect(url_for('login'))
  elif(request.method=="POST"):
    name = request.form['name']
    email = request.form['email']
    mobile = request.form['mobile']
    dob = request.form['dob']
    height = request.form['height']
    weight = request.form['weight']
    address = request.form['address']
    plan = request.form['plan']
    disease = request.form['disease']

    try:
      conn = connection()
      cursor = conn.cursor()

      #Creating Table users if it don't exist
      cursor.execute("""CREATE TABLE IF NOT EXISTS person (
    name VARCHAR(100) NOT NULL,           -- Compulsory Name
    email VARCHAR(100) UNIQUE ,            -- Unique Email
    mobile VARCHAR(14) NOT NULL,   -- Compulsory Mobile Number (Assuming 15-digit max for international format)
    dob DATE NOT NULL,          -- Compulsory Date of Birth
    height DECIMAL(5,2),                  -- Height in cm (can handle up to 999.99 cm)
    weight DECIMAL(5,2),                  -- Weight in kg (can handle up to 999.99 kg)
    address TEXT NOT NULL,                -- Compulsory Address
    plan ENUM('Monthly', 'Quarterly', 'Yearly') NOT NULL, -- Plan (Dropdown options)
    disease VARCHAR(255) DEFAULT 'NA', -- Any chronic disease (NA if not)
    trainer varchar(32) NOT NULL, -- Trainer's Name
    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Automatic current join date
    FOREIGN KEY (email) REFERENCES users(email)
    ON UPDATE CASCADE
);
""")
      
      #CREATING QUERY FOR INSERTION
      query_insert = 'INSERT INTO person(name,email,mobile,dob,height,weight,address,plan,disease) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
      cursor.execute(query_insert,(name,email,mobile,dob,height,weight,address,plan,disease))
      conn.commit()
      cursor.close()
      conn.close()
      print('One insert query has been successfully executed')
      return redirect(url_for("payment"))
    
    except Error as e:
      return jsonify({'error': str(e)})
    
   
    
    
# SIGNUP FOR USERS/TRAINERS AND STORING DATA IN USERS TABLE IN THE DATABASE
@app.route("/signup", methods = ["POST","GET"])
def signup():
  if(request.method=="GET"):
    return render_template("signup.html")
  elif(request.method == "POST"):
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    hash_password = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
    hash_pass_str = hash_password.decode('utf-8')
    role = request.form['role']

    try:
      conn = connection()
      cursor = conn.cursor()

      cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        role varchar(15) NOT NULL DEFAULT 'user',
        created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
      )
      query_insert = 'INSERT INTO users(username, email, password, role) VALUES (%s,%s,%s,%s);'
      cursor.execute(query_insert,(username,email,hash_pass_str,role))
      
      for i in range(7):
        query = "INSERT INTO routine(member_id,week_day,gym_day)"
        cursor.execute(query,(email,i,i+1))
      conn.commit()
      cursor.close()
      conn.close()
      print('One insert query has been successfully executed')
      return render_template("login.html")
    
    except Error as e:
      return jsonify({'error': str(e)})


# LOGIN FOR USERS/TRAINERS/ADMIN AND VERIFYING DATA FROM THE DATA IN DATABASE
@app.route("/login", methods = ["POST","GET"])
def login():
  if (request.method== "GET"):
    return render_template("login.html")
  
  elif(request.method == "POST"):
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    conn = connection()
    cursor = conn.cursor()

    query = 'SELECT email, password, role FROM users WHERE email = %s AND role = %s '
    cursor.execute(query,(email,role))
    login_data = cursor.fetchone()
    if login_data:
      password_get= login_data[1]
      pass_final = password_get.encode('utf-8')
      if(bcrypt.checkpw(password.encode('utf-8'),pass_final)):
        session['email'] = email
        session['role'] = role
        if(session['role']=='user'):
          return render_template("user_after_login.html")
        elif session['role']=='admin':
          return redirect(url_for("admin_main_page"))
        elif session['role']=='trainer':
          return ("Ye trainer wala page hai")
      else:
        return(f'Incorrect password for {email}')
    else:
      return ("NO USER FOUND!!!")



# @app.route("/user_after_login",methods = ["POST","GET"])
# def user_after_login():
#   if(request.method=="GET"):
#     profile = get_user_profile()
#     weekly_plan = get_weekly_plan()
#     attendance_data = get_attendance_data()

#     # Render template and pass data to the frontend
#     return render_template('user_after_login.html',profile,weekly_plan,attendance_data)

@app.route("/logged_in_home")
def logged_in_home_render():
  return render_template("user_after_login.html")
@app.route("/logged_in_plans")
def logged_in_plans_render():
  return render_template("logged_in_plans.html")
@app.route("/logged_in_about")
def logged_in_about_render():
  return render_template("logged_in_about.html")

# ADMIN MAIN PAGE RENDERING AND FUNCTIONALITY
@app.route("/admin")
def admin_main_page():
  if session['role']=='admin':
    return render_template("admin_login.html")
  else:
    return ("You are not athorised for this page")
@app.route("/inventory")
def inventory():
  return ("bana raha hu")


@app.route("/logout")
def logout():
  session.clear()
  return render_template("index.html")
@app.route("/payment")
def payment():
  return("This is the place where you need to pay!!!")

@app.route("/exercises")
def exercise():
  conn = connection()
  cursor = conn.cursor()
  query1 = "select * from exercise"
  cursor.execute(query1)
  exercises = cursor.fetchall()
  url_got = [urls[3] for urls in exercises]  
  exercise_name = [name[1] for name in exercises]
  exercises = [exercise + (fetch_video(str(url)),) +(target_muscles(str(ex_name)),)  for exercise, url, ex_name in zip(exercises, url_got, exercise_name)]
  print(exercises[0])

  return render_template("exercise_corner.html", exercises = exercises)

@app.route("/admin/inventory")
def show_inventory():
  return render_template("admin_inventory.html")

@app.route('/member_id')
def get_current_member_id():
  memberId = session.get('email')
  return jsonify({'member_id':memberId})

@app.route('/user/profile/workout-day', methods=["GET"])
def workout_day():
    member_id = request.args.get('memberId')
    week_day = request.args.get('weekDay')
    if not member_id or not week_day:
        return jsonify({'error': 'missing parameters'})

    conn = connection()
    cursor = conn.cursor()
    query = 'select gym_days.name from gym_days join routine on gym_days.gym_day_id = routine.gym_day where routine.member_id=%s AND routine.week_day = %s'
    cursor.execute(query, (member_id, week_day))
    result = cursor.fetchall()

    if not result:
        return jsonify({'error': 'no workout day found'}), 404

    return jsonify({'gymDayName': result[0][0]})

@app.route('/user/profile/member-info',methods = ['GET'])
def fetch_join_date():
  member_id = request.args.get('memberId')
  if not member_id:
    return jsonify({'error':"Missing parameters"}), 400
  conn = connection()
  cursor = conn.cursor()
  query = "select Date(join_date),height,weight from person where email=%s"
  cursor.execute(query,(member_id,))
  response = cursor.fetchall()
  print(response)
  return jsonify({'joinDate':response[0][0],
                  'height':float(response[0][1]),
                  'weight':float(response[0][2])                  
                  })

@app.route("/profile")
def view_profile():
  if 'email' in session:
    email = session['email']
    try:
      conn = connection()
      cursor = conn.cursor()
      query = "select username from users where email = %s"
      cursor.execute(query, (email,))
      name = cursor.fetchone()
      query_check ="Select * from person where email=%s"
      cursor.execute(query_check,(email,))
      if(name and cursor.fetchone()):
        session['name']=name[0]
        Dates_info = joinDate()
        if Dates_info[1]==0:
          Dates_info[1]=1
        join_date = Dates_info[0]
        total_days = Dates_info[1]
        present_days = Dates_info[2]
        dob = Dates_info[3]
        disease = Dates_info[4]
        print(join_date)
        return render_template("logged_in_user_profile.html",name=session['name'],email=session['email'],join_date=join_date,total_days=total_days,present_days=present_days,disease=disease,dob=dob)
      else:
        return render_template("forms.html")
    except Error as e:
      return jsonify({'error': str(e)})
  else:
    return "You are not authorised to access the page!"
  
@app.route('/user/profile/exercises',methods=['GET'])
def fetch_exercises():
  muscle = request.args.get('target_muscle')
  query = 'select exercise.exercise_name, exercise.exercise_description, difficulty_level, exercise_url from exercise join exercise_muscle_group on exercise.exercise_id = exercise_muscle_group.exercise_id join muscle_group on exercise_muscle_group.muscle_group_id = muscle_group.muscle_group_id where muscle_group_name =%s limit 5'
  conn = connection()
  cursor = conn.cursor()
  cursor.execute(query,(muscle,))
  response = cursor.fetchall()
  return response

@app.route('/user/profile/attendance',methods = ['GET'])
def fetch_dates():
  memberId = request.args.get('memberId')
  query = 'select distinct extract(day from check_in_time) as attendance_days from user_attendance where member_id=%s and date(check_in_time) between date(now()) - interval day(now()) +1 day and last_day(now()) order by attendance_days'
  conn = connection()
  cursor = conn.cursor()
  cursor.execute(query,(memberId,))
  result = cursor.fetchall()
  attendance_data = [dates[0] for dates in result]
  print(attendance_data)
  return jsonify({'attendance_data':attendance_data})

@app.route("/user/markAttendance", methods = ["POST"])
def markAttendance():
  member_id = session.get('email')
  conn =  connection()
  cursor = conn.cursor()
  query = 'Insert into user_attendance(member_id) values (%s)'
  cursor.execute(query,(member_id,))
  conn.commit()
  cursor.close()
  conn.close()
  return jsonify({'message': 'Attendance was marked successfully!'})

@app.route('/user/update_routine',methods = ["POST"])
def update_schedule():
  gym_days = {
    'Biceps Day':1,
    'Triceps Day':2,
    'Legs Day':3,
    'Core Day':4,
    'Shoulders Day':5,
    'Chest Day':7,
    'Back Day':8,
    'Rest Day':9
  }
  monday_ex = request.form['monday']
  tuesday_ex = request.form['tuesday']
  wednesday_ex = request.form['wednesday']
  thursday_ex = request.form['thursday']
  friday_ex = request.form['friday']
  saturday_ex = request.form['saturday']
  sunday_ex = request.form['sunday']
  conn = connection()
  cursor = conn.cursor()
  for i in [sunday_ex,monday_ex,tuesday_ex,wednesday_ex,thursday_ex,friday_ex,saturday_ex]:
    j=0
    query = 'Update routine set gym_day=%s where week_day=%s'
    cursor.execute(query,(gym_days[i],j))
    j+=1
  conn.commit()
  cursor.close()
  conn.close()
  return render_template("logged_in_user_profile.html")

# Daily progress Pics
@app.route('/user/upload_prog_pics', methods=['POST'])
def upload_progress_pic():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    description = request.form.get('description', '')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Create unique filename using timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f"{timestamp}_{file.filename}")
        
        # Ensure upload directory exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        # Save file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Save to database
        try:
            db = connection()
            cursor = db.cursor()
            query = 'Insert into prog_pics(member_id, image_path, description) values (%s,%s,%s)'
            cursor.execute(query,(session.get('email'),filename, description))
            db.commit()
            
            return jsonify({
                'success': True,
                'message': 'Image uploaded successfully',
                'image_path': filename
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/user/get_prog_pics', methods=['GET'])
def get_progress_pics():
    try:
        db = connection()
        cursor = db.cursor()
        cursor.execute('''
            SELECT image_path, description, upload_date 
            FROM prog_pics 
            WHERE member_id = ? 
            ORDER BY upload_date DESC 
            LIMIT 1
        ''', (session['email'],))
        
        result = cursor.fetchone()
        
        if result:
            return jsonify({
                'success': True,
                'image_path': result[0],
                'description': result[1],
                'upload_date': result[2]
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No progress pictures found'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
  
  


@app.route('/admin/add_staff', methods=['POST'])
def add_staff():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    phone = request.form['phone']
    join_date = request.form['hire_date']
    salary = request.form['salary']
    department= request.form['department']
    conn = connection()
    cursor = conn.cursor()
    
    query = """
    INSERT INTO staff 
    (first_name, last_name, email, phone, 
    hire_date, salary, department) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    values = (
        first_name,last_name,email, phone,join_date,salary,department
    )
    
    try:
        cursor.execute(query, values)
        conn.commit()
        return jsonify({"status": "success", "message": "Staff added successfully"})
    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": str(err)})
    finally:
        cursor.close()
        conn.close()
      
# Search Staff
@app.route('/search_staff', methods=['GET'])
def search_staff():
    query = request.args.get('query', '')
    department = request.args.get('department', '')
    
    conn = connection()
    cursor = conn.cursor(dictionary=True)
    
    sql_query = """
    SELECT * FROM staff 
    WHERE (first_name LIKE %s OR last_name LIKE %s OR email LIKE %s)
    AND (department = %s OR %s = '')
    """
    
    search_param = f'%{query}%'
    params = (search_param, search_param, search_param, department, department)
    
    cursor.execute(sql_query, params)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(results)

@app.route('/delete_staff/<int:staff_id>', methods=['DELETE'])
def delete_staff(staff_id):
    conn = connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM staff WHERE id = %s", (staff_id,))
        conn.commit()
        return jsonify({"status": "success", "message": "Staff deleted successfully"})
    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": str(err)})
    finally:
        cursor.close()
        conn.close()

@app.route("/admin/staff", methods = ["GET"])
def render_admin_staff():
   return render_template("staff.html")
   

@app.route("/admin/membership", methods = ["GET"])
def render_membershi():
   return render_template("membership.html")
# Add Membership
@app.route('/admin/add_membership', methods=['POST'])
def add_membership():
    member_id = request.form['member_id']
    plan = request.form['plan']
    amount = request.form['amount']
    conn = connection()
    cursor = conn.cursor()
    
    try:
        query = """
        INSERT INTO memberships 
        (member_id, plan, purchase_date, amount, status) 
        VALUES (%s, %s, %s, %s, %s)
        """
        
        purchase_date = datetime.now().date()
        values = (
            member_id,
            plan,
            purchase_date,
            amount,
            'Active'
        )
        
        cursor.execute(query, values)
        conn.commit()
        
        return jsonify({
            "status": "success", 
            "message": "Membership added successfully",
            "membership_id": cursor.lastrowid
        })
    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": str(err)})
    finally:
        cursor.close()
        conn.close()

# Search Memberships
@app.route('/admin/search_memberships', methods=['GET'])
def search_memberships():
    plan = request.args.get('plan', '')
    status = request.args.get('status', '')
    member_id = request.args.get('member_id', '')
    
    conn = connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT * FROM memberships 
    WHERE 1=1
    """
    params = []
    
    if plan:
        query += " AND plan LIKE %s"
        params.append(f'%{plan}%')
    
    if status:
        query += " AND status = %s"
        params.append(status)
    
    if member_id:
        query += " AND member_id = %s"
        params.append(member_id)
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(results)

# Delete Membership
@app.route('/delete_membership/<int:membership_id>', methods=['DELETE'])
def delete_membership(membership_id):
    conn = connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM memberships WHERE membership_id = %s", (membership_id,))
        conn.commit()
        return jsonify({"status": "success", "message": "Membership deleted successfully"})
    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": str(err)})
    finally:
        cursor.close()
        conn.close()

@app.route('/update_membership/<int:membership_id>', methods=['PUT'])
def update_membership(membership_id):
    data = request.json
    conn = connection()
    cursor = conn.cursor()
    
    try:
        # Determine new purchase date and renewal date
        current_date = datetime.now().date()
        
        query = """
        UPDATE memberships 
        SET plan = %s, 
            purchase_date = %s, 
            renewal_date = %s, 
            amount = %s 
        WHERE membership_id = %s
        """
        
        values = (
            data.get('plan'),
            current_date,
            current_date,
            data.get('amount'),
            membership_id
        )
        
        cursor.execute(query, values)
        conn.commit()
        
        return jsonify({
            "status": "success", 
            "message": "Membership updated successfully"
        })
    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": str(err)})
    finally:
        cursor.close()
        conn.close()

@app.route('/get_suppliers')
def get_suppliers():
    conn = connection()
    cur = conn.cursor()
    cur.execute('''SELECT supplier_id, name, company_name FROM suppliers''')
    suppliers = cur.fetchall()
    cur.close()
    return jsonify([{'id': s[0], 'name': s[1], 'company': s[2]} for s in suppliers])

@app.route('/get_locations')
def get_locations():
    conn = connection()
    cur = conn.cursor()
    cur.execute('''SELECT location_id, location_name FROM product_location''')
    locations = cur.fetchall()
    cur.close()
    return jsonify([{'id': l[0], 'name': l[1]} for l in locations])

@app.route('/get_categories')
def get_categories():
    conn = connection()
    cur = conn.cursor()
    cur.execute('''SELECT category_id, category_name FROM product_categories''')
    categories = cur.fetchall()
    cur.close()
    return jsonify([{'id': c[0], 'name': c[1]} for c in categories])

@app.route('/get_products')
def get_products():
    conn = connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT p.product_id, p.product_name, p.description, p.quantity, 
               p.min_threshold, p.manufacture_date, p.expiry_date,
               s.Name as supplier_name, l.location_name, pc.category_name,
               date(p.purchased_at), p.price
        FROM products p 
        JOIN suppliers s ON p.supplier_id = s.supplier_id
        JOIN product_location l ON p.location_id = l.location_id
        JOIN product_categories pc ON p.category_id = pc.category_id
    ''')
    products = cur.fetchall()
    cur.close()
    
    return jsonify([{
        'id': p[0],
        'name': p[1],
        'description': p[2],
        'quantity': p[3],
        'min_threshold': p[4],
        'manufacture_date': p[5].strftime('%Y-%m-%d') if p[5] else None,
        'expiry_date': p[6].strftime('%Y-%m-%d') if p[6] else None,
        'supplier': p[7],
        'location': p[8],
        'category': p[9],
        'purchased_at': p[10],
        'price':p[11]
    } for p in products])

@app.route('/add_product', methods=['POST'])
def add_product():
    try:
        data = request.json
        conn = connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO products (
                location_id, supplier_id, category_id, product_name,
                description, manufacture_date, expiry_date,
                min_threshold, quantity,price
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            data['location_id'], data['supplier_id'], data['category_id'],
            data['product_name'], data['description'], data['manufacture_date'],
            data['expiry_date'], data['min_threshold'], data['quantity'],
            data['purchased_at']
        ))
        conn.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/delete_product/<int:pid>', methods=['DELETE'])
def delete_product(pid):
    try:
        conn = connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM products WHERE product_id = %s', (pid,))
        conn.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
@app.route('/update_product/<int:pid>', methods = ['PUT'])
def update_product(pid):
   data = request.json
   conn = connection()
   cursor = conn.cursor()
   print(pid)
   query = """
   UPDATE products
   set quantity=%s, min_threshold = %s,price= %s
   where product_id = %s
   """
   values = (int(data['quantity']),int(data['min_threshold']),int(data['price'],pid))
   print(values)
   cursor.execute(query,values)
   return jsonify({'status': "success"})   
   




if __name__ == "__main__":
  app.run(debug=True , host='0.0.0.0',port=9000)


