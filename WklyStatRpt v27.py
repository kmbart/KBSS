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


import sys
import copy
import sqlite3
from sqlite3 import Error

# create a sort order dictionary for player status
statusOrder   = {'Active':1,'Open':1,'Pending':2,'Reserved':3,'Minors':4}
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

emptyStats = (0,) * 36

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
    diff = ('StatDiff'
            ,n[1]
            ,n[2]
            ,n[3]
            ,n[4]
            ,n[5]
            ,n[6]  - o[6]
            ,n[7]  - o[7]
            ,n[8]  - o[8]
            ,n[9]  - o[9]
            ,n[10] - o[10]
            ,n[11] - o[11]
            ,n[12] - o[12]
            ,n[13] - o[13]
            ,n[14] - o[14]
            ,n[15] - o[15]
            ,n[16] - o[16]
            ,n[17] - o[17]
            ,n[18] - o[18]
            ,n[19] - o[19]
            ,n[20] - o[20]
            ,n[21] - o[21]
            ,n[22] - o[22]
            ,n[23] - o[23]
            ,n[24] - o[24]
            ,n[25] - o[25]
            ,n[26] - o[26]
            ,n[27] - o[27]
            ,n[28] - o[28]
            ,n[29] - o[29]
            ,n[30] - o[30]
            ,n[31] - o[31]
            ,n[32] - o[32]
            ,n[33] - o[33]
            ,n[34] - o[34]
            ,n[35] - o[35]
            )
    return (diff)

# find eligible positions using a stats tuple 
def findPositions(s) -> str:
    eligPos = '' 
    maxPos = min(20, max(s[18], s[19], s[20], s[21], s[22], s[23]))
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

    return (eligPos)

# determine if player is hitter or pitcher
def getListType (s, p):                      # status, player type
    if s > 1:
        lType = 'E'
    elif p == 'P':
        lType = 'P'
    else:
        lType = 'H'
        
    return (lType)

# do a SQL SELECT on the stats for a given player for that season + week
# def getPlayerStats(statWeek, PlayerID) -> playerStats:
def getPlayerStats(sWk, PID):
    _SQL = 'select * from WklyStats where CCYYMMDD = ? and ID = ?'
    cursRWDB.execute(_SQL, (sWk, PID))

    return (cursRWDB.fetchone())

# determine if player is hitter or pitcher
def getPlayerType (s, p) -> str:                    # stats, position type
#    print ('stats:', s, ',pos:', p)
    if s == None:
#        print ('stats = None')
        if p == '01': pType = 'P'
        else: pType = 'H'

    elif (s[6] > 0
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
       or s[23] > 0):
        pType    = 'H'

    else:
        pType = 'P'
        
#    print ('ptype:', pType)
    return (pType)

# print headers for hitters
def makeHeaderHitters() -> str:
    return ("{:^30}".format('Player')
           + "{:^10}".format('ID')
           + "{:^5}".format('$')
           + "{:^5}".format('Con')
           + "{:^6}".format('AB')
           + "{:^5}".format('Hits')
           + "{:^6}".format('HR')
           + "{:^4}".format('RBI')
           + "{:^6}".format('RS')
           + "{:^5}".format('SB')
           + "{:^7}".format('BA')
           + "{:^11}".format('Positions')
              )

# print headers for pitcher
def makeHeaderPitchers() -> str:
    return ("{:^30}".format('Player')
           + "{:^10}".format('ID')
           + "{:^5}".format('$')
           + "{:^5}".format('Con')
           + "{:^4}".format('W')
           + "{:^4}".format('SV')
           + "{:^8}".format('IP')
           + "{:^5}".format('H')
           + "{:^4}".format('BB')
           + "{:^6}".format('ER')
           + "{:^4}".format('K')
           + "{:^9}".format('ERA')
           + "{:^8}".format('WHIP')
            )

# print hitter stats
def makeHitterStatsStr(s, e) -> str:                      # stats, positions
    sStr = ' '.join(
    [' '
    , "{: 4d}".format(s[6])                           # AB
    , "{: 5d}".format(s[8])                           # hits
    , "{: 4d}".format(s[11])                          # HR
    , "{: 4d}".format(s[12])                          # RBI
    , "{: 4d}".format(s[7])                           # runs
    , "{: 4d}".format(s[13])                          # steals
    , "{: 6.4f}".format(s[8] / s[6])                  # BA
    , ' <' + e + '>'                                  # positions
     ])

    return (sStr)

