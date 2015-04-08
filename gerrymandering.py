from pyGDsandbox import dataIO
import pandas as pd
import numpy as np
import re
import unicodedata
import shapefile
from shapely.geometry import Polygon
import math
from scipy import stats
'''
README:
The Congress object reads in the dbf file from the 113 congressional district
shapefile and merges in data about each representative. Note that
states that are majoritarian or otherwise do not allocate representatives by
districting recieve NaNs for their representative data. Representative data
is current (Apr 2015). 
'''


class Congress(object):
    def __init__(self):
        self.path = "/Users/LaughingMan/Desktop/projects/gerrymandering/"
        self.dbf = None
        self.district_to_fips = None
        self.all_rep_info = None
        self.merged = None
        self.sf = None

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
                                 "cb_2013_us_cd113_20m/" +
                                 "cb_2013_us_cd113_20m.dbf")
        self.district_to_fips = pd.read_csv(path +
                                            "national_cd113.txt",
                                            sep=r"\s\s+")
        self.all_rep_info = pd.read_excel(path + 'excel-labels-114.xls',
                                          page=0)
        self.sf = shapefile.Reader(path + "cb_2013_us_cd113_20m/" +
                                   "cb_2013_us_cd113_20m")

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
        cnames = ['STATE', 'STATEFP', 'CD113FP', 'NAMELSAD', 'DISTRICT']
        district_to_fips.columns = cnames
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
        all_rep_info = all_rep_info[~pd.isnull(all_rep_info['first_name'])]
        all_rep_info['first_name'] = \
            all_rep_info['first_name']\
            .apply(lambda x: x.encode('ascii', 'ignore'))
        all_rep_info['last_name'] = \
            all_rep_info['last_name']\
            .apply(lambda x: x.encode('ascii', 'ignore'))
        all_rep_info['party'] = \
            all_rep_info['party']\
            .apply(lambda x: x.encode('ascii', 'ignore'))
        all_rep_info = all_rep_info.drop('stdis', axis=1)
        self.all_rep_info = all_rep_info

    def clean_dbf(self):
        '''
        INPUT: None.
        OUTPUT: None.

        This prepares the dbf file for merging.
        '''
        dbf = self.dbf
        dbf['CD113FP'] = \
            dbf['CD113FP'].apply(lambda x: '00' if x == 'ZZ' else x)
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
        merged = pd.merge(merged, self.all_rep_info, how='left',
                          on=['DISTRICT', 'STATE'])
        self.merged = merged

    def describe(self):
        '''
        INPUT: None.
        OUTPUT: None.

        This prints the head of each of the data frames in the object.
        '''
        print 'district_to_fips', self.district_to_fips.shape
        print self.district_to_fips.head()
        print 'dbf', self.dbf.shape
        print self.dbf.head()
        print 'all_rep_info', self.all_rep_info.shape
        print self.all_rep_info.head()
        print 'merged', self.merged.shape
        print self.merged.head()

    def metrics(self):
        '''
        INPUT: None.
        OUTPUT: None.

        This creates metrics for compactness of all the shapes in the data
        frame.
        '''
        Polsby_Popper = []
        Schwartzberg = []
        Convex_Hull = []
        Reock = []
        for s in self.sf.iterShapes():
            poly = Polygon(s.points)
            Polsby_Popper\
                .append((poly.length ** 2) / (poly.area * 4 * math.pi))
            Schwartzberg\
                .append(poly.length / (2 * (math.pi * poly.area) ** .5))
            Convex_Hull\
                .append(poly.convex_hull.area / poly.area)
            bbox = poly.bounds
            radius = max(abs(bbox[0]-bbox[2]), abs(bbox[1]-bbox[3]))/2
            Reock.append(math.pi * (radius ** 2) / poly.area)

        Polsby_Popper = [x / max(Polsby_Popper) for x in Polsby_Popper]
        Schwartzberg = [x / max(Schwartzberg) for x in Schwartzberg]
        Convex_Hull = [x / max(Convex_Hull) for x in Convex_Hull]
        Reock = [x / max(Reock) for x in Reock]
        Polsby_Popper = \
            [stats.percentileofscore(Polsby_Popper, a, 'weak') \
                for a in Polsby_Popper]
        Schwartzberg = \
            [stats.percentileofscore(Schwartzberg, a, 'weak') \
                for a in Schwartzberg]
        Convex_Hull = \
            [stats.percentileofscore(Convex_Hull, a, 'weak') \
                for a in Convex_Hull]
        Reock = \
            [stats.percentileofscore(Reock, a, 'weak') for a in Reock]

        self.merged['Polsby_Popper'] = Polsby_Popper
        self.merged['Schwartzberg'] = Schwartzberg
        self.merged['Convex_Hull'] = Convex_Hull
        self.merged['Reock'] = Reock

    def write(self):
        '''
        INPUT: None.
        OUTPUT: None.

        This writes the merged dataframe to the previous dbf and creates an
        ID column.
        '''
        self.merged['ID'] = self.merged['STATE'] + self.merged['CD113FP']
        dataIO.df2dbf(self.merged,
                      self.path + "cb_2013_us_cd113_20m/" +
                      "cb_2013_us_cd113_20m.dbf")

if __name__ == '__main__':
    c = Congress()
    c.load()
    c.clean_district_to_fips()
    c.clean_all_rep_info()
    c.clean_dbf()
    c.mergers()
    c.metrics()
    c.describe()
    c.write()
