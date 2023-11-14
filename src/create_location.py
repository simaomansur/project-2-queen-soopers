'''
CS3250 - Software Development Methods and Tools - Fall 2023
Instructor: Thyago Mota
Student: 
Description: Project 2 - Queen Soopers Web App
'''

import os
from square.client import Client

square = Client(
    access_token=os.environ['SQUARE_ACCESS_TOKEN'],
    environment='sandbox')

location = {
    'name': 'Queen Soopers Denver'
}

result = square.locations.create_location(
        body = { 'location': location }
    )
    
if result.is_success():
    location = result.body['location']
    print(f"Location {location['name']} with id {location['id']} created successfully!")
else:
    print(result.errors)