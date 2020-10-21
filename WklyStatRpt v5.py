#  WklyStatRpt - generate a week's stats
#  create a sort order dictionary for player status
#  create a sort order dictionary for roster positions
#
#  create a dictionary for each season (CCYY) with a tuple of the stat dates in each season (MMDD)
#  set current year for season (CCYY format), select that season's weeks tuple
#  set the league name
#  set pathname for database access
#
#  set connection filenames for DSL and RWDB
#  
#  initialize counts
#
#  connect to the databases
#  create cursors for the databases
#
#  SQL SELECT on the team info
#  sort on team owner's name and create a list of the sorted team names
#
#  for each week in the tuple
#    initialize the counters for the league
#
#    for each team in the league
#      initialize the counters for the team
#      append the team header info to the team page
#      get all the players on the team for that week
#
#      for each player on the team
#        get the stats for that player
#        if the player is active
#          add to the team's stats
#        append the player to the appropriate category (active, reserved, minors, etc.)
#
#      append the active player stats to the team page
#      append the pending player stats to the team page
#      append the reserved player stats to the team page
#      append the minor player stats to the team page
#      append the team stat totals to the team page
#
#      insert the team stat totals into the standings lists
#
#    calculate the standings
#    print the standings
#    for each team
#      print the team page


import sqlite3
from sqlite3 import Error
import sys

# create a sort order dictionary for player status
statusOrder   = {'Active':1,'Open':1,'Reserved':2,'Pending':2,'Minors':3}
positionOrder = {'P':'01','U':'02','X':'03','C':'04','1':'05','2':'06','S':'07','3':'08','W':'09',
                 'M':'10','O':'11'}

# create a template for team stats as a list of dictionary elts
leagueStats              = {}

statsTemplate            = {}
statsTemplate['AB']      = 0
statsTemplate['H_Runs']  = 0
statsTemplate['H_Hits']  = 0
statsTemplate['H_HR']    = 0
statsTemplate['H_RBI']   = 0
statsTemplate['H_SB']    = 0
statsTemplate['P_Wins']  = 0
statsTemplate['P_Saves'] = 0
statsTemplate['P_IP']    = 0
statsTemplate['P_Hits']  = 0
statsTemplate['P_BB']    = 0
statsTemplate['P_ERuns'] = 0
statsTemplate['P_K']     = 0
# print ('template:', statsTemplate)

# create a dictionary of the weeks in each season (MMDD format) as a tuple
weeks = {2020:('0101',),
    2019:('0409','0416','0423','0430','0507','0514','0521','0528','0604','0611','0618','0625','0702','0709','0716','0723','0730','0806','0813','0820','0827','0903','0910','0917','0924','1001'),
    2018:('0410','0417','0424','0501','0508','0515','0522','0529','0605','0612','0619','0626','0703','0710','0717','0724','0731','0807','0814','0821','0828','0904','0911','0918','0925','1002'),
    2017:('0411','0418','0425','0502','0509','0516','0523','0530','0606','0613','0620','0627','0704','0711','0718','0725','0801','0808','0815','0822','0829','0905','0912','0919','0926','1003'),
    2016:('0412','0419','0426','0503','0510','0517','0524','0531','0607','0614','0621','0628','0705','0712','0719','0726','0802','0809','0816','0823','0830','0906','0913','0920','0927','1004'),
    2015:('0410','0414','0421','0428','0505','0512','0519','0526','0602','0609','0616','0623','0630','0707','0714','0721','0728','0804','0811','0818','0825','0901','0908','0915','0922','0929','1006'),
    2014:('0408','0415','0422','0429','0506','0513','0520','0527','0603','0610','0617','0624','0701','0708','0715','0722','0729','0805','0812','0819','0826','0902','0909','0916','0923'),
    2013:('0402','0409','0416','0423','0430','0507','0514','0521','0528','0604','0611','0618','0625','0702','0709','0716','0723','0730','0806','0813','0820','0827','0903','0910','0917','0924','1001'),
    2012:('0410','0417','0424','0501','0508','0515','0522','0529','0605','0612','0619','0626','0703','0710','0717','0724','0731','0807','0814','0821','0828','0904','0911','0918','0925','1002'),
    2011:('0405','0412','0419','0426','0503','0510','0517','0524','0531','0607','0614','0621','0628','0705','0712','0719','0726','0802','0809','0816','0823','0830','0906','0913','0920','0927','0928'),
    2010:('0412','0419','0426','0503','0510','0517','0524','0531','0607','0614','0621','0628','0705','0712','0719','0726','0802','0809','0816','0823','0830','0906','0913','0920','0927','1004')
    }

