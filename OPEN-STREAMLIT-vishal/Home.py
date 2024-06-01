import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from io import BytesIO
from streamlit_option_menu import option_menu
from numerize.numerize import numerize
import time
from PIL import Image, ImageEnhance, ImageFilter, ImageOps,ImageDraw
import matplotlib.pyplot as plt
from streamlit_extras.metric_cards import style_metric_cards
st.set_option('deprecation.showPyplotGlobalUse', False)
import plotly.graph_objs as go
#uncomment this line if you use mysql
#from query import *

# Set page configuration with the new unicorn emoji as the page icon
st.set_page_config(page_title="BUSINESS ANALYTICS DASHBOARD", page_icon="🦄", layout="wide")

#all graphs we use custom css not streamlit 
theme_plotly = None 

# load Style css
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

#uncomment these two lines if you fetch data from mysql
#result = view_all_data()
#df=pd.DataFrame(result,columns=["Policy","Expiry","Location","State","Region","Investment","Construction","BusinessType","Earthquake","Flood","Rating","id"])

#load excel file | comment this line when  you fetch data from mysql
df=pd.read_excel('data.xlsx', sheet_name='Sheet1')
#df=pd.DataFrame(result,columns=["Policy","Expiry","Location","State","Region","Investment","Construction","BusinessType","Earthquake","Flood","Rating","id"])

#side bar logo
image = Image.open('data\Business Anaytics_Logo.png')
st.sidebar.image(image, caption='Business Analytics')

#switcher (Sidebar Filters)
st.sidebar.header('Filter Options')
region=st.sidebar.multiselect(
    "SELECT REGION",
     options=df["Region"].unique(),
     default=df["Region"].unique(),
)
location=st.sidebar.multiselect(
    "SELECT LOCATION",
     options=df["Location"].unique(),
     default=df["Location"].unique(),
)
construction=st.sidebar.multiselect(
    "SELECT CONSTRUCTION",
     options=df["Construction"].unique(),
     default=df["Construction"].unique(),
)

df_selection=df.query(
    "Region==@region & Location==@location & Construction ==@construction"
)
# Displaying Data

st.title('Dashboard for Policy Data Analysis')
#st.header("ANALYTICAL PROCESSING, KPI, TRENDS & PREDICTIONS")
# Load the image
image1 = Image.open("data/logo_unicorn.png")  # Corrected the file path

# Make the image color more shadowy by reducing brightness
enhancer = ImageEnhance.Brightness(image1)
shadow_image = enhancer.enhance(0.6)  # Adjust the factor as needed (0.6 is an example)

# Create a mask to make the corners soft
mask = Image.new("L", shadow_image.size, 0)
mask_draw = ImageDraw.Draw(mask)
mask_draw.ellipse((0, 0, *shadow_image.size), fill=255)

# Apply the mask to the image
soft_corners_image = ImageOps.fit(shadow_image, mask.size, centering=(0.5, 0.5))
soft_corners_image.putalpha(mask)

# Convert the image to the base64 string

