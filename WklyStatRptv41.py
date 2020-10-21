#  StatsReport - generate stats on a weekly basis for part or all of a season
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
import os
import copy
import sqlite3
from sqlite3 import Error

# create a sort order dictionary for player status
statusOrder = {'Active': 1, 'Open': 1, 'Pending': 2, 'Reserved': 3, 'Minors': 4, 'Waived': 5}
positionOrder = {'P': '01', 'U': '02', 'X': '03', 'C': '04', '1': '05', '2': '06', 'S': '07', '3': '08', 'W': '09',
                 'M': '10', 'O': '11'}

# create a template for team stats as a list of dictionary elts
seasonStats = {}
weeklyStats = {}

statsTemplate = {}
statsTemplate['AB'] = 0
statsTemplate['H_Runs'] = 0
statsTemplate['H_Hits'] = 0
statsTemplate['H_HR'] = 0
statsTemplate['H_RBI'] = 0
statsTemplate['H_SB'] = 0
statsTemplate['P_Wins'] = 0
statsTemplate['P_Saves'] = 0
statsTemplate['P_IP'] = 0
statsTemplate['P_Hits'] = 0
statsTemplate['P_BB'] = 0
statsTemplate['P_ERuns'] = 0
statsTemplate['P_K'] = 0

emptyStats = (0,) * 36

# create a dictionary of the weeks in each season (MMDD format) as a tuple
weeks = {2020: ('0101',),
         2019: (
#         '0409', ),
         '0409', '0416', '0423', '0430', '0507', '0514', '0521', '0528', '0604', '0611', '0618', '0625', '0702', '0709',
         '0716', '0723', '0730', '0806', '0813', '0820', '0827', '0903', '0910', '0917', '0924', '1001'),
         2018: (
         '0410', '0417', '0424', '0501', '0508', '0515', '0522', '0529', '0605', '0612', '0619', '0626', '0703', '0710',
         '0717', '0724', '0731', '0807', '0814', '0821', '0828', '0904', '0911', '0918', '0925', '1002'),
         2017: (
         '0411', '0418', '0425', '0502', '0509', '0516', '0523', '0530', '0606', '0613', '0620', '0627', '0704', '0711',
         '0718', '0725', '0801', '0808', '0815', '0822', '0829', '0905', '0912', '0919', '0926', '1003'),
         2016: (
         '0412', '0419', '0426', '0503', '0510', '0517', '0524', '0531', '0607', '0614', '0621', '0628', '0705', '0712',
         '0719', '0726', '0802', '0809', '0816', '0823', '0830', '0906', '0913', '0920', '0927', '1004'),
         2015: (
         '0410', '0414', '0421', '0428', '0505', '0512', '0519', '0526', '0602', '0609', '0616', '0623', '0630', '0707',
         '0714', '0721', '0728', '0804', '0811', '0818', '0825', '0901', '0908', '0915', '0922', '0929', '1006'),
         2014: (
         '0408', '0415', '0422', '0429', '0506', '0513', '0520', '0527', '0603', '0610', '0617', '0624', '0701', '0708',
         '0715', '0722', '0729', '0805', '0812', '0819', '0826', '0902', '0909', '0916', '0923'),
         2013: (
         '0402', '0409', '0416', '0423', '0430', '0507', '0514', '0521', '0528', '0604', '0611', '0618', '0625', '0702',
         '0709', '0716', '0723', '0730', '0806', '0813', '0820', '0827', '0903', '0910', '0917', '0924', '1001'),
         2012: (
         '0410', '0417', '0424', '0501', '0508', '0515', '0522', '0529', '0605', '0612', '0619', '0626', '0703', '0710',
         '0717', '0724', '0731', '0807', '0814', '0821', '0828', '0904', '0911', '0918', '0925', '1002'),
         2011: (
         '0405', '0412', '0419', '0426', '0503', '0510', '0517', '0524', '0531', '0607', '0614', '0621', '0628', '0705',
         '0712', '0719', '0726', '0802', '0809', '0816', '0823', '0830', '0906', '0913', '0920', '0927', '0928'),
         2010: (
         '0412', '0419', '0426', '0503', '0510', '0517', '0524', '0531', '0607', '0614', '0621', '0628', '0705', '0712',
         '0719', '0726', '0802', '0809', '0816', '0823', '0830', '0906', '0913', '0920', '0927', '1004')
         }


