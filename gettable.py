'''
Requires internet connection. These classes only work for time series data. Trying to input cross-sectional data returns None for gettable and getcsv.
gettable takes in a string (singstat.gov.sg tablebuilder code), and returns a dataframe.
getcsv takes in a string (singstat.gov.sg tablebuilder code), and returns a dataframe that's formatted to look like the csv you get from the singstat website.
combineCSV takes in a dictionary of {tablebuilder code:sheetnames} and a string for the output excel file.
'''
import json
import pandas as pd
import urllib.request

class gettable:
    '''Input a string - tablebuilder code. 
    .meta gives the metadata.
    .df gives the important values and columns in a DF.
    .getmeta ets the DOS table as a json (then parses it as nested dict).
    '''
    def __init__(self, code: str):
        self.code = code
        self.df = None
        self.meta = self.getmeta()['Data']
        try:
            self.meta['records']['tableType']            
        except:
            self.TSDF()
        else:
            self.CSDF()
    
    def getmeta(self):
        '''input table code, fetches json data, returns a dictionary'''
        mainurl = "https://tablebuilder.singstat.gov.sg/api/table/metadata/"+self.code
        try:
            openurl = urllib.request.urlopen(mainurl)
        except:
            return print(f"Can't open table with code '{self.code}'. Check manually.")
        else:
            return json.loads(openurl.read())    
    
    def getjson(self,offset):
        '''input table code, fetches json data, returns a dictionary'''
        mainurl = "https://tablebuilder.singstat.gov.sg/api/table/tabledata/"\
            +self.code +"?offset=" +str(offset)
        openurl = urllib.request.urlopen(mainurl)
        return json.loads(openurl.read())    
 
    def TSDF(self):
        '''Takes json data and stores dataframe of time series data in self.df
        i.e. everything in Data>row>columns.'''
        dic = {}
        offset = 0
        for j in range(self.numloops()):
            rows = self.getjson(offset)['Data']['row']
            tmp = self.getdictfromrows(rows) # Dict{rowtext:Dataframe (1 row of timeseries)}
            offset += 2000
            for key in tmp:
                if not dic: # empty dic, don't waste time
                    dic = tmp
                    break
                elif key in dic: # for incomplete rows, we want to merge the dataframes.
                    dic[key] = pd.concat([dic[key], tmp[key]])
                else: # add on new rows.
                    dic[key] = tmp[key]
        self.df = pd.concat(dic.values(),axis=1)

    def CSDF(self):
        pass

    def numloops(self):
        '''The DOS developer API limits json records to 2000 per request.
        This figures out how many times we should loop to get the whole table.'''
        metaurl = "https://tablebuilder.singstat.gov.sg/api/table/metadata/"+self.code
        metadata = json.loads(urllib.request.urlopen(metaurl).read())
        return metadata['Data']['records']['total'] //2000 +1
            
    def getdictfromrows(self,rows):
        '''input: rows = list of dicts, where dicts['columns'] accesses list of {k:v} 
        we make dataframe from dicts['columns'], then
        output: {rowtext:dataframe}'''
        dic = {i['rowText'] : pd.DataFrame(i['columns'])
             .rename(columns={'key':'Data Series','value':i['rowText']}) 
             .set_index('Data Series') for i in rows if i['columns']}
        return dic

class getcsv(gettable): 
    '''
    inherits from gettable - instantiate with tablebuilder code.
    .csv gives a dataframe that's meant to be converted into excel sheets that resemble the
    formatting given when you download the csvs directly from singstat.gov.sg.
    
    .toCSV calls the 3 methods and with its own .df, creates the dataframe.
    .topfringe creates the top half of the sheet.
    .footnotes creates the sheet footnotes.
    .botfringe creates the bottom half of the sheet.
    '''
    def __init__(self, code):
        super().__init__(code)
        self.csv = None
        self.toCSV()

    def toCSV(self):
        '''
        Called upon instantiation. Gets the metadata and creates a dataframe 
        with sheet formatting.
        '''
        try: 
            self.meta['tableType']
        except:
            topfringe = self.topfringe()
            botfringe = self.botfringe()
            footnotes = self.footnotes()
            valuable_data = self.df.fillna('na').reset_index().T.reset_index() 
            
            self.csv = pd.concat([topfringe, valuable_data, footnotes, botfringe])
                
        else:
            # todo: Cross sectional data -> csv.
            pass
        
    def topfringe(self):
        topfringe = pd.DataFrame([
            'Table Title: '+self.meta['records']['title'],
            '',
            'Table ID: '+self.meta['records']['id'],
            '',
            'Data last updated: '+self.meta['records']['dataLastUpdated'],
            '',
            'Source: '+self.meta['records']['dataSource'],
            '',
            'Units of Measurement: '+self.meta['records']['row'][0]['uoM'],
            ''
            ]).rename(columns={0:'index'})
        return topfringe
 
    def botfringe(self):
        botfringe = pd.DataFrame(
            ['',
            'Notation:',
            'na   not available or not applicable',
            'nec  not elsewhere classified',
            'nes  not elsewhere specified',
            ' -     nil or negligible or not significant',
            '',
            'Notes',
            'Numbers may not add up to the totals due to rounding.',
            'Data are the latest available at the time of access or download. Some statistics, particularly those for the most recent time periods, are provisional and may be subject to revision at a later date.',
            'Values are shown in Singapore dollars (unless otherwise specified).']
            + [' ',
               'Generated by: '+self.meta['generatedBy'],
               'Date generated: '+self.meta['dateGenerated']]
            ).rename(columns={0:'index'})
        return botfringe

    def footnotes(self):
            footnotes = pd.DataFrame(
                ['','','Footnotes:',self.meta['records']['footnote']]\
                + [f"{i['rowText']} ({i['uoM']}): {i['footnote']}" for i in self.meta['records']['row'] if i['footnote']]
                ).rename(columns={0:'index'})
            return footnotes

class combineCSV:
    def __init__(self, sheetnames: dict, exceltitle: str):
        ''' 
        params:
        tabletitles : dict of {table code : sheet title}
        exceltitle : title of output xlsx sheet.
        
        return:
        writes a .xlsx with combined sheets from all the tablebuilder codes.
        '''
        self.sheetnames = sheetnames
        self.exceltitle = exceltitle
        self.combine()
        
    def combine(self):
        with pd.ExcelWriter(f'{self.exceltitle}') as writer:
            for i,code in enumerate(self.sheetnames.keys()):
                tmp = getcsv(code).csv
                tmp.to_excel(writer, sheet_name=self.sheetnames[code], index=False, header=False)
                print(f'Completed sheet {i+1} of {len(self.sheetnames.keys())}')
            print('All tables done.')
                
if __name__=="__main__":
    print("check testfile.xlsx")
    combineCSV({'M015661':'Sheet First','M400221':'Sheet Later'},'testfile.xlsx')
