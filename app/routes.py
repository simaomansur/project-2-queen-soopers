'''
CS3250 - Software Development Methods and Tools - Fall 2023
Instructor: Thyago Mota
Student: 
Description: Project 2 - Queen Soopers Web App
'''

from app import app, db, cache
from app.square import square, get_latest_orders, get_order
from app.models import User
from app.forms import SignUpForm, SignInForm, OrdersForm
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, login_user, logout_user, current_user
import bcrypt, uuid
import os
from datetime import datetime

# routes
@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index(): 
    return render_template('index.html')

@app.route('/users/signin', methods=['GET', 'POST']) # users/signin is the URL for the sign in page, and the methods are GET and POST
def users_signin(): # this function is called when the user visits the sign in page
    form = SignInForm() # create a sign in form and use SignInForm() from forms.py
    if form.validate_on_submit(): # if the request is a POST
        user = User.query.filter_by(id=form.id.data).first()  # get the user from the database via id
        if not user: # if the user does not exist.
            flash('Could not find user. Try again?')  # flash a message
            return redirect(url_for('index'))
        if not bcrypt.checkpw(form.passwd.data.encode('utf-8'), user.passwd): # Check if the password entered matches the hashed password stored
            flash('Invalid password') # flash a message if it is incorrect.
            return render_template('signin.html', form=form) 
        login_user(user)  # Log in the user
        print(user.customer_id) # to get stuff from square:
        result = square.customers.retrieve_customer(customer_id = user.customer_id)
        if result.is_success():
            print(result.body)
        if result.is_error():
            print(result.errors)
        return redirect(url_for('orders'))
    return render_template('signin.html', form=form)

@app.route('/users/signup', methods=['GET', 'POST']) # users/signup is the URL for the sign up page, and the methods are GET and POST
def users_signup(): # this function is called when the user visits the sign up page
    form = SignUpForm() # create a sign up form and use SignUpForm() from forms.py
    if form.validate_on_submit(): # if the request is a POST
        existing_user = User.query.filter_by(id=form.id.data).first() # get the user from the database via id
        if existing_user: # if the user exists
            flash('Email already in use') # flash a message
            return render_template('signup.html', form=form) # render the sign up page again
        if form.passwd.data != form.passwd_confirm.data:    # Check if the passwords match
            flash('Passwords do not match') # flash a message if they don't
            return render_template('signup.html', form=form) # render the sign up page again
        # Create a new customer profile in Square
        customers_api = square.customers # get the customers API
        request_body = { # create a request body
            "idempotency_key": str(uuid.uuid4()), # generate a unique idempotency key
            "given_name": form.given_name.data, # get the given name from the form
            "family_name": form.family_name.data, # get the family name from the form
            "email_address": form.email_address.data, # get the email address from the form
            # potential other fields
        }
        response = customers_api.create_customer(request_body) # create the customer profile
        if response.is_success(): # if the customer profile was created successfully
            newcustomer_id = response.body['customer']['id'] # get the customer id
            # Hash password
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(form.passwd.data.encode('utf-8'), salt)
            # Create a new user
            new_user = User(
                email=form.email_address.data,
                id = form.id.data,
                passwd=hashed_password,
                customer_id=newcustomer_id
                # ...possibly other fields ...
            )
            db.session.add(new_user) # add the new user to the database
            try: # try to commit the changes
                db.session.commit() # commit the changes
                flash('Account created successfully! Your customer ID is ' + newcustomer_id + '.') # flash a message
                return redirect(url_for('index')) # redirect to the index page
            except Exception as e: # if an exception occurs
                db.session.rollback() # rollback the changes
                # Log the exception 
                print(e)
                flash('An error occurred while creating your account. Please try again.')
        else:
            print(response.errors) # print the errors
            flash('An error occurred while creating your Square customer account. Please try again.')
    return render_template('signup.html', form=form)
    
@login_required
@app.route('/users/signout', methods=['GET', 'POST'])
def users_signout():
    logout_user()
    return redirect(url_for('index'))

@login_required
@app.route('/orders')
def orders():
    # Get the latest orders for the current user.
    # Cache the orders for 5 minutes (untested)
    order = cache.get(f"order#{current_user.customer_id}")
    if not order: 
        # cache miss!
        orders = get_latest_orders(current_user.customer_id)
        cache.set(f"order#{current_user.customer_id}", order)
        # List for holding orders
        orders_info = []
        # If there are any orders...
        if orders:
            # Process each order.
            for order in orders:
                # Extract the necessary information from each order.
                order_info = {
                    'id': order['id'],
                    'date': order['metadata']['created_at'],
                }
                # Add the processed order information to our list.
                orders_info.append(order_info)
            return render_template('orders.html', orders_info=orders_info)
        else:
            flash("No orders exist.")
            return redirect(url_for('index'))
    # Note that we're using 'orders_info' here to match your template.
    

