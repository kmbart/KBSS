#! Week By Week Search and Select
#  define weeks in calendar as a tuple
#  initialize search term
#  initialize counts
#  for each week in the tuple
#    open the YTDS<mmdd> file
#    print 'Opening file:' YTDS<mmdd>
#    get the contents of the YTDS<mmdd> file
#    close the YTDS<mmdd> file
#    perform searchFile

# searchFile function
#    reset found-in-file flag
#    for each line in the YTDS<mmdd> file
#      if the search term is present
#        set found-in-file flag
#        increment count of lines found
#        print the entire line
#    if found-in-file
#      increment count of files found
#  print count of lines, count of files found

#  define weeks in calendar as a tuple
weeks2019 = ('0409','0416','0423','0430','0507','0514','0521','0528','0604','0611','0618','0625','0702','0709','0716','0723','0730','0806','0813','0820','0827','0903','0910','0917','0924','1001')

#  initialize search term
#  initialize counts
searchTerm   = 'KOPS Pitching For Week:'
countOfLines = 0
countOfFiles = 0

#  for each week in the tuple
#    open the YTDS<mmdd> file
#    print 'Opening file:' YTDS<mmdd>
#    get the contents of the YTDS<mmdd> file
#    close the YTDS<mmdd> file
for week in weeks2019:
    fileName = 'YTDS' + week + '.DSL'
#    print ('filename:', fileName)

    try:
#        YTDSfile = open('C:\\DSL\\' + fileName)
        with open('C:\\DSL\\' + fileName) as YTDSfile:
            linelist = YTDSfile.readlines()

#    reset found-in-file flag
            foundInFile = False
    
#    for each line in the YTDS<mmdd> file
#      if the search term is present
#        set found-in-file flag
#        increment count of lines found
#        print the entire line
            for line in linelist:
                if searchTerm in line:
                    foundInFile = True
                    countOfLines += 1
                    print (week,line,end='')
        
#    if found-in-file
#      increment count of files found
            if foundInFile:
                countOfFiles += 1
#        print ('Found in file:', fileName)


    except IOError:
        print ('Error opening file:', fileName)
        
#    YTDSfile.close()

#  print count of lines, count of files found
print ('Lines found:', countOfLines)
print ('Files found:', countOfFiles)
