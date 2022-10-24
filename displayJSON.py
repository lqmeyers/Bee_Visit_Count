##Program to display visits.json as a table

from tabulate import tabulate
import json 
from pandas import DataFrame  
import numpy as np

#file = 'visits.json'

def displayPerFlower(file='visits.json'):
    '''creates a table displaying visits per flower from visits.json'''
    red = json.load(open(file))
    for v in range(len(red['Statistics']['Visits_per_Flower'])):
        #print(v)
        red['Statistics']['Visits_per_Flower'][str(v)] = [red['Statistics']['Visits_per_Flower'][str(v)]]
        red['Statistics']['Visits_per_Flower']['Flower '+str(v)] = red['Statistics']['Visits_per_Flower'].pop(str(v))
        #print(red['Statistics']['Visits_per_Flower'][v])
    print(tabulate(red['Statistics']['Visits_per_Flower'],headers='keys',tablefmt='fancy_grid'))

def displayPerInd(file='visits.json'):
    '''creates a table displaying visits per
    track_id from visits.json'''
    red = json.load(open(file))
    '''
    for v in range(len(red['Statistics']['Visits_per_Flower'])):
        #print(v)
        red['Statistics']['Visits_per_Flower'][str(v)] = [red['Statistics']['Visits_per_Flower'][str(v)]]
        red['Statistics']['Visits_per_Flower']['Flower '+str(v)] = red['Statistics']['Visits_per_Flower'].pop(str(v))
    '''
    print(tabulate(red['Statistics']['Visits_per_Individual']))

#displayPerInd()