from pyGDsandbox import dataIO
import pandas as pd
import numpy as np
import re
import unicodedata


class Congress(object):
    def __init__(self):
        self.path = "/Users/LaughingMan/Desktop/projects/gerrymandering/"
        self.dbf = None
        self.district_to_fips = None
        self.all_rep_info = None
        self.merged = None

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

    def clean_district_to_fips(self):
        district_to_fips = self.district_to_fips
        district_to_fips['DISTRICT'] = \
            district_to_fips['NAMELSAD'].apply(lambda x: re.findall('not|Large|[0-9]+', x)[0])
        district_to_fips['DISTRICT'] = district_to_fips['DISTRICT'].apply(lambda x: '0' + x if len(x) == 1 else x)
        cnames = ['STATE', 'STATEFP', 'CD114FP', 'NAMELSAD', 'DISTRICT']
        district_to_fips.columns = cnames
        district_to_fips['CD114FP'] = district_to_fips['CD114FP'].apply(lambda x: '0' + x if len(x) == 1 else x)
        district_to_fips['CD114FP'] = district_to_fips['CD114FP'].apply(lambda x: '00' if x == 'ZZ' else x)
        self.district_to_fips = district_to_fips

    def clean_all_rep_info(self):
        all_rep_info = self.all_rep_info
        keep_columns = ['FirstName', 'LastName', '114 St/Dis', 'Party']
        all_rep_info = all_rep_info[keep_columns]
        all_rep_info.columns = ['first_name', 'last_name', 'stdis', 'party']
        all_rep_info['STATE'] = all_rep_info['stdis'].apply(lambda x: x[0:2])
        all_rep_info['DISTRICT'] = all_rep_info['stdis'].apply(lambda x: x[2:5])
        all_rep_info = all_rep_info.drop('stdis', axis=1)
        self.all_rep_info = all_rep_info

    def clean_dbf(self):
        dbf = self.dbf
        dbf['CD114FP'] = dbf['CD114FP'].apply(lambda x: '00' if x == 'ZZ' else x)
        dbf['STATEFP'] = dbf['STATEFP'].apply(lambda x: int(x))
        self.dbf = dbf

    def mergers(self):
        merged = self.dbf.merge(self.district_to_fips)
        merged = pd.merge(merged, self.all_rep_info, how='inner', on=['DISTRICT','STATE'])
        self.merged = merged

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

if __name__ == '__main__':
    c = Congress()
    c.load()
    c.clean_district_to_fips()
    c.clean_all_rep_info()
    c.clean_dbf()
    c.mergers()
    c.describe()


# dbf = pd.merge(dbf, legislators, how='outer', on=['DISTRICT','STATENAME'])
# c.legislators.loc[400,'last_name']
# dal =  ['Alaska', 'Delaware', 'Montana', 'North Dakota', 'South Dakota', 'Vermont', 'Wyoming']
