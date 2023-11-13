import pandas as pd
import seaborn as sns 
import streamlit as st 
import matplotlib.pyplot as plt 
from streamlit_option_menu import option_menu
from datetime import datetime
import math
import calendar
import io

from data_functions import day_mean, convert_df, month_mean, month_mean_dict
sns.set(color_codes = True)

# using pandas to open the csv file
weather = pd.read_csv("climate-daily.csv", low_memory = False)

# next steps:
# add short analysis bits for each graph
# come up with new graphs
# do a future forecast (likely just info on a specific date in the future)

# page config
st.set_page_config(page_title = "Historical Weather Network", layout = "wide")

# options menu
with st.sidebar:
    selected = option_menu(
        menu_title = "Navigation",
        options = ["Home", "Daily Weather", "Interesting Graphs", "Extra", "Future Forecast"]
    )

# set up the available days and months that can be selected
months = list(calendar.month_name[1:])
days = [day for day in range(1,32)]

# code for each navigation option
if selected == "Home":
    # home page containing basic information about the csv file
    st.header("climate-daily.csv File Information:")
    # converting the weather dataframe into a downloadable csv and creating a download button
    downloadable_csv = convert_df(weather)
    st.download_button(label = "Download climate-daily.csv", data = downloadable_csv)
    # creating two columns to have overview and null values appear side by side on the website
    info_columns = st.columns(2)
    info_columns[0].subheader("Dataframe Overview:")
    info_columns[1].subheader("Sum of Null Columns:")
    with info_columns[0]:
        # creating an in-memory text buffer as df.info() is printed to sys.stdout and is
        # harder to use that way
        buffer = io.StringIO()
        weather.info(buf=buffer)
        weather_overview = buffer.getvalue()
        # printing the overview of the weather dataframe given from weather.info()
        st.text(weather_overview)
    with info_columns[1]:
        # printing the sum of null values for each column in the weather dataframe
        st.text(weather.isnull().sum())

elif selected == "Daily Weather":
    st.header("Today's Historical Weather Report")
    current_date = datetime.today()
    # display the current date and some basic info for that date
    st.subheader(f"Today is {calendar.month_name[current_date.month]} {current_date.day}, {current_date.year}")
    st.write(f"The average temperature for today is {round(day_mean(current_date.day, current_date.month, 'MEAN_TEMPERATURE'),1)} °C")

    st.write()

    # specific date information gathering
    st.subheader("Enter a specific date and info to sort by")
    with st.form("day_entry"):
        # setting up the three column selection options for specific date information gathering
        info_type_day, day_select, month_select_day = st.columns(3)
        month_select_day.selectbox("Select Month:", months, index = current_date.month - 1, key = "days_month")
        day_select.selectbox("Select Day:", days, index = current_date.day - 1, key = "day")
        info_type_day.selectbox("Select Info:", ["MEAN_TEMPERATURE", "MAX_TEMPERATURE",
        "MIN_TEMPERATURE", "TOTAL_PRECIPITATION", "SNOW_ON_GROUND"], key = "days_header")

        # button to submit choices and see results
        day_submit = st.form_submit_button("Find Info:")
        if day_submit: 
            # avg outputting
            used_day = st.session_state["day"]
            used_month = months.index(st.session_state["days_month"]) + 1
            used_days_header = str(st.session_state["days_header"])
            # accounting for invalid dates (ex. feb 30)
            if math.isnan(day_mean(used_day, used_month, used_days_header)):
                st.write("This is an invalid date")
            else:
                st.write(f"{day_mean(used_day, used_month, used_days_header)}")
    
    # month information gathering
    st.subheader("Enter the specifications for the month sort")
    with st.form("month_entry"):
        # setting up the three column selection options for month information gathering
        info_type_month, month_select_month, output_type = st.columns(3)
        # creating a copy of months so I can include an "All Months" options
        aug_months = months.copy()
        aug_months.insert(0,"All Months")
        # select boxes for month entry
        month_select_month.selectbox("Select Month:", aug_months, index = current_date.month,
        key = "months_month")
        info_type_month.selectbox("Select Info:", ["MEAN_TEMPERATURE", "MAX_TEMPERATURE",
        "MIN_TEMPERATURE", "TOTAL_PRECIPITATION", "SNOW_ON_GROUND"], key = "months_info")
        output_type.selectbox("Output Type (Only for 'All Months'):", ["None", "Dict", "Max", "Min"], key = "output_type")

        # submit box for month entry
        month_submit = st.form_submit_button("Find Info:")
        if month_submit:
            if not st.session_state["output_type"] == "None" and st.session_state["months_month"] == "All Months":
                if st.session_state["output_type"] == "Dict":
                    for key, value in month_mean_dict(st.session_state["months_info"], month_num = False).items():
                        st.write(f"{key} : {value}")

                elif st.session_state["output_type"] == "Max":
                    max_value = -999
                    max_key = ""
                    for key, value in month_mean_dict(st.session_state["months_info"], month_num = False).items():
                        if value > max_value:
                            max_value = value
                            max_key = key
                    st.write(f"{max_key} : {max_value}")

                elif st.session_state["output_type"] == "Min":
                    max_value = 999
                    max_key = ""
                    for key, value in month_mean_dict(st.session_state["months_info"], month_num = False).items():
                        if value < max_value:
                            max_value = value
                            max_key = key
                    st.write(f"{max_key} : {max_value}")
            elif st.session_state["output_type"] == "None" and not st.session_state["months_month"] == "All Months":
                used_month_months = months.index(st.session_state["months_month"]) + 1
                used_months_header = st.session_state["months_info"]
                st.write(f"{month_mean(used_month_months, used_months_header)}")
            else:
                st.write("Invalid input. Please try again.")





elif selected == "Interesting Graphs":
    # graph title
    st.subheader("Average Monthly Max Temperature")

    # plotting graph
    monthly_avg_temp = weather.groupby(["LOCAL_YEAR", "LOCAL_MONTH"])["MAX_TEMPERATURE"].mean().reset_index()

    avg_max_temp_month, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=monthly_avg_temp, x='LOCAL_MONTH', y='MAX_TEMPERATURE', hue="LOCAL_YEAR", palette='coolwarm', ax=ax)
    ax.set_title('Average Monthly Max Temperature')
    ax.set_xlabel('Month')
    ax.set_ylabel('Average Temperature (°C)')

    st.pyplot(avg_max_temp_month)