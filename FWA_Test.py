
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

########################################################################
# FWA from QB64              
#     hist is an 2D array with columns:
#         0   Open:                                                     #
#         1   High:                                                     #
#         2   Low:                                                      #
#         3   Close:                                                    #
#         4   Date:                                                     #
#         5   HHLL_Zero:   2 char.s "  ", "LL", "HL", "LH", "HH", ". "  #
#         6   HHLL_One:    2 char.s "  ", "LL", "HL", "LH", "HH", ". "  #
#         7   HHLL_Two:    2 char.s "  ", "LL", "HL", "LH", "HH", ". "  #
#         8   HHLL_Three:  2 char.s "  ", "LL", "HL", "LH", "HH", ". "  #
#         9   Close_One:           Close, if level-1 mark               #
#        10   Close_Two:           Close, if level-2 mark               #
#        11   Close_Three:         Close, if level-3 mark               #
#        12   Scratch_1:                                                #
#        13   Scratch_2:                                                #
#        14   Scratch_3:                                                #
#########################################################################


def Initialize():
    global currentRec, currentDate, currentPx, previousDate, previousPx  
    global h, maxPx, maxRecminPx, minRec, currentDirection               

    currentRec = 1                              
    currentDate = h[1,4]                        
    currentPx = h[1,3]                          
    previousDate = h[0,4]                       
    previousPx = h[0,3]                         
    if currentPx >= previousPx :                
        maxPx = currentPx                       
        maxRec = 1                              
        minPx = previousPx                      
        minRec = 0                              
        currentDirection[0] = "Up"              
    else:                                       
        maxPx = previousPx                      
        maxRec = 0                              
        minPx = currentPx                       
        minRec = 1                              
        currentDirection[0] = "Down"            
#---- End Initialize ---------------------------


def WaveLogic():                       # currentRec == n in loop         
    global currentRec, currentDate, currentPx, previousDate, previousPx  
    global h, maxPx, maxRecminPx, minRec, currentDirection, mark         
    global pattern, zagrec,                                              
    previousPrice = currentPrice                                         
    previousDate = currentDate                                           
    currentPrice = h[currentRec,3]                                       
    currentDate = h[currentRec, 4]                                       

    previousDirection[0] = currentDirection[0]                           
    if currentPx > previousPx:                                           
        currentDirection[0] = "Up"                                       
    elif currentPx < previousPx:                                         
        currentDirection[0] = "Down"                                     
    else:                                                                
        pass                                                             
        #  if price is the same, currentDirection is the same            

    #' -------------------------------------------
    #' Check for Level 0 turn and mark            
    #' -------------------------------------------
    if currentDirection[0] != previousDirection[0]: # Change of Direction  
        if currentDirection[0] == "Up":                                    
            CheckPreviousMark(0, currentRec, "H", currentPx)               
        else:                                                              
            CheckPreviousMark(0, currentRec, "L", currentPx)               
        # MarkWave(currentRec, 0, mark)             # move Mark forward    
        # CheckPreviousMark also marks current record                      
    else:                                           # Same Direction       
        mark = h[currentRec-1,5]                    # previous L-0 mark    
        h[currentRec-1,5] = ". "                    # erase previous       
        CheckPreviousMark(0, currentRec, mark[-1], currentpx)              
        # MarkWave(currentRec, 0, mark)             # move Mark forward    
        # CheckPreviousMark also marks current record                      

#   ' ------------------------------------------------------------------ 
#   ' At each degree check for a zig-zag penetration that promotes a     
#   ' recent pullup or pullback to the next level.  For instance a LH    
#   ' and then a LL at level zero is a ZEE DOWN that would raise the     
#   ' most recent level zero zig-zag HH to level 1.                      
#   ' Note Shadowing logic:  The most recent zig-zag HH may not be the   
#   ' highest zig-zag HH since the previous ZEE DOWN, a requirement.     
#   ' ------------------------------------------------------------------ 

    checkhigher = True                  ' check higher levels if needed  
    CheckPatternAndPromote(0)                                            
    if checkhigher:                                                      
        CheckPatternAndPromote(1)                                        
        if checkhigher:                                                  
            CheckPatternAndPromote(2)                                    
            if checkhigher:                                              
                CheckPatternAndPromote(3)                                


