def _make_df(bars):
    df = util.df(bars)
    df.set_index('date',inplace=True)
    df.index = df.index.tz_localize(None)
    return df 
import pandas as pd
import datetime
import pandas_market_calendars as mcal
import os
from ib_insync import *
# Create a calendar
nyse = mcal.get_calendar('NYSE')
def get_historical_1m_data_fast(ib,symbol,start_date,end_date,what_to_show='TRADES',use_rth=False):    
    messup_count=0
    df_list=[]
    start_date = datetime.datetime.strptime(start_date,'%Y%m%d').date() # .date() is important to get correct date!
    start_date.strftime('%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date,'%Y%m%d').date()
    end_date.strftime('%Y-%m-%d')
    dates = nyse.schedule(start_date=start_date, end_date=end_date)
    dates = [t.strftime('%Y%m%d') for t in mcal.date_range(dates, frequency='1D').tolist()]
    dates = [datetime.datetime.strptime(t,'%Y%m%d').date() for t in dates]
    contract = Stock(symbol=symbol,exchange='SMART',currency='USD')
    ib.qualifyContracts(contract)
        
    last_end_date = dates[-1]+datetime.timedelta(days=1)
    for end_date in dates[::-1]:
        if end_date>=last_end_date: continue
        if messup_count>=2: break
        try:
            print("Retrieving data for ",symbol," for ",end_date)
            bars=ib.reqHistoricalData(contract,endDateTime=end_date,
                                                    barSizeSetting='1 min',whatToShow=what_to_show,useRTH=use_rth,
                                 durationStr='1 W')
            df=_make_df(bars)
            last_end_date=bars[0].date.date()
            df_list.append(df)
        except Exception as e:
            messup_count+=1
            print(e)
            print("No data for ",end_date)
        else:
            messup_count=0
    return pd.concat(df_list).sort_index()