'''
CS3250 - Software Development Methods and Tools - Fall 2023
Instructor: Thyago Mota
Student: 
Description: Project 2 - Queen Soopers Web App
'''

import os, uuid, sys
from csv import DictReader
from time import sleep
from square.client import Client

square = Client(
    access_token=os.environ['SQUARE_ACCESS_TOKEN'],
    environment='sandbox')

if len(sys.argv) != 3: 
    print('Use: python3 src/orders_ingest.py <user_id> <customer_id>')
    sys.exit(1)
user_id = sys.argv[1]
customer_id = sys.argv[2]
with open(f'data/{user_id}_orders.csv', 'rt') as f: 
    csv = DictReader(f)
    order = None
    for row in csv: 
        if not order:
            order = {
                'location_id': os.environ['LOCATION_ID'],
                'customer_id': customer_id,
                'line_items': [ ], 
                'metadata': {
                    'created_at': row['date']
                }
            }
        if row['date'] != order['metadata']['created_at']:
            result = square.orders.create_order(
                body = { 
                    'idempotency_key': str(uuid.uuid4()), 
                    'order': order
                }
            )
            if result.is_success():
                order = result.body['order']
                print(f"{order['id']}")
                sleep(2)
            else:
                print(result.errors)
            order = {
                'location_id': os.environ['LOCATION_ID'],
                'customer_id': customer_id,
                'line_items': [ ], 
                'metadata': {
                    'created_at': row['date']
                }
            }
        item = {
            'name': row['item'],
            'quantity': '1',
            'base_price_money': {
                'amount': int(float(row['paid']) * 100),
                'currency': 'USD'
            }, 
            'metadata': {
                'upc': row['upc']
            }
        }
        order['line_items'].append(item)
# last order
if order: 
    result = square.orders.create_order(
        body = { 
            'idempotency_key': str(uuid.uuid4()), 
            'order': order
        }
    )
    if result.is_success():
        order = result.body['order']
        print(f"{order['id']}")
    else:
        print(result.errors)