def CheckPatternAndPromote(level):                                                            
    global checkhigher, pattern, zagrec                                                       
    GetPattern(level)                                       # Level 1 pattern                 
    if pattern[level] == "HL-HH":                           # Is pattern a zig-zag up?        
        Promote(zagrec, "L", level)   # Promote lowest recent LL-1 to HL-2 or LL-2            
    elif pattern[1] == "LH-LL":                         # Is pattern a zig-zag dn?            
        Promote(zagrec, "H", level)   # Promote highest recent HH-1 to HH-2 or LH-2           
    else:                                                                                     
        checkhigher = False       # nothing to check at higher levels                         
    #  End If                                                                                 
# --- End of CheckPatternAndPromote()-------------------------------------                    


def CheckPreviousMark(level, rec, hl, px):                                                               
    global currentRec, mark, h                                                                           
#    '---------------------------------------------------------------------------------------------------
#    '  Look back, starting just before rec, for first previous mark at level level of type              
#    '  hl ("H" or "L").  When found, compare price at that rec vs px and  set h[rec, level+5] as a      
#    '  higher or lower version of hl.  e.g. If hl = "H", h[] will be either "HH" or "LH".               
#    '  If no previous mark is found, set h[] to "HH" or "LL".                                           
#    '---------------------------------------------------------------------------------------------------
    for r in range(rec - 1,1, -1):                                       # Look back                     
        mark = h[r,level+5]                                              # mark at rec=r, level=l        
        m = mark[-1]                                                     # "H" or "L"                    
        if m == hl:                                                      # matched type                  
            if hl== "H":                                                 # checking a High               
                if h[r,3] < px:                                          # check price vs px             
                    h[rec,level+5] = "HH"                                # Current Price is Higher High  
                else:                                                                                    
                    h[rec,level+5] = "LH"                                # Current Price is a Lower High 
                #  End If                                                                                
            else:                                                        # checking a Low                
                if h[r,3] > px:                                                                          
                    h[rec,level+5] = "LL"                                # Current Price is Lower Low    
                else:                                                                                    
                    h[rec,level+5] = "HL"                                # Current Price is a Higher Low 
                #  End If                                                                                
            #  End If                                                                                    
            #  mark = h[rec,level+5]                                     # pass mark back                
            return                                                       # Finished checking             
        #  End If                                                                                        
    #  Next r                                                            #  Not done, keep looking       
    if hl == "H':                                                                                        
        h[rec,level+5] = " HH"                                           # set H as HH                   
    else:                                                                #                               
        h[rec,level+5] = " LL"                                           # set L as LL                   
 # End Sub


def MarkWave(rec, level, hl):
    global h   
                                                                                                      
    h[rec,level+5] = hl                        # put H/L mark passed at (rec, level)                  
    if hl == ".":                              # if erasing                                           
        h[rec,level+5] = ". "                  # Two characters                                       
        for l in range(l+1,3):                                                                        
            if h[rec,l+5] != "   ":                                                                   
                h[rec, l+5] = ". "             # erase all levels previously marked                   
            ## End If                                                                                 
        ## Next l                                                                                     
    ##  End If                                                                                        

def GetPattern(checklevel):                                                                          
    global pattern, currentRec, zagrec, zigrec, h                                                    

#   '   ---------------------------------------------------------------------------------------------
#   '   Starting with CurrentRec, set Pattern$(CheckLevel) as "HL-HH", "LH-LL", etc.                 
#   '   We are setting the pattern to determine if a zig-zag has been completed at level CheckLevel. 
#   '   ---------------------------------------------------------------------------------------------

    pattern[checklevel] = "     "                 # start blank                                         
    For r in range(currentRec,1,-1)               # look back                                           
        wsave = h[r, 5+checklevel]                # The record r wavemark at checklevel                 
        if len(wsave) > 1:                        # Found recent mark at CheckLevel                     
            zagrec = r                            # pattern ends at zagrec                              
            for rr in range(r-1,1,-1)             # Look back                                           
                wwsave = h[rr, 5+checklevel]                                                            
                if len(wwsave) > 1:               # Most recent prior CheckLevel Mark                   
                    pattern[checklevel] = wwsave+"-"+wsave                                              
                    zigrec = rr                   # pattern starts at zigrec                            
                    return  #  Exit Sub           # found pattern, done here                            
               #  End If                                                                                
            #  Next RR                                                                                  
            return #  Exit Sub                    # No mark prior to most recent ==> No pattern         
        #  End If                                                                                       
    # Next r '  Not done, keep looking                                                                  
