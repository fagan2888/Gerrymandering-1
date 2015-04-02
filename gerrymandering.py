from pyGDsandbox import dataIO
import pandas as pd
import numpy as np
import re
import unicodedata
'''
README:
The Congress object reads in the dbf file from the 114 congressional district
tigerline shapefile and merges in data about each representative. Note that
states that are majoritarian or otherwise do not allocate representatives by
districting recieve NaNs for their representative data.
'''


class Congress(object):
    def __init__(self):
        self.path = "/Users/LaughingMan/Desktop/projects/gerrymandering/"
        self.dbf = None
        self.district_to_fips = None
        self.all_rep_info = None
        self.merged = None

    def load(self, path=None):
        '''
        INPUT: directory of relelvant data files. Note the default is set to
               my personal directory.
        OUTPUT: None.

        This method merely reads the data into the congress object from the
        specified directory. In this case, it needs the shapefile, a file that
        maps between districts/states and their fips codes, and a file with
        representative/district/state information.
        '''
        if path:
            self.path = path
        else:
            path = self.path
        self.dbf = dataIO.dbf2df(path +
                                 "tl_2014_us_cd114/tl_2014_us_cd114.dbf")
        self.district_to_fips = pd.read_csv(path +
                                            "national_cd113.txt",
                                            sep=r"\s\s+")
        self.all_rep_info = pd.read_excel(path + 'excel-labels-114.xls',
                                          page=0)

    def clean_district_to_fips(self):
        '''
        INPUT: None.
        OUTPUT: None.

        This prepares the fips mapping file for merging.
        '''
        district_to_fips = self.district_to_fips
        district_to_fips['DISTRICT'] = \
            district_to_fips['NAMELSAD']\
            .apply(lambda x: re.findall('not|Large|[0-9]+', x)[0])
        district_to_fips['DISTRICT'] = \
            district_to_fips['DISTRICT']\
            .apply(lambda x: '0' + x if len(x) == 1 else x)
        cnames = ['STATE', 'STATEFP', 'CD114FP', 'NAMELSAD', 'DISTRICT']
        district_to_fips.columns = cnames
        district_to_fips['CD114FP'] = \
            district_to_fips['CD114FP']\
            .apply(lambda x: '0' + x if len(x) == 1 else x)
        district_to_fips['CD114FP'] = \
            district_to_fips['CD114FP']\
            .apply(lambda x: '00' if x == 'ZZ' else x)
        self.district_to_fips = district_to_fips

    def clean_all_rep_info(self):
        '''
        INPUT: None.
        OUTPUT: None.

        This prepares the representatives file for merging.
        '''
        all_rep_info = self.all_rep_info
        keep_columns = ['FirstName', 'LastName', '114 St/Dis', 'Party']
        all_rep_info = all_rep_info[keep_columns]
        all_rep_info.columns = ['first_name', 'last_name', 'stdis', 'party']
        all_rep_info['STATE'] = \
            all_rep_info['stdis'].apply(lambda x: x[0:2])
        all_rep_info['DISTRICT'] = \
            all_rep_info['stdis'].apply(lambda x: x[2:5])
        all_rep_info = all_rep_info.drop('stdis', axis=1)
        self.all_rep_info = all_rep_info

    def clean_dbf(self):
        '''
        INPUT: None.
        OUTPUT: None.

        This prepares the dbf file for merging.
        '''
        dbf = self.dbf
        dbf['CD114FP'] = \
            dbf['CD114FP'].apply(lambda x: '00' if x == 'ZZ' else x)
        dbf['STATEFP'] = \
            dbf['STATEFP'].apply(lambda x: int(x))
        self.dbf = dbf

    def mergers(self):
        '''
        INPUT: None.
        OUTPUT: None.

        This merges all the data.
        '''
        merged = self.dbf.merge(self.district_to_fips)
        merged = pd.merge(merged, self.all_rep_info, how='inner',
                          on=['DISTRICT', 'STATE'])
        self.merged = merged

    def _describe(self):
        '''
        INPUT: None.
        OUTPUT: None.

        This prints the head of each of the data frames in the object.
        '''
        print 'district_to_fips'
        print self.district_to_fips.head()
        print 'dbf'
        print self.dbf.head()
        print 'all_rep_info'
        print self.all_rep_info.head()
        print 'merged'
        print self.merged.head()
        print self.merged.shape

    def write(self):
        '''
        INPUT: None.
        OUTPUT: None.

        This writes the merged dataframe to the previous dbf.
        '''
        dataIO.df2dbf(self.merged,
                      self.path + "tl_2014_us_cd114/tl_2014_us_cd114.dbf")

if __name__ == '__main__':
    c = Congress()
    c.load()
    c.clean_district_to_fips()
    c.clean_all_rep_info()
    c.clean_dbf()
    c.mergers()
    #c.write()
