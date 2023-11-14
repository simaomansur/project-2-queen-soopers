'''
CS3250 - Software Development Methods and Tools - Fall 2023
Instructor: Thyago Mota
Student: 
Description: Project 2 - Queen Soopers Web App
'''

import logging
import os
from square.client import Client

square = Client(
    access_token=os.environ['SQUARE_ACCESS_TOKEN'],
    environment='sandbox')
# Environment variables:
# 'SQUARE_ACCESS_TOKEN' = ""
# 'LOCATION_ID' = ""

# Helper functions

# returns the latest (last 100) orders given the id of a customer 
def get_latest_orders(customer_id):
    # Access the Orders API
    orders_api = square.orders
    location_ids = [os.environ['LOCATION_ID']]
    # Define the search parameters
    body = {
        "location_ids": location_ids,
        "query": {
            "filter": {
                "customer_filter": {
                    "customer_ids": [customer_id]  # Wrap the customer_id inside a list
                }
            },
        },
        "limit": 100  # or however many orders you want to retrieve
    }
    # Search for the orders
    result = orders_api.search_orders(body=body)
    # Check if the request was successful
    if result.is_success():
        if 'orders' in result.body:
            orders = result.body['orders']
            return orders
        else:
            print("No 'orders' key in the response body.")
            return []
    elif result.is_error():
        print(result.errors)  # Log the error
        return None  # or handle this case as appropriate for your application

# print(latest_orders)
def get_order(order_id): 
    # Access the Orders API
    orders_api = square.orders
    # Define the search parameters
    body = {
        "order_ids": [order_id]  # Expecting a single order_id
    }
    # Search for the orders
    result = orders_api.batch_retrieve_orders(body=body)
    # Check if the request was successful
    if result.is_success():
        orders = result.body.get('orders', [])
        if orders:
            order = orders[0]  # Assume the first order is the one we're looking for
            detailed_items = []  # List to hold detailed item info
            for line_item in order.get('line_items', []):
                # Extract the necessary information from each line item.
                item_info = {
                    'id': order_id,
                    'date': order.get('metadata', {}).get('created_at', ''),
                    'upc': line_item.get('metadata', {}).get('upc', ''),
                    'item': line_item.get('name', ''),
                    'paid': line_item.get('base_price_money', {}).get('amount', 0) / 100  # Convert from cents to dollars
                }
                detailed_items.append(item_info)
            return detailed_items  # Return detailed items directly
        else:
            logging.warning("No orders found in the response for order_id: %s", order_id)
            return None
    elif result.is_error():
        logging.error("Error occurred while retrieving order: %s", result.errors)
        return None  # Consistent return type
    return None  # Fallback in case of unexpected issues