# calculate difference of two groups of stats
def calcStatDiff(n,o):
    diff = statsTemplate

# print hitter stats
def findPositions(s) -> str:
    eligPos = '' 
    maxPos = min(20, max(s[18], s[19], s[20], s[21], s[22], s[23]))
#    print ('max:', maxPos)
    if s[18] >= maxPos:
        eligPos = eligPos + 'C'
    if s[19] >= maxPos:
        eligPos = eligPos + '1'
    if s[20] >= maxPos:
        eligPos = eligPos + '2'
    if s[21] >= maxPos:
        eligPos = eligPos + '3'
    if s[22] >= maxPos:
        eligPos = eligPos + 'S'
    if s[23] >= maxPos:
        eligPos = eligPos + 'O'
#    print ('pos:', eligPos)
    return (eligPos)

# determine if player is hitter or pitcher
def getPlayerType (s) -> str:
    pType = 'P' 
    if   (s[6] > 0
       or s[7] > 0
       or s[8] > 0
       or s[9] > 0
       or s[10] > 0
       or s[11] > 0
       or s[12] > 0
       or s[13] > 0
       or s[14] > 0
       or s[15] > 0
       or s[16] > 0
       or s[17] > 0
       or s[18] > 0
       or s[19] > 0
       or s[20] > 0
       or s[21] > 0
       or s[22] > 0
       or s[23] > 0): pType = 'H'                      #Hitter stats
    print ('ptype:', pType)
    return (pType)

# print hitter stats
def printHitterStats(s, e):
    print (' ',
           s[6],                                               # AB
           s[8],                                               # hits
           s[11],                                              # HR
           s[12],                                              # RBI
           s[7],                                               # runs
           s[13],                                              # steals
           "{:0>1.4f}".format(s[8] / s[6]),                    # BA
           ' <' + e + '>'                                      # positions
        )

# print pitcher stats
def printPitcherStats(s):
    print (' ',
           s[24],                                              # wins
           s[26],                                              # saves
           "{:0>3.1f}".format(s[28]),                          # innings pitched
           s[29],                                              # hits
           s[31],                                              # walks
           s[34],                                              # earned runs
           s[35],                                              # strikeouts
           "{:0>2.3f}".format(9 * (s[34] / s[28])),            # ERA
           "{:0>2.3f}".format((s[29] + s[31]) / s[28])         # WHIP
        )

# print player info
def printPlayerInfo(p):
    print (p[0][0],                                            # status
           p[1],                                               # position
           "{:25s}".format(p[3] + ' ' + p[2]),                 # full name
           "{:0>8d}".format(p[4]),                             # ID
           "{:0>2.2f}".format(p[5]),                           # salary
           "{:2s}".format(p[6]),end='')                        # contract

# sum pitcher stats for a team
def sumHitterStats(t, s):
    print ()
    leagueStats[t]['AB']     += s[6]                         # AB
    leagueStats[t]['H_Hits'] += s[8]                         # hits
    leagueStats[t]['H_HR']   += s[11]                        # HR
    leagueStats[t]['H_RBI']  += s[12]                        # RBI
    leagueStats[t]['H_Runs'] += s[7]                         # runs
    leagueStats[t]['H_SB']   += s[13]                        # steals
#    print ('leagstats:', leagueStats)

# sum pitcher stats for a team
def sumPitcherStats(t, s):
    leagueStats[t]['P_Wins']   += s[24]                        # wins
    leagueStats[t]['P_Saves']  += s[26]                        # saves
    leagueStats[t]['P_IP']     += s[28]                        # innings pitched
    leagueStats[t]['P_Hits']   += s[29]                          # hits
    leagueStats[t]['P_BB']     += s[31]                        # walks
    leagueStats[t]['P_ERuns']  += s[34]                        # earned runs
    leagueStats[t]['P_K']      += s[35]                        # strikeouts
#    print ('leagstats:', leagueStats)

# do a SQL SELECT on the stats for a given player for that season + week
# def getPlayerStats(statWeek, PlayerID) -> playerStats:
def getPlayerStats(statWeek, PlayerID):
    _SQL = 'select * from WklyStats where CCYYMMDD = ? and ID = ?'
    cursRWDB.execute(_SQL, (statWeek, PlayerID))

    return (cursRWDB.fetchone())
        
# set current year for season (CCYY format), select the weeks tuple, and the league name
seasonCCYY         = 2019
weeksList          = weeks[seasonCCYY]
prevSeasonCCYY     = seasonCCYY - 1
prevSeasonLastWeek = str(prevSeasonCCYY) + weeks[prevSeasonCCYY][-1]
# print ('prevlastwk:', prevSeasonLastWeek)
leagueName         = 'DSL'

