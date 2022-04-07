from flask import render_template, request, abort, redirect, flash, make_response, session, url_for
from sqlalchemy import insert, desc
import json, requests, random 
from conferenceapp import app,db, Message, mail
from conferenceapp.mymodels import User,State,Skill,Breakout, user_sessions, Contactus, Posts, Comments, Myorder, Payment, OrderDetails
from conferenceapp.forms import LoginForm, ContactForm



@app.route("/")
def home():
    login = LoginForm()
    id = session.get('loggedin')
    userdeets = User.query.get(id)
    b = Breakout.query.all()
    skills = Skill.query.all()
    contact = ContactForm()
    
    try:
        #connect to API
        response = requests.get('http://127.0.0.1:8082/api/v1.0/listall')
        #connect to API if there is authentication
        # response = requests.get('http://127.0.0.1:8082/api/v1.0/listall', auth=('sam','1234'))
        #retrieve the json in the request
        hostel_json = response.json() #or json.loads(response.text)
        status = hostel_json.get('status') #to pick the status
        
    except:
        hostel_json = {}
         #pass it to the template as hostel_json=hostel_json
        return render_template("user/index.html", userdeets=userdeets, b=b, skills=skills, login=login, contact=contact, hostel_json=hostel_json)
   

@app.route("/register/", methods=['POST','GET'])
def register():
    if request.method == 'GET':
        states = db.session.query(State).all()
        skills = db.session.query(Skill).all()
        contact = ContactForm()
        login = LoginForm()
        return render_template("/user/register.html", states=states, skills=skills, contact=contact, login=login)
    else:
        email = request.form.get('email')
        pwd1 = request.form.get('pwd1')
        pwd2 = request.form.get('pwd2')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        state = request.form.get('state')
        skill = request.form.get('skill')
        
        if email =='' or pwd1 =='' or fname =='' or lname =='' or state =='' or skill =='':
            flash("please ensure all fields are filled accurately") 
            return redirect('/register')
        
        elif pwd1 != pwd2:
            flash('please reconfirm password')
            return redirect('/register')
            
        else:
            u = User(user_email=email, user_pass=pwd1, user_fname=fname, user_lname=lname, user_skillid=skill, user_stateid=state)
            db.session.add(u)
            db.session.commit()
            id = u.user_id
            session['loggedin'] = id #storing the id in a session for it to be remembered
            return redirect('/userhome')
   
            
@app.route("/userhome/")
def userhome():
    contact = ContactForm()
    login = LoginForm()
    loggedin = session.get('loggedin') #retrieving the id from the session
    if loggedin == None: #to ensure only logged in users can view the dashboard (secured page)
        return redirect("/")
    else:
         userdeets = db.session.query(User).get(loggedin) #retrieving other details from the id
         return render_template('user/userhome.html', loggedin=loggedin, userdeets=userdeets, contact=contact, login=login)
     
     
     
@app.route("/user/editprofile", methods=['GET','POST'])
def profile():
    if request.method == 'GET':
        states = db.session.query(State).all()
        skills = db.session.query(Skill).all()
       
    loggedin = session.get('loggedin')
    if loggedin == None:
         return redirect("/")
    else:
        userdeets = db.session.query(User).get(loggedin)
        return render_template('user/profile.html', userdeets=userdeets, states=states, skills=skills)
    


@app.route("/user/update", methods=['POST','GET'])
def user_update(): 
    contact = ContactForm()
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect('/')
    if request.method =='GET':
        return redirect('/userhome')
    
    #instance of the user
    user = User.query.get(loggedin)
    
    #change the fields
    
    user.user_fname = request.form.get('updatedfname')
    user.user_lname = request.form.get('updatedlname')
    user.user_phone = request.form.get('newphone')
    user.user_skillid = request.form.get('newskill')
    user.user_stateid = request.form.get('newstate')
    user.user_address = request.form.get('newaddress')   
    
    #commit changes
    db.session.commit()
    flash("Details submitted successfully")
    return redirect('/user/editprofile', contact=contact)

       
            
# @app.route("/user/update/<id>", methods=['POST','GET'])
# def user_update(id): 
#     loggedin = session.get('loggedin')
#     if loggedin == None:
#         return redirect('/')
#     if request.method =='GET':
#         return redirect('/userhome')
    
#     #retrieve form data 
    
#     fname = request.form.get('updatedfname')
#     lname = request.form.get('updatedlname')
#     phone = request.form.get('newphone')
#     skill = request.form.get('newskill')
#     state = request.form.get('newstate')
#     address = request.form.get('newaddress')   
    
