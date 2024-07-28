from geopy.geocoders import Nominatim
from libraries import *
import time
import warnings
warnings.filterwarnings('ignore')
inst = Nominatim(user_agent ='mostafa') 
import baseCleaner as bc

datapath = 'Data/globalterrorismdb_0718dist.csv'
Unncessarycolumns = ['eventid','country','region','targsubtype1_txt','weapsubtype1_txt','attacktype1','targtype1','targsubtype1','natlty1','weaptype1','weapsubtype1', 'INT_LOG', 'INT_IDEO', 'INT_MISC','INT_ANY']
chosenColumns =  ['iyear', 'imonth', 'iday', 'extended', 'country_txt', 'region_txt',
        'city', 'latitude', 'longitude', 'doubtterr', 'success',
       'suicide', 'attacktype1_txt', 'targtype1_txt', 'target1', 'natlty1_txt',
       'gname', 'individual', 'weaptype1_txt', 'nkill',
       'nwound', 'property', 'dbsource']

def pandas_cleaner(path):
    pandas = bc.pandasCleaner(path)
    pandas.pdloader()
    pandas.drop_columns(20)    
    pandas.drop_unnecessary(Unncessarycolumns)
    pandas.drop_duplicates()
    pandas.sorting_index()
    pandas.chosen_columns(chosenColumns)
    pandas.drop_duplicates()
    pandas.converting_numeric()
    pandas.missing_values()
    pandas.drop_duplicates()    
#    print('done from pandas')
#     # #pandas.fillingCityfromLocation(inst)
#     # #pandas.fillingLocationFromCity(inst)
#     # #pandas.finalizing()

def dask_cleaner(path):
    dask = bc.daskCleaner(path)
    dask.ddloader()
    dask.drop_columns(20)
    dask.drop_unnecessary(Unncessarycolumns)
    dask.drop_duplicates()
    #dask.sorting_index()
    dask.chosen_columns(chosenColumns)
    dask.drop_duplicates()
    dask.converting_numeric()
    dask.missing_values()
    dask.drop_duplicates()
    #print('done from dask')
#     # #dask.fillingCityfromLocation(inst)
#     # #dask.fillingLocationFromCity(inst)
#     # #dask.finalizing()

def __main__():
    start = time.time()
    pandas_cleaner(datapath)
    print(f"Pandas Time: {time.time() - start}")
    start = time.time()
    dask_cleaner(datapath)
    print(f"Dask Time: {time.time() - start}")

if __name__ == "__main__":
    __main__()