# calculate difference of two groups of stats
def calcStatDiff(n, o):
    diff = ('StatDiff'
            , n[1]
            , n[2]
            , n[3]
            , n[4]
            , n[5]
            , n[6] - o[6]
            , n[7] - o[7]
            , n[8] - o[8]
            , n[9] - o[9]
            , n[10] - o[10]
            , n[11] - o[11]
            , n[12] - o[12]
            , n[13] - o[13]
            , n[14] - o[14]
            , n[15] - o[15]
            , n[16] - o[16]
            , n[17] - o[17]
            , n[18] - o[18]
            , n[19] - o[19]
            , n[20] - o[20]
            , n[21] - o[21]
            , n[22] - o[22]
            , n[23] - o[23]
            , n[24] - o[24]
            , n[25] - o[25]
            , n[26] - o[26]
            , n[27] - o[27]
            , n[28] - o[28]
            , n[29] - o[29]
            , n[30] - o[30]
            , n[31] - o[31]
            , n[32] - o[32]
            , n[33] - o[33]
            , n[34] - o[34]
            , n[35] - o[35]
            )
    return (diff)


# find eligible positions using a stats tuple
def findPositions(s) -> str:
    eligPos = ''

    if s[18:24] != (0, 0, 0, 0, 0, 0):
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
def getListType(s, p):  # status, player type
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
def getPlayerType(s, p) -> str:  # stats, position type
    #    print ('stats:', s, ',pos:', p)
    if s == None:
        #        print ('stats = None')
        if p == '01':
            pType = 'P'
        else:
            pType = 'H'

    elif s[6:24] != (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0):
        pType = 'H'

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
def makeHitterStatsStr(s, e) -> str:  # stats, positions

    if s[6] == 0: battingAverage = 0
    else:         battingAverage = s[8] / s[6]

    sStr = ' '.join(
        [' '
            , "{: 4d}".format(s[6])  # AB
            , "{: 5d}".format(s[8])  # hits
            , "{: 4d}".format(s[11])  # HR
            , "{: 4d}".format(s[12])  # RBI
            , "{: 4d}".format(s[7])  # runs
            , "{: 4d}".format(s[13])  # steals
            , "{: 6.4f}".format(battingAverage)  # BA
            , ' <' + e + '>'  # positions
         ])

    return (sStr)


# print pitcher stats
def makePitcherStatsStr(s) -> str:  # stats

    if s[28] == 0:
        ERA  = 0
        WHIP = 0
    else:
        ERA =  s[34] / s[28]
        WHIP = (s[29] + s[31]) / s[28]

    sStr = ' '.join(
        [' '
            , "{: 3d}".format(s[24])  # wins
            , "{: 3d}".format(s[26])  # saves
            , "{: 6.1f}".format(s[28])  # innings pitched
            , "{: 4d}".format(s[29])  # hits
            , "{: 4d}".format(s[31])  # walks
            , "{: 4d}".format(s[34])  # earned runs
            , "{: 4d}".format(s[35])  # strikeouts
            , "{: 7.3f}".format(9 * ERA)  # ERA
            , "{: 7.3f}".format(WHIP)  # WHIP
         ])

    return (sStr)


# print player info
def makePlayerInfoStr(p) -> str:  # player
    infoStr = ' '.join(
        [p[0][0]  # status
            , "{:2s}".format(p[1])  # position
            , "{:25s}".format(p[3] + ' ' + p[2])  # full name
            , "{:0>8d}".format(p[4])  # ID
            , "{: >5.2f}".format(p[5])  # salary
            , "{:2s}".format(p[6])  # contract
         ])

    return (infoStr)


# print hitter stat totals for a team
def makeTeamHitterTotalsStr(l, t) -> str:  # league, stat totals
    totStr = ' '.join(
        [t
            , ' - Hitter Totals:                          '  # team abbr
            , "{: 5d}".format(l[t]['AB'])  # AB
            , "{: 5d}".format(l[t]['H_Hits'])  # hits
            , "{: 4d}".format(l[t]['H_HR'])  # HR
            , "{: 4d}".format(l[t]['H_RBI'])  # RBI
            , "{: 4d}".format(l[t]['H_Runs'])  # runs
            , "{: 4d}".format(l[t]['H_SB'])  # steals
            , "{: 6.4f}".format(l[t]['H_Hits'] / l[t]['AB'])  # BA
         ])

    return (totStr)


