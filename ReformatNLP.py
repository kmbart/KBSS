#  ReformatNLP - Fix NLP<MMDD> file to put one player on each line
#  define weeks in calendar as a tuple
#  
#  initialize counts
#  
#  for each week in the tuple
#    open the NLP<mmdd> file



import re
# import sys

# define a good line as 22 sets of <word>,<,> pairs, then a newline
# GoodLine   = re.compile('([\w| |\'|\.]+,){22}\d+\n')
GoodLine   = re.compile('([\w| |\'|\.|\-]+,){2}(\d){4,7},(\w){2,3},((\d+\.?\d*),){12}\d+\n')
   
# set all weeks in a given season as a tuple
Weeks2020 = ('0927',)
Weeks2019 = ('0409','0416','0423','0430','0507','0514','0521','0528','0604','0611','0618','0625','0702','0709','0716','0723','0730','0806','0813','0820','0827','0903','0910','0917','0924','1001')
Weeks2018 = ('0410','0417','0424','0501','0508','0515','0522','0529','0605','0612','0619','0626','0703','0710','0717','0724','0731','0807','0814','0821','0828','0904','0911','0918','0925','1002')
Weeks2017 = ('0411','0418','0425','0502','0509','0516','0523','0530','0606','0613','0620','0627','0704','0711','0718','0725','0801','0808','0815','0822','0829','0905','0912','0919','0926','1003')
Weeks2016 = ('0412','0419','0426','0503','0510','0517','0524','0531','0607','0614','0621','0628','0705','0712','0719','0726','0802','0809','0816','0823','0830','0906','0913','0920','0927','1004')
Weeks2015 = ('0410','0414','0421','0428','0505','0512','0519','0526','0602','0609','0616','0623','0630','0707','0714','0721','0728','0804','0811','0818','0825','0901','0908','0915','0922','0929','1006')
Weeks2014 = ('0408','0415','0422','0429','0506','0513','0520','0527','0603','0610','0617','0624','0701','0708','0715','0722','0729','0805','0812','0819','0826','0902','0909','0916','0923')
# Weeks2014 = ('0506',)
Weeks2013 = ('0402','0409','0416','0423','0430','0507','0514','0521','0528','0604','0611','0618','0625','0702','0709','0716','0723','0730','0806','0813','0820','0827','0903','0910','0917','0924','1001')
Weeks2012 = ('0410','0417','0424','0501','0508','0515','0522','0529','0605','0612','0619','0626','0703','0710','0717','0724','0731','0807','0814','0821','0828','0904','0911','0918','0925','1002')
Weeks2011 = ('0405','0412','0419','0426','0503','0510','0517','0524','0531','0607','0614','0621','0628','0705','0712','0719','0726','0802','0809','0816','0823','0830','0906','0913','0920','0927','0928')
Weeks2010 = ('0412','0419','0426','0503','0510','0517','0524','0531','0607','0614','0621','0628','0705','0712','0719','0726','0802','0809','0816','0823','0830','0906','0913','0920','0927','1004')

# set year parm and select the appropriate year's tuple
StatCCYY = '2020'
WeekMMDD = Weeks2020

FilesOpened = 0
PreLine     = ''

#  for each week in the tuple
for CountOfFiles, Week in enumerate(WeekMMDD):

    FileName = 'C:\\RW\\RW' +StatCCYY + '\\NLP' + StatCCYY[3:4] + Week + '.txt'
    print ('filename:', FileName)

    try:
        with open(FileName) as NLPFile:
            FilesOpened += 1
            LinesRead   = 0
            
            LineList = NLPFile.readlines()

            WriteLines = []

# for each line in the file
            for CountOfLines, NextLine in enumerate(LineList):
                if CountOfLines == 0: continue    #skip the header line
#                if CountOfLines > 66: break
#                print (CountOfLines, ':(', len(NextLine), ')=', NextLine)
                                
                LinesRead  += 1
                
# if there is nothing leftover from the previous line check this line
                if PreLine == '':
# check this line and if it is good then write it to the output list and continue
                    moGoodLine = GoodLine.match(NextLine)
                    if moGoodLine != None:
#                        print ('good line:', NextLine)
                        WriteLines.append(NextLine)
                        continue

# the line is not good as-is, so try to split it on blank; replace blanks in the name with underscore
                NextLine = NextLine[0:44].replace(' ', '_') + NextLine[44:]
#                print ('replaced=', NextLine)                    
                LineTails = NextLine.split(' ')
#                print ('linetails after split:', LineTails)
                CountTails = len(LineTails)
                if CountTails > 2:
                    CopyTails  = [LineTails[0]]
#                    print ('linetails after [0]:', LineTails)
#                    print ('copytails after [0]:', CopyTails)
                    TrailerStr = ''
                    for Trailer in LineTails[1:CountTails + 1]:
                        TrailerStr = TrailerStr + str(Trailer) + ' '
#                    print ('trailstr:', TrailerStr)
                    CopyTails.append(TrailerStr.strip(' '))
#                    print ('copytails final:', CopyTails)
                    LineTails = CopyTails
                    CountTails = len(LineTails)
#                print ('count tails:', CountTails)
#                print ('linetails final:', LineTails)
                
# if the line is split then check each tail
                if CountTails > 1:
                    for ix, Tail in enumerate(LineTails):
                        TailStr = str(Tail)
# undo the replace blanks with underscore from above
                        TailStr = TailStr[0:44].replace('_', ' ') + TailStr[44:]

# append a newline to the first tail
                        if ix == 0:
                            TailStr = TailStr + '\n'

#                        print ('tail', ix, ':', TailStr)

                        if PreLine != '':
                            TailStr = PreLine + TailStr
#                            print ('pre in tail@', PreLine, '+', TailStr)
                            
# test the tail and if it is good then write it to the output list
                        moGoodLine = GoodLine.match(TailStr)
                        if moGoodLine != None:
#                            print ('good tail#', ix, TailStr)
                            WriteLines.append(TailStr)
                            PreLine  = ''
                            NextLine = ''
                            
# the tail was not good so make it the next thing to check
                        else:
                            NextLine = TailStr
#                            print ('tail hangover', NextLine)
                        
# if the line is null then get the next line
                if NextLine == '': continue

# if the line is abbreviated the put it in PreLine
                if len(NextLine) < 45:
                    PreLine = NextLine[0:len(NextLine) - 1] + ' '
#                    print ('preline:', PreLine)
                    continue
                    
# else concatenate PreLine with this line to make a good line
                else:                      # the line is a trailer w/o an overhang
# undo the replace blanks with underscore from above
                    NextLine = NextLine[0:44].replace('_', ' ') + NextLine[44:]
                    NextLine = PreLine + NextLine
                    PreLine = ''
                    moGoodLine = GoodLine.match(NextLine)
                    if moGoodLine != None:
#                        print ('good trailer>', NextLine)
                        WriteLines.append(NextLine)
                        continue
         
                print ('unknown:', NextLine)
                   
#            for Liner in WriteLines:
#                print (''.join(Liner))
            print ('lines read:', LinesRead)

    except IOError:
        print ('Error opening file:', FileName)

    FileName = 'C:\\RW\\RW' +StatCCYY + '\\NFP' + StatCCYY[3:4] + Week + '.txt'
    print ('writefile:', FileName)
    with open(FileName,'w') as OutFile:
        for Line in WriteLines:
            OutFile.write(Line)
#            print ('writing:', Line)
        
print ('files found:', FilesOpened)
