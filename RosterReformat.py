#  RosterReformat:  Reformat a roster text file into player and team CSV files.
#  Pull ROST files from Previous Years
#  Open the roster file
#  Read in the roster file
#  Close the roster file
#
#  for each week in the season
#    Open the player and team CSV files
#    Read each line in the roster file
#      if the record type is:
#        '*' then change the TeamAbbr
#        '=' then set asterisk trade and write to team CSV file
#        '+' or '-' or '&' or '~' line then
#            parse player (last name, first name, ID, salary, position, contract)
#              and write to player CSV file
#        '$' then parse FAB (month, day, amount, last name, first name) and write to team CSV file
#        '#' then parse pick (year, optional team, round/pick#) and write to team CSV file
#    Close the player and team CSV files
#
#  write counts for number of teams, players per team, etc.


import re
from decimal import *

reCurrent  = re.compile(r'.*Current')
bypassTypes = {'/':'Free Agent', '%':'Owner', '@':'Email'}
playerTypes = {'+':'Active', '?':'Open', '-':'Reserved', '&':'Minors', '~':'Waived', '!':'Pending'}

#  set the weeks in each season (MMDD format) as a tuple
Weeks2020 = ('0101',)
# Weeks2019 = ('0402',)
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
# There are not rosters for seasons prior to 2018
SeasonCCYY = '2020'
Weeks = Weeks2020
rosterPathname = 'C:\\Users\\keith\\OneDrive\\Documents\\DSL\\Previous Years\\DSL-' + SeasonCCYY + '\\'

for Week in Weeks:
    
# Generate input date (SeasonCCYY + Week)
    inputDate = SeasonCCYY + Week
    inputCCYY = inputDate[0:4]
    inputMMDD = inputDate[4:8]
    print ('inputDate=', inputDate)

    rosterFilename = rosterPathname + 'ROST' + inputMMDD + '.DSL'
    print('filename= ', rosterFilename[57:])

# Open roster file
    rosterFile = open(rosterFilename)

# Read in roster file
    lineList = rosterFile.readlines()

# Close roster file
    rosterFile.close()

# Open player CSV file
    CSVPFile = open('C:\\Rosters\\CSVP' + inputMMDD + '.txt','w')
# Open team CSV file
    CSVTFile = open('C:\\Rosters\\CSVT' + inputMMDD + '.txt','w')

# Read each line in roster file
    lineCnt = 0
    for line in lineList:
        lineCnt += 1
# if lineCnt > 111: break
    
        lineType = line[0:1]
# print ('read in type:', lineType, ' on line=', line[0:44])

# if it is a '*' line, change the TeamAbbr
        if lineType == '*':
            teamAbbr = line[1:5]
#        print ('found abbreviation:', teamAbbr)
        
# if it is a '=' line then set asterisk trade
        elif lineType == '=':
            teamAsterisk = line[16:25].strip()
            print (inputDate, ',', teamAbbr, ',', 'Asterisk', ',', teamAsterisk, file=CSVTFile)

#    if it is a '+' or '-' or '&' or '~' line then ParsePlayer
        elif lineType in playerTypes:
            playerName     = line[1:19]
            names          = playerName.split(',')
#            print ('names:', names)
            lastName       = names[0]
            if len(names) < 2: print ('missing firstName:', names)
            else: firstName      = names[1]
            playerID       = line[19:27]
            playerSalary   = line[28:33]
            playerPos      = line[34:35]
            playerStatus   = playerTypes [lineType]
            if lineType == '&':
                playerContract = 'M '
            else:
                playerContract = line[36:38]
            print (inputDate, ',', 'DSL', ',', teamAbbr, ',', playerStatus, ',', playerPos, ',', lastName, ',', firstName, ',', playerID, ',', playerSalary, ',', playerContract, file=CSVPFile)

# if it is a '$' line then ParseFab
        elif lineType == '$':
            FABMM      = line[1:3]
            FABDD      = line[4:6]
            FABPrice   = line[25:30]
            FABName    = line[30:55].strip()
            FABLName   = ' '
            FABFName   = ' '
            if FABName != '':
                FABNames   = FABName.split(',')
                FABLName   = FABNames[0]
                FABFName   = FABNames[1]
            print (inputCCYY + FABMM + FABDD, ',', teamAbbr, ',', 'FAB', ',', FABPrice, ',', FABFName, ',', FABLName, file=CSVTFile)

# if it is a '#' line then ParsePick
        elif lineType == '#':
            minorsPick   = line.strip()
            minorsPickYY = '20' + minorsPick [1:3]
            if minorsPick [4:5] == '#':
                thisPick     = minorsPick [4:7]
                thisPickTeam = ' '
            else:
                thisPick     = minorsPick [9:12]
                thisPickTeam = minorsPick [4:8]
            print (inputDate, ',', teamAbbr, ',', 'Pick', ',', minorsPickYY, ',', thisPickTeam, ',', thisPick, file=CSVTFile)

        else:
            if not (lineType in bypassTypes): print ('invalid lineType:', lineType, ' - rejected')

# Close player CSV file
    CSVPFile.close()

# Close team CSV file
    CSVTFile.close()
