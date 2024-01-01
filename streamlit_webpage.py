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

# next steps:
# add short analysis bits for each graph

# page config
st.set_page_config(page_title = "Historical Weather Network", layout = "wide")

# options menu
with st.sidebar:
    selected = option_menu(
        menu_title = "Navigation",
        options = ["Home", "Daily Weather", "Interesting Graphs", "Future Forecast"]
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
            mean_for_year[f"{calendar.month_name[month]} {day}"] = {"MEAN_TEMPERATURE": temps_day, "Temperature Rating": temp_class, "Rain Probability %": rain_probability, "Rain Rating": rain_class, "Snow Probability %": snow_probability, "Snow Rating": snow_class, "SNOW_ON_GROUND": snow_ground_day, "Snow on Ground Probability %": snow_ground_probability, "Snow on Ground Rating": snow_ground_class}
means_for_year_pandas = pd.DataFrame(mean_for_year).T

# code for each navigation option
if selected == "Home":
    # home page containing basic information about the csv file
    st.header("climate-daily.csv File Information:")
    # converting the weather dataframe into a downloadable csv and creating a download button
    downloadable_csv = convert_df(weather)
    st.download_button(label = "Download climate-daily.csv", data = downloadable_csv)
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

    # specific date information gathering
    st.subheader("Enter a specific date and info to sort by")
    with st.form("day_entry"):
        # setting up the three column selection options for specific date information gathering
        info_type_day, day_select, month_select_day = st.columns(3)
        month_select_day.selectbox("Select Month:", months, index = current_date.month - 1, key = "days_month")
        day_select.selectbox("Select Day:", days, index = current_date.day - 1, key = "day")
        info_type_day.selectbox("Select Info:", ["MEAN_TEMPERATURE", "MAX_TEMPERATURE",
        "MIN_TEMPERATURE", "TOTAL_RAIN", "SNOW_ON_GROUND", "TOTAL_SNOW", "TOTAL_RAIN (Probability)", "SNOW_ON_GROUND (Probability)",
        "TOTAL_SNOW (Probability)"], key = "days_header")

        # button to submit choices and see results
        day_submit = st.form_submit_button("Find Info:")
        if day_submit: 
            # avg outputting
            used_day = st.session_state["day"]
            used_month = months.index(st.session_state["days_month"]) + 1
            # option to use probability instead of average values
            if "Probability" in st.session_state["days_header"]:
                # string slicing to cut out the (Probability) part
                used_days_header = st.session_state["days_header"][:-14]
                # accounting for invalid dates (ex. feb 30)
                if math.isnan(weather_probability(used_day, used_month, used_days_header)):
                    st.write("This is an invalid date")
                else:
                    st.write(f"{weather_probability(used_day, used_month, used_days_header)}")
            else:
                used_days_header = st.session_state["days_header"]
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
            if "Probability" in st.session_state["months_info"]:
                month_info_type = st.session_state["months_info"][:-14]
                probability_calc = True
            else:
                month_info_type = st.session_state["months_info"]
                probability_calc = False

            if st.session_state["output_type"] != "None" and st.session_state["months_month"] == "All Months":
                if st.session_state["output_type"] == "Dict":
                    for key, value in month_mean_dict(month_info_type, month_num = False, probability = probability_calc).items():
                        st.write(f"{key} : {value}")

                elif st.session_state["output_type"] == "Max":
                    max_value = -999
                    max_key = ""
                    for key, value in month_mean_dict(month_info_type, month_num = False, probability = probability_calc).items():
                        if value > max_value:
                            max_value = value
                            max_key = key
                    st.write(f"{max_key} : {max_value}")

                elif st.session_state["output_type"] == "Min":
                    max_value = 999
                    max_key = ""
                    for key, value in month_mean_dict(month_info_type, month_num = False, probability = probability_calc).items():
                        if value < max_value:
                            max_value = value
                            max_key = key
                    st.write(f"{max_key} : {max_value}")
            elif st.session_state["output_type"] == "None" and st.session_state["months_month"] != "All Months":
                used_month_months = months.index(st.session_state["months_month"]) + 1
                used_months_header = month_info_type
                st.write(f"{month_mean(used_month_months, used_months_header, probability = probability_calc)}")
            else:
                st.write("Invalid input. Please try again.")


elif selected == "Interesting Graphs":
    st.header("Interesting Graphs")

    # graph title
    st.subheader("Average Monthly Mean Temperature")
    st.write("add analysis")

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
    weather_graph_month = st.selectbox('Select a Month:', list(calendar.month_name)[1:], key = "month_graph_month")
    month_graph_type = st.selectbox('Select a Weather Type:', means_for_year_pandas.columns, key = "month_graph_type")
    # Create a function to calculate the probability of rain for each day in a month
    # Filter the data to only include the selected month
    df_monthly_filtered = means_for_year_pandas[means_for_year_pandas.index.str.startswith(st.session_state["month_graph_month"])]
    weather_probability_graph_month, ax = plt.subplots(figsize=(16,4))
    # Create a line plot of the probability of rain for each day in the selected month
    sns.barplot(data=df_monthly_filtered, x=df_monthly_filtered.index.str.split().str[1], y=st.session_state["month_graph_type"], hue=df_monthly_filtered.index.str.split().str[1], palette='viridis')
    ax.set_xlabel('Day of the Month')
    ax.set_ylabel(f'{st.session_state["month_graph_type"]}')
    ax.set_title(f'{st.session_state["month_graph_type"]} for Each Day in {st.session_state["month_graph_month"]}')

    # Display the plot
    st.pyplot(weather_probability_graph_month)

    # frequency of different temperature values
    st.subheader("Frequency of Temperature Values (Mean, Max, Min)")
    st.write('add analysis')
    temperature_graphs = st.columns(3)
    st.slider("Select the Number of Bins", min_value = 5, max_value = 100, value = 20, step = 1, key = "num_bins_slider")
    with temperature_graphs[0]:
        temperature_freq_graph_mean, ax = plt.subplots(figsize=(12,6))
        sns.histplot(weather['MEAN_TEMPERATURE'], bins=st.session_state["num_bins_slider"], kde=True, color='gray')
        ax.set_title('Temperature Distribution (Mean)')
        ax.set_xlabel('MEAN_TEMPERATURE')
        ax.set_ylabel('Frequency')
        st.pyplot(temperature_freq_graph_mean)
    with temperature_graphs[1]:
        temperature_freq_graph_max, ax = plt.subplots(figsize=(12,6))
        sns.histplot(weather['MAX_TEMPERATURE'], bins=st.session_state["num_bins_slider"], kde=True, color='salmon')
        ax.set_title('Temperature Distribution (Max)')
        ax.set_xlabel('MAX_TEMPERATURE')
        ax.set_ylabel('Frequency')
        st.pyplot(temperature_freq_graph_max)
    with temperature_graphs[2]:
        temperature_freq_graph_min, ax = plt.subplots(figsize=(12,6))
        sns.histplot(weather['MIN_TEMPERATURE'], bins=st.session_state["num_bins_slider"], kde=True, color='steelblue')
        ax.set_title('Temperature Distribution (Min)')
        ax.set_xlabel('MIN_TEMPERATURE')
        ax.set_ylabel('Frequency')
        st.pyplot(temperature_freq_graph_min)

    #probability of weather type throughout entire year
    st.subheader("Weather Over the Year")
    weather_graph_year = st.selectbox('Select a Weather Type:', means_for_year_pandas.columns, key = "year_graph_type")
    # Create a new column 'Day' for day
    means_for_year_pandas['Day'] = means_for_year_pandas.index.str.split().str[1]

    # Create a new column 'Month' for month
    means_for_year_pandas['Month'] = means_for_year_pandas.index.str.split().str[0]

    # Plotting
    weather_probability_graph_year, ax = plt.subplots(figsize=(16,4))
    sns.barplot(data=means_for_year_pandas, x='Month', y=st.session_state["year_graph_type"], hue='Month', palette='viridis')

    # Formatting x-axis labels
    ax.set_xticks(range(len(months)))  # Set x-ticks for each month
    ax.set_xticklabels(months)  # Set x-tick labels as month names

    ax.set_xlabel('Month of the Year')
    ax.set_ylabel(f'{st.session_state["year_graph_type"]}')
    ax.set_title("Weather Over the Year")

    st.pyplot(weather_probability_graph_year)

elif selected == "Future Forecast":
    st.header("Find a day that best fits your specifications")
    # explaining the rating system at the top of the page using four columns
    st.subheader("Rating System Key")
    key_columns = st.columns(4)
    with key_columns[0]:
        st.subheader("Temperature Rating")
        st.write("0 - Very Cold")
        st.write("1 - Cold")
        st.write("2 - Chilly")
        st.write("3 - Cool")
        st.write("4 - Warm")
        st.write("5 - Hot")
        st.write("6 - Very Hot")
    with key_columns[1]:
        st.subheader("Rain Rating")
        st.write("0 - Unlikely to Rain")
        st.write("1 - Possibility of Rain")
        st.write("2 - Likely to Rain")
        st.write("3 - May 10th")
        st.write("Note: The only rating 3 for rain is on May 10th with May 9th coming very close as well. I'm not sure "
        "why it's these two specific days in May but if you're looking for a rainy day these are definitely your best bet.")
    with key_columns[2]:
        st.subheader("Snow Rating")
        st.write("0 - No Chance of Snow")
        st.write("1 - Very Low Chance of Snow")
        st.write("2 - Unlikely to Snow")
        st.write("3 - Possibility to Snow")
        st.write("4 - Likley to Snow")
        st.write("5 - Very Likley to Snow")
    with key_columns[3]:
        st.subheader("Snow on Ground Rating")
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
    sort_columns = st.multiselect('Select columns to sort by:', means_for_year_pandas.columns[1:])
    # add max and mix button options for each parameter that is selected
    for parameters in range(1, len(sort_columns)+1):
        st.radio(f"Parameter {parameters}:", ["max", "min"], key=f"parameter{parameters}")
        ascending.append(st.session_state[f"parameter{parameters}"] == "min")

    # use a slider to allow the user to decide how many columns they want to look at
    st.slider("Select the Number of Rows to View:", min_value = 1, max_value = 365, value = 10, step = 1, key = "num rows")

    # sorting and displaying the dataframe based on user input
    df_sorted = means_for_year_pandas.sort_values(by=sort_columns, ascending=ascending)
    st.dataframe(df_sorted.head(st.session_state["num rows"]))

    # extra explanation for how the page works
    st.subheader("Important Notes:")
    st.write("The following page uses input parameters so sort the below dataframe. It prioritizes the first input when "
    "sorting which means that using columns such as \"MEAN_TEMPERATURE\" with \"SNOW_ON_GROUND\" will not give great results. "
    "I decided to leave the option to sort by these in but it is more reccommended to use the rating system which relies less "
    "on exact decimal values and so allows for a more applicable sorting process. The key for what each rating means can be found "
    "below the graph. Additionally, there is the option to click on a column of the graph to sort by it in ascending or "
    " descending order. This seems to be built in with streamlit dataframe visualization but it only allows sorting by one column"
    " at a time.")