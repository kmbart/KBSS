#  POINTSTEST

import sqlite3
from sqlite3 import Error
import sys

# create list of teams and values
# create empty array of points
# HHRList = [('WARD', 317), ('PMOB', 266), ('BOYS', 250), ('ACES', 243), ('KOPS', 239), ('CRIT', 235), ('PWIZ', 225), ('LOUS', 208), ('DLAY', 207), ('SQDS', 204), ('RAKE', 182), ('BALZ', 171)]
HHRList = [('WARD', 317), ('PMOB', 266), ('BOYS', 250), ('ACES', 250), ('KOPS', 250), ('CRIT', 235), ('PWIZ', 225), ('LOUS', 208), ('DLAY', 207), ('SQDS', 204), ('RAKE', 171), ('BALZ', 171)]
# HHRList = [('WARD', 317), ('PMOB', 266), ('BOYS', 250), ('ACES', 250), ('KOPS', 250), ('CRIT', 235), ('PWIZ', 225), ('LOUS', 208), ('DLAY', 207), ('SQDS', 204), ('RAKE', 204), ('BALZ', 171)]
# ptsArray = []

# set remaining points to max
# set max team index to max
# set team index to 0
# set loop-at-end to false
remainingPts = 12
maxTeamIx    = 11
teamIx       = 0
loopAtEnd    = False

# while not loop-at-end
#   if team index = max
#     this list entry gets remaining points
while not loopAtEnd:
    print('in outer loop team:', teamIx, ' pts=', remainingPts)
    if teamIx == maxTeamIx:
        print ('at last team:', teamIx, HHRList[teamIx][0], ' val=',  HHRList[teamIx][0], ' pts=', remainingPts)
#        ptsArray.insert (teamIx, remainingPts)
        HHRList[teamIx] += (remainingPts,)

#   elif this value <> next value
#     this list entry gets remaining points
    elif HHRList [teamIx][1] != HHRList [teamIx + 1][1]:
        print ('diff vals:', teamIx, HHRList[teamIx][0], ' val=',  HHRList[teamIx][1],
                             teamIx + 1, HHRList[teamIx + 1][0], ' val=',  HHRList[teamIx + 1][1], ' pts=', remainingPts)
#        ptsArray.insert (teamIx, remainingPts)
        HHRList[teamIx] += (remainingPts,)
        remainingPts -= 1

#   else this value = next value, begin looping through tied teams
    else:
#     set team offset to 0
#     shared points = remaining points
#     set loop-at-end to false
        teamOffset   = 0
        sharedPoints = remainingPts
        loopAtEnd    = False

#     while not loop-at-end
        while not loopAtEnd:
            print('tied at:', teamIx, HHRList[teamIx + teamOffset][0], ' val=', HHRList[teamIx + teamOffset][0],
                  ' pts=', remainingPts, 'offset=', teamOffset, 'shared=', sharedPoints)

#         if team+offset > max
#           set loop-at-end to true
            if teamIx + teamOffset == maxTeamIx:
                print ('reached max teams')
                loopAtEnd = True

#       if this team+offset value = next value
#         subtract 1 from remaining points
#         add remaining points to shared points
#         add 1 to team offset
            elif HHRList [teamIx + teamOffset][1] == HHRList [teamIx + teamOffset + 1][1]:
                print('tied team:', teamIx + teamOffset)
                remainingPts -= 1
                sharedPoints += remainingPts
                teamOffset += 1

#       else
#         set loop-at-end to true
            else:
                print('end of tied teams:', teamIx + teamOffset)
                loopAtEnd = True

#     shared points = shared points / (offset - 1)
#     for team in range (team index, team+offset + 1)
#       list entry gets shared points

        sharedPoints = sharedPoints / (teamOffset + 1)
        print('shared pts:', sharedPoints)
        for ix in range(teamIx, teamIx + teamOffset + 1):
            print('shared at:', ix, ' = ', sharedPoints)
#            ptsArray.insert (ix, sharedPoints)
            HHRList[ix] += (sharedPoints,)

#     team index = team+offset
#     subtract 1 from remaining
        teamIx = teamIx + teamOffset
        remainingPts -= 1
        print('ix after tie but before inc:', teamIx, 'and remaining pts=', remainingPts)

    teamIx += 1

    if teamIx > maxTeamIx:
        loopAtEnd = True
    else:
        loopAtEnd = False

# print ('Pts Array:', ptsArray)
print ('list with points:', HHRList)
