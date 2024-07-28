from libraries import *
import time

class baseCleaner:
    def __init__(self, data):
        self.data = data

    def check_encoding(self): # check the encoding method as not all files can be read using 'UTF-8'
        with open(self.data,'rb') as file:
                result = chardet.detect(file.read(15000))
                return result['encoding']
        
    def sorting_index(self):
        self.data.sort_index(inplace=True)
        return self
    
    def drop_unnecessary(self, cols):
        self.data = self.data.drop(columns=cols, axis=1)
        return self
    
    def drop_duplicates(self):
        self.data = self.data.drop_duplicates()
        return self
    def chosen_columns(self, cols):
        self.data = self.data[cols]
        return self
    
        # Dealing with Unknow Cities
    def fillingCityfromLocation(self , inst):
        for index , row in self.data.iterrows():
            if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                if row['city'] == 'Unknown' or pd.isna(row['city']):
                    try: 
                        response = inst.reverse(f"{row['latitude']},{row['longitude']}" , language='en')
                        city = response.raw['address']
                        if 'city' in city.keys(): 
                            self.data.at[index, 'city'] = city['city']
                        elif 'town' in city.keys():
                            self.data.at[index, 'city'] = city['town']
                        elif 'village' in city.keys():
                            self.data.at[index, 'city'] = city['village']
                        elif 'county' in city.keys():
                            self.data.at[index, 'city'] = city['county']
                        elif 'state' in city.keys():
                            self.data.at[index, 'city'] = city['state']
                        else:
                            self.data.at[index, 'city'] = city['country']
                    except:
                        continue
                else:    
                    continue
            else:
                continue
        return self
    # Dealing with Unknow Locations
    def fillingLocationFromCity(self , inst):
        for index , row in self.data.iterrows():
            if pd.isna(row['latitude']) and pd.isna(row['longitude']):
                try:
                    if pd.notna(row['city']): 
                        location = inst.geocode(row['city'])
                        row['latitude'] = location.latitude
                        row['longitude'] = location.longitude
                        print(row['city'], row['latitude'], row['longitude'])
                    else:
                        location = inst.geocode(row['country_txt'])
                        row['latitude'] = location.latitude
                        row['longitude'] = location.longitude
                        print(row['country_txt'], row['latitude'], row['longitude'])
                except:
                    continue
        return self
    def finalizing(self):
        self.data['city'] = self.data['city'].replace({'Unknown': 'New York City'})
        self.data = self.data.dropna()
        return self    

class pandasCleaner(baseCleaner):
    def __init__(self, data):
        super().__init__(data)

    def pdloader(self):
        encoder = self.check_encoding()
        try:
            self.data = pd.read_csv(self.data, encoding=encoder)
            return self
        except:
            self.data = pd.read_csv(self.data, encoding='utf-8')
            return self
    
    def converting_numeric(self):
        self.data['success'] = self.data['success'].replace({1 : "Yes" , 0 : "No"})
        self.data['suicide'] = self.data['suicide'].replace({1:"Yes" , 0 : "No"})
        self.data['individual'] = self.data['individual'].replace({1:"Yes" , 0: "No"})
        self.data['property'] = self.data['property'].replace({0:"No" , 1: "Yes" , -9: "Unknown"})
        self.data['doubtterr'] = self.data['doubtterr'].replace({1.: "Yes" , 0:"No", -9:"Unknown"})
        self.data['extended'] = self.data['extended'].replace({0:"No" , 1:"Yes"})
        return self
    
    def missing_values(self):
        kills_median = self.data['nkill'].median()
        wounded_median = self.data['nwound'].median()
        doubtterrmode = self.data['doubtterr'].mode()[0]
        nationalitymode = self.data['natlty1_txt'].mode()[0]
        targetmode = self.data['target1'].mode()[0]
        #-------------------------------------------------------------
        self.data['nkill'].fillna(value = kills_median , inplace= True)
        self.data['nkill'] = self.data['nkill'].astype(int)
        self.data['nwound'].fillna(value = wounded_median , inplace = True)
        self.data['nwound'] = self.data['nwound'].astype(int)
        self.data['doubtterr'] = self.data['doubtterr'].fillna(value = doubtterrmode)
        self.data['natlty1_txt'] = self.data['natlty1_txt'].fillna(value = nationalitymode)
        self.data['target1'] = self.data['target1'].fillna(value = targetmode)
        return self
    
    def drop_columns(self, percent): 
        percentage = self.data.isna().sum() / self.data.shape[0] * 100
        nullPerc = pd.DataFrame(percentage.sort_values(ascending=False)).reset_index()
        nullPerc.columns = ['Cols', 'Percentage']
        colmns = nullPerc[nullPerc['Percentage'] >= percent]
        dropped = colmns['Cols'].values
        #print('Dropped Columns:', dropped)
        self.data.drop(columns=dropped,axis = 1, inplace=True)
        return self