# print stat totals for a team
def makeTeamPitcherTotalsStr(l, t) -> str:  # league, stats totals
    totStr = ' '.join(
        [t
            , ' - Pitcher Totals:                          '  # team abbr
            , "{: 3d}".format(l[t]['P_Wins'])  # wins
            , "{: 3d}".format(l[t]['P_Saves'])  # saves
            , "{: 6.1f}".format(l[t]['P_IP'])  # IP
            , "{: 3d}".format(l[t]['P_Hits'])  # hits
            , "{: 4d}".format(l[t]['P_BB'])  # walks
            , "{: 3d}".format(l[t]['P_ERuns'])  # earned runs
            , "{: 3d}".format(l[t]['P_K'])  # strikeouts
            , "{: 7.3f}".format(9 * (l[t]['P_ERuns'] / l[t]['P_IP']))  # ERA
            , "{: 7.3f}".format((l[t]['P_Hits'] + l[t]['P_BB']) / l[t]['P_IP'])  # WHIP
         ])

    return (totStr)


# sum pitcher stats for a team
def sumHitterStats(l, t, s):  # league, team, stats
    l[t]['AB'] += s[6]  # AB
    l[t]['H_Runs'] += s[7]  # runs
    l[t]['H_Hits'] += s[8]  # hits
    l[t]['H_HR'] += s[11]  # HR
    l[t]['H_RBI'] += s[12]  # RBI
    l[t]['H_SB'] += s[13]  # steals


#    print ('leagstats:', weeklyStats)

# sum pitcher stats for a team
def sumPitcherStats(l, t, s):  # league, team, stats
    l[t]['P_Wins'] += s[24]  # wins
    l[t]['P_Saves'] += s[26]  # saves
    l[t]['P_IP'] += s[28]  # innings pitched
    l[t]['P_Hits'] += s[29]  # hits
    l[t]['P_BB'] += s[31]  # walks
    l[t]['P_ERuns'] += s[34]  # earned runs
    l[t]['P_K'] += s[35]  # strikeouts


#    print ('leagstats:', weeklyStats)

# put points on list - assumes list is sorted (asc or desc) and that each elt is a tuple of team name and catg value;
#   return a list of tuples that are team name, catg value, and points
def putPointsOnList(n, catgList):  # number of teams, category list (team, value) -> (team, value, points)
    # set remaining points to max
    # set max team index to max
    # set team index to 0
    # set loop-at-end to false
    remainingPts = n
    maxTeamIx = n - 1
    teamIx = 0
    loopAtEnd = False

    # while not loop-at-end
    #   if team index = max
    #     this list entry gets remaining points
    while not loopAtEnd:
        #        print('in outer loop team:', teamIx, ' pts=', remainingPts)
        if teamIx == maxTeamIx:
            #            print('at last team:', teamIx, catgList[teamIx][0], ' val=', catgList[teamIx][0], ' pts=', remainingPts)
            #        ptsArray.insert (teamIx, remainingPts)
            catgList[teamIx] += (remainingPts,)

        #   elif this value <> next value
        #     this list entry gets remaining points
        elif catgList[teamIx][1] != catgList[teamIx + 1][1]:
            #            print('diff vals:', teamIx, catgList[teamIx][0], ' val=', catgList[teamIx][1],
            #                  teamIx + 1, catgList[teamIx + 1][0], ' val=', catgList[teamIx + 1][1], ' pts=', remainingPts)
            catgList[teamIx] += (remainingPts,)
            remainingPts -= 1

        #   else this value = next value, begin looping through tied teams
        #     set team offset to 0
        #     shared points = remaining points
        #     set loop-at-end to false
        else:
            teamOffset = 0
            sharedPoints = remainingPts
            loopAtEnd = False

            #     while not loop-at-end
            #       if team+offset > max
            #         set loop-at-end to true
            while not loopAtEnd:
                #                print('tied at:', teamIx, catgList[teamIx + teamOffset][0], ' val=', catgList[teamIx + teamOffset][0],
                #                      ' pts=', remainingPts, 'offset=', teamOffset, 'shared=', sharedPoints)

                if teamIx + teamOffset == maxTeamIx:
                    #                    print('reached max teams')
                    loopAtEnd = True

                #       if this team+offset value = next value
                #         subtract 1 from remaining points
                #         add remaining points to shared points
                #         add 1 to team offset
                elif catgList[teamIx + teamOffset][1] == catgList[teamIx + teamOffset + 1][1]:
                    #                    print('tied team:', teamIx + teamOffset)
                    remainingPts -= 1
                    sharedPoints += remainingPts
                    teamOffset += 1

                #       else
                #         set loop-at-end to true
                else:
                    #                    print('end of tied teams:', teamIx + teamOffset)
                    loopAtEnd = True

            #     shared points = shared points / (offset - 1)
            #     for team in range (team index, team+offset + 1)
            #       list entry gets shared points
            sharedPoints = sharedPoints / (teamOffset + 1)
            #            print('shared pts:', sharedPoints)
            for ix in range(teamIx, teamIx + teamOffset + 1):
                #                print('shared at:', ix, ' = ', sharedPoints)
                catgList[ix] += (sharedPoints,)

            #     team index = team+offset
            #     subtract 1 from remaining
            teamIx = teamIx + teamOffset
            remainingPts -= 1
        #            print('ix after tie but before inc:', teamIx, 'and remaining pts=', remainingPts)

        teamIx += 1

        if teamIx > maxTeamIx:
            loopAtEnd = True
        else:
            loopAtEnd = False

    #    print('list with points:', catgList)

    return ()