#  End Sub                                                                                              


def Promote(endrec, hl, level)                                                                          
    #---------------------------------------------------------------------------------------------------
    # Zig Zag found at level [level] in direction hl (H or L) ending at record[endrec]                  
    # If HighLow$ is "L" :                                                                              
    # This routine will Promote lowest LL-[Level] since most recent previous                            
    # [Level+1] High to HL or LL at level [Level+1]                                                     
    #---------------------------------------------------------------------------------------------------
    # The look-back period ends at EndRec.  The look-back period begins at the most recent              
    # previous [HighLowopposite] at level [Level + 1}                                                   

    if hl == "H":                                                                                       
       w="L"             ' promoting a high; looking for beginning at a Level+1 Low                     
    else                                                                                                
       w="H"             ' promoting a low; looking for the beginning at a Level+1 high                 
    #  End If                                                                                           
    High = 0                                                                                            
    Low  = 9999999                                                                                      
    RHigh = 0                                                                                           
    RLow = 0                                                                                            
    RangeStart=1                                                                                        
    For r in range(endrec-1,1,-1):                                                                      
        m = h[r,level+5]                                                                                
        if m[-1] == w:                                                                                  
           RangeStart=r+1                                                                               
           break                                              #   Found previous HighLow opposite       
        # End If                                                                                        
        if m[-1] != " ":                                      #   Found HighLow                         
           if h[r,3] < Low:                                                                             
               Low = h[r,3]                                                                             
               RLow = r                                       # Track Lowest                            
           if h[r,3] > High:                                                                            
               High = h[r,3]                                                                            
               RHigh = r                                      # Track Highest                           
        # End If                                                                                        
    # Next RR                                                 # Keep looking until opposite or RR=1     
                                                                                                        
    if (hl=="H" and RHigh==0) or (hl=="L" and RLow=0):                                                  
       #  There is no level [Level] HighLow$ to promote above EndRec                                    
       return # Exit Sub                                                                                
    # END IF                                                                                            
                                                                                                        
    if hl == "H":                                             ' promoting a high                        
       CheckMark(RHigh, level+1)                                                                        
       MarkWave(RHigh, level+1, m)                            '   Promote RH to HH or LH at Level+1     
    elif hl == "L":                                           ' promoting a low                         
       CheckMark(RLow, level+1)                                                                         
       MarkWave(RLow, level+1, m)                             '   Promote RL to LL or HL at Level+1     
    # End If                                                                                              
                                                                                                        
#  ==>  There may be another, previously marked Low or High at Level+1 in the search range that should  
#  ==>  be revoked by the one just found.  Search again from RH-1/RL-1 to RangeStart and revoke.        
#  ==>    PROOF:  Level 1 HL at 8/19/2020 should be revoked by Level 1 LL on 9/8/2020                   
                                                                                                        
   if hl="H":                                                                                           
       RangeEnd=RHigh-1                                                                                 
   else:                                                                                                
       RangeEnd=RLow-1                                                                                  
   for r in range(RangeStart, RangeEnd):                                                                
       if h[r,level+6] != "  ":                                                                         
          h[r,level+6) = ". "                                                                           
          #  if If MaxLevel < Level+1 Then MaxLevel = Level+1  '                                        
       # End If                                                                                         
   # Next RR                                                                                            
                                                                                                        
