'''
CS3250 - Software Development Methods and Tools - Fall 2023
Instructor: Thyago Mota
Student: 
Description: Project 2 - Queen Soopers Web App
'''

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired

class SignUpForm(FlaskForm):
    id = StringField('Id', validators=[DataRequired()])
    family_name = StringField('Family Name')
    given_name = StringField('Given Name')
    email_address = StringField('Email')
    passwd = PasswordField('Password', validators=[DataRequired()])
    passwd_confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Confirm')
    customer_id = StringField('Customer Id')
    
class SignInForm(FlaskForm):
    id = StringField('Id', validators=[DataRequired()])
    passwd = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Confirm')

class OrdersForm(FlaskForm):
    #date
    date = DateField('Date', validators=[DataRequired()])
    # upc
    upc = StringField('Item UPC', validators=[DataRequired()])
    #item
    item = StringField('Item', validators=[DataRequired()])
    # paid amount
    paid = StringField('Paid Amount', validators=[DataRequired()])
    #other order fields