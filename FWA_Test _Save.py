
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

########################################################################
# FWA from Excel              
#     hist is an 2D array with columns:
#         0   Open:                                                     #
#         1   High:                                                     #
#         2   Low:                                                      #
#         3   Close:                                                    #
#         4   Date:                                                     #
#         5   HL_Zero:                                                  #
#         6   HHLL_Zero:                                                #
#         7   Z_Zero:                                                   #
#         8   Z_Zero_Price:                                             #
#         9   HL_One:                                                   #
#        10   HHLL_One:                                                 #
#        11   Z_One:                                                    #
#        12   Z_One_Price:                                              #
#        13   HL_Two:                                                   #
#        14   HHLL_Two:                                                 #
#        15   Z_Two:                                                    #
#        16   Z_Two_Price:                                              #

#########################################################################


def do_HL_Zero():
    global h, lastDataRow                                       #
    trend = 0                 #  no trend

    for n in range(1,lastDataRow-1):
        h[n,5] = ""       # Blank out existing HL data
        PreviousPrice = h[n-1, 3]
        ThisPrice     = h[n,3]
        NextPrice     = h[n+1,3]

        if (ThisPrice > PreviousPrice):
            trend = 1                         # trend is up
            if (ThisPrice > NextPrice):
                h[n, 5] = "H"                 # this price is a local high (H)
        elif (ThisPrice < PreviousPrice):
            trend = -1                        # trend is down
            if (ThisPrice < NextPrice):
                h[n,5] = "L"                  # this price is a local low (L)
        else:                                 # this price is the same as previous price
            if (ThisPrice > NextPrice) and (trend == 1):
                h[n, 5] = "H"                 # this price is a local high (H)
            if (ThisPrice < NextPrice) and (trend == -1):
                h[n, 5] = "L"                 # this price is a local low (L)



def do_HHLL_Zero():
# Sub sets a blank or one of "HH", "LH", "HL" or "LL"   #
# in each row of Column 5                               #
# Column 3 is Close, Column 4 is "H","L" or blank       #
    global h, lastDataRow

    for n in range(0,lastDataRow-1):
        h[n,6] = ""
        HL = h[n,5]                              # HL is either "H" or "L" or blank
        if (HL != ""):                           # If the entry is a blank, row is blank
            PXHL = h[n,3]                        # Price at Current H/L is in column 3
            for m in range(n-1,0,-1):
                if (h[m,5] == HL):               # Find most recent  H/L
                    PPHL = h[m, 3]               # Previous H/L Price
                    if (HL == "H"):              # Working with an "H"
                        if PXHL >= PPHL:
                            h[n, 6] = "HH"       # Higher H
                        else:
                            h[n,6] = "LH"        # Lower H
                    else:                        # Working on an "L"
                        if PXHL <= PPHL:
                            h[n,6] = "LL"        # Lower L
                        else:
                            h[n,6] = "HL"        # Higher L
                    break                        #  Exit For m = loop
            ###                                  Next m
    ###             Next n



def do_Z_Zero():
# Sub sets a blank or "ZEE UP" or "ZEE DOWN"   #
# in each row of Column 7                               #
    global h, lastDataRow

    for n in range(2, lastDataRow-1):
        Z = h[n,6]                                 # HH, HL, LH or LL in column 5
        h[n,7] = ""                                # Row starts blank
        h[n,8] = ""
        if ((Z == "HH") or (Z == "LL")):           # Possible end of Zee Pattern
            for m in range(n-1, 1, -1):
                Q = h[m, 6]                        # HH, HL, LH or LL in column 5
                if (len(Q)>1 ):
                    Pattern = Q + "-" + Z          # Pattern is 5 character string
                    if (Pattern == "HL-HH"):
                        h[n, 7] = "ZEE UP"
                        h[n, 8] = h[n, 3]          # Add Price if ZEE
                        break                      ###  Exit For - found a Z pattern
                    elif (Pattern == "LH-LL"):
                        h[n, 7] = "ZEE DOWN"
                        h[n, 8] = h[n, 3]          # Add Price if ZEE
                        break                      ###  Exit For - found a Z pattern
                    ###  End If
                    break                          ###  Exit For - found a non-Z pattern
                ### End If
            ### Next m
        ### End If
    ### Next n

#-----------------------------------------------------------------------------------
# Level-1 routines
#-----------------------------------------------------------------------------------

def do_HL_One():
    global h, lastDataRow