#   MAIN ROUTINE
# set current and previous years for season (CCYY format), select the weeks tuple, and the league name
seasonCCYY = 2019
weeksList = weeks[seasonCCYY]
prevSeasonCCYY = seasonCCYY - 1
prevSeasonLastWeek = str(prevSeasonCCYY) + weeks[prevSeasonCCYY][-1]
leagueName = 'DSL'
numOfTeams = 12

# set pathname for database access
pathName = 'C:\\SQLite\\RotoDB\\'

# set connection filenames for DSL and RWDB
dbDSL = 'DSL.db'
dbRWDB = 'RWDB.db'

# initialize counts
countOfWeeks = 0

# open season temp stats file
statsFilename = 'ST' + str(seasonCCYY) + weeksList[-1] + '.txt'
# print ('sfilename:', statsFilename)
seasonTempFile = open(statsFilename, 'w')

try:
# connect to the databases
    connDSL = sqlite3.connect(pathName + dbDSL)
    connRWDB = sqlite3.connect(pathName + dbRWDB)

# create cursors for the databases
    cursDSL = connDSL.cursor()
    cursRWDB = connRWDB.cursor()

# Generate dictionary of previous season's positions for all players
    _SQL = 'select * from WklyStats where CCYYMMDD = ?'
    lastWk = int(prevSeasonLastWeek)
    cursRWDB.execute(_SQL, (lastWk,))
    previousSeasonPos = cursRWDB.fetchall()
#    print ('prevPos:', previousSeasonPos)
    prevPosDict = {}
    for px in previousSeasonPos:
        prevPosDict[px[3]] = findPositions(px)
#    sys.exit()

# SQL SELECT on the team info
    _SQL = 'select TeamAbbr, TeamOwner, TeamName, TeamPhoneNumber, TeamEmail, DeadSkipper from TeamInfo where CCYY = ? and LeagueAbbr = ?'
    cursDSL.execute(_SQL, (seasonCCYY, leagueName))

# get the results of the SQL call
    teamInfoResults = cursDSL.fetchall()

# sort on team owner's name and create a list of the sorted team names
    teamAbbrList = [teamTuple[0] for teamTuple in
                    (sorted(teamInfoResults, key=lambda teamInfo: (teamInfo[1].split()[1] + teamInfo[1].split()[0])))]
#    print ('teams:', teamAbbrList)

    prevWeek = ''
# for each week in the tuple
    for week in weeksList:

# open weekly temp stats file
        tempFilename = 'WT' + str(seasonCCYY) + str(week) + '.txt'