#     if int(loggedin) == int(id): #checks to ensure logged in user can edit only their details..ensure they are both ints
#         #instance of the user
#         user = User.query.get(id)
#         #change the fields
#         user.user_fname=fname
#         user.user_lname=lname
#         user.user_phone=phone
#         user.user_address=address
#         user.user_skillid=skill
#         user.user_stateid=state
#         db.session.commit()
#         flash("Details submitted successfully")
#     return redirect('/user/editprofile')

       


#logout simply means ending the session hence the .pop() user shld be redirected to the home page
@app.route("/logout/")
def logout():
    session.pop('loggedin')
    return redirect('/')

#login using forms on forms.py
@app.route("/user/login/", methods=['POST'])
def submit_login():
    #instantiate the form
    login = LoginForm()
    contact = ContactForm()
    
    #retrieve form data
    username = request.form.get('username') #method1
    pwd = login.pwd.data #method2
    
    #validate
    if login.validate_on_submit():
        deets = User.query.filter(User.user_email==username, User.user_pass==pwd).first() #.all returns all in a list
        # deets = User.query.filter(User.user_email==username).filter(User.user_pass==pwd).first() #.first returns without list.
        
        if deets:
            #retrieve his user_id and then keep in session
            id = deets.user_id
            session['loggedin']=id
            #redirect him/her to userhome
            return redirect('/userhome')
        else:
            #keep a failed message in flash, then redirect him to login again
            flash('Invalid credentials...Please try again')
            return redirect('/')
            
    else:
        return render_template("user/index.html", login=login, contact=contact)
    
            
@app.route('/user/breakout/')
def userbreakout():
    contact = ContactForm()
    loggedin = session.get('loggedin') 
    if loggedin == None: 
        return redirect("/")
    else:
        userdeets = User.query.get(loggedin)
        userskill = userdeets.user_skillid
        breakouts = db.session.query(Breakout).filter(Breakout.break_skillid == userskill).all()
        
        return render_template('user/breakout.html', breakouts=breakouts, userdeets=userdeets, contact=contact) #loopover the breakout on the template
    
        
@app.route('/user/breakout/<id>')
def viewdetails(id):
    contact = ContactForm()
    return render_template('/user/showbreakout.html', contact=contact)


@app.route("/user/regbreakout", methods=['POST'])
def reg_breakout():
    #getlist() to retrieve multiple form elements with same name
    bid = request.form.getlist('bid')
    loggedin = session.get('loggedin')
    contact = ContactForm()
    user = User.query.get(loggedin)
    db.session.execute(f"DELETE FROM user_breakout WHERE user_id='{loggedin}'") #use to delete things users can always change b4 saving the new one..things like category
    db.session.commit()
    for i in bid:
        
        #method 1 - SQL alchemy core
        #  q = user_sessions.insert().values(user_id=loggedin, breakout_id=i)
        #  db.session.execute(q)
        #  db.session.commit()
        
        #method 2 - Using SQLAlchemy ORM
        item = Breakout.query.get(i)
        user.mybreakouts.append(item)
        db.session.commit()
   
    return redirect('/user/breakout/', contact=contact)


@app.route('/contact/us')
def contactus():
    contact = ContactForm()
    return render_template('user/layout.html', contact=contact)


@app.route('/contact/msg', methods=['GET','POST'])
def contactmsg():
    contact = ContactForm()
    if contact.validate_on_submit():
        name=contact.fullname.data #request.args.get() ---use for method get alone
        email=contact.email.data #can also use request.value.get('name') #request.value() ---use for both post and get
        message=contact.message.data #request.form.get() - this works for post methods alone
        c = Contactus(contact_name=name, contact_email=email, contact_message=message)
        db.session.add(c)
        db.session.commit()  
        id = c.contact_id
        if id:
            return json.dumps({"id":id,"message":"Your message has been sent"}) #use this format to send two or more messages(strings on int)
            
        else:
            return "Sorry, please try again"
    else:
        flash('You need to complete all the fields')
        return redirect('/')
    

@app.route('/demo/available')
def available():
    return render_template("user/availability.html")


@app.route('/check/result')
def check():
    user = request.args.get('username')
    deets = User.query.filter(User.user_email==user).all()
    if deets:
        return "Username is taken"    
    else:
        return f"{user} Available"
    

@app.route('/check/lga')
def check_lga():
    if request.method == 'GET':
        states = db.session.query(State).all()
    return render_template('user/load_lga.html', states=states)     



@app.route('/demo/lga', methods=['POST'])
def show_lga():
    state = request.form.get('stateid')
    #TO DO: write a query that wll fetch from LGA table where state_id =state
    res = db.session.execute(f"SELECT * FROM lga WHERE state_id={state}")
    results = res.fetchmany(20)

    select_html = "<select>"
    for x,y,z in results:
        select_html = select_html + f"<option value='{x}'>{z}</option>"
    
    select_html = select_html + "</select>"

    return select_html