# -- Find first non-blank pattern
    for n in range(2,lastDataRow-1):
        NewPattern = h[n,7]                   # blank, ZEE UP, or ZEE Down
        if (len(NewPattern) > 0):             # a ZEE pattern end
            if (NewPattern == "ZEE UP"):      # Is this pattern a ZEE UP
                h[n, 9] = "H"                 # Yes; Set High of Level-One ZEE UP series
            else:
                h[n, 9] = "L"                 # No; Set Low of Level-One ZEE DOWN series
            ###   End If
            OldPattern = NewPattern           # save the previous pattern
            OldPrice = h[n,3]                 # price at end of previous ZEE pattern
            oldn = n                          # save row number of previous ZEE pattern
            break                             # Exit For loop:  first Zee pattern found
        ### End if
    ###  Next n


    for n in range(oldn + 1, lastDataRow):       # move forward from ZEE pattern
        NewPattern = h[n, 7]                  # potential next pattern
        if (len(NewPattern) > 0):             # found next ZEE pattern end
            NewPrice = h[n,3]                 # price at end of next pattern
            if (NewPattern == OldPattern):         # Does NextPattern match previous Pattern?
                if (NewPattern == "ZEE DOWN"):     # Yes; two matching ZEE DOWN patterns in a row
                    if (NewPrice <= OldPrice):     # Is the new price equal or lower than previous
                        h[oldn, 9] = ""            # erase H from previous ZEE DOWN
                        h[n, 9] = "L"              # mark this as Low of ZEE DOWN series
                        OldPrice = NewPrice        # Yes; Save Price at new ZEE DOWN Low
                        oldn = n                   # save row number of previous ZEE DOWN
                    ###  End If
                else:                              # No, but: two matching ZEE UP patterns in a row
                    if (NewPrice >= OldPrice):        # Is the new price equal or higher than previous
                        h[oldn, 9] = ""            # erase H from previous ZEE UP
                        h[n, 9] = "H"              # mark this as High of ZEE UP series
                        OldPrice = NewPrice        # Yes; Save Price at new ZEE UP High
                        oldn = n                   # save row number of previous ZEE UP
                    ###  End If
                ###  End If
            else:                             # The ZEE Pattern is different than previous
                if (NewPattern == "ZEE UP"):       # Is new pattern a ZEE UP
                    h[n, 9] = "H"                  # Yes; Set High of Level-One ZEE UP series
                else:
                    h[n, 9] = "L"                  # No; Set Low of Level-One ZEE DOWN series
                ###   End If
                OldPattern = NewPattern           # Current Pattern
                OldPrice = h[n, 3]                # Save price at end of pattern
                oldn = n                          # save row number of previous ZEE pattern
            ###  End If
        ###  End If
    ###  Next n


def do_HHLL_One():
    global h, lastDataRow

    for m in range(2, lastDataRow):
        h[m, 10] = ""                              # row starts blank
        HL = h[m, 9]                               # HL is either "H" or "L" or blank
        if (len(HL) > 0):                          # If the entry is not blank
            PXHL = h[m, 3]                         # Price at Current H/L is in 3
            for n in range(m - 1,1,-1):            # look back for previous matching HL
                if (h[n, 9] == HL):                # if a match
                    PPHL = h[n, 3]                 # Previous H/L Price
                    if (HL == "H"):                # Working with an "H"
                        if PXHL >= PPHL:
                            h[m, 10] = "HH"        # Higher than previous H
                        else:
                            h[m, 10] = "LH"        # Lower than previous H
                        ###  End If
                    else:                         # Working on an "L"
                        if PXHL <= PPHL:
                            h[m, 10] = "LL"       # Lower than previous L
                        else:
                            h[m, 10] = "HL"       # Higher than previous L
                        ###      End If
                    ###  End If
                    break                         # Done this m, exit n loop
                ###   End If
            ###  Next n
        ###  End If
    ###  Next m

def do_Z_One():
    global h, lastDataRow

    for n in range(2, lastDataRow-1):
        Z = h[n, 10]                          # HH, HL, LH or LL in column 10
        h[n, 11] = ""                         # Row starts blank
        h[n, 12] = ""                         # Price starts blank
        if ((Z == "HH") or (Z == "LL")):
            for m in range(n - 1,1,-1):
                Q = h[m, 10]
                if (len(Q)>1 ):
                    Pattern = Q + "-" + Z    # Pattern is 5 character
                    if (Pattern == "HL-HH"):
                        h[n, 11] = "ZEE UP"
                        h[n, 12] = h[n, 3]
                        break     ###  Exit For m loop
                    elif (Pattern == "LH-LL"):
                        h[n, 11] = "ZEE DOWN"
                        h[n, 12] = h[n, 3]
                        break  ###   Exit For m loop
                    ###   End If
                    break  ###    Exit For
                ###  End If
            ###  Next m
        ###  End If
    ###  Next n