# print pitcher stats
def makePitcherStatsStr(s) -> str:                           # stats
    sStr = ' '.join(
    [' '
    , "{: 3d}".format(s[24])                             # wins
    , "{: 3d}".format(s[26])                             # saves
    , "{: 6.1f}".format(s[28])                           # innings pitched
    , "{: 4d}".format(s[29])                             # hits
    , "{: 4d}".format(s[31])                             # walks
    , "{: 4d}".format(s[34])                             # earned runs
    , "{: 4d}".format(s[35])                             # strikeouts
    , "{: 7.3f}".format(9 * (s[34] / s[28]))             # ERA
    , "{: 7.3f}".format((s[29] + s[31]) / s[28])         # WHIP
     ])
    
    return (sStr)

# print player info
def makePlayerInfoStr(p) -> str:                             # player
    infoStr = ' '.join(
    [p[0][0]                                             # status
    , "{:2s}".format(p[1])                                               # position
    , "{:25s}".format(p[3] + ' ' + p[2])                 # full name
    , "{:0>8d}".format(p[4])                             # ID
    , "{: >5.2f}".format(p[5])                           # salary
    , "{:2s}".format(p[6])                               # contract
    ])
    
    return (infoStr)

# print hitter stat totals for a team
def makeTeamHitterTotalsStr(l, t) -> str:                # league, stat totals
    totStr = ' '.join(
    [t
    , ' - Hitter Totals:                          '      # team abbr
    , "{: 5d}".format(l[t]['AB'])                        # AB
    , "{: 5d}".format(l[t]['H_Hits'])                    # hits
    , "{: 4d}".format(l[t]['H_HR'])                      # HR
    , "{: 4d}".format(l[t]['H_RBI'])                     # RBI
    , "{: 4d}".format(l[t]['H_Runs'])                    # runs
    , "{: 4d}".format(l[t]['H_SB'])                      # steals
    , "{: 6.4f}".format(l[t]['H_Hits'] / l[t]['AB'])     # BA
    ])
            
    return (totStr)

# print stat totals for a team
def makeTeamPitcherTotalsStr(l, t) -> str:                                # league, stats totals
    totStr = ' '.join(
    [t
    , ' - Pitcher Totals:                          '                      # team abbr
    , "{: 3d}".format(l[t]['P_Wins'])                                     # wins
    , "{: 3d}".format(l[t]['P_Saves'])                                    # saves
    , "{: 6.1f}".format(l[t]['P_IP'])                                     # IP
    , "{: 3d}".format(l[t]['P_Hits'])                                     # hits
    , "{: 4d}".format(l[t]['P_BB'])                                       # walks
    , "{: 3d}".format(l[t]['P_ERuns'])                                    # earned runs
    , "{: 3d}".format(l[t]['P_K'])                                        # strikeouts
    , "{: 7.3f}".format(9 * (l[t]['P_ERuns'] / l[t]['P_IP']))             # ERA
    , "{: 7.3f}".format((l[t]['P_Hits'] + l[t]['P_BB']) / l[t]['P_IP'])   # WHIP
    ])
    
    return (totStr)
    
# sum pitcher stats for a team
def sumHitterStats(l, t, s):                                   # league, team, stats
    l[t]['AB']     += s[6]                                     # AB
    l[t]['H_Runs'] += s[7]                                     # runs
    l[t]['H_Hits'] += s[8]                                     # hits
    l[t]['H_HR']   += s[11]                                    # HR
    l[t]['H_RBI']  += s[12]                                    # RBI
    l[t]['H_SB']   += s[13]                                    # steals
#    print ('leagstats:', leagueStats)

# sum pitcher stats for a team
def sumPitcherStats(l, t, s):                                  # league, team, stats
    l[t]['P_Wins']   += s[24]                                  # wins
    l[t]['P_Saves']  += s[26]                                  # saves
    l[t]['P_IP']     += s[28]                                  # innings pitched
    l[t]['P_Hits']   += s[29]                                  # hits
    l[t]['P_BB']     += s[31]                                  # walks
    l[t]['P_ERuns']  += s[34]                                  # earned runs
    l[t]['P_K']      += s[35]                                  # strikeouts
#    print ('leagstats:', leagueStats)
        
# set current year for season (CCYY format), select the weeks tuple, and the league name
seasonCCYY         = 2020
weeksList          = weeks[seasonCCYY]
prevSeasonCCYY     = seasonCCYY - 1
prevSeasonLastWeek = str(prevSeasonCCYY) + weeks[prevSeasonCCYY][-1]
leagueName         = 'DSL'

# set pathname for database access
pathName = 'C:\\SQLite\\RotoDB\\'

