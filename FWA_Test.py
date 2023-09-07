
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
#         5   HHLL_Zero:                                                #
#         6   HHLL_One:                                                 #
#         7   HHLL_Two:                                                 #
#         8   HHLL_Three:                                               #
#         9   Close_One:                                                #
#        10   Close_Two:                                                #
#        11   Close_Three:                                              #
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


def WaveLogic():
    global currentRec, currentDate, currentPx, previousDate, previousPx  
    global h, maxPx, maxRecminPx, minRec, currentDirection               

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
    if currentDirection != previousDirection:     # Change of Direction  
        if currentDirection[0] == "Up":                                  
            CheckPreviousMark(0, currentRec, "H", currentPx)             
        else:                                                            
            CheckPreviousMark(0, currentRec, "L", currentPx)             
        #  done:  MarkWave(currentRec, 0, Mark)                          
    else:                                         # Same Direction       
        Mark = h[currentRec-1,5]                  # previous L-0 mark    
        h[currentRec-1,5] = "."                   # erase previous       
        CheckPreviousMark(0, currentRec, Mark[-1], currentpx)            
        # Done:  MarkWave(currentRec, 0, Mark)    # move Mark forward    



##  Sub CheckPreviousMark (CheckLevel, CheckRec, WSave$, PSave!) 
def CheckPreviousMark(level, rec, hl, px):                                        
    global currentRec   
#    '----------------------------------------------------------------------------------------------------
#    '  Look back, starting just before rec, for first previous mark at level level of type               
#    '  hl ("H" or "L").  When found, compare price at that rec vs px and  set h[rec, level+5] as a       
#    '  higher or lower version of hl.  e.g. If hl = "H", h[] will be either "HH" or "LH".                
#    '  If no previous mark is found, set h[] to "HH" or "LL".                                            
#    '----------------------------------------------------------------------------------------------------
   For r in range(rec - 1,1, -1):                                        ' Look back                     
        mark = h[r,level+5]                                              ' mark at rec=r, level=l        
        m = mark[-1]                                                     ' "H" or "L"                    
        if m == hl:                                                      ' matched type                  
            if hl== "H":                                                 ' checking a High               
                if h[r,3] < px:                                          ' check price vs px             
                    h[rec,level+5] = " HH"                               ' Current Price is Higher High  
                else:                                                                                    
                    h[rec,level+5] = " LH"                               ' Current Price is a Lower High 
                #  End If                                                                                
            else:                                                        ' checking a Low                
                if h[r,3] > px:                                                                          
                    h[rec,level+5] = " LL"                              ' Current Price is Lower Low     
                else:                                                                                    
                    h[rec,level+5] = " HL"                               ' Current Price is a Higher Low 
                #  End If                                                                                
            #  End If                                                                                    
            return                                                       ' Finished checking             
        #  End If                                                                                           
    #  Next RR                                                              '  Not done, keep looking       
 # End Sub







# ---------------------------------------------
# Sub MarkWave (REC, DGREE, W$)                                                                         
# ---------------------------------------------
def MarkWave(rec, level, hl):
    global h   
    Shared WAVE$(), MaxLevel, MaxDgre%                                                                
    Shared MSSG$, ANSWER$, DEBUG$                                                                     
                                                                                                      
    h[rec,level+5] = hl                        # put H/L mark passed at (rec, level)                  
    if hl == " . ":                            # if erasing                                           
        for l in range(l+1,3):                                                                        
            if h[rec,l+5] != "   ":                                                                   
                h[rec, l+5] = " . "            # erase all levels previously marked                   
            ## End If                                                                                 
        ## Next l                                                                                     
    ##  End If                                                                                        



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