@app.route('/user/discussion')
def discussion():
    contact = ContactForm()
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect("/")
    else:
        userdeets = User.query.get(loggedin)
        postdeets = db.session.query(Posts).all()
        return render_template("user/discussion.html", contact=contact, userdeets=userdeets, postdeets=postdeets)
    

@app.route('/post/details/<id>')
def postdetails(id):
    contact = ContactForm()
    loggedin = session.get('loggedin')
    userdeets = User.query.get(loggedin)
    if loggedin == None:
        return redirect("/")
    else:
        postdeets = db.session.query(Posts).get(id)
        
        commentdeets = db.session.query(Comments).filter(Comments.c_postid==id).order_by(desc(Comments.c_date)).all()
        return render_template("user/postdetails.html", userdeets=userdeets, postdeets=postdeets, contact=contact, commentdeets=commentdeets)
        
    
@app.route("/post/comment", methods=['POST'])
def post_comment():
    #retrieve data
    loggedin = session.get('loggedin',0) #0 means return zero if nothing is found in loggedin..default vlue
    postid = request.form.get('postid')
    comment = request.form.get('comment')
    
     #insert into db
     
    # Method1
    c = Comments()
    db.session.add(c)
    c.c_userid=loggedin
    c.c_postid=postid
    c.c_comment=comment
    db.session.commit()
    
    # Method 2
    # c = Comments(c_userid=loggedin, c_postid=postid, c_comment=comment)
    # db.session.add()
    # db.session.commit()
    
      #insert into association table
    # Method 3
    user = User.query.get(loggedin)
    dpost = Posts.query.get(postid)
    c = Comments()
    db.session.add(c)
    user.user_comments.append(c)
    dpost.post_comments.append(c)
    c.c_comment=comment
    db.session.commit()
    #{"comment":comment,"total":6}
    ddate = c.c_date
    return f"{comment} and {ddate}"
    

    
@app.route('/donate', methods=['POST','GET'])
def donation():
    if request.method=='GET':
        return render_template('user/donation.html')
    else:
        fullname = request.form.get('fullname')  #ensure form details are first saved and displayed to users for confirmation b4 sending to payment gateway
        email = request.form.get('email')
        amount = request.form.get('amount')
        status = 'pending'
        
        #generate a random number as transaction ref
        ref = int(random.random() * 10000000)
        #keep ref in session
        session['refno'] = ref
        #insert into the database
        db.session.execute(f"INSERT INTO donation SET fullname ='{fullname}', email ='{email}', amount='{amount}', status='pending', ref='{ref}'")
        db.session.commit()
        return "successful"
    

@app.route('/confirmpay', methods=['POST','GET'])
def confirmpay():
    ref = session.get('refno')
    #run the query to retrieve details of this donation
    qry = db.session.execute(f"SELECT * FROM donation WHERE ref={ref}")
    data =qry.fetchone()
    return render_template("user/payconfirm.html", data=data)
        
        
@app.route('/show/breakout/')
def breakoutshow():
    contact = ContactForm()
    loggedin = session.get('loggedin') 
    if loggedin == None: 
        return redirect("/")
    else:
        userdeets = User.query.get(loggedin)
        userskill = userdeets.user_skillid
        breakouts = db.session.query(Breakout).filter(Breakout.break_skillid == userskill).all()
        
        return render_template('user/breakoutpay.html', breakouts=breakouts, userdeets=userdeets, contact=contact)
    


#The user submits selected breakouts to this route
@app.route("/send/breakout", methods=['POST','GET'])
def send_breakout():
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect("/")
    if request.method=='POST':
        #retrieve form data, breakout ids
        bid = request.form.getlist('bid')

        #insert new record into myorder,
        mo = Myorder(order_userid=loggedin)
        db.session.add(mo)
        db.session.commit()
        orderid = mo.order_id
        #generate a trans ref using random (save in session), insert into payment table
        ref = int(random.random() * 10000000)
        session['refno'] = ref
        #loop over the selected breakout ids and insert into
        #order_details, 
        totalamt = 0
        for b in bid:
            breakdeets = Breakout.query.get(b)
            break_amt = breakdeets.break_amt
            totalamt = totalamt + break_amt
            od = OrderDetails(det_orderid=orderid,det_breakid=b,det_breakamt=break_amt)
            db.session.add(od)

        db.session.commit()
        p = Payment(pay_userid=loggedin,pay_orderid=orderid,pay_ref=ref,pay_amt=totalamt)       
        db.session.add(p) 
        db.session.commit()
        return redirect("/user/confirm_breakout")    
    else:
        return redirect("/")