# set connection filenames for DSL and RWDB
dbDSL  = 'DSL.db'
dbRWDB = 'RWDB.db'

# initialize counts
countOfWeeks = 0

# open main output file
statsFile = open('statfile.txt', 'w')

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
    teamInfoResults = cursDSL.fetchall()

# sort on team owner's name and create a list of the sorted team names
    teamAbbrList = [teamTuple[0] for teamTuple in (sorted(teamInfoResults, key=lambda teamInfo: (teamInfo[1].split()[1] + teamInfo[1].split()[0])))]
#    print ('teams:', teamAbbrList)

    prevWeek = ''    
# for each week in the tuple
    for week in weeksList:

        if week > '0409':
            break
        
# for each team in the league
        for team in teamAbbrList:
#            print ('team:', team)

# open temp team file, temp pitcher file, temp hitter file
            tempEList = []
            tempHList = []
            tempPList = []
            tempTList = []
            
            if team == 'SQDS':
                break
            
# initialize the counters for the team
           
# append the team header info to the team page
            teamInfo    = [aTuple for aTuple in teamInfoResults if aTuple[0] == team]
            teamAbbr    = teamInfo[0][0]
            teamOwner   = teamInfo[0][1]
            teamName    = teamInfo[0][2]
            teamPhone   = teamInfo[0][3]
            if teamPhone == None: teamPhone = '<no phone>'
            teamEmail   = teamInfo[0][4]
            if teamEmail == None: teamEmail = '<no email>'
            teamSkipper = teamInfo[0][5]
#            print ('teaminfo:', teamAbbr, ',', teamName, ',', teamOwner, ',',
#                                teamPhone, ',', teamEmail, ',', teamSkipper)

            tempTList.append (teamName
                        + ' ('
                        + teamAbbr
                        + ') '
                        + teamOwner
                        + ','
                        + teamPhone
                        + ','
                        + teamEmail
                        + ','
                        + teamSkipper
                        )

            leagueStats[teamAbbr] = copy.deepcopy(statsTemplate)

# do a SQL SELECT for that season + week + + league + team to get all the players on the team for that week
            statWeek = str(seasonCCYY) + week
            _SQL = 'select Status, Position, LastName, FirstName, ID, Salary, Contract from Rosters where CCYYMMDD = ? and League = ? and Team = ?'
            cursDSL.execute(_SQL, (statWeek, leagueName, teamAbbr))

# get the results of the SQL call and sort the roster by status
            roster = cursDSL.fetchall()
            roster.sort(key=lambda k: str(statusOrder[k[0]]) + positionOrder[k[1]] + k[2] + k[3])
#            print ('sorted:', roster)

            oldStatus   = 0
            oldPosition = ' '
            
            for player in roster:

                playerID     = player[4]
#                print ('player:', player[2], player[3])
                currStatus   = statusOrder[player[0]]
#                print ('currStatus:', currStatus)
                currPosition = positionOrder[player[1]]

                currStats    = getPlayerStats (statWeek, playerID)
#                print (); print ('currstats:', currStats); print ()
                
                playerType   = getPlayerType(currStats, currPosition)
#                print ('p type:', playerType)
                               
# check for break of active pitchers or hitters - change in status or change in position
#                print ('currStatus:', currStatus, 'oldStatus:', oldStatus)
                if oldStatus != currStatus:
                    if oldStatus == 1:
                        tempPList.append(makeTeamPitcherTotalsStr (leagueStats, teamAbbr))
                        tempHList.append(makeTeamHitterTotalsStr (leagueStats, teamAbbr))

                oldStatus   = currStatus
                oldPosition = currPosition

                fileType = getListType (currStatus, playerType)
#                print ('f type:', fileType)
                if fileType == 'E':
                    tempList = tempEList
                elif fileType == 'P':
                    tempList = tempPList
                else:
                    tempList = tempHList

                playerInfoStr = makePlayerInfoStr (player)
#                print ('pList:', playerInfoList)
                        
                if currStats == None:
                    statStr = '  <No stats returned>'

                else:                
                    if prevWeek != '':
                        prevStats = getPlayerStats (prevWeek, playerID)
                        if prevStats == None:
                            prevStats = emptyStats
                    else:                        
                        prevStats = emptyStats
#                    print (); print ('prevstats:', prevStats); print ()
                    
