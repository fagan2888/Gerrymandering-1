from pyGDsandbox import dataIO
import time
import datetime
from datetime import datetime
import pandas as pd
import numpy as np
import re
import unicodedata

states = {'AK': 'Alaska' ,'AL': 'Alabama', 'AR': 'Arkansas',
          'AS': 'American Samoa', 'AZ': 'Arizona', 'CA': 'California',
          'CO': 'Colorado', 'CT': 'Connecticut', 'DC': 'District of Columbia',
          'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'GU': 'Guam',
          'HI': 'Hawaii', 'IA': 'Iowa', 'ID': 'Idaho', 'IL': 'Illinois',
          'IN': 'Indiana', 'KS': 'Kansas', 'KY': 'Kentucky',
          'LA': 'Louisiana', 'MA': 'Massachusetts', 'MD': 'Maryland',
          'ME': 'Maine', 'MI': 'Michigan', 'MN': 'Minnesota',
          'MO': 'Missouri', 'MP': 'Northern Mariana Islands',
          'MS': 'Mississippi', 'MT': 'Montana', 'NA': 'National',
          'NC': 'North Carolina', 'ND': 'North Dakota', 'NE': 'Nebraska',
          'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico',
          'NV': 'Nevada', 'NY': 'New York', 'OH': 'Ohio', 'OK': 'Oklahoma',
          'OR': 'Oregon', 'PA': 'Pennsylvania', 'PR': 'Puerto Rico',
          'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota',
          'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VA': 'Virginia',
          'VI': 'Virgin Islands', 'VT': 'Vermont', 'WA': 'Washington',
          'WI': 'Wisconsin', 'WV': 'West Virginia', 'WY': 'Wyoming'
}


class Congress(object):
    def __init__(self):
        self.path = "/Users/LaughingMan/Desktop/projects/gerrymandering/"
        self.dbf = None
        self.district_to_fips = None
        self.all_rep_info = None
        self.merged = None
        self.all_fips = None

    def load(self, path = None):
        if path:
            self.path = path
        else:
            path = self.path

        self.dbf = dataIO.dbf2df(path +
            "tl_2014_us_cd114/tl_2014_us_cd114.dbf")
        self.district_to_fips = pd.read_csv(path +
            "national_cd113.txt", sep=r"\s\s+")
        self.all_rep_info = pd.read_excel(path + 'excel-labels-114.xls',
            page=0)
        self.all_fips = pd.read_excel(path + 'fips_codes_website.xls')

    def clean_district_to_fips(self):
        district_to_fips = self.district_to_fips
        district_to_fips['STATE'] = \
            district_to_fips['STATE'].apply(lambda x : states[x])
        district_to_fips['District'] = \
            district_to_fips['NAMELSAD'].apply(lambda x: re.findall('not|Large|[0-9]+', x)[0])
        district_to_fips = district_to_fips[['STATE', 'STATEFP', 'CD113FP', 'District']]
        cnames = ['STATE', 'STATEFP', 'CD114FP', 'DISTRICT']
        district_to_fips.columns = cnames
        cond1 = district_to_fips['DISTRICT'] != 'Large'
        cond2 = district_to_fips['DISTRICT'] != 'not'
        district_to_fips = district_to_fips[cond1 & cond2]
        district_to_fips['DISTRICT'] = district_to_fips['DISTRICT'].apply(lambda x: int(x))
        district_to_fips = district_to_fips[['STATE', 'STATEFP']]
        district_to_fips = district_to_fips.drop_duplicates()
        self.district_to_fips = district_to_fips

    def clean_all_rep_info(self):
        all_rep_info = self.all_rep_info
        keep_columns = ['FirstName', 'LastName', '114 St/Dis', 'Party']
        all_rep_info = all_rep_info[keep_columns]
        all_rep_info.columns = ['first_name', 'last_name', 'stdis', 'party']
        all_rep_info['State'] = all_rep_info['stdis'].apply(lambda x: x[0:2])
        all_rep_info['District'] = all_rep_info['stdis'].apply(lambda x: x[2:5])
        all_rep_info = all_rep_info.drop('stdis', axis=1)
        all_rep_info['State'] = all_rep_info['State'].apply(lambda x: x.encode('ascii', 'ignore'))
        all_rep_info['State'] = all_rep_info['State'].apply(lambda x: states[x])
        cnames = ['first_name', 'last_name', 'party', 'STATE', 'DISTRICT']
        all_rep_info.columns = cnames
        all_rep_info = all_rep_info[all_rep_info['DISTRICT'] != '00']
        all_rep_info['DISTRICT'] = all_rep_info['DISTRICT'].apply(lambda x: int(x))
        self.all_rep_info = all_rep_info

    def clean_dbf(self):
        dbf = self.dbf
        dbf['CD114FP'] = dbf['CD114FP'].apply(lambda x: int(x) if x != 'ZZ' else x)
        dbf['STATEFP'] = dbf['STATEFP'].apply(lambda x: int(x))
        dbf['DISTRICT'] = \
            dbf['NAMELSAD'].apply(lambda x: re.findall('not|Large|[0-9]+', x)[0])
        self.dbf = dbf

    def clean all_fips(self):
        all_fips = self.all_fips
        

    def mergers(self):
        self.merged = self.all_rep_info.merge(self.district_to_fips)
        #self.merged = self.dbf.merge(self.merged)

    def describe(self):
        print 'district_to_fips'
        print self.district_to_fips.head()
        print 'dbf'
        print self.dbf.head()
        print 'all_rep_info'
        print self.all_rep_info.head()
        print 'merged'
        print self.merged.head()
        print self.merged.shape
        print 'all_fips'
        print self.all_fips.head()

if __name__ == '__main__':
    c = Congress()
    c.load()
    c.clean_district_to_fips()
    c.clean_all_rep_info()
    c.clean_dbf()
    c.mergers()



# dbf = pd.merge(dbf, legislators, how='outer', on=['DISTRICT','STATENAME'])
# c.legislators.loc[400,'last_name']
# dal =  ['Alaska', 'Delaware', 'Montana', 'North Dakota', 'South Dakota', 'Vermont', 'Wyoming']
