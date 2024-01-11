import pandas as pd
import seaborn as sns 
import streamlit as st 
import matplotlib.pyplot as plt 
from streamlit_option_menu import option_menu
from datetime import datetime
import math
import calendar
import io

from data_functions import day_mean, convert_df, month_mean, month_mean_dict, weather_probability
sns.set(color_codes = True)

# using pandas to open the csv file
weather = pd.read_csv("climate-daily.csv", low_memory = False)

# page config
st.set_page_config(page_title = "Historical Weather Network", layout = "wide")

# options menu
with st.sidebar:
    selected = option_menu(
        menu_title = "Navigation",
        options = ["Home", "Daily Weather", "Future Forecast", "Interesting Graphs"]
    )

# set up the available days and months that can be selected
months = list(calendar.month_name[1:])
days = [day for day in range(1,32)]

# creating a pandas dataframe for the averages for each day (setting up here for use in Future Forecast)
# by doing it here it should prevent it from rerunning and recreating the dataframe
# every time Future Forecast is selected
mean_for_year = {}
months = list(calendar.month_name[1:])
for month in range(1, 13):
    for day in range(1, 32):
        # assigning variables for each piece of data that needs to go into the new dataframe
        temps_day = day_mean(day, month, "MEAN_TEMPERATURE")
        rain_probability = weather_probability(day, month, "TOTAL_RAIN")
        snow_probability = weather_probability(day, month, "TOTAL_SNOW")
        snow_ground_day = day_mean(day, month, "SNOW_ON_GROUND")
        snow_ground_probability = weather_probability(day, month, "SNOW_ON_GROUND")
        if not math.isnan(temps_day):
            # calculating the rating for each value in the averages dataframe
            temp_class = (temps_day // 5) + 2
            rain_class = rain_probability // 15

            # for both snow_probability and snow_ground_probability there is a specific rating for 0% as its own rating
            if not snow_probability:
                snow_class = 0
            else:
                snow_class = (snow_probability // 10) + 1
            
            if not snow_ground_probability:
                snow_ground_class = 0
            else:
                snow_ground_class = (snow_ground_probability // 20) + 1
            mean_for_year[f"{calendar.month_name[month]} {day}"] = {"MEAN_TEMPERATURE (°C)": temps_day, "Temperature Rating": temp_class, "Rain Probability %": rain_probability, "Rain Rating": rain_class, "Snow Probability %": snow_probability, "Snow Rating": snow_class, "SNOW_ON_GROUND (cm)": snow_ground_day, "Snow on Ground Probability %": snow_ground_probability, "Snow on Ground Rating": snow_ground_class}
means_for_year_pandas = pd.DataFrame(mean_for_year).T

# code for each navigation option
if selected == "Home":
    # home page containing basic information about the csv file
    st.header("climate-daily.csv File Information:")
    # converting the weather dataframe into a downloadable csv and creating a download button
    home_header_columns = st.columns(2)
    with home_header_columns[0]:
        st.subheader("Download the CSV File Here:")
        downloadable_csv = convert_df(weather)
        st.download_button(label = "Download climate-daily.csv", data = downloadable_csv)
        st.image("https://climatedata.ca/site/assets/uploads/2019/02/logo-climate-data-ca-1.png", caption = "Climate Data Canada Logo (Source of climate-daily.csv)",
        width = 150)
    with home_header_columns[1]:
        st.subheader("Welcome to the Historical Weather Network")
        st.write("The Historical Weather Network uses a weather data csv file for a station in Toronto, Onatrio, Canada.")
        st.write("The csv data was downloaded from Climate Data Canada from this page: https://climatedata.ca/download/#station-download.")
        st.write("All information presented on this website is based off of historical averages and does not truly predict anything.")
        st.write("This website is written in python using streamlit with all dataframe operations being done by python. The graphs were "
        "made using seaborn and plotly.")
    
    st.header("Website Summary")
    summary_columns = st.columns(3)
    with summary_columns[0]:
        st.subheader("Daily Weather")
        st.write("The Daily Weather page relies on historical averages and allows the user to find information on any day of the year. "
        "The page includes a set of weather characteristics for the current day such as minimum temperature and the chance of rain or snow. "
        "Below the weather summary there is one input area that allows the user to find historical averages for a specific category on a specific day "
        "and another input area that allows the user to find these same historical averages except for the entire month. The daily weather section "
        "allows the user to find useful information from the dataframe in a more appealing and easier to use format")
    with summary_columns[1]:
        st.subheader("Future Forecast")
        st.write("The Future Forecast page uses a seperate dataframe from the complete one created using the csv. It contains daily averages for every day of the year "
        "and only uses useful or applicable columns. The purpose of this page is to find specific days that best suit the user's requirements for weather characteristics. "
        "The input box allows the user to enter the columns they wish to sort by (see more on the Important Notes section of the page). It is well suited to planning out "
        "ideal days for special events (ex. plan a picnic day by finding the lowest rain and highest mean temperature from historical data).")
    with summary_columns[2]:
        st.subheader("Interesting Graphs")
        st.write("The Interesting Graphs page contains four graphs, two of them being general information with a bit of analysis and two of them being "
        "weather characteristic based with an option for user input to shift what the graph shows. This page gives insight into the data provided "
        "by the csv file and also provides the user with a more visually appealing way to see some of the relevant information from earlier pages.")

    # printing out the full dataframe
    st.subheader("See Full Dataframe Here:")
    st.dataframe(weather)
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
    st.subheader("NOTE: This page uses historical weather data and does not actually forecast the weather for the day")
    current_date = datetime.today()
    # display the current date and some basic info for that date
    st.subheader(f"Today is {calendar.month_name[current_date.month]} {current_date.day}, {current_date.year}")
    st.write(f"The average temperature for today is {round(day_mean(current_date.day, current_date.month, 'MEAN_TEMPERATURE'), 1)} °C")
    st.write(f"You can expect a high temperature of {round(day_mean(current_date.day, current_date.month, 'MAX_TEMPERATURE'), 1)} °C "
    f"and a low temperature of {round(day_mean(current_date.day, current_date.month, 'MIN_TEMPERATURE'), 1)} °C")
    st.write(f"There is a {weather_probability(current_date.day, current_date.month, 'TOTAL_RAIN')}% of rain today " 
    f"and a {weather_probability(current_date.day, current_date.month, 'TOTAL_SNOW')}% chance of snow")
    st.write(f"This may or not be obvious depending on the season but there is also a " 
    f"{weather_probability(current_date.day, current_date.month, 'SNOW_ON_GROUND')}% chance of there being snow on the ground.")

    st.write()
    st.write("NOTE: Submitting with a blank box will default to \"MEAN_TEMPERATURE\" for info type and the current date (month or day).")

    # specific date information gathering
    st.subheader("Enter a specific date and column to get a historical average")
    with st.form("day_entry"):
        # setting up the three selection options for specific date information gathering
        info_type_day, day_select, month_select_day = st.columns(3)
        month_select_day.selectbox("Select Month:", months, index = current_date.month - 1, key = "days_month")
        day_select.selectbox("Select Day:", days, index = current_date.day - 1, key = "day")
        info_type_day.selectbox("Select Info:", ["MEAN_TEMPERATURE", "MAX_TEMPERATURE",
        "MIN_TEMPERATURE", "TOTAL_RAIN", "SNOW_ON_GROUND", "TOTAL_SNOW", "TOTAL_RAIN (Probability)", "SNOW_ON_GROUND (Probability)",
        "TOTAL_SNOW (Probability)"], key = "days_header")

        # button to submit choices and see results
        day_submit = st.form_submit_button("Find Info:")
        if day_submit: 
            # average outputting
            used_day = st.session_state["day"]
            used_month = months.index(st.session_state["days_month"]) + 1
            # option to use probability instead of average values
            if "Probability" in st.session_state["days_header"]:
                # string slicing to cut out the (Probability) part
                used_days_header = st.session_state["days_header"][:-14]
                # accounting for invalid dates (ex. feb 30)
                if math.isnan(day_mean(used_day, used_month, used_days_header)):
                    st.write("This is an invalid date")
                else:
                    st.write(f"{weather_probability(used_day, used_month, used_days_header)}%")
            else:
                used_days_header = st.session_state["days_header"]
                # accounting for invalid dates (ex. feb 30)
                if math.isnan(day_mean(used_day, used_month, used_days_header)):
                    st.write("This is an invalid date")
                else:
                    # setting a tail string to add on to the end of the returned data
                    unit_tail = ""
                    if "TEMPERATURE" in st.session_state["days_header"]:
                        day_unit_tail = "°C"
                    elif "SNOW" in st.session_state["days_header"]:
                        day_unit_tail = "cm"
                    elif "RAIN" in st.session_state["days_header"]:
                        day_unit_tail = "mm"

                    st.write(f"{day_mean(used_day, used_month, used_days_header)} {day_unit_tail}")
    
    # month information gathering
    st.subheader("Enter a specific month and column to get a monthly historical average")
    st.write("Extra Info: This averages the daily information for each day in a month and returns that value. For example, if you select \"MEAN_TEMPERATURE\" "
    "in June it will return the average temperature for the average day in June. The output type box is there to help users compare the stats for each month "
    "instead of just looking at one individually. For example, you could have it list out each month and its probability of rain by selecting \"Dict\" "
    "or finding the month with the highest or lowest chance of rain by using \"Max\" or \"Min\"")
    with st.form("month_entry"):
        # setting up the three column selection options for month information gathering
        info_type_month, month_select_month, output_type = st.columns(3)
        # creating a copy of months so I can include an "All Months" options
        all_months = months.copy()
        all_months.insert(0,"All Months")
        # select boxes for month entry
        month_select_month.selectbox("Select Month:", all_months, index = current_date.month,
        key = "months_month")
        info_type_month.selectbox("Select Info:", ["MEAN_TEMPERATURE", "MAX_TEMPERATURE",
        "MIN_TEMPERATURE", "TOTAL_RAIN", "SNOW_ON_GROUND", "TOTAL_SNOW", "TOTAL_RAIN (Probability)", "SNOW_ON_GROUND (Probability)",
        "TOTAL_SNOW (Probability)"], key = "months_info")
        output_type.selectbox("Output Type (Only for 'All Months'):", ["None", "Dict", "Max", "Min"], key = "output_type")

        # submit box for month entry
        month_submit = st.form_submit_button("Find Info:")
        # accounting for probability checking option
        if month_submit:
            month_unit_tail = ""
            if "Probability" in st.session_state["months_info"]:
                # string slicing to cut out the (Probability) part
                month_info_type = st.session_state["months_info"][:-14]
                probability_calc = True
                month_unit_tail = "%"
            else:
                month_info_type = st.session_state["months_info"]
                # setting a tail string to add on to the end of the returned data
                if "TEMPERATURE" in month_info_type:
                        month_unit_tail = " °C"
                elif "SNOW" in month_info_type:
                    month_unit_tail = " cm"
                elif "RAIN" in month_info_type:
                    month_unit_tail = " mm"
                probability_calc = False
            
            # accounting for invalid inputs (can't output a min or max for just one month)
            if st.session_state["output_type"] != "None" and st.session_state["months_month"] == "All Months":
                # setting up each option for the output type
                if st.session_state["output_type"] == "Dict":
                    for key, value in month_mean_dict(month_info_type, month_num = False, probability = probability_calc).items():
                        st.write(f"{key} : {value}{month_unit_tail}")

                elif st.session_state["output_type"] == "Max":
                    # -999 is a safe min value to use as there is no number lower than it and it is easier to spot an issue if the loop is not working
                    max_value = -999
                    max_key = ""
                    for key, value in month_mean_dict(month_info_type, month_num = False, probability = probability_calc).items():
                        if value > max_value:
                            max_value = value
                            max_key = key
                    st.write(f"{max_key} : {max_value}{month_unit_tail}")

                elif st.session_state["output_type"] == "Min":
                    # using 999 for the same reasoning as -999
                    max_value = 999
                    max_key = ""
                    for key, value in month_mean_dict(month_info_type, month_num = False, probability = probability_calc).items():
                        if value < max_value:
                            max_value = value
                            max_key = key
                    st.write(f"{max_key} : {max_value}{month_unit_tail}")
            elif st.session_state["output_type"] == "None" and st.session_state["months_month"] != "All Months":
                used_month_months = months.index(st.session_state["months_month"]) + 1
                used_months_header = month_info_type
                st.write(f"{month_mean(used_month_months, used_months_header, probability = probability_calc)}{month_unit_tail}")
            else:
                st.write("Invalid input. Please try again.")

elif selected == "Future Forecast":
    st.header("Find a day that best fits your specifications")

    # extra explanation for how the page works
    st.subheader("Important Notes:")
    st.write("The following page uses input parameters so sort the below dataframe. It prioritizes the first input when "
    "sorting which means that using columns such as \"MEAN_TEMPERATURE\" with \"SNOW_ON_GROUND\" will not give great results. "
    "I decided to leave the option to sort by these in but it is more recommended to use the rating system which relies less "
    "on exact decimal values and so allows for a more applicable sorting process. The key for what each rating means can be found "
    "below the graph. Additionally, there is the option to click on a column of the graph to sort by it in ascending or "
    " descending order. This seems to be built in with streamlit dataframe visualization but it only allows sorting by one column"
    " at a time.")
    st.write("\"Rain Probability %\" is the same as \"TOTAL_RAIN (Probability)\" on the previous page, this goes for the snow and snow on ground columns too. "
    "They simply have different names because the Future Forecast uses a seperate dataframe based on averages for each day instead of the raw full csv file.")

    # explaining the rating system at the top of the page using four columns
    st.subheader("Rating System Key")
    key_columns = st.columns(4)
    with key_columns[0]:
        st.subheader("Temperature Rating")
        st.write("(5 °C Increments)")
        st.write("0 - Very Cold")
        st.write("1 - Cold")
        st.write("2 - Chilly")
        st.write("3 - Cool")
        st.write("4 - Warm")
        st.write("5 - Hot")
        st.write("6 - Very Hot")
    with key_columns[1]:
        st.subheader("Rain Rating")
        st.write("(15% Increments)")
        st.write("0 - Unlikely to Rain")
        st.write("1 - Possibility of Rain")
        st.write("2 - Likely to Rain")
        st.write("3 - May 10th")
        st.write("Note: May 9th is also super rainy")
    with key_columns[2]:
        st.subheader("Snow Rating")
        st.write("(10% Increments)")
        st.write("0 - No Chance of Snow")
        st.write("1 - Very Low Chance of Snow")
        st.write("2 - Unlikely to Snow")
        st.write("3 - Possibility to Snow")
        st.write("4 - Likley to Snow")
        st.write("5 - Very Likley to Snow")
    with key_columns[3]:
        st.subheader("Snow on Ground Rating")
        st.write("(20% Increments)")
        st.write("0 - No Snow on Ground")
        st.write("1 - Very Little Snow on Ground")
        st.write("2 - Little Snow on Ground")
        st.write("3 - Moderate Snow on Ground")
        st.write("4 - Lots of Snow on Ground")
        st.write("5 - Skiing Days")
    
    # using the means_for_year_pandas dataframe from the start of the code for this section

    # create a list called ascending to use in the sorting function
    ascending = []
    # give options to sort by all columns in the dataframe
    sort_columns = st.multiselect('Select columns to sort by:', means_for_year_pandas.columns)
    # add max and mix button options for each parameter that is selected
    for parameters in range(1, len(sort_columns)+1):
        st.radio(f"Parameter {parameters}:", ["max", "min"], key=f"parameter{parameters}")
        ascending.append(st.session_state[f"parameter{parameters}"] == "min")

    # use a slider to allow the user to decide how many columns they want to look at
    st.slider("Select the Number of Rows to View:", min_value = 1, max_value = 365, value = 10, step = 1, key = "num rows")

    # sorting and displaying the dataframe based on user input
    df_sorted = means_for_year_pandas.sort_values(by=sort_columns, ascending=ascending)
    st.dataframe(df_sorted.head(st.session_state["num rows"]))


elif selected == "Interesting Graphs":
    st.header("Interesting Graphs")

    # graph title
    st.subheader("Average Monthly Mean Temperature")
    st.write("This graph shows the mean temperature throughout the year, with each line representating data from one year. This graph shows some pretty "
    "obvious things, such as how the year starts off cold in January then gets steadily warmer around the summer before going back to cold during fall and winter. "
    "However, this graph also shows the effects of global warming on local temperatures. The hue of each line is determined by the local year that the data is from "
    "and there is a clear trend of the mean temperature rising over the last 150 years, regardless of season. While this data is only from one station in Toronto "
    "it is fairly safe to assume that other stations around Canada have seen a similar trend of rising temperatures.")

    # plotting graph
    monthly_avg_temp = weather.groupby(["LOCAL_YEAR", "LOCAL_MONTH"])["MEAN_TEMPERATURE"].mean().reset_index()

    avg_max_temp_month, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=monthly_avg_temp, x='LOCAL_MONTH', y='MEAN_TEMPERATURE', hue="LOCAL_YEAR", palette='coolwarm', ax=ax)
    ax.set_title('Average Monthly Mean Temperature')
    ax.set_xlabel('Month')
    ax.set_ylabel('Average Temperature (°C)')

    st.pyplot(avg_max_temp_month)
    
    # probability of weather type for each month
    st.subheader("Weather over a Month")
    # creating select boxes for the user
    weather_graph_month = st.selectbox('Select a Month:', list(calendar.month_name)[1:], key = "month_graph_month")
    month_graph_type = st.selectbox('Select a Weather Type:', means_for_year_pandas.columns, key = "month_graph_type")
    # filtering the data for one month
    df_monthly_filtered = means_for_year_pandas[means_for_year_pandas.index.str.startswith(st.session_state["month_graph_month"])]
    weather_probability_graph_month, ax = plt.subplots(figsize=(16,4))
    # making a line plot for the selected info type
    sns.barplot(data=df_monthly_filtered, x=df_monthly_filtered.index.str.split().str[1], y=st.session_state["month_graph_type"], hue=df_monthly_filtered.index.str.split().str[1], palette='viridis')
    ax.set_xlabel('Day of the Month')
    ax.set_ylabel(f'{st.session_state["month_graph_type"]}')
    ax.set_title(f'{st.session_state["month_graph_type"]} for Each Day in {st.session_state["month_graph_month"]}')

    st.pyplot(weather_probability_graph_month)

    # frequency of different temperature values
    st.subheader("Frequency of Temperature Values (Mean, Max, Min)")
    st.write("The following three graphs are histograms, which are plots that show the frequency of data using a number of rectangles, specified by the number of \"bins.\" "
    "The number of bins, or rectangles, is set to 20 by default but there is a slider at the bottom to change this number.")
    st.write("What's interesting about these histograms is how the peaks seem to be around 0 or 20 °C for all three types of temperature graphs. This is likely "
    "related to Canada's wide range of seasons and temperatures. The graphs indicate that in general, Canadian weather is either chilly or warm and does not see "
    "that many days that are simply \'cool\' in the mid-range of temperatures.")
    # using st.columns to have all 3 graphs side by side for comparison
    # set their x and y limits to be the same for proper visual comparison
    temperature_graphs = st.columns(3)
    st.slider("Select the Number of Bins", min_value = 5, max_value = 100, value = 20, step = 1, key = "num_bins_slider")
    with temperature_graphs[0]:
        # MEAN_TEMPERATURE histplot
        temperature_freq_graph_mean, ax = plt.subplots(figsize=(12,6))
        sns.histplot(weather['MEAN_TEMPERATURE'], bins=st.session_state["num_bins_slider"], kde=True, color='gray')
        ax.set_title('Temperature Distribution (Mean)')
        ax.set_xlabel('MEAN_TEMPERATURE')
        ax.set_ylabel('Frequency')
        ax.set_ylim(0,7000)
        ax.set_xlim(-30,40)
        st.pyplot(temperature_freq_graph_mean)
    with temperature_graphs[1]:
        # MAX_TEMPERATURE histplot
        temperature_freq_graph_max, ax = plt.subplots(figsize=(12,6))
        sns.histplot(weather['MAX_TEMPERATURE'], bins=st.session_state["num_bins_slider"], kde=True, color='salmon')
        ax.set_title('Temperature Distribution (Max)')
        ax.set_xlabel('MAX_TEMPERATURE')
        ax.set_ylabel('Frequency')
        ax.set_ylim(0,7000)
        ax.set_xlim(-30,40)
        st.pyplot(temperature_freq_graph_max)
    with temperature_graphs[2]:
        # MIN_TEMPERATURE histplot
        temperature_freq_graph_min, ax = plt.subplots(figsize=(12,6))
        sns.histplot(weather['MIN_TEMPERATURE'], bins=st.session_state["num_bins_slider"], kde=True, color='steelblue')
        ax.set_title('Temperature Distribution (Min)')
        ax.set_xlabel('MIN_TEMPERATURE')
        ax.set_ylabel('Frequency')
        ax.set_xlim(0,7000)
        ax.set_xlim(-30,40)
        st.pyplot(temperature_freq_graph_min)

    # graph for different info types over the year
    st.subheader("Weather Over the Year")
    weather_graph_year = st.selectbox('Select a Weather Type:', means_for_year_pandas.columns, key = "year_graph_type")

    # string splitting to create a month column in the means_for_year_pandas dict
    means_for_year_pandas['Month'] = means_for_year_pandas.index.str.split().str[0]

    weather_probability_graph_year, ax = plt.subplots(figsize=(16,4))
    sns.barplot(data=means_for_year_pandas, x='Month', y=st.session_state["year_graph_type"], hue='Month', palette='viridis')

    # setting x axis labels to show as months
    ax.set_xticks(range(len(months)))  
    ax.set_xticklabels(months)

    # setting y axis labels
    ax.set_xlabel('Month of the Year')
    ax.set_ylabel(f'{st.session_state["year_graph_type"]}')
    ax.set_title("Weather Over the Year")

    st.pyplot(weather_probability_graph_year)
