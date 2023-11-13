import pandas as pd
import seaborn as sns 
import streamlit as st 
import matplotlib.pyplot as plt 
from streamlit_option_menu import option_menu
from datetime import datetime
import calendar
weather = pd.read_csv("climate-daily.csv", low_memory = False)

def day_mean(day, month, column, rounded = True):
    ''' finds the mean value of a column on a specific day
        ex. average high temperature on March 7

        arguments:
            day: the numerical day to use, int
            month: the numerical month to use, int
            column: the column on the .csv to sort by (ex. 'MEAN_TEMPERATURE'), string
            rounded: an optional argument to round the averages to two decimal points
                set to true by default, boolean
        
        return:
            the numerical mean on that column and day
        '''

    df_oneday = weather.loc[(weather["LOCAL_MONTH"] == month) & (weather["LOCAL_DAY"] == day)]
    mean_value = df_oneday[column].mean()

    if rounded:
        return round(mean_value, 2)

def month_mean(month, column, rounded = True):
    ''' find the value of a column for a daily average of a full month
    ex. average amount of daily snow in December

    arguments:
        month: the numerical month, int
        column: the column on the .csv to sort by (ex. 'SNOW_ON_GROUND), string
        rounded: an optional argument to round the averages to two decimal points
                set to true by default, boolean

    return:
        the daily average of the column value for that month
    '''

    df_onemonth = weather.loc[(weather["LOCAL_MONTH"] == month)]
    mean_value = df_onemonth[column].mean()

    if round:
        return round(mean_value, 2)
    else:
        return mean_value

def month_mean_dict(column, month_num = True):
    ''' creates a dictionary for the means of each month, sorting for a column

    argument:
        column: the column on the .csv to sort by (ex. 'MEAN_TEMPERATURE')
        month_num: an optional argument to have the dictionary keys be month numbers
                set to true by default, boolean

    return:
        a dictionary with each month matched up to the mean value for the column on that month
    '''

    if month_num == True:
        month_means = {month : month_mean(month, column) for month in range(1,13)}
    else:
        month_means = {calendar.month_name[month] : month_mean(month, column) for month in range(1,13)}

    return month_means

@st.cache_data
def convert_df(dataframe):
    ''' converts a dataframe into a csv to be downloaded
    
    arguments:
        dataframe: the dataframe to be converted into csv, dataframe

    return:
        the csv version of the dataframe
    '''
    return dataframe.to_csv().encode('utf-8')