@login_required
@app.route('/orders/<id>')
def order(id):
    # Retrieve the specific order by ID.
    # This function should be defined to fetch the order details from your database or API.
    items = get_order(id)
    if items:
        return render_template('order.html', items=items)
    else:
        flash("No order found.")
        return redirect(url_for('orders'))

@login_required
@app.route('/monthly', methods=['GET', 'POST'])
def monthly():
    # retrieve the monthly orders for the current user
    # Try fetching from the cache
    orders = cache.get(f"order#{current_user.customer_id}")
    if not orders:
        # If cache miss, fetch orders from the function
        orders = get_latest_orders(current_user.customer_id)
        cache.set(f"order#{current_user.customer_id}", orders)
    # Dictionary for holding monthly totals
    monthly_totals = {}
    # If there are any orders...
    if orders:
        # Process each order.
        for order in orders:
            # Parse the date to get month and year
            date_obj = datetime.strptime(order['metadata']['created_at'], '%m/%d/%y')
            month_year = date_obj.strftime('%m/%Y')  # Format as MM/YYYY
            # Calculate the order's total amount.
            amount = order['total_money']['amount'] / 100
            # Add the order's amount to the corresponding month's total.
            if month_year not in monthly_totals:
                monthly_totals[month_year] = 0
            monthly_totals[month_year] += amount
        # Print monthly totals for debugging
        print("Monthly Totals:", monthly_totals)
        return render_template('monthly.html', monthly_totals=monthly_totals)
    else:
        flash("No orders exist.")
        return redirect(url_for('index'))

@login_required
@app.route('/orders/topfive', methods=['GET', 'POST'])
# fetch the top five items from your database or API.
def topfive():
    # retrieve the five most bought items for the current user
    # Try fetching from the cache
    orders = cache.get(f"order#{current_user.customer_id}")
    if not orders:
        # If cache miss, fetch orders from the function
        orders = get_latest_orders(current_user.customer_id)
        cache.set(f"order#{current_user.customer_id}", orders)
    # Dictionary for holding the top five items
    top_five = {}
    # If there are any orders...
    if orders:
        # Process each order.
        for order in orders:
            # Process each item in the order.
            for line_item in order['line_items']:
                # Get the item's name.
                item_name = line_item['name']
                # if item_name is not in top_five, add it to top_five with value 1
                if item_name not in top_five:
                    top_five[item_name] = 1
                # else, increment the value by 1
                else:
                    top_five[item_name] += 1
        # Sort the top five dictionary by value (descending) and slice the top five items.
        top_five = dict(sorted(top_five.items(), key=lambda item: item[1], reverse=True)[:5])
        # Print top five items for debugging
        print("Top Five Items:", top_five)
        return render_template('topfive.html', top_five=top_five)
    else:
        flash("No orders exist.")
        return redirect(url_for('index'))
    
@login_required
@app.route('/orders/topfive2', methods=['GET', 'POST'])
# fetch the top five most expensive items from your database or API.
def topfive2():
    # retrieve the five most expensive items for the current user
    # Try fetching from the cache
    orders = cache.get(f"order#{current_user.customer_id}")
    if not orders:
        # If cache miss, fetch orders from the function
        orders = get_latest_orders(current_user.customer_id)
        cache.set(f"order#{current_user.customer_id}", orders)
    # Dictionary for holding the top five items
    top_five2 = {}
    # If there are any orders...
    if orders:
        # Process each order.
        for order in orders:
            # Process each item in the order.
            for line_item in order['line_items']:
                # Get the item's name.
                item_name = line_item['name']
                # Get the item's price.
                item_price = line_item['base_price_money']['amount'] / 100
                # if item_name is not in top
                if item_name not in top_five2:
                    top_five2[item_name] = item_price
                # else, increment the value by 1
                else:
                    top_five2[item_name] += item_price
        # Sort the top five dictionary by value (descending) and slice the top five items.
        top_five2 = dict(sorted(top_five2.items(), key=lambda item: item[1], reverse=True)[:5])
        # Print top five items for debugging
        print("Top Five Items:", top_five2)
        return render_template('topfive2.html', top_five2=top_five2)
    else:
        flash("No orders exist.")
        return redirect(url_for('index'))
