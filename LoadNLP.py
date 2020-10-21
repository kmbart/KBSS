NOT USED ANY MORE -
  NOW LOADING ALL PITCHERS INTO A SINGLE TABLE BECAUSE PYTHON CANNOT USE TABLENAMES AS PARMS
#
#  set current year for season (CCYY format) and weeks in season (MMDD format)
#  set database filename to RWDB.db
#  set folder for season from basic path and current year
#  
#  initialize counts
#
#  for each week in the tuple
#    set the StatDate
#    open the RWDB connection
#    set the RWH<CCYYMMDD> table name and create the table
#    get the column header names and numbers as a list of tuples
#    set the pitcher filename
#    read in the pitcher file without the header line
#    set a parm string of '?,' ColumnCnt times for the VALUES feed
#    import the NLP<Y><MMDD>.txt file without the header line
#    commit the import changes
#    close the RWDB connection

import sqlite3
from sqlite3 import Error
import csv

#  set the weeks in each season (MMDD format) as a tuple
# Weeks2019 = ('0101',)
Weeks2019 = ('0409','0416','0423','0430','0507','0514','0521','0528','0604','0611','0618','0625','0702','0709','0716','0723','0730','0806','0813','0820','0827','0903','0910','0917','0924','1001')
Weeks2018 = ('0410','0417','0424','0501','0508','0515','0522','0529','0605','0612','0619','0626','0703','0710','0717','0724','0731','0807','0814','0821','0828','0904','0911','0918','0925','1002')
Weeks2017 = ('0411','0418','0425','0502','0509','0516','0523','0530','0606','0613','0620','0627','0704','0711','0718','0725','0801','0808','0815','0822','0829','0905','0912','0919','0926','1003')
Weeks2016 = ('0412','0419','0426','0503','0510','0517','0524','0531','0607','0614','0621','0628','0705','0712','0719','0726','0802','0809','0816','0823','0830','0906','0913','0920','0927','1004')
Weeks2015 = ('0410','0414','0421','0428','0505','0512','0519','0526','0602','0609','0616','0623','0630','0707','0714','0721','0728','0804','0811','0818','0825','0901','0908','0915','0922','0929','1006')
Weeks2014 = ('0408','0415','0422','0429','0506','0513','0520','0527','0603','0610','0617','0624','0701','0708','0715','0722','0729','0805','0812','0819','0826','0902','0909','0916','0923')
Weeks2013 = ('0402','0409','0416','0423','0430','0507','0514','0521','0528','0604','0611','0618','0625','0702','0709','0716','0723','0730','0806','0813','0820','0827','0903','0910','0917','0924','1001')
Weeks2012 = ('0410','0417','0424','0501','0508','0515','0522','0529','0605','0612','0619','0626','0703','0710','0717','0724','0731','0807','0814','0821','0828','0904','0911','0918','0925','1002')
Weeks2011 = ('0405','0412','0419','0426','0503','0510','0517','0524','0531','0607','0614','0621','0628','0705','0712','0719','0726','0802','0809','0816','0823','0830','0906','0913','0920','0927','0928')
Weeks2010 = ('0412','0419','0426','0503','0510','0517','0524','0531','0607','0614','0621','0628','0705','0712','0719','0726','0802','0809','0816','0823','0830','0906','0913','0920','0927','1004')


#  set current year for season (CCYY format) and select the weeks tuple
SeasonCCYY = '2010'
Weeks = Weeks2010

#  set database filename to RWDB.db
RWDB = 'C:\\SQLite\\RotoDB\\RWDB.db'

#  set folder for season from basic path and current year
PathRW = 'C:\\RW\\RW' + SeasonCCYY + '\\'

#  initialize counts
CountOfFiles = 0

#    open the RWDB connection and create a cursor for it
try:
    conn = sqlite3.connect(RWDB)
    curs = conn.cursor()
    
except Error as err:
    print ('connection attempt failed with error:', err)
    conn.close()
    sys.exit()

#  for each week in the tuple
for Week in Weeks:

#    set the StatDate
    StatDate = SeasonCCYY + Week

#    set the RWH<CCYYMMDD> table name and create the table
    TableName = 'RWP' + StatDate
    curs.execute('DROP TABLE IF EXISTS ' + TableName)
    curs.execute('CREATE TABLE IF NOT EXISTS ' + TableName +
                 '(CCYYMMDD     INTEGER,'
                 'FirstName     TEXT,'
                 'LastName      TEXT,'
                 'ID            INTEGER,'
                 'Team          TEXT,'
                 'Games         INTEGER,'
                 'Wins          INTEGER,'
                 'Losses        INTEGER,'
                 'Saves         INTEGER,'
                 'BlownSaves    INTEGER,'
                 'IP            INTEGER,'
                 'Hits          INTEGER,'
                 'HR            INTEGER,'
                 'Walks         INTEGER,'
                 'HBP           INTEGER,'
                 'Runs          INTEGER,'
                 'ERuns         INTEGER,'
                 'K             INTEGER)')

#    get the column header names and numbers as a list of tuples
    curs.execute('PRAGMA table_info(' + TableName + ');')
    ColumnNames = curs.fetchall()
#    print ('column names:', ColumnNames)
    
    ColumnCnt = len(ColumnNames)
#    print ('column count:', ColumnCnt)
    
    ColumnNameList = list()
#    The column name tuples have the column's #, name, type, 0, None, 0
#      so the column name itself is in position 1
    for hdr in ColumnNames:
        ColumnNameList.append(hdr[1])
#    print ('column name list:', ColumnNameList)
        
    Headers = ','.join(ColumnNameList)
#    print ('headers:', Headers)

#    set the pitcher filename
#    FileName = 'NLP' + SeasonCCYY [3:4] + Week + '.txt'
    FileName = 'NFP' + SeasonCCYY [3:4] + Week + '.txt'
    print ('filename:', FileName)

#    read in the pitcher file without the header line
    try:
        with open(PathRW + FileName, 'r') as NLPFile:
            reader = csv.reader(NLPFile)
            
            CSVList = list()
            for row in reader:
                CSVList.append(row)

#            print ('csvlist:', CSVList)

#    set a parm string of '?,' ColumnCnt times for the VALUES feed
            ParmStr = '?,' * (ColumnCnt - 1)
            ParmStr = ParmStr[:-1]

#    import the NLP<Y><MMDD>.txt file without the header line
            SQLInsert = 'INSERT INTO ' + TableName + '(' + Headers + ') VALUES (' + StatDate + ',' + ParmStr + ')'
                        
            curs.executemany (SQLInsert, CSVList)
#        print the entire line
#            for line in linelist:
#                print ('line:', line.strip())

#    commit the import changes
        conn.commit()
        
        CountOfFiles += 1
        
    except IOError:
        print ('Error opening file:', FileName)

#    if CountOfFiles > 0: break

#    close the RWDB connection
conn.close()

print()
print ('database is:', RWDB)
print ('path is:', PathRW)
print ('Files found:', CountOfFiles)