#This route will show all chosen sessions and connect to paystack
@app.route("/user/confirm_breakout", methods=['POST','GET'])
def confirm_break():
    loggedin = session.get('loggedin')
    ref = session.get('refno')
    if loggedin == None or ref == None:
        return redirect("/")
    userdeets = User.query.get(loggedin) 
    deets = Payment.query.filter(Payment.pay_ref==ref).first() 

    if request.method == 'GET':          
        contact = Contactus()                
        return render_template("user/show_breakout_confirm.html",deets = deets,userdeets=userdeets,contact=contact)
    else:
         
        data = {"email":userdeets.user_email,"amount":deets.pay_amt*100, "reference":deets.pay_ref}

        headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_here"}

        response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=json.dumps(data))

        rspjson = json.loads(response.text) 
        if rspjson.get('status') == True:
            authurl = rspjson['data']['authorization_url']
            return redirect(authurl)
        else:
            return "Please try again"

#4. This  is the landing page for paystack, you are to connect to paystack and check the actual details of the transaction, then update yopur database
@app.route("/user/paystack")
def paystack():
    reference = request.args.get('reference')
    ref = session.get('refno')
    #update our database 
    headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_here"}

    response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
    rsp =response.json()#in json format
    if rsp['data']['status'] =='success':
        amt = rsp['data']['amount']
        ipaddress = rsp['data']['ip_address']
        p = Payment.query.filter(Payment.pay_ref==ref).first()
        p.pay_status = 'paid'
        db.session.add(p)
        db.session.commit()
        return "Payment Was Successful"  #update database and redirect them to the feedback page
    else:
        p = Payment.query.filter(Payment.pay_ref==ref).first()
        p.pay_status = 'failed'
        db.session.add(p)
        db.session.commit()
        return "Payment Failed"  
    #return render_template("user/demo.html", response=rsp)
    
@app.route("/sendmail")
def sendmail():
    subject = "Automated Email"
    sender = ("Samteddy","eventstrolley@gmail.com")
    recipient = ["samuelokediya@gmail.com"]
    
    #instantiate an object of Message..
    try:
        msg=Message(subject=subject,sender=sender,recipients=recipient, body="<b>Samteddy is going to miss you guys. See you at the top senior dev.</b>")
       
       #method2
        # msg= Message()
        # msg.subject=subject
        # msg.sender=sender
        # msg.body =""
        # msg.recipients=recipient
        
        htmlstr = "<h6>How are you Sammie?</h6><p><img src='https://www.google.com/search?q=images&tbm=isch&source=iu&ictx=1&vet=1&fir=LHY-1Uagl8fCxM%252Cl-X2y9oJGN2i-M%252C_%253BtFT2spaQpfBwhM%252CcMRXOd2p22EgNM%252C_%253B-Iap6zp20DK6KM%252Cl-X2y9oJGN2i-M%252C_%253Ba4JmwRU0zcHUtM%252CISkb2KM1Sl3SmM%252C_%253BkGZWolysFFKPOM%252CM_GLqoPzx6T9DM%252C_%253B2nDXavJs9DoKTM%252CB51x0PBR9KNzvM%252C_%253BWu_WLS_uDRWvOM%252CcMRXOd2p22EgNM%252C_%253BDH7p1w2o_fIU8M%252CBa_eiczVaD9-zM%252C_%253BUpvqeWupXuaMrM%252CISkb2KM1Sl3SmM%252C_%253Bn5hAWsQ-sgKo_M%252C-UStXW0dQEx4SM%252C_%253BsPwUW2x5Z3mupM%252CnBiD9BWYMB87aM%252C_%253BUVAHTXdge9JbrM%252CtnVTsEa64LdCyM%252C_%253BzAGiSuQh5zpsUM%252CtOfiwT7ULtBHIM%252C_%253BD7PWmTEZbduE6M%252C7aaqRtckvukvLM%252C_&usg=AI4_-kS0pZ2iM0yXeFy5Xao-cp2U4n3uYw&sa=X&ved=2ahUKEwj4uKfY1oH3AhVux4UKHUKbASAQ9QF6BAgDEAE#imgrc=LHY-1Uagl8fCxM'></p>"
        
        msg.html = htmlstr
        
        with app.open_resource("invite_saveas.pdf") as fp:   #to attach a file
            msg.attach("invite.pdf", "application/pdf", fp.read()) #application/pdf is the mimetype for pdf
        
        mail.send(msg)
        return "Email sent successfully" 
    except:  
        return "Connection Refused."    
        


