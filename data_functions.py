import pandas as pd
import seaborn as sns 
import streamlit as st 
import matplotlib.pyplot as plt 
from streamlit_option_menu import option_menu
from datetime import datetime
import calendar
weather = pd.read_csv("climate-daily.csv", low_memory = False)

def day_mean(day, month, column):
    ''' finds the mean value of a column on a specific day
        ex. average high temperature on March 7

        arguments:
            day: the numerical day to use, int
            month: the numerical month to use, int
            column: the column on the .csv to sort by (ex. 'MEAN_TEMPERATURE'), string
        
        return:
            the numerical mean on that column and day
        '''

    df_oneday = weather.loc[(weather["LOCAL_MONTH"] == month) & (weather["LOCAL_DAY"] == day)]
    mean_value = df_oneday[column].mean()

    return mean_value