# ==>  It may also be that the low or high that was revoked (just above) has exposed a previous         
# ==>  Level+1 mark at RangeStart (opposite HighLow$) that was not revoked when it should have been     
# ==>  due to being protected (shadowed) by the (HighLow$) mark just revoked.  In such a case, there    
# ==>  will be a maximum/minimum within the Range that is more extreme than the price at RangeStart.    
# ==>  We can check.  For instance:  If HighLow$ is "L", the mark (Level+1) at RangeStart will be an    
# ==>  "H".  We have saved (but not used) PHigh! and RH in this example.  If PHigh! at RH is greater    
# ==>  than PCLOSE$ at RangeStart AND RH comes before RL, then the level+1 mark at RangeStart should    
# ==>  be revoked and the level+1 mark at RH should be made.                                            
# ==>  CHECK:  HH at level 1 on 8/12/2020 should be moved to 9/2/2020                                   
                                                                                                        
 if RangeStart > 1:   ======>>>> HERE                                                                                  
   Get #2, RangeStart-1                                                                                 
   If HighLow$ = "L" then                                                                               
      If PHigh! >= Val(PCLOSE$) and RH < RL then                                                        
         Call MarkWave(RangeStart-1, Level+1, " . ")         ' Unmark RangeStart                        
         Call CheckMark(RH, Level+1)                       ' Check RH for HH vs LH                      
         Call MarkWave(RH, Level+1, WMark$)                ' Mark Level+1 at RH                         
         ' Recheck promotion                                                                            
         Call CheckMark(RL, Level+1)                                                                    
         Call MarkWave(RL, Level+1, WMark$)                ' Promote RL to LL or HL at Level+1          
      End If                                                                                            
   Else                                                    ' HighLow$ = "H"                             
      If PLow! <= Val(PCLOSE$) and RL < RH then                                                         
         Call MarkWave(RangeStart-1, Level+1, " . ")         ' Unmark RangeStart                        
         Call CheckMark(RL, Level+1)                       ' Check RL for HL vs LL                      
         Call MarkWave(RL, Level+1, WMark$)                ' Mark Level+1 at RH                         
         ' Recheck promotion                                                                            
         Call CheckMark(RH, Level+1)                                                                    
         Call MarkWave(RH, Level+1, WMark$)                ' Promote RH to HH or LH at Level+1          
      End If                                                                                            
   End If                                                                                               
 End If                                                                                                 
End Sub                                                                                                 


Sub CheckMark (CheckRec, CheckDgree)                                     
    Shared CURRENTREC, CURRENTPX!, CURRENTDT$                            
    Shared WAVE$(), PCLOSE$, WMark$                                      
    Shared MSSG$, ANSWER$                                                
    '   -----------------------------------------------------------------
    '   WaveLogic has detected a ZEE UP or ZEE DOWN at the current record at degree CheckDgree-1.
    '   The previous HH (on a zee down) or LL (on a zee up) will be promoted to level DG if it has
    '   not already been promoted.  The purpose of this routine is to determine if the record to be
    '   promoted should be a HH or a LH (if it is a high) or a HL or LL (if it is a low).  There is
    '   a loop which looks back for the previous (appropriate) High or Low at CheckDgree.

    Get #2, CheckRec                                                                              
    WSave$ = Right$(WAVE$(CheckDgree - 1), 1) ' The record to be checked is either an "H" or "L". 
    PSave! = Val(PCLOSE$)                     ' Price to check                                    
    For RR = (CheckRec - 1) To 1 Step -1      ' Look back                                         
        Get #2, RR                            '                                                   
        If Right$(WAVE$(CheckDgree), 1) = WSave$ Then     ' Most recent CheckDgree H or L         
            If WSave$ = "H" Then                          ' checking a High                       
                If Val(PCLOSE$) < PSave! Then                                                     
                    WMark$ = " HH"                        ' CheckRec is Higher High               
                Else                                                                              
                    WMark$ = " LH"                        ' CheckRec is a Lower High              
                End If                                                                            
            Else                                          ' checking a Low                        
                If Val(PCLOSE$) > PSave! Then                                                     
                    WMark$ = " LL"                        ' CheckRec is Lower Low                 
                Else                                                                              
                    WMark$ = " HL"                        ' CheckRec is a Higher Low              
                End If                                                                            
            End If                                                                                
            Exit Sub                          ' Finished checking against previous same-level     
        End If                                                                                    
    Next RR                                   '  Not done, keep looking                           
    '  If here then:  No previous mark at this degree                                             
    If WSave$ = "H" Then WMark$ = " HH" Else WMark$ = " LL"     ' Default to HH or LL             
End Sub                                                                                           









tick = yf.Ticker('^DJI')                       # Dow Jones Industrial Average
hist = tick.history(start='2015-10-01', end='2023-08-30')

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)