def do_HL_Two():
    global h, lastDataRow

    # -- Find first non-blank pattern
    for n in range(2, lastDataRow-1):
        NewPattern = h[n,11]                   # blank, ZEE UP, or ZEE Down
        if (len(NewPattern) > 0):              # a ZEE pattern end
            if (NewPattern == "ZEE UP"):       # Is this pattern a ZEE UP
                h[n, 13] = "H"                 # Yes; Set High of Level-One ZEE UP series
            else:
                h[n, 13] = "L"                 # No; Set Low of Level-One ZEE DOWN series
            ###   End If
            OldPattern = NewPattern            # save the previous pattern
            OldPrice = h[n, 3]                 # price at end of previous ZEE pattern
            oldn = n                           # save row number of previous ZEE pattern
            break                              # Exit For loop:  first Zee pattern found
        ### End if
    ###  Next n

    for n in range(oldn + 1, lastDataRow):         # move forward from ZEE pattern
        NewPattern = h[n, 11]                      # potential next pattern
        if (len(NewPattern) > 0):                  # found next ZEE pattern end
            NewPrice = h[n,3]                      # price at end of next pattern
            if (NewPattern == OldPattern):         # Does NextPattern match previous Pattern?
                if (NewPattern == "ZEE DOWN"):     # Yes; two matching ZEE DOWN patterns in a row
                    if (NewPrice <= OldPrice):     # Is the new price equal or lower than previous
                        h[oldn, 13] = ""           # erase H from previous ZEE DOWN
                        h[n, 13] = "L"             # mark this as Low of ZEE DOWN series
                        OldPrice = NewPrice        # Yes; Save Price at new ZEE DOWN Low
                        oldn = n                   # save row number of previous ZEE DOWN
                    ###  End If
                else:                              # No, but: two matching ZEE UP patterns in a row
                    if (NewPrice >= OldPrice):     # Is the new price equal or higher than previous
                        h[oldn, 13] = ""           # erase H from previous ZEE UP
                        h[n, 13] = "H"             # mark this as High of ZEE UP series
                        OldPrice = NewPrice        # Yes; Save Price at new ZEE UP High
                        oldn = n                   # save row number of previous ZEE UP
                    ###  End If
                ###  End If
            else:                                  # The ZEE Pattern is different than previous
                if (NewPattern == "ZEE UP"):       # Is new pattern a ZEE UP
                    h[n, 13] = "H"                 # Yes; Set High of Level-One ZEE UP series
                else:
                    h[n, 13] = "L"                 # No; Set Low of Level-One ZEE DOWN series
                ###   End If
                OldPattern = NewPattern            # Current Pattern
                OldPrice = h[n, 3]                 # Save price at end of pattern
                oldn = n                           # save row number of previous ZEE pattern
            ###  End If
        ###  End If
    ###  Next n

def do_HHLL_Two():
    global h, lastDataRow

    for m in range(2, lastDataRow):
        h[m, 14] = ""                              # row starts blank
        HL = h[m, 13]                              # HL is either "H" or "L" or blank
        if (len(HL) > 0):                          # If the entry is not blank
            PXHL = h[m, 3]                         # Price at Current H/L is in 3
            for n in range(m - 1,1,-1):            # look back for previous matching HL
                if (h[n, 13] == HL):               # if a match
                    PPHL = h[n, 3]                 # Previous H/L Price
                    if (HL == "H"):                # Working with an "H"
                        if PXHL >= PPHL:
                            h[m, 14] = "HH"        # Higher than previous H
                        else:
                            h[m, 14] = "LH"        # Lower than previous H
                        ###  End If
                    else:                          # Working on an "L"
                        if PXHL <= PPHL:
                            h[m, 14] = "LL"        # Lower than previous L
                        else:
                            h[m, 14] = "HL"        # Higher than previous L
                        ###      End If
                    ###  End If
                    break                          # Done this m, exit n loop
                ###   End If
            ###  Next n
        ###  End If
    ###  Next m


def do_Z_Two():
    global h, lastDataRow

    for n in range(2, lastDataRow-1):
        Z = h[n, 14]                          # HH, HL, LH or LL in column 10
        h[n, 15] = ""                         # Row starts blank
        h[n, 16] = ""                         # Price starts blank
        if ((Z == "HH") or (Z == "LL")):
            for m in range(n - 1,1,-1):
                Q = h[m, 14]
                if (len(Q)>1 ):
                    Pattern = Q + "-" + Z    # Pattern is 5 character
                    if (Pattern == "HL-HH"):
                        h[n, 15] = "ZEE UP"
                        h[n, 16] = h[n, 3]
                        break     ###  Exit For m loop
                    elif (Pattern == "LH-LL"):
                        h[n, 15] = "ZEE DOWN"
                        h[n, 16] = h[n, 3]
                        break  ###   Exit For m loop
                    ###   End If
                    break  ###    Exit For
                ###  End If
            ###  Next m
        ###  End If
    ###  Next n