class daskCleaner(baseCleaner):
    def __init__(self, data):
        super().__init__(data)
    def ddloader(self):
        encoder = self.check_encoding()
        dtype = {
            'approxdate': 'object', 'attacktype2_txt': 'object', 'attacktype3_txt': 'object',
            'claimmode2_txt': 'object', 'claimmode3_txt': 'object', 'corp2': 'object', 'corp3': 'object',
            'divert': 'object', 'doubtterr': 'float64', 'gname2': 'object', 'gname3': 'object',
            'gsubname': 'object', 'gsubname2': 'object', 'gsubname3': 'object', 'hostkidoutcome_txt': 'object',
            'multiple': 'float64', 'natlty1': 'float64', 'natlty2_txt': 'object', 'natlty3_txt': 'object',
            'ransom': 'float64', 'ransomnote': 'object', 'related': 'object', 'target2': 'object',
            'target3': 'object', 'targsubtype1': 'float64', 'targsubtype2_txt': 'object',
            'targsubtype3_txt': 'object', 'targtype2_txt': 'object', 'targtype3_txt': 'object',
            'weapsubtype2_txt': 'object', 'weapsubtype3_txt': 'object', 'weaptype2_txt': 'object',
            'weaptype3_txt': 'object','guncertain1': 'float64',
            'ishostkid': 'float64',
            'resolution': 'object',
            'specificity': 'float64',
            'weapsubtype4_txt': 'object',
            'weaptype4_txt': 'object'
        }
        try:
            self.data = dd.read_csv(self.data, encoding=encoder , dtype=dtype)
            return self
        except:
            self.data = dd.read_csv(self.data, encoding='utf-8' , dtype=dtype)
            return self
    def drop_columns(self, percent): 
        percentage = self.data.isna().sum().compute() / len(self.data) * 100
        nullPerc = pd.DataFrame(percentage.sort_values(ascending=False)).reset_index()
        nullPerc.columns = ['Cols', 'Percentage']
        colmns = nullPerc[nullPerc['Percentage'] >= percent]
        dropped = colmns['Cols'].values
        self.data = self.data.drop(columns=dropped)
        return self
    def converting_numeric(self):
        self.data['success'] = self.data['success'].map({1 : "Yes" , 0 : "No"})
        self.data['suicide'] = self.data['suicide'].map({1:"Yes" , 0 : "No"})
        self.data['individual'] = self.data['individual'].map({1:"Yes" , 0: "No"})
        self.data['property'] = self.data['property'].map({0:"No" , 1: "Yes" , -9: "Unknown"})
        self.data['doubtterr'] = self.data['doubtterr'].map({1.: "Yes" , 0:"No", -9:"Unknown"})
        self.data['extended'] = self.data['extended'].map({0:"No" , 1:"Yes"})
        return self
    
    def missing_values(self):
        kills_median = self.data['nkill'].median_approximate()
        wounded_median = self.data['nwound'].median_approximate()
        doubtterrmode = self.data['doubtterr'].mode()[0]
        nationalitymode = self.data['natlty1_txt'].mode()[0]
        targetmode = self.data['target1'].mode()[0]
        self.data['nkill'] = self.data['nkill'].fillna(value=kills_median).astype(int)
        self.data['nwound'] = self.data['nwound'].fillna(value=wounded_median).astype(int)
        self.data['doubtterr'] = self.data['doubtterr'].fillna(value=doubtterrmode)
        self.data['natlty1_txt'] = self.data['natlty1_txt'].fillna(value=nationalitymode)
        self.data['target1'] = self.data['target1'].fillna(value=targetmode)
        return self