# îndex=Date:  Open High Low Close Volume Dividends Stock Splits
del hist ['Volume']               # delete Volume data
del hist ['Dividends']            # delete Dividend data
del hist ['Stock Splits']         # delete Splits data
hist['Date'] = hist.index         # create a new column with the datetime index value

hist['HHLL_Zero'] = ""          # create new columns for constructing FWA data
hist['HHLL_One'] = ""                                                         
hist['HHLL_Two'] = ""                                                         
hist['HHLL_Three'] = ""                                                       

hist['Close_One'] = ""                                                        
hist['Close_Two'] = ""                                                        
hist['Close_Three'] = ""                                                      

hist['Scratch_One'] = ""                                                      
hist['Scratch_Two'] = ""                                                      
hist['Scratch_Three'] = ""                                                    

h = hist.to_numpy()          # Create numpy Matrix from pd DataFrame          

lastDataRow = len(h)         # number of rows of data                         
for i in range(0, lastDataRow):                                               
    h[i, 0]=round(h[i, 0])   # Open  rounded                                  
    h[i, 1]=round(h[i, 1])   # High  rounded                                  
    h[i, 2]=round(h[i, 2])   # Low   rounded                                  
    h[i, 3]=round(h[i, 3])   # Close rounded                                  
    h[i, 4]=h[i, 4].strftime("%Y")+h[i, 4].strftime("%m")+h[i, 4].strftime("%d")   # YYYYMMDD

Initialize()                                                                                 
for n in range(2, lastDataRow):                                                              
    currentRec = n                                                                           
    WaveLogic()                                                                              
# ------- End of main loop ---------------------------                                       




print('Date   Close  HHLL_Zero   HHLL_One   HHLL_Two  HHLL_Three   Close_One  Close_Two  Close_Three')
for i in range(0, len(h)):
    print(h[i,4], h[i,3], h[i,5], h[i,6], h[i,7], h[i,8], h[i,9], h[i,10], h[i,11] )                  



hist2 = pd.DataFrame(h)                                 # Create hist2 dataframe from h[] to make chart

hist2[4]= pd.to_datetime(hist2[4])            # convert date column to datetime

#print(hist2)

hist2['diff'] = hist2[3] - hist2[0]                      # Close - Open determines candlestick color
hist2.loc[hist2['diff']>=0, 'color'] = 'green'
hist2.loc[hist2['diff']<0, 'color'] = 'red'



fig3 = make_subplots()                                  #specs=[[{"secondary_y": True}]])

## Create Candlestick chart
fig3.add_trace(go.Candlestick(x=hist2[4],
                              open=hist2[0],
                              high=hist2[1],
                              low=hist2[2],
                              close=hist2[3],
                              name='Price'))

# Add 100-day moving average
#fig3.add_trace(go.Scatter(x=hist2[4],y=hist2[3].rolling(window=100).mean(),marker_color='blue',name='100 Day MA'))


fig3.add_trace(go.Scatter(x=hist2[4],y=hist2[9],mode='lines+markers',name='FWA Level-1',
                          marker=dict(
                              color='yellow',
                              size=7,
                              line=dict(
                                  color='greenyellow',
                                  width=2
                              )
                          ),
                          ))




# Add Level-2 FWA line chart
fig3.add_trace(go.Scatter(x=hist2[4],y=hist2[10],mode='lines+markers',name='FWA Level-2',
                          marker=dict(
                              color='LightSkyBlue',
                              size=10,
                              line=dict(
                                  color='MediumPurple',
                                  width=2
                              )
                          ),
                          ))



#fig3.add_trace(go.Bar(x=hist2[4], y=hist2['Volume'], name='Volume', marker={'color':hist['color']}),secondary_y=True)
#fig3.update_yaxes(range=[0,700000000],secondary_y=True)
#fig3.update_yaxes(visible=False, secondary_y=True)

#fig3.update_layout(xaxis_rangeslider_visible=False)  #hide range slider
fig3.update_layout(title={'text':'DJI', 'x':0.5})
fig3.update_layout(xaxis_range=['2019-01-01','2023-08-29'])



##  Hide weekends, non-work hours, Christmas and New Years
fig3.update_xaxes(rangebreaks = [
                       dict(bounds=['sat','mon']),
                       #dict(bounds=[16, 9.5], pattern='hour'),
                       dict(values=["2021-12-25","2022-01-01"])
                                ])


fig3.show()