# find difference of current and previous week's stats
                    statDiff = calcStatDiff (currStats, prevStats)

                    if playerType == 'P':
                        sumPitcherStats (leagueStats, teamAbbr, statDiff)
                        statStr = makePitcherStatsStr (currStats)
                    else:
                        currPos = findPositions (currStats)
                        prevEOYStats = getPlayerStats (prevSeasonLastWeek, playerID)
                        
                        if prevEOYStats != None:
                            prevPos = findPositions (prevEOYStats)
                            bothPos = ''
                            if 'C' in prevPos or 'C' in currPos: bothPos += 'C'
                            if '1' in prevPos or '1' in currPos: bothPos += '1'
                            if '2' in prevPos or '2' in currPos: bothPos += '2'
                            if '3' in prevPos or '3' in currPos: bothPos += '3'
                            if 'S' in prevPos or 'S' in currPos: bothPos += 'S'
                            if 'O' in prevPos or 'O' in currPos: bothPos += 'O'
                            currPos = bothPos

                        sumHitterStats(leagueStats, teamAbbr, statDiff)
                        statStr = makeHitterStatsStr (currStats, currPos)

# append the current player's info and stats to the appropriate list
                tempList.append(playerInfoStr + statStr)
                    
# insert the contents of each list into the output file
            for aLine in tempTList: print (aLine, file=statsFile)

            print (makeHeaderPitchers(), file=statsFile)
            for aLine in tempPList: print (aLine, file=statsFile)
            print (' ', file = statsFile)
            
            print (makeHeaderHitters(), file=statsFile)
            for aLine in tempHList: print (aLine, file=statsFile)
            print (' ', file = statsFile)
            
            print (team, ' - Reserved and Minor League Players', file = statsFile)
            for aLine in tempEList: print (aLine, file=statsFile)
            print (' ', file = statsFile)
            print (' ', file = statsFile)

            tempEList = []
            tempHList = []
            tempPList = []
            tempTList = []
            
# save this week as the previous week
        prevWeek = str(seasonCCYY) + week
#        print ('prevWk:', prevWeek)

except Error as err:
    print ('DSL connection attempt failed with error:', err)
    connDSL.close()
    sys.exit()

# print ('League Stats:', leagueStats)

PWList = sorted ([(t[0], t[1]['P_Wins']) for t in leagueStats.items()], key = lambda k: k[1], reverse=True)
# print ('PWList:', PWList)
PSList = sorted ([(t[0], t[1]['P_Saves']) for t in leagueStats.items()], key = lambda k: k[1], reverse=True)
# print ('PSList:', PSList)
PKList = sorted ([(t[0], t[1]['P_K']) for t in leagueStats.items()], key = lambda k: k[1], reverse=True)
# print ('PKList:', PKList)
PERAList = sorted ([(t[0], float((t[1]['P_ERuns'] * 9)/ t[1]['P_IP'])) for t in leagueStats.items()], key = lambda k: k[1])
# print ('PERAList:', PERAList)
PWHIPList = sorted ([(t[0], float((t[1]['P_Hits'] + t[1]['P_BB'])/ t[1]['P_IP'])) for t in leagueStats.items()], key = lambda k: k[1])
# print ('PWHIPList:', PWHIPList)

HHRList = sorted ([(t[0], t[1]['H_HR']) for t in leagueStats.items()], key = lambda k: k[1], reverse=True)
# print ('HHRList:', HHRList)
HRBIList = sorted ([(t[0], t[1]['H_RBI']) for t in leagueStats.items()], key = lambda k: k[1], reverse=True)
# print ('HRBIList:', HRBIList)
HRUNSList = sorted ([(t[0], t[1]['H_Runs']) for t in leagueStats.items()], key = lambda k: k[1], reverse=True)
# print ('HRUNSList:', HRUNSList)
HSBList = sorted ([(t[0], t[1]['H_SB']) for t in leagueStats.items()], key = lambda k: k[1], reverse=True)
# print ('HSBList:', HSBList)
HBAList = sorted ([(t[0], float(t[1]['H_Hits']/t[1]['AB'])) for t in leagueStats.items()], key = lambda k: k[1], reverse=True)
# print ('HBAList:', HBAList)

print('Wins', 'Saves', 'Strikeouts', 'ERA', 'WHIP')
for ix in range(0, 4):
    print (PWList[ix][0],'=',"{: 4d}".format(PWList[ix][1]),
           PSList[ix][0],'=',"{: 4d}".format(PSList[ix][1]),
           PKList[ix][0],'=',"{: 5d}".format(PKList[ix][1]),
           PERAList[ix][0],'=',"{: 7.4f}".format(PERAList[ix][1]),
           PWHIPList[ix][0],'=',"{: 7.4f}".format(PWHIPList[ix][1]))


# close output file
statsFile.close()
