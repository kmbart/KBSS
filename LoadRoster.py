#  LoadRoster - insert a CSV roster file in the Roster table
#
#  set current year for season (CCYY format) and weeks in season (MMDD format)
#  set database filename to DSL.db
#  set folder for season from basic path and current year
#  
#  initialize counts
#
#  create the Roster table if it does not exist
#  get the column header names and numbers as a list of tuples
#
#  for each week in the tuple
#    set the StatDate
#    open the DSL connection
#    set the CSV roster filename
#    read in the CSV roster file
#    set a parm string of '?,' ColumnCnt times for the VALUES feed
#    import the CSV roster file
#    commit the import changes
#    close the DSL connection

import sqlite3
from sqlite3 import Error
import csv

#  register a dialect for the CSV reader that removes spaces
csv.register_dialect ('trimmed', skipinitialspace=True)

#  set the weeks in each season (MMDD format) as a tuple
Weeks2020 = ('0101',)
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
SeasonCCYY = '2020'
Weeks = Weeks2020

#  set database filename to RotoDB.db
DSL = 'C:\\SQLite\\RotoDB\\DSL.db'

#  set folder for season from basic path and current year
PathDSL = 'C:\\Rosters\\'

#  initialize counts
CountOfFiles = 0

#    open the RotoDB connection and create a cursor for it
try:
    conn = sqlite3.connect(DSL)
    curs = conn.cursor()

#    set the ROST<CCYYMMDD> table name and create the table
    TableName = 'Rosters'
#    curs.execute('DROP TABLE IF EXISTS ' + TableName)
    curs.execute('CREATE TABLE IF NOT EXISTS ' + TableName +
                 '(CCYYMMDD     INTEGER,'
                 'League        TEXT,'
                 'Team          TEXT,'
                 'Status        TEXT,'
                 'Position      TEXT,'
                 'LastName      TEXT,'
                 'FirstName     TEXT,'
                 'ID            INTEGER,'
                 'Salary        FLOAT,'
                 'Contract      TEXT)')

#    get the column header names and numbers as a list of tuples
    curs.execute('PRAGMA table_info(' + TableName + ');')
    ColumnNames = curs.fetchall()
#    print (TableName, ' column names:', ColumnNames)

    ColumnCnt = len(ColumnNames)
#    print ('column count:', ColumnCnt)

    ColumnNameList = list()
#    The column name tuples have the column's #, name, type, 0, None, 0
#      so the column name itself is in index position 1
    for hdr in ColumnNames:
        ColumnNameList.append(hdr[1])
#    print ('column name list:', ColumnNameList)
        
    Headers = ','.join(ColumnNameList)
#    print ('headers:', Headers)
    
except Error as err:
    print ('connection attempt failed with error:', err)
    conn.close()
    sys.exit()

#  for each week in the tuple
for Week in Weeks:

#    set the StatDate
    StatDate = SeasonCCYY + Week

#    set the CSV roster filename
    FileName = 'CSVP' + Week + '.txt'
    print ('filename:', FileName)

#    read in the CSV roster file
    try:
        with open(PathDSL + FileName, 'r') as CSVRFile:
            reader = csv.reader(CSVRFile, 'trimmed')
            
            CSVList = list()
            for row in reader:
                strippedRow = [elt.strip() for elt in row]
#                print ('strippedRow:', strippedRow)
                CSVList.append(strippedRow)

#            print ('csvlist:', CSVList)

#    set a parm string of '?,' ColumnCnt times for the VALUES feed
            ParmStr = '?,' * ColumnCnt
            ParmStr = ParmStr[:-1]

#    import the CSV roster file
            SQLInsert = 'INSERT INTO ' + TableName + '(' + Headers + ') VALUES (' + ParmStr + ')'
                        
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

#    close the RotoDB connection
conn.close()

print()
print ('database is:', DSL)
print ('path is:', PathDSL)
print ('Files found:', CountOfFiles)