#        print ('sfilename:', statsFilename)
        weeklyTempFile = open(tempFilename, 'w')

        if week > '0530':
            break

        # for each team in the league
        for team in teamAbbrList:
            #            print ('team:', team)

            # open temp team file, temp pitcher file, temp hitter file
            tempEList = []
            tempHList = []
            tempPList = []
            tempTList = []

            #            if team == 'SQDS':
            #                break

            # initialize the counters for the team

            # append the team header info to the team page
            teamInfo = [aTuple for aTuple in teamInfoResults if aTuple[0] == team]
            teamAbbr = teamInfo[0][0]
            teamOwner = teamInfo[0][1]
            teamName = teamInfo[0][2]
            teamPhone = teamInfo[0][3]
            if teamPhone == None: teamPhone = '<no phone>'
            teamEmail = teamInfo[0][4]
            if teamEmail == None: teamEmail = '<no email>'
            teamSkipper = teamInfo[0][5]
#            print ('teaminfo:', teamAbbr, ',', teamName, ',', teamOwner, ',',
#                                teamPhone, ',', teamEmail, ',', teamSkipper)

            tempTList.append(teamName
                             + ' ('
                             + teamAbbr
                             + ') '
                             + teamOwner
                             + ','
                             + str(teamPhone)
                             + ','
                             + teamEmail
                             + ','
                             + teamSkipper
                             )

            weeklyStats[teamAbbr] = copy.deepcopy(statsTemplate)

            # do a SQL SELECT for that season + week + + league + team to get all the players on the team for that week
            statWeek = str(seasonCCYY) + week
            _SQL = 'select Status, Position, LastName, FirstName, ID, Salary, Contract from Rosters where CCYYMMDD = ? and League = ? and Team = ?'
            cursDSL.execute(_SQL, (statWeek, leagueName, teamAbbr))

            # get the results of the SQL call and sort the roster by status
            roster = cursDSL.fetchall()
            roster.sort(key=lambda k: str(statusOrder[k[0]]) + positionOrder[k[1]] + k[2] + k[3])
            #            print ('sorted:', roster)

            oldStatus = 0
            oldPosition = ' '

            for player in roster:

                playerID = player[4]
                #                print ('player:', player[2], player[3])
                currStatus = statusOrder[player[0]]
                #                print ('currStatus:', currStatus)
                currPosition = positionOrder[player[1]]

                currStats = getPlayerStats(statWeek, playerID)
                #                print (); print ('currstats:', currStats); print ()

                playerType = getPlayerType(currStats, currPosition)
                #                print ('p type:', playerType)

                # check for break of active pitchers or hitters - change in status or change in position
                #                print ('currStatus:', currStatus, 'oldStatus:', oldStatus)
                if oldStatus != currStatus:
                    if oldStatus == 1:
                        tempPList.append(makeTeamPitcherTotalsStr(weeklyStats, teamAbbr))
                        tempHList.append(makeTeamHitterTotalsStr(weeklyStats, teamAbbr))

                oldStatus = currStatus
                oldPosition = currPosition

                fileType = getListType(currStatus, playerType)
                #                print ('f type:', fileType)
                if fileType == 'E':
                    tempList = tempEList
                elif fileType == 'P':
                    tempList = tempPList
                else:
                    tempList = tempHList

                playerInfoStr = makePlayerInfoStr(player)
#                print ('pInfo:', playerInfoStr)

                if currStats == None:
                    statStr = '  <No stats returned>'

                else:
                    if prevWeek != '':
                        prevStats = getPlayerStats(prevWeek, playerID)
                        if prevStats == None:
                            prevStats = emptyStats
                    else:
                        prevStats = emptyStats
                    #                    print (); print ('prevstats:', prevStats); print ()

                    # find difference of current and previous week's stats
                    statDiff = calcStatDiff(currStats, prevStats)

                    if playerType == 'P':
                        if currStatus == 1:
                            sumPitcherStats(weeklyStats, teamAbbr, statDiff)
                        statStr = makePitcherStatsStr(currStats)
                    else:
                        currPos = findPositions(currStats)
                        prevEOYStats = getPlayerStats(prevSeasonLastWeek, playerID)

                        if prevEOYStats != None:
                            prevPos = prevPosDict[playerID]
#                            print ('pID=', playerID, ',prevPos=', prevPos)
                            bothPos = ''
                            if 'C' in prevPos or 'C' in currPos: bothPos += 'C'
                            if '1' in prevPos or '1' in currPos: bothPos += '1'
                            if '2' in prevPos or '2' in currPos: bothPos += '2'
                            if '3' in prevPos or '3' in currPos: bothPos += '3'
                            if 'S' in prevPos or 'S' in currPos: bothPos += 'S'
                            if 'O' in prevPos or 'O' in currPos: bothPos += 'O'
                            currPos = bothPos

                        if currStatus == 1:
                            sumHitterStats(weeklyStats, teamAbbr, statDiff)
