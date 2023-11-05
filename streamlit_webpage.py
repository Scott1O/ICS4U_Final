import pandas as pd
import seaborn as sns 
import streamlit as st 
import matplotlib.pyplot as plt 
from streamlit_option_menu import option_menu
from datetime import datetime
import math
import calendar

from data_functions import day_mean
sns.set(color_codes = True)

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
        options = ["Home", "Today's Weather", "Interesting Graphs", "Extra", "Future Forecast"]
    )

years = [year for year in range(1840, 2001)]
months = list(calendar.month_name[1:])
days = [day for day in range(1,32)]

if selected == "Today's Weather":
    st.header("Today's Historical Weather Report")
    current_date = datetime.today()
    st.subheader(f"Today is {calendar.month_name[current_date.month]} {current_date.day}, {current_date.year}")
    st.write(f"The average temperature for today is {round(day_mean(current_date.day, current_date.month, 'MEAN_TEMPERATURE'),1)} °C")

    st.subheader("Enter the Date")
    with st.form("entry_form"):
        info_type, day_select, month_select = st.columns(3)
        month_select.selectbox("Select Month:", months, key = "month")
        day_select.selectbox("Select Day:", days, key = "day")
        info_type.selectbox("Select Info:", ["MEAN_TEMPERATURE", "MAX_TEMPERATURE",
        "MIN_TEMPERATURE", "TOTAL_PRECIPITATION"], key = "header")

        submitted = st.form_submit_button("Find Info:")
        if submitted: 
            # avg outputting
            used_day = st.session_state["day"]
            used_month = months.index(st.session_state["month"]) + 1
            used_header = str(st.session_state["header"])
            if math.isnan(day_mean(used_day, used_month, used_header)):
                st.write("This is an invalid date")
            else:
                st.write(f"{day_mean(used_day, used_month, used_header)}")


elif selected == "Interesting Graphs":
    # streamlit plotting setup
    st.title("Average Monthly Max Temperature")

    # plotting
    monthly_avg_temp = weather.groupby(["LOCAL_YEAR", "LOCAL_MONTH"])["MAX_TEMPERATURE"].mean().reset_index()

    avg_max_temp_month, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=monthly_avg_temp, x='LOCAL_MONTH', y='MAX_TEMPERATURE', hue="LOCAL_YEAR", palette='coolwarm', ax=ax)
    ax.set_title('Average Monthly Max Temperature')
    ax.set_xlabel('Month')
    ax.set_ylabel('Average Temperature (°C)')

    st.pyplot(avg_max_temp_month)