# set pathname for database access
pathName = 'C:\\SQLite\\RotoDB\\'

# set connection filenames for DSL and RWDB
dbDSL  = 'DSL.db'
dbRWDB = 'RWDB.db'

# initialize counts
countOfWeeks = 0

try:
# connect to the databases
    connDSL  = sqlite3.connect(pathName + dbDSL)
    connRWDB = sqlite3.connect(pathName + dbRWDB)

# create cursors for the databases
    cursDSL  = connDSL.cursor()
    cursRWDB = connRWDB.cursor()

# SQL SELECT on the team info
    _SQL = 'select TeamAbbr, TeamOwner, TeamName, TeamPhoneNumber, TeamEmail, DeadSkipper from TeamInfo where CCYY = ? and LeagueAbbr = ?'
    cursDSL.execute(_SQL, (seasonCCYY, leagueName))

# get the results of the SQL call
    res = cursDSL.fetchall()

# sort on team owner's name and create a list of the sorted team names
    teamAbbrList = [teamTuple[0] for teamTuple in (sorted(res, key=lambda teamInfo: (teamInfo[1].split()[1] + teamInfo[1].split()[0])))]
#    print ('teams:', teamAbbrList)

    prevWeek = ''    
# for each week in the tuple
    for week in weeksList:

        if week > '0423':
            break
        
# for each team in the league
        for team in teamAbbrList:
            print ('team:', team)
            if team != 'KOPS':
                break
            
# initialize the counters for the team
           
# append the team header info to the team page
            teamInfo    = [aTuple for aTuple in res if aTuple[0] == team]
            teamAbbr    = teamInfo[0][0]
            teamOwner   = teamInfo[0][1]
            teamName    = teamInfo[0][2]
            teamPhone   = teamInfo[0][3]
            teamEmail   = teamInfo[0][4]
            teamSkipper = teamInfo[0][5]
            print ('teaminfo:', teamAbbr, ',', teamName, ',', teamOwner, ',',
                               teamPhone, ',', teamEmail, ',', teamSkipper)
            leagueStats[teamAbbr] = statsTemplate

# get all the players on the team for that week

# do a SQL SELECT on the players for that season + week + + league + team
            statWeek = str(seasonCCYY) + week
            _SQL = 'select Status, Position, LastName, FirstName, ID, Salary, Contract from Rosters where CCYYMMDD = ? and League = ? and Team = ?'
#            print ('_SQL =', _SQL)
#            print ('wk:', statWeek, 'leag:', leagueName, 'team:', teamAbbr)
            cursDSL.execute(_SQL, (statWeek, leagueName, teamAbbr))

# get the results of the SQL call
            roster = cursDSL.fetchall()
#            print ('results:', roster)

# sort the roster by status
            roster.sort(key=lambda k: str(statusOrder[k[0]]) + positionOrder[k[1]] + k[2] + k[3])
#            print ('sorted:', roster)
            
            for player in roster:

                playerID = player[4]

# get the results of the SQL call
                currStats = getPlayerStats (statWeek, playerID)
                if prevWeek != '':
                    prevStats = getPlayerStats (prevWeek, playerID)
                    print ('prevstats:', prevStats); print ()


                printPlayerInfo(player)

                if currStats == None:
                    print ('  <No stats returned>')

                else:                
                    playerType = getPlayerType(currStats)
                    print ('type:', playerType)
                    if playerType == 'P':
                        sumPitcherStats(teamAbbr, currStats)
#                        printPitcherStats(stats)
                    else:
                        currPos = findPositions(currStats)
                        prevEOYStats = getPlayerStats (prevSeasonLastWeek, playerID)
                        
                        if prevEOYStats != None:
                            prevPos = findPositions(prevEOYStats)
                            print (); print ('prev pos:', prevPos)
                            bothPos = ''
                            if 'C' in prevPos or 'C' in currPos: bothPos += 'C'
                            if '1' in prevPos or '1' in currPos: bothPos += '1'
                            if '2' in prevPos or '2' in currPos: bothPos += '2'
                            if '3' in prevPos or '3' in currPos: bothPos += '3'
                            if 'S' in prevPos or 'S' in currPos: bothPos += 'S'
                            if 'O' in prevPos or 'O' in currPos: bothPos += 'O'
                            currPos = bothPos

                        sumHitterStats(teamAbbr, currStats)
                        printHitterStats(currStats, currPos)

# save this week as the previous week
        prevWeek = str(seasonCCYY) + week
        print ('prevWk:', prevWeek)

except Error as err:
    print ('DSL connection attempt failed with error:', err)
    connDSL.close()
    sys.exit()