#                        print ('hitStats:', currStats)
                        statStr = makeHitterStatsStr(currStats, currPos)

                # append the current player's info and stats to the appropriate list
                tempList.append(playerInfoStr + statStr)

            # insert the contents of each list into the output file
            for aLine in tempTList: print(aLine, file=weeklyTempFile)

            print(makeHeaderPitchers(), file=weeklyTempFile)
            for aLine in tempPList: print(aLine, file=weeklyTempFile)
            print(' ', file=weeklyTempFile)

            print(makeHeaderHitters(), file=weeklyTempFile)
            for aLine in tempHList: print(aLine, file=weeklyTempFile)
            print(' ', file=weeklyTempFile)

            print(team, ' - Reserved and Minor League Players', file=weeklyTempFile)
            for aLine in tempEList: print(aLine, file=weeklyTempFile)
            print(' ', file=weeklyTempFile)
            print(' ', file=weeklyTempFile)

            tempEList = []
            tempHList = []
            tempPList = []
            tempTList = []

        # save this week as the previous week
        prevWeek = str(seasonCCYY) + week
#        print ('prevWk:', prevWeek)

# close weekly temp file
        weeklyTempFile.close()

# print ('League Stats:', weeklyStats)

        PWList = sorted([(t[0], t[1]['P_Wins']) for t in weeklyStats.items()], key=lambda k: k[1], reverse=True)
        putPointsOnList(numOfTeams, PWList)
        PSList = sorted([(t[0], t[1]['P_Saves']) for t in weeklyStats.items()], key=lambda k: k[1], reverse=True)
        putPointsOnList(numOfTeams, PSList)
        PKList = sorted([(t[0], t[1]['P_K']) for t in weeklyStats.items()], key=lambda k: k[1], reverse=True)
        putPointsOnList(numOfTeams, PKList)
        PERAList = sorted([(t[0], float((t[1]['P_ERuns'] * 9) / t[1]['P_IP'])) for t in weeklyStats.items()],
                          key=lambda k: k[1])
        putPointsOnList(numOfTeams, PERAList)
        PWHIPList = sorted([(t[0], float((t[1]['P_Hits'] + t[1]['P_BB']) / t[1]['P_IP'])) for t in weeklyStats.items()],
                           key=lambda k: k[1])
        putPointsOnList(numOfTeams, PWHIPList)

        HHRList = sorted([(t[0], t[1]['H_HR']) for t in weeklyStats.items()], key=lambda k: k[1], reverse=True)
        putPointsOnList(numOfTeams, HHRList)
        HRBIList = sorted([(t[0], t[1]['H_RBI']) for t in weeklyStats.items()], key=lambda k: k[1], reverse=True)
        putPointsOnList(numOfTeams, HRBIList)
        HRUNSList = sorted([(t[0], t[1]['H_Runs']) for t in weeklyStats.items()], key=lambda k: k[1], reverse=True)
        putPointsOnList(numOfTeams, HRUNSList)
        HSBList = sorted([(t[0], t[1]['H_SB']) for t in weeklyStats.items()], key=lambda k: k[1], reverse=True)
        putPointsOnList(numOfTeams, HSBList)
        HBAList = sorted([(t[0], float(t[1]['H_Hits'] / t[1]['AB'])) for t in weeklyStats.items()], key=lambda k: k[1],
                         reverse=True)
        putPointsOnList(numOfTeams, HBAList)

        pointTotals = {}
        for ix in PWList:
            pointTotals[ix[0]] = [ix[2], 0, ix[2]]

        for ix in PSList:
            pointTotals[ix[0]] = [pointTotals[ix[0]][0] + ix[2], pointTotals[ix[0]][1], pointTotals[ix[0]][2] + ix[2]]

        for ix in PKList:
            pointTotals[ix[0]] = [pointTotals[ix[0]][0] + ix[2], pointTotals[ix[0]][1], pointTotals[ix[0]][2] + ix[2]]

        for ix in PERAList:
            pointTotals[ix[0]] = [pointTotals[ix[0]][0] + ix[2], pointTotals[ix[0]][1], pointTotals[ix[0]][2] + ix[2]]

        for ix in PWHIPList:
            pointTotals[ix[0]] = [pointTotals[ix[0]][0] + ix[2], pointTotals[ix[0]][1], pointTotals[ix[0]][2] + ix[2]]

        for ix in HHRList:
            pointTotals[ix[0]] = [pointTotals[ix[0]][0], pointTotals[ix[0]][1] + ix[2], pointTotals[ix[0]][2] + ix[2]]

        for ix in HRBIList:
            pointTotals[ix[0]] = [pointTotals[ix[0]][0], pointTotals[ix[0]][1] + ix[2], pointTotals[ix[0]][2] + ix[2]]

        for ix in HRUNSList:
            pointTotals[ix[0]] = [pointTotals[ix[0]][0], pointTotals[ix[0]][1] + ix[2], pointTotals[ix[0]][2] + ix[2]]

        for ix in HSBList:
            pointTotals[ix[0]] = [pointTotals[ix[0]][0], pointTotals[ix[0]][1] + ix[2], pointTotals[ix[0]][2] + ix[2]]

        for ix in HBAList:
            pointTotals[ix[0]] = [pointTotals[ix[0]][0], pointTotals[ix[0]][1] + ix[2], pointTotals[ix[0]][2] + ix[2]]

        pitRankList = sorted(pointTotals.items(), key=lambda k: k[1][0], reverse=True)
        # print (pitRankList)
        hitRankList = sorted(pointTotals.items(), key=lambda k: k[1][1], reverse=True)
        # print (hitRankList)
        totRankList = sorted(pointTotals.items(), key=lambda k: k[1][2], reverse=True)
        # print (totRankList)

