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
        self.legislators = None
        self.district_to_fips = None
        self.name_to_district = None
        self.all_rep_info = None
        self.merged = None

    def load(self, path = None):
        if path:
            self.path = path
        else:
            path = self.path

        self.dbf = dataIO.dbf2df(path +
            "cb_2013_us_cd113_20m/cb_2013_us_cd113_20m.dbf")
        self.legislators = pd.read_csv(path + "legislators-current.csv")
        self.district_to_fips = pd.read_csv(path +
            "national_cd113.txt", sep=r"\s\s+")
        name_to_district = pd.read_html(path +
            'congress114.html', header = 0)
        self.name_to_district = name_to_district[0]
        self.all_rep_info = pd.read_excel(path + 'excel-labels-114.xls',
            page=0)

    def clean_legislators(self):
        legislators = self.legislators
        legislators = legislators[legislators['type']=='rep']
        legislators = legislators[['last_name', 'first_name', 'state', 'district', 'party']]
        for c in ['first_name', 'last_name']:
            legislators[c] = legislators[c].apply(lambda x: x.decode('unicode-escape'))
            legislators[c] = legislators[c].apply(lambda x: x.encode('ascii','ignore'))
        self.legislators = legislators

    def clean_district_to_fips(self):
        district_to_fips = self.district_to_fips
        district_to_fips['STATE'] = \
            district_to_fips['STATE'].apply(lambda x : states[x])
        district_to_fips['District'] = \
            district_to_fips['NAMELSAD'].apply(lambda x: re.findall('not|Large|[0-9]+',x)[0])
        district_to_fips = district_to_fips[['STATE', 'STATEFP', 'CD113FP', 'District']]
        cnames = ['STATE', 'STATEFP', 'CD113FP', 'DISTRICT']
        district_to_fips.columns = cnames
        cond1 = district_to_fips['DISTRICT'] != 'Large'
        cond2 = district_to_fips['DISTRICT'] != 'not'
        district_to_fips = district_to_fips[cond1 & cond2]
        district_to_fips['DISTRICT'] = district_to_fips['DISTRICT'].apply(lambda x: int(x))
        self.district_to_fips = district_to_fips

    def clean_name_to_district(self):
        name_to_district = self.name_to_district
        name_to_district['first_name'] = \
            name_to_district['Representative'].apply(lambda x: x.split(',')[0])
        name_to_district['last_name'] = \
            name_to_district['Representative'].apply(lambda x: x.split(',')[1].split(' ')[1])
        name_to_district['first_name'] = \
            name_to_district['first_name'].apply(lambda x: x.replace(' ', ''))
        name_to_district['last_name'] = \
            name_to_district['last_name'].apply(lambda x: x.replace(' ', ''))
        name_to_district['District'] = \
            name_to_district['District'].apply(lambda x: re.findall('Comm|Delegate|Large|[0-9]+',x)[0])
        name_to_district = \
            name_to_district[name_to_district['District'] != 'Delegate']
        name_to_district = name_to_district[['first_name', 'last_name',
                                             'State', 'District']]
        name_to_district['State'] = \
            name_to_district['State'].apply(lambda x: states[x])
        # for c in ['first_name', 'last_name']:
        #     name_to_district[c] = name_to_district[c].apply(lambda x: x.decode('unicode-escape'))
        #     name_to_district[c] = name_to_district[c].apply(lambda x: x.encode('ascii','ignore'))
        self.name_to_district = name_to_district

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

    def mergers(self):
        self.merged = self.all_rep_info.merge(self.district_to_fips)

    def describe(self):
        print 'legislators'
        print self.legislators.head()
        print 'name_to_district'
        print self.name_to_district.head()
        print 'district_to_fips'
        print self.district_to_fips.head()
        print 'dbf'
        print self.dbf.head()
        print 'all_rep_info'
        print self.all_rep_info.head()

if __name__ == '__main__':
    c = Congress()
    c.load()
    c.clean_legislators()
    c.clean_name_to_district()
    c.clean_district_to_fips()
    c.clean_all_rep_info()



# dbf = pd.merge(dbf, legislators, how='outer', on=['DISTRICT','STATENAME'])
# c.legislators.loc[400,'last_name']
# dal =  ['Alaska', 'Delaware', 'Montana', 'North Dakota', 'South Dakota', 'Vermont', 'Wyoming']
