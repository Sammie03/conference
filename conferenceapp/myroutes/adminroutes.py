import math, random, os, string

from flask import render_template, request, abort, redirect, flash, make_response, session

from werkzeug.security import generate_password_hash, check_password_hash

from conferenceapp import app,db
from conferenceapp.mymodels import User,State,Skill,Admin, Breakout
from conferenceapp.forms import LoginForm




@app.route("/admin/login/", methods=['GET','POST'])
def adminlogin():
    return render_template("admin/login.html")


@app.route("/admin/reg/")
def registrations():
    # users = db.session.query(User,State,Skill).join(State).join(Skill).all()
      users = User.query.join(State).join(Skill).add_columns(State, Skill).filter(~Skill.skill_name.in_(['Junior developer'])).all()
    # users = User.query.outerjoin(State,User.user_stateid==State.state_id)
      return render_template("admin/allusers.html", users=users)
  

# @app.route("/submit/admin/",  methods=['POST'])
# def submit_adminlogin():
#         username = request.form.get('adminusername')
#         password = request.form.get('adminpassword')
        
#         if username=='' or password=='':
#             flash('please ensure all fields are filled')
#             return redirect('/admin/login')
            
#         else:
#             deets= db.session.query(Admin).filter(Admin.admin_username==username).filter(Admin.admin_password==password).first()
#             if deets:
#                 session['admin'] = deets.admin_id
#                 return redirect('/admin/home')
#             else:
#                 flash("Invalid login credentials")
#                 return redirect('/admin/login')

#line of codes with encrpted password


@app.route("/submit/admin/",  methods=['POST'])
def submit_adminlogin():
        username = request.form.get('adminusername')
        password = request.form.get('adminpassword')
        
        if username=='' or password=='':
            flash('please ensure all fields are filled')
            return redirect('/admin/login')
            
        else:
            deets= db.session.query(Admin).filter(Admin.admin_username==username).first()
            formated_password = deets.admin_password
            chk = check_password_hash(formated_password,password)
            if chk:
                session['admin'] = deets.admin_id
                return redirect('/admin/home')
            else:
                flash("Invalid login credentials")
                return redirect('/admin/login')
            
            
        
@app.route("/admin/home/")
def adminpage():
    Adminid = session.get('admin')
    if Adminid ==None:
        return redirect('/admin/login/')
    admindeets = db.session.query(Admin).get(Adminid)
    return render_template('/admin/index.html',admindeets=admindeets)


#file upload
@app.route("/admin/upload/", methods=['POST','GET'])
def admin_upload():
    Adminid = session.get('admin')
    if Adminid ==None:
        return redirect('/admin/login/')
    if request.method == 'GET':
        return render_template('admin/test.html')
    else:
        data = request.files.get('image') 
        original_name = data.filename 
        #generate randomstring to be used as filename
        
        #method1
        fn = math.ceil(random.random() * 100000000)
        #get the original extension
        # ext = original_name.split('.') #ext[-1] concat with '.' then the ext[-1]
        
        # data.save(f'conferenceapp/static/assets/{original_name}') 
        # return "submitted"
    
        
        #a better way to know the file extension
        ext = os.path.splitext(original_name)
        save_as = str(fn)+ext[1]
        
        #to allow only a certain type of extension or filter images from other files
        allowed = ['.jpg', '.png', '.gif', '.svg', '.jpeg']
        if ext[1].lower() in allowed:
                data.save(f'conferenceapp/static/assets/img/{save_as}')
                return f"submitted and saved as {save_as}"
        else:
            return "file type not allowed"
        

@app.route("/admin/breakout/")
def breakout():
    Adminid = session.get('admin')
    if Adminid ==None:
        return redirect('/admin/login/')
    else:
           breakdeets= Breakout.query.all()
           #db.session.query(Breakout).all()
           return render_template('/admin/breakout.html', breakdeets=breakdeets)
        
       
    
@app.route("/admin/addbreakout/", methods=['GET','POST'])
def addbreakout():
    Adminid = session.get('admin')
    if Adminid ==None:
        return redirect('/admin/login/')
    if request.method == 'GET':
        skills = Skill.query.all()
        return render_template('admin/breakoutform.html', skills=skills)
    else:
        #Retrieve form data (request.form....)
        title = request.form.get('title')
        level = request.form.get('level')
        #request file
        pic_object = request.files.get('image')
        original_file =  pic_object.filename
        if title =='' or level =='':
            flash("Title and Level cannot be empty")
            return redirect('/admin/addbreakout')
        if original_file !='': #check if file is not empty
            extension = os.path.splitext(original_file)
            if extension[1].lower() in ['.jpg','.png']:
                fn = math.ceil(random.random() * 100000000)  
                save_as = str(fn)+extension[1] 
                pic_object.save(f"conferenceapp/static/assets/img/{save_as}")
                #insert other details into db
                b = Breakout(break_title=title, break_picture=save_as, break_skillid=level)
                db.session.add(b)
                db.session.commit()            
                return redirect("/admin/breakout")
            else:
                flash('File Not Allowed')
                return redirect("/admin/addbreakout")

        else:
            save_as =""
            b = Breakout(break_title=title, break_picture=save_as, break_skillid=level)
            db.session.add(b)
            db.session.commit() 
            return redirect("/admin/breakout")  
        
   
        
@app.route('/admin/breakout/delete/<id>')
def admin_deletebreakout(id):
    Adminid = session.get('admin')
    if Adminid ==None:
        return redirect('/admin/login/')
    else:
          b = db.session.query(Breakout).get(id)
          db.session.delete(b)
          db.session.commit()
          flash(f"Breakout session {id} deleted")
          return redirect('/admin/breakout')
  


@app.route("/admin/logout/")
def adminlogout():
    session.pop('admin')
    return redirect('/admin/login/')


@app.route("/admin/signup/", methods=['POST','GET'])
def admin_signup():
    if request.method == 'GET':
        return render_template('admin/signup.html')     
    else: 
       username = request.form.get('adminusername')
       password = request.form.get('adminpassword')
       password2 = request.form.get('adminpassword2')
       
       if password == password2:
           formated = generate_password_hash(password) #to encrypt the password...has to be decypted b4 users can logiin
           ad = Admin(admin_username=username, admin_password=formated)
           db.session.add(ad)
           db.session.commit()
           flash("New user signed up")
           return redirect('/admin/login')
       else:
           flash('The two passwords do not match')
           return redirect('/admin/signup')
       
     
           
       
     

