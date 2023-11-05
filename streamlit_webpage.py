import pandas as pd
import seaborn as sns 
import streamlit as st 
import matplotlib.pyplot as plt 
from streamlit_option_menu import option_menu
from datetime import datetime
import calendar

from data_functions import day_mean
sns.set(color_codes = True)

weather = pd.read_csv("climate-daily.csv", low_memory = False)

# page config
st.set_page_config(page_title = "Historical Weather Network", layout = "wide")

# options menu
with st.sidebar:
    selected = option_menu(
        menu_title = "Navigation",
        options = ["Home", "Today's Weather", "Interesting Graphs", "Extra"]
    )

years = [year for year in range(1840, 2001)]
months = list(calendar.month_name[1:])
days = [day for day in range(1,32)]

if selected == "Today's Weather":
    st.header("Enter the Date")
    with st.form("entry_form"):
        info_type, day_select, month_select = st.columns(3)
        month_select.selectbox("Select Month:", months, key = "month")
        day_select.selectbox("Select Day:", days, key = "day")
        info_type.selectbox("Select Info:", ["MEAN_TEMPERATURE", "MAX_TEMPERATURE",
        "MIN_TEMPERATURE", "TOTAL_PRECIPITATION"], key = "header")

        submitted = st.form_submit_button("Find Info:")
        if submitted: 
            # avg outputting
            used_day = int(st.session_state["day"])
            used_month = int(months.index(str(st.session_state["month"]))) + 1
            used_header = str(st.session_state["header"])
            st.write(f"{day_mean(used_day, used_month, used_header)}")