# open weekly stats file for standings
        statsFilename = 'W' + str(seasonCCYY) + str(week) + '.txt'
# print ('sfilename:', statsFilename)
        weeklyStatsFile = open(statsFilename, 'w')

        print('   Wins        ', 'Saves      ', 'Strikeouts        ', 'ERA             ', 'WHIP', file=weeklyStatsFile)
        for ix in range(0, numOfTeams):
            print(PWList[ix][0], "{: 4d}".format(PWList[ix][1]), '   ',
                  PSList[ix][0], "{: 4d}".format(PSList[ix][1]), '   ',
                  PKList[ix][0], "{: 5d}".format(PKList[ix][1]), '   ',
                  PERAList[ix][0], "{: 7.4f}".format(PERAList[ix][1]), '   ',
                  PWHIPList[ix][0], "{: 7.4f}".format(PWHIPList[ix][1]), file=weeklyStatsFile)

        print(' ', file=weeklyStatsFile)
        print('    HR           ', 'RBI         ', 'Runs          ', 'SB            ', 'BA', file=weeklyStatsFile)
        for ix in range(0, numOfTeams):
            print(HHRList[ix][0], "{: 4d}".format(HHRList[ix][1]), '   ',
                  HRBIList[ix][0], "{: 4d}".format(HRBIList[ix][1]), '   ',
                  HRUNSList[ix][0], "{: 4d}".format(HRUNSList[ix][1]), '   ',
                  HSBList[ix][0], "{: 4d}".format(HSBList[ix][1]), '   ',
                  HBAList[ix][0], "{: 7.4f}".format(HBAList[ix][1]), file=weeklyStatsFile)

        print(' ', file=weeklyStatsFile)
        print('Pitching Points    ', 'Hitting Points      ', 'Total Points', file=weeklyStatsFile)
        for ix in range(0, numOfTeams):
            print(pitRankList[ix][0], "{: 10.2f}".format(pitRankList[ix][1][0]), '   ',
                  hitRankList[ix][0], "{: 10.2f}".format(hitRankList[ix][1][1]), '   ',
                  totRankList[ix][0], "{: 10.2f}".format(totRankList[ix][1][2]), file=weeklyStatsFile)

# put a spacer line after standings and before team stats
        print (' ', file=weeklyStatsFile)

# open weekly temp file to append to standings
        weeklyTempFile = open(tempFilename, 'r')
        for aLine in weeklyTempFile:
            print (aLine, end='', file=weeklyStatsFile)

# close weekly temp and stats files
        weeklyTempFile.close()
        os.remove(tempFilename)
        weeklyStatsFile.close()


except Error as err:
    print('DSL connection attempt failed with error:', err)
    connDSL.close()
    sys.exit()

# close season stats  file
seasonTempFile.close()