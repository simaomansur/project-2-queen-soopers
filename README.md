[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/hu9ddNip)
# Overview

You are a software developer who works for **Queen Soopers**, a supermarket chain. All purchases made by **Queen Soopers** customers who have joined the chain's loyalty program are recorded on [Square](https://squareup.com/), a financial services platform aimed at small and medium-sized businesses. **Queen Soopers** stakeholders would like to allow their customers to view their most recent purchases and gain insights into their purchasing habits. With the aim of developing an online platform that meets this product vision, a Scrum Team was formed, having Mr. T appointed as Product Owner (PO) of the software product to be developed Mr. T kicked off the project by creating 6 (six) user stories (product backlog items). 

The deadline for this project is set to 3 (three) weeks, to be developed in 3 one-week sprints. Sprint planning meetings will take no longer than 15m. The Scrum Team must use [Jira](https://onlinejira.com/) as the project management tool. The team should elect a Scrum Master among themselves. The Scrum Master will create the project on Jira and invite Mr. T to join the project. Mr. T will held Sprint Planning meetings with each team on Thursdays during the 2nd half of class. The Scrum Master will organize Daily Scrums with the developers. 

![Queen Soopers Logo](pics/pic1.png)

Queen Soopers Logo

# User Stories

The user stories are described in descending order of their value. 

## US#1

*As a user, I want to register on the online platform so that I can have my shopping recorded. Given that a user provides a unique ID, their name, email, and password, when the user clicks on the "Sign Up" button then their user information is saved and a customer profile is created.*

Additional Information: 

* In addition to having user information saved in the online platform's database for authentication purposes, a customer profile must be created on Square
* Square customer IDs must be linked to the online platform user ID.
* To test the application, at least 2 (two) users must be created: 
    * User ID "jane" linked to customer "Jane Austen" with email "jausten@gmail.com"; and 
        customer ID = RGG60F4C9ZWDP06ZKSRQRGZG5C
    * User ID "bob" linked to customer "Bob Marley" with email "bmarley@gmail.com". 
        customer ID = WADHYN712SVP28BR7HNAGCD5ZW
* After creating the 2 users above, purchased items must be uploaded to each of the respective linked customer profiles on Square (see Setup section). 

## US#2

*As a registered user, I want to log in to the online platform so I can retrieve the most recent purchases associated with my Square customer profile. Since a registered user has provided their ID and password, when the registered user clicks the “Sign In” button then, if their credentials are valid, they are presented with a list of the most recent purchases associated with their Square customer profile; otherwise, an error message is returned.*

Additional Information: 

* By "most recent purchases" assume the last 100 purchases. 
* By default, Square's "search order" returns the orders in chronological order (most recent orders first); use parameter "limit" to specify that you want the last 100 purchases. 

## US#3

*As an authenticated user, I want to retrieve all items from a given order so I can check how much I paid for each item. Given that an authenticated user views a list of orders, when they selects one of the orders, all order items are displayed, including its "upc" number, its description and the price paid.* 

* To avoid unnecessary calls to Square, the implemented solution must first check if the order information is in the local cache. 
* In the case of a "cache miss", the order information must be retrieved from Square and saved in the local cache for future use. 

## US#4

*As an authenticated user, I want to know how much I am spending on purchases each month so I can better control my expenses. Once an authenticated user selects a specific option, the amount spent on purchases each month (among the most recent purchases) is returned in the form of a table or graph.*

* This user story requires all items purchased in the most recent orders to be summarized. 
* Therefore, use of cache is necessary (see US#3).
 

## US#5

*As an authenticated user, I want to know which items I buy most often so I can learn more about my shopping habits. Once an authenticated user selects a specific option, the most frequently purchased items (among the most recent purchases) are returned in the form of a table or graph.*

* By "most frequently purchased items" assume the top 5 (five) items.
* This user story requires all items purchased in the most recent orders to be summarized. 
* Therefore, use of cache is necessary (see US#3). 

## US#6

*As an authenticated user, I want to know what the most expensive items I purchased were so I can better control my spending. Once an authenticated user selects a specific option, the most expensive items purchased (among the most recent purchases) are returned as a table or graph.* 

* By "most expensive items" assume the top 5 (five) items.
* This user story requires all items purchased in the most recent orders to be summarized. 
* Therefore, use of cache is necessary (see US#3).

# Setup 

Start by signing up as a developer on [Square](https://squareup.com/signup?country_code=us&v=developers). Then go to [https://developer.squareup.com/apps](https://developer.squareup.com/apps) and create an app called "Queen Soopers" (you can safelly skip all the questions when prompted). Create an environment variable named "SQUARE_ACCESS_TOKEN" and assign your app's access token to it. 

For the Flask app setup, create a virtual environment and install the packages in **requirements.txt**. As done in the previous project, create the two environment variables: "FLASK_APP" and "SECRET_KEY". The basic structure of the app is shared with you. An extra module called **square** was added to setup Square's API client. We suggest adding to this module helper functions that you may need when communicating with the API. One of them is described so you can get the idea. 

The first script you should run is [/src/create_location.py](src/create_location.py). Save the store's location ID and create an environment variable named "LOCATION_ID". Once your get the **sign-in** functionality to work, create users *jane* and *bob*, saving their customer's ID. Of course, you can only do that after completing US#1. After a successful sign-up, have your procedure display the customer ID linked to the account and returned by Square.

Next, proceed to the data ingestion part by running the [/src/orders_ingest.py](src/orders_ingest.py) script. The script requires the user ID ("jane" or "bob") and their correspondent customer ID. Since the data load will be performed by the script, as opposed to customers actually shopping, all orders will be created on the same date, which is undesirable. To workaround this problem, the [/src/orders_ingest.py](src/orders_ingest.py) script adds a "created_at" field in each Order's metadata with the date of the shopping. Also, the same script adds a "upc" field in each Item's metadata with the UPC (Universal Product Code). UPC is important to uniquely identify an item purchased. 

Square's API documentation is found at [https://developer.squareup.com/reference/square](https://developer.squareup.com/reference/square).

# Caching 

As mentioned before, one of the technical requirements of this project is to incorporate caching. **Flask-Caching** is a module that adds caching support to Flask. The following lines were added to **__init__.py**, which sets the caching timeout to 5 minutes. 

```
# cache setup
from flask_caching import Cache
cache = Cache()
cache.init_app(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})
```

The example below illustrates how to use caching to query for an order given its id (recorded in variable **order_id**). 

```
from app import cache

order = cache.get(f"order#{order_id}")
if not order: 
    # cache miss!
    order = get_order(order_id) # call to Square API
    cache.set(f"order#{order_id}", order)
```

# Project Evaluation

More important than completion, your team will be evaluated on how close you managed this project according to the Scrum framework and how well you worked as a Srcum team. Each user story must have a clear estimate of effort in terms of points. Each sprint must have a clear set of goals. The team must take notes of their daily scrum meetings. There should also be notes for the sprint review and retrospective meetinsg at the end of each sprint. See the [/scrum] folder for a sprint documentation template. You should create one file for each sprint, named *sprint#.md* replace the pound with the number of the sprint. 

# Rubric 

+25 for each sprint, divided like the following:

    +5 sprint created and managed on Jira

    +5 sprint planning (from notes)

    +5 sprint daily scrums (from notes)

    +5 sprint review (from notes)

    +5 sprint retrospective (from notes)

+10 burn up/down chart showing steady progress (you will loose points if the chart shows burst of work towards the end of the project, for example)

+15 team/self evaluation