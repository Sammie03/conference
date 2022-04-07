from re import M
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField

from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    
    username = StringField("Your email:", validators=[DataRequired(), Email()]) #form labels are inputted as parameters to the function
    
    pwd = PasswordField("Enter Password:")
   
    loginbtn = SubmitField("Login")
    
    
class ContactForm(FlaskForm):
    
    fullname = StringField("Fullname:", validators=[DataRequired()]) 
    
    email = StringField("Your email:", validators=[DataRequired(), Email()])
    
    message = TextAreaField("Message:", validators=[DataRequired()]) 
    
    btn = SubmitField("Send")
    
    
     