buffered = BytesIO()
soft_corners_image.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue()).decode()
# Add CSS to position the image container on the right side of the page
st.markdown(
    """
    <style>
    .image-container {
        position: fixed;
        top: 1px;
        right: 330px;
        width:85px; /* Adjust width as needed */
        z-index: 999;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Display the image in the container
st.markdown(
    f"""
    <div class="image-container">
        <img src="data:image/png;base64,{img_str}" style="width:300%;">
    </div>
    """,
    unsafe_allow_html=True
)

# Display the name right
st.markdown(
    """
    <div style="text-align: right;">
        <span style="font-size: 60px; color: green; font-weight: bold;">Vishal Kothari</span>
    </div>
    """,
    unsafe_allow_html=True
)

# Function to format large numbers
def numerize(value):
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}K"
    else:
        return str(value)

# Function to style metric cards
def style_metric_cards():
    st.markdown(
        """
        <style>
        .stMetric {
            background-color: #FFFFFF;
            border-left: 5px solid #686664;
            border: 1px solid #000000;
            box-shadow: 0 0 10px #F71938;
            padding: 10px;
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def Home():
    with st.expander("VIEW EXCEL DATASET"):
        showData = st.multiselect('Filter: ', df_selection.columns, default=["Policy","Expiry","Location","State","Region","Investment","Construction","BusinessType","Earthquake","Flood","Rating"])
        st.dataframe(df_selection[showData], use_container_width=True)

    # Compute top analytics
    total_investment = float(df_selection['Investment'].sum())
    investment_mode = float(df_selection['Investment'].mode()[0])
    investment_mean = float(df_selection['Investment'].mean())
    investment_median = float(df_selection['Investment'].median())
    rating = float(df_selection['Rating'].sum())

    total1, total2, total3, total4, total5 = st.columns(5, gap='small')
    with total1:
        st.info('Sum Investment', icon="💵")
        st.metric(label="Sum INR", value=f"{total_investment:,.0f}")

    with total2:
        st.info('Most Investment', icon="📈")
        st.metric(label="Mode INR", value=f"{investment_mode:,.0f}")

    with total3:
        st.info('Average', icon="📊")
        st.metric(label="Average INR", value=f"{investment_mean:,.0f}")

    with total4:
        st.info('Central Earnings', icon="💰")
        st.metric(label="Median INR", value=f"{investment_median:,.0f}")

    with total5:
        st.info('Ratings', icon="⭐")
        st.metric(label="Rating", value=numerize(rating), help=f""" Total Rating: {rating} """)
    
    style_metric_cards()

    # Variable distribution Histogram
    with st.expander("DISTRIBUTIONS BY FREQUENCY"):
        fig, ax = plt.subplots(figsize=(16, 8))
        df_selection['Investment'].hist(ax=ax, color='#898784', zorder=2, rwidth=0.9)
        ax.set_title('Investment Distribution')
        ax.set_xlabel('Investment')
        ax.set_ylabel('Frequency')
        st.pyplot(fig)


def graphs():
    # Bar graph: Investment by Business Type
    investment_by_business_type = (
        df_selection.groupby(by=["BusinessType"]).count()[["Investment"]].sort_values(by="Investment")
    )
    fig_investment = px.bar(
       investment_by_business_type,
       x="Investment",
       y=investment_by_business_type.index,
       orientation="h",
       title="<b> INVESTMENT BY BUSINESS TYPE </b>",
       color_discrete_sequence=["#0083B8"]*len(investment_by_business_type),
       template="plotly_white",
    )
    fig_investment.update_layout(
     plot_bgcolor="rgba(0,0,0,0)",
     font=dict(color="black"),
     yaxis=dict(showgrid=True, gridcolor='#cecdcd'),  
     paper_bgcolor='rgba(0, 0, 0, 0)',
     xaxis=dict(showgrid=True, gridcolor='#cecdcd'),
    )

    # Line graph: Investment by State
    investment_state = df_selection.groupby(by=["State"]).count()[["Investment"]]
    fig_state = px.line(
       investment_state,
       x=investment_state.index,
       y="Investment",
       orientation="v",
       title="<b> INVESTMENT BY STATE </b>",
       color_discrete_sequence=["#0083b8"]*len(investment_state),
       template="plotly_white",
    )
    fig_state.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    #yaxis=(dict(showgrid=False))
    yaxis=dict(showgrid=True, gridcolor='#cecdcd'),  
    paper_bgcolor='rgba(0, 0, 0, 0)',
    )

    left, right, center = st.columns(3)
    left.plotly_chart(fig_state, use_container_width=True)
    right.plotly_chart(fig_investment, use_container_width=True)
    
    with center:
        # Pie chart: Ratings by Regions
        fig = px.pie(df_selection, values='Rating', names='State', title='RATINGS BY REGIONS')
        fig.update_layout(legend_title="Regions", legend_y=0.9,plot_bgcolor="rgba(0,0,0,0)",
     font=dict(color="black"),
     yaxis=dict(showgrid=True, gridcolor='#cecdcd'),  
     paper_bgcolor='rgba(0, 0, 0, 0)',
     xaxis=dict(showgrid=True, gridcolor='#cecdcd'),)
        fig.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True)


