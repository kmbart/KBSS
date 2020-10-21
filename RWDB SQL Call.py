# RWDB SQL CALL = make SQL call to RWDB

import sqlite3

# initialize the SQL statement
_SQL = '''
          select FirstName, LastName, ID, round(IP, 1) as IP, K from RWP20191001 as KP,
              (select max(K) as maxK from RWP20191001) as Max 
              where KP.K > (Max.maxK * 0.8) order by KP.K desc
    '''
print ('_SQL =', _SQL)

# connect to RWDB
conn = sqlite3.connect('C:\SQLite\RotoDB\RWDB.db')

# create a cursor into the database
curs = conn.cursor()
curs.execute(_SQL)

# get the results of the SQL call
res = curs.fetchall()
print (res)

# conn.commit()

# close the cursor
curs.close()

# close the connection to RWDB
conn.close()