tick = yf.Ticker('^DJI')                       # Dow Jones Industrial Average
hist = tick.history(start='2015-10-01', end='2023-08-30')

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)


# îndex=Date:  Open High Low Close Volume Dividends Stock Splits
del hist ['Volume']               # delete Volume data
del hist ['Dividends']            # delete Dividend data
del hist ['Stock Splits']         # delete Splits data
hist['Date'] = hist.index         # create a new column with the datetime index value

hist['HL_Zero'] = ""          # create new columns for constructing FWA data
hist['HHLL_Zero'] = ""
hist['Z_Zero'] = ""
hist['Z_Zero_Price'] = ""

hist['HL_One'] = ""
hist['HHLL_One'] = ""
hist['Z_One'] = ""
hist['Z_One_Price'] = ""

hist['HL_Two'] = ""
hist['HHLL_Two'] = ""
hist['Z_Two'] = ""
hist['Z_Two_Price'] = ""

# Open High Low Close Date   HL_Zero HHLL_Zero Z_Zero Z_Zero_Price
#                            HL_One HHLL_One Z_One Z_One_Price
#                            HL_Two HHLL_Two Z_Two Z_Two_Price

h = hist.to_numpy()          # Create numpy Matrix from pd DataFrame

lastDataRow = len(h)         # number of rows of data
for i in range(0, lastDataRow):
    h[i, 0]=round(h[i, 0])   # Open  rounded
    h[i, 1]=round(h[i, 1])   # High  rounded
    h[i, 2]=round(h[i, 2])   # Low   rounded
    h[i, 3]=round(h[i, 3])   # Close rounded
    h[i, 4]=h[i, 4].strftime("%Y")+h[i, 4].strftime("%m")+h[i, 4].strftime("%d")   # YYYYMMDD


do_HL_Zero()                # fill column 5, HL_Zero, with H or L at end of up or down moves
do_HHLL_Zero()              # fill column 6, HHLL_Zero, with HH, LH, HL or LL as appropriate
do_Z_Zero()                 # fill column 7, Z_Zero, with ZEE UP or ZEE DOWN for end of zig-zags
                            # fill column 8, Z_Zero_Price, with close price at zig-zag completion
do_HL_One()                 # fill column 9, HL_One, with H or L at end of Level-Zero ZEE moves
do_HHLL_One()               # fill column 10, HHLL_One, with HH, LH, HL, or LL as appropriate
do_Z_One()                  # fill column 11, Z_One, with ZEE UP or ZEE DOWN for end of zig-zags
                            # fill column 12, Z_One_Price, with close price at zig-zag completion
do_HL_Two()                 # fill column 13, HL_Two, with H or L at end of Level-Zero ZEE moves
do_HHLL_Two()               # fill column 14, HHLL_Two, with HH, LH, HL, or LL as appropriate
do_Z_Two()                  # fill column 15, Z_Two, with ZEE UP or ZEE DOWN for end of zig-zags
                            # fill column 16, Z_Two_Price, with close price at zig-zag completion


print('Date   Close  HL_Zero   HHLL_Zero   Z_Zero   HL_One   HHLL_One  Z_One  HL_Two  HHLL_Two')
for i in range(0, len(h)):
    print(h[i,4], h[i,3], h[i,5], h[i,6], h[i,9], h[i,10], h[i,12], h[i,13], h[i,14], h[i,16] )



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


fig3.add_trace(go.Scatter(x=hist2[4],y=hist2[12],mode='lines+markers',name='FWA Level-1',
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
fig3.add_trace(go.Scatter(x=hist2[4],y=hist2[16],mode='lines+markers',name='FWA Level-2',
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

#fig3.update_xaxes(
#    rangeslider_visible=True,
#    rangeselector=dict(
#        buttons=list([
#            dict(count=1, label="1m", step="month", stepmode="backward"),
#            dict(count=6, label="6m", step="month", stepmode="backward"),
#            dict(count=1, label="YTD", step="year", stepmode="todate"),
#            dict(count=1, label="1y", step="year", stepmode="backward"),
#            dict(step="all")
#        ])
#    )
#)




fig3.show()