def Progressbar():
    # Style the progress bar with a gradient color
    st.markdown(
        """<style>.stProgress > div > div > div > div { background-image: linear-gradient(to right, #99ff99 , #FFFF00)}</style>""",
        unsafe_allow_html=True,
    )

    # Define the target and current investment values
    target = 3000000000  # Target investment value in INR
    current = df_selection["Investment"].sum()  # Sum of current investments from filtered data
    percent = round((current / target * 100))  # Calculate the percentage of the target achieved

    # Initialize the progress bar
    mybar = st.progress(0)

    # Display the progress and message
    if percent > 100:
        st.subheader("Target done!")
    else:
        st.write("You have ", percent, "% of ", (format(target, 'd')), " TZS")
        for percent_complete in range(percent):
            time.sleep(0.1)  # Delay to animate the progress bar
            mybar.progress(percent_complete + 1, text=" Target Percentage")

def Progressbar():
    # Style the progress bar with a gradient color
    st.markdown(
        """<style>.stProgress > div > div > div > div { background-image: linear-gradient(to right, #99ff99 , #FFFF00)}</style>""",
        unsafe_allow_html=True,
    )

    # Define the target and current investment values
    target = 3000000000  # Replace this with the realistic target value you determine
    current = df_selection["Investment"].sum()  # Sum of current investments from filtered data
    percent = round((current / target * 100))  # Calculate the percentage of the target achieved

    # Initialize the progress bar
    mybar = st.progress(0)

    # Display the progress and message
    if percent > 100:
        st.subheader("Target done!")
    else:
        st.write("You have ", percent, "% of ", (format(target, 'd')), " INR")
        for percent_complete in range(percent):
            time.sleep(0.1)  # Delay to animate the progress bar
            mybar.progress(percent_complete + 1, text=" Target Percentage")


# Define the sidebar menu and handle page navigation
def sideBar():
    with st.sidebar:
        selected = option_menu(
            menu_title="Main Menu",
            options=["Home", "Progress"],
            icons=["house", "eye"],
            menu_icon="cast",
            default_index=0
        )
    if selected == "Home":
        Home()
        graphs()
    if selected == "Progress":
        Progressbar()
        graphs()

# Call the sidebar function to display the menu
sideBar()

# Add a logo image to the sidebar
st.sidebar.image("data/business_analytics_dashb.png", caption="")

# Feature selection and displaying a Plotly box plot
st.subheader('PICK FEATURES TO EXPLORE DISTRIBUTIONS TRENDS BY QUARTILES')
feature_y = st.selectbox('Select feature for y Quantitative Data', df_selection.select_dtypes("number").columns)
fig2 = go.Figure(
    data=[go.Box(x=df['BusinessType'], y=df[feature_y])],
    layout=go.Layout(
        title=go.layout.Title(text="BUSINESS TYPE BY QUARTILES OF INVESTMENT"),
        plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent background
        paper_bgcolor='rgba(0, 0, 0, 0)',  # Transparent background
        xaxis=dict(showgrid=True, gridcolor='#cecdcd'),  # X-axis grid color
        yaxis=dict(showgrid=True, gridcolor='#cecdcd'),  # Y-axis grid color
        font=dict(color='#cecdcd'),  # Text color
    )
)
# Display the Plotly figure using Streamlit
st.plotly_chart(fig2, use_container_width=True)

# Custom theme to hide Streamlit default menu, footer, and header
hide_st_style = """ 
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

