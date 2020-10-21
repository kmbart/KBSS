#! StatCompare: Compare category totals for each team between Rotowire and KS.
#  Read in KS standings and pull out category totals for each team, then store them in the KS dictionary.
#  Read in Rotowire standings and pull out category totals for each team, then store them in the RW dictionary.
#  Compare the RW category entries with the equivalent KS entries; if they differ, put them on a new list.
#  Show the differences or confirm they match.

#  Read in KS standings and pull out category totals for each team, then store them in the KS dictionary.
#    Open the KS standings file and read in the contents
#    For each line in the KS file
#      If line contains "Current"
#        Pull off the team name
#        If line contains "Pitching"
#          Load KS dictionary with team name and category/value for
#            W (2), SV (2), K (4), ERA (1.3), WHIP (1.3), IP (4.1), H (3), BB (3), ER (3)
#        If line contains "Hitting"
#          Load KS dictionary with team name and category/value for
#            AB (4), H (4), HR (3), RBI (3), RS (3), SB (3), BA (1.4)

import re
from decimal import *

reCurrent  = re.compile(r'.*Current')
rePitching = re.compile(r'.*Pitching')
reHitting  = re.compile(r'.*Hitting')

KSfile = open('C:\\DSL\\KS-Stats.txt')
linelist = KSfile.readlines()
KSfile.close()

KSTotals = {}

for line in linelist:
    if reCurrent.search(line):
        teamName = line[0:4]
        if rePitching.search(line):
            KSTotals.setdefault(teamName+'-W', int(line[28:31]))
            KSTotals.setdefault(teamName+'-SV',int(line[32:35]))
            KSTotals.setdefault(teamName+'-K',int(line[36:41]))
            KSTotals.setdefault(teamName+'-ERA',round(float(line[41:49]),3))
            KSTotals.setdefault(teamName+'-WHIP',round(float(line[49:57]),3))
#            print (teamName,'WHIP-raw',line[49:57],',WHIP-dec',decimal(line[49:57]),',WHIP-round',decimal(line[49:57]))
#            KSTotals.setdefault(teamName+'-IP',float(line[57:64]))
#            KSTotals.setdefault(teamName+'-PHits',int(line[64:69]))
#            KSTotals.setdefault(teamName+'-BB',int(line[69:74]))
#            KSTotals.setdefault(teamName+'-ER',int(line[74:79]))

        if reHitting.search(line):
#            KSTotals.setdefault(teamName+'-AB', int(line[28:33]))
#            KSTotals.setdefault(teamName+'-HHits', int(line[33:38]))
            KSTotals.setdefault(teamName+'-HR', int(line[38:43]))
            KSTotals.setdefault(teamName+'-RBI', int(line[43:48]))
            KSTotals.setdefault(teamName+'-RS', int(line[48:53]))
            KSTotals.setdefault(teamName+'-SB', int(line[54:58]))
            KSTotals.setdefault(teamName+'-BA', round(float(line[58:67]),3))

#  Read in RW standings and pull out category totals for each team, then store them in the RW dictionary.
#    Open the RW standings file and read in the contents
#    Build dictionary for category lookups
#    Build dictionary for team name lookups
#    Build dictionary for integer vs. floating category values
#    For each line in the RW file
#      If the line is all commas, reset category and team names
#      Use split to parse out the first and second strings before commas
#      If category name found, save it
#      Else if team name found, save it
#      If category AND team names present, load RW dictionary with value
#    Compare the KS and RW dictionaries and print confirmation message or differences
    

RWfile = open('C:\\DSL\\RW-Stats.txt')
linelist = RWfile.readlines()
RWfile.close()

RWTotals = {}
categoryName = ''
RWTeamNames = {'Kops':'KOPS','Chris B Critters':'CRIT','Pinball Wizard':'PWIZ','BoilerRakers':'RAKE',
               'So.Philly SquallyD':'SQDS','Dwane Delays':'DLAY','M\' Bal Zarhari':'BALZ','PMOB':'PMOB',
               'Lou\'s Cannons':'LOUS','BobsBigBoys':'BOYS','Wall-Aces':'ACES','Wardens':'WARD'}
RWCategoryNames = {'Batting Average':'BA','Home Runs (Batter)':'HR','RBI':'RBI','Runs (Batter)':'RS','Stolen Bases':'SB',
                   'ERA':'ERA','Saves':'SV','Strikeouts':'K','WHIP':'WHIP','Wins':'W'}
RWCategoryTypes = ['BA','ERA','WHIP']

CorypreComma = re.compile(r'([^,]+?),?')
# preComma = re.compile(r'.*,')
# preComma = re.compile(r'(.*),?')
# preComma = re.compile(r'(.*)\,?')
# preComma = re.compile(r'(.*)?,')
# preComma = re.compile(r'(.*)?,')
# preComma = re.compile(r'(.*)?,?')
# preComma = re.compile(r'(.*,){1}?')
# preComma = re.compile(r'(.*),{1}?')
# preComma = re.compile(r'(.*,)?')
# preComma = re.compile(r'(.*,)')
# preComma = re.compile(r'(.*)\,')
# preComma = re.compile(r'(.*)\,{1}?')
# preComma = re.compile(r'(.*\,){1}?')
preComma = re.compile(r'(.*?),')     #  Success!

for line in linelist:

#    print ('Line:',line [0:22])
#    moPrecomma = preComma.search(line)
#    Elt = preComma.findall(line)
#    print ('Elt:',Elt)
    
    if line [0:7] == ',,,,,,,':
        categoryName = ''
        teamName     = ''

    else:
        lineElts = line.split(',')
        lineElt1 = lineElts [0]
        lineElt2 = lineElts [1]

#    print ('catName:',categoryName,',Elt1:',lineElt1,',Elt2:',lineElt2)
        
    categoryTemp = RWCategoryNames.get(lineElt1,'None')
#    print ('Category Temp:',categoryTemp)
    
    if categoryTemp != 'None':
        categoryName = categoryTemp
#        print ('Category Name:',categoryName)
    
    else:
        teamTemp = RWTeamNames.get(lineElt1,'None')
#        print ('Team Temp:',teamTemp)
    
        if teamTemp != 'None':
            teamName = teamTemp
#            print ('Team Name:',teamName,'Category Name:',categoryName)
            
            if categoryName != '':
                teamFloatValue = 0
                teamIntValue   = 0
                if categoryName in RWCategoryTypes:
                    teamFloatValue = round(float(lineElt2),3)
                    RWTotals.setdefault(teamName+'-'+categoryName, teamFloatValue)
#                    print (teamName+'-'+categoryName,'Raw:',lineElt2,',Float:',float(lineElt2),',Round:',round(float(lineElt2),3))
                else:
                    teamIntValue   = int(lineElt2)
                    RWTotals.setdefault(teamName+'-'+categoryName, teamIntValue)
#                    print ('Int:',teamIntValue)

            
# print ('KSTotals:',KSTotals)
# print ('RWTotals:',RWTotals)

if KSTotals == RWTotals:
    print ('Values match!')
    
else:
    print ('Differences:')    
    for k,v in KSTotals.items():
        if k in RWTotals:
            x = RWTotals.get(k,None)
            if v != x:
                print (k,'has values:',v,'and',x)
        else:
            print (k,'not found in RW')
    
    for k,v in RWTotals.items():
        if k in KSTotals:
            x = KSTotals.get(k,None)
            if v != x:
                print (k,'has values:',v,'and',x)
        else:
            print (k,'not found in KS')
