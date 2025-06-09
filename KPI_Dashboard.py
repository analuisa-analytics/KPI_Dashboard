import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Title of the app
st.title("📊  Production and Quality Performance Dashboard")



############## FILES

# Path of the current file
current_dir = os.path.dirname(__file__)

# Absolute path of the files
production_path = os.path.join(current_dir, "production_data.csv")
occurences_path = os.path.join(current_dir, "occurences_data.csv")

# Load the data
df_production = pd.read_csv(production_path, sep='\t')
df_nc = pd.read_csv(occurences_path, sep='\t')



############## FILTER 

# Sidebars Title
st.sidebar.header("Filter")

# Sidebar for Date 
dates = st.sidebar.date_input("Date", [])



############################################# PRODUCTION TAB

# Sidebar for shifts
shifts = st.sidebar.multiselect("Shift", df_production["Shift"].unique(), default=df_production["Shift"].unique())

df_filtered = df_production

# Assure that 'Date' is datetime
df_filtered["Date"] = pd.to_datetime(df_filtered["Date"])

# Filter for date
if len(dates) == 2:
    start_date, end_date = pd.to_datetime(dates[0]), pd.to_datetime(dates[1])
    df_filtered = df_filtered[(df_filtered["Date"] >= start_date) & (df_filtered["Date"] <= end_date)]

# Filter for shifts
if shifts and len(shifts) < len(df_filtered['Shift'].unique()):
    df_filtered = df_nc_filtered[df_filtered['Shift'].isin(shifts)]



######### PLANNED VS REAL


# Create column with the first day of the month
df_filtered["Month_Year"] = pd.to_datetime(df_filtered["Date"]).dt.to_period("M").dt.to_timestamp()

# Create column with Month and Year
df_filtered["Month"] = pd.to_datetime(df_filtered["Date"]).dt.strftime("%b %Y")  # Ex: "Jan 2025"

# Group by month and sum the values
df_month = df_filtered.groupby(["Month_Year", "Month"])[["Planned_Quantity", "Produced_Quantity"]].sum().reset_index()
df_month = df_month.sort_values("Month_Year")

# New Bar Plot
df_melted = df_month.melt(id_vars=["Month_Year", "Month"], 
                            value_vars=['Planned_Quantity', 'Produced_Quantity'],
                            var_name='Type', value_name='Quantity')
fig1 = px.bar(df_melted, 
             x='Month_Year', 
             y='Quantity', 
             color='Type', 
             barmode='group',
             title='📈 Planned vs. Real',
             labels={'Month_Year': 'Month', 'Quantity': 'Quantity', 'Type': 'Type'})

fig1.update_layout(
    xaxis_title_font=dict(size=14, family='Arial', color='black'),
    yaxis_title_font=dict(size=14, family='Arial', color='black'),
    xaxis_tickfont=dict(size=14),
    yaxis_tickfont=dict(size=14)
)

fig1.update_xaxes(
    tickmode='array',
    tickvals=df_month['Month_Year'],
    ticktext=df_month['Month']
)


######### KPI

goal_values = {
    'OEE': 0.85,          
    'Performance': 0.90,  
    'Availability': 0.95, 
    'Quality': 0.98      
}


# KPI Mean
mean_values = df_filtered[['OEE', 'Performance', 'Availability', 'Quality']].mean().round(2)

# Prepare Data
labels = mean_values.index.tolist()
values = mean_values.tolist()

# Create half donut
def create_half_donut(kpi, value, color):
    goal = goal_values[kpi]
    
    fig = go.Figure(go.Pie(
        values=[value*100, 100 - value*100],
        labels=[f'{value*100:.0f}%',' ',' '],
        marker_colors=[color, "#E8E8E8", 'rgba(0,0,0,0)'],
        hole=0.6,
        rotation=180,  
        direction='clockwise',
        textinfo='label',
        textfont=dict(size=30, color='black'),
        sort=False,
        textposition='inside',
        showlegend=False
    ))

    # Only superior part
    fig.update_traces(domain=dict(x=[0, 1], y=[0, 1]), hoverinfo='label+percent', hovertemplate='%{label}')
    
    fig.add_annotation(
        text=f"🎯 Goal: {goal * 100:.0f}%",
        x=0.5,
        y=0.5,  # dentro da área visível do gráfico
        xref='paper',
        yref='paper',
        showarrow=False,
        font=dict(size=16, color="gray"),
        xanchor='center'
    )
    
    fig.update_layout(
        title={'text': f'{kpi} - Mean', 'x': 0.3},
        margin=dict(t=30, b=0, l=0, r=0),
        height=200,
        paper_bgcolor='white'
    )

    return fig


# Colors for each KPI
colors = {
    'OEE': '#636EFA',
    'Performance': '#EF553B',
    'Availability': '#00CC96',
    'Quality': '#AB63FA'
}

############ OCCURENCES

df_monthly_occur = df_filtered.groupby("Month_Year").size().reset_index(name="NC_Occurrences")

fig7 = px.line(df_monthly_occur,
              x="Month_Year",
              y="NC_Occurrences",
              title="📉 Occurrences per Month",
              markers=True)

fig7.update_layout(
    xaxis_title="Month",
    yaxis_title="Occurrences",
    xaxis_title_font=dict(size=14, family='Arial', color='black'),
    yaxis_title_font=dict(size=14, family='Arial', color='black'),
    xaxis_tickfont=dict(size=14),
    yaxis_tickfont=dict(size=14),
    hovermode="x unified")


############ DOWNTIME MINUTES PER MONTH

df_downtime_available = df_filtered.groupby("Month_Year")[["Downtime_Minutes", "Available_Time_Minutes"]].sum().reset_index()

# Convert the dataframe to long format
df_downtime_melted = df_downtime_available.melt(id_vars="Month_Year",
                                       value_vars=["Downtime_Minutes", "Available_Time_Minutes"],
                                       var_name="Type", value_name="Minutes")

# Horizontal bar chart
fig9 = go.Figure()

# Available minutes (bar base)
fig9.add_trace(go.Bar(
    y=df_downtime_available["Month_Year"].dt.strftime('%b %Y'),
    x=df_downtime_available["Available_Time_Minutes"],
    name='Available (min)',
    orientation='h',
    marker=dict(color='green')
))

# Downtime minutes (above the bar base)
fig9.add_trace(go.Bar(
    y=df_downtime_available["Month_Year"].dt.strftime('%b %Y'),
    x=df_downtime_available["Downtime_Minutes"],
    name='Downtime (min)',
    orientation='h',
    marker=dict(color='red')
))

# Layout
fig9.update_layout(
    barmode='stack',
    title='🧱 Downtime and Available Time (min)',
    xaxis_title='Minutes',
    yaxis_title='Month',
    xaxis_title_font=dict(size=14, family='Arial', color='black'),
    yaxis_title_font=dict(size=14, family='Arial', color='black'),
    xaxis_tickfont=dict(size=14),
    yaxis_tickfont=dict(size=14),
    legend=dict(x=0.7, y=1.1, orientation='h'),
    template='plotly_white',
    height=500
)


######## TAB1

tab1, tab2 = st.tabs(["📦 Production", "✅ Quality"])

with tab1:
    st.subheader("KPI Production Process")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(fig1)

    with col2:
        st.plotly_chart(fig7)

    with col3:
        st.plotly_chart(fig9)
        


    col3, col4, col5 = st.columns(3, gap = "small")

    with col3:
        with st.container():
            st.plotly_chart(create_half_donut('OEE', mean_values['OEE'], colors['OEE']), use_container_width=True)
            st.plotly_chart(create_half_donut('Performance', mean_values['Performance'], colors['Performance']), use_container_width=True)
    with col4:
        with st.container():
            st.plotly_chart(create_half_donut('Availability', mean_values['Availability'], colors['Availability']), use_container_width=True)
            st.plotly_chart(create_half_donut('Quality', mean_values['Quality'], colors['Quality']), use_container_width=True)

    with col5:
        # Choose the indicator
        indicator = st.selectbox("Select the KPI", ['OEE', 'Performance', 'Availability', 'Quality'])
    
        fig2 = px.line(df_filtered, x='Date', y=indicator, title=f'Tendency of {indicator} through time')
        fig2.update_layout(
            xaxis_title='Date', 
            yaxis_title=indicator,
            xaxis_title_font=dict(size=14, family='Arial', color='black'),
            yaxis_title_font=dict(size=14, family='Arial', color='black'),
            xaxis_tickfont=dict(size=14),
            yaxis_tickfont=dict(size=14))

        # Add horizontal line with the goal
        fig2.add_hline(y=goal_values[indicator], line_dash="dash", line_color="red", annotation_text="Goal", annotation_position="top left")
        st.plotly_chart(fig2)
    

    
    

############################################# QUALITY TAB

status = st.sidebar.multiselect("Status", df_nc["status"].unique(), default=df_nc["status"].unique())
severity_bar = st.sidebar.multiselect("Severity", df_nc["severity"].unique(), default=df_nc["severity"].unique())

df_nc['date'] = pd.to_datetime(df_nc['date'])

df_nc_filtered = df_nc.copy()

# Filter dates if selected
if len(dates) == 2:
    start_date, end_date = pd.to_datetime(dates[0]), pd.to_datetime(dates[1])
    df_nc_filtered = df_nc_filtered[(df_nc_filtered['date'] >= start_date) & (df_nc_filtered['date'] <= end_date)]

# Filter status if selected
if status and len(status) < len(df_nc['status'].unique()):
    df_nc_filtered = df_nc_filtered[df_nc_filtered['status'].isin(status)]

# Filter status if selected
if severity_bar and len(severity_bar) < len(df_nc['severity'].unique()):
    df_nc_filtered = df_nc_filtered[df_nc_filtered['severity'].isin(severity_bar)]

######### PARETO

# Count the occurences by type of non conformity
nc_counts = df_nc_filtered['type_nonconformity'].value_counts().reset_index()
nc_counts.columns = ['Type', 'Count']

# Calculation of percentage and cumulative
nc_counts['Percent'] = 100 * nc_counts['Count'] / nc_counts['Count'].sum()
nc_counts['Cumulative'] = nc_counts['Percent'].cumsum()

# Bar Plot for Quantity
bar = go.Bar(x=nc_counts['Type'], y=nc_counts['Count'], name='Count')

# Line Plot for Cumulative
line = go.Scatter(x=nc_counts['Type'], y=nc_counts['Cumulative'], 
                  name='Cumulative %', yaxis='y2')

# Layout
layout = go.Layout(
    title='Pareto of Non Conformity',
    yaxis=dict(
        title='Quantity',
        titlefont=dict(size=14, family='Arial', color='black'),
        tickfont=dict(size=14)
    ),
    yaxis2=dict(
        title='Cumulative (%)',
        titlefont=dict(size=14, family='Arial', color='black'),
        tickfont=dict(size=14),
        overlaying='y',
        side='right',
        range=[0, 110]
    ),
    xaxis=dict(
        title='Type',
        titlefont=dict(size=14, family='Arial', color='black'),
        tickfont=dict(size=14)
    ),
    bargap=0.2
)

fig3 = go.Figure(data=[bar, line], layout=layout)


######### SEVERITY

# Count the activities for each severity
severity_counts = df_nc_filtered['severity'].value_counts()

# Values with fallback (in case they don't exist)
high = severity_counts.get("High", 0)
medium = severity_counts.get("Medium", 0)
low = severity_counts.get("Low", 0)

def metric_card(label, value, color, width="90%", font_size_title="18px", font_size_value="30px", padding="1px"):
    return f"""
    <div style="background-color:{color};
                padding:{padding};
                border-radius:10px;
                margin-bottom:10px;
                text-align:center;
                width:{width};
                box-shadow: 2px 2px 6px rgba(0,0,0,0.15);">
        <h4 style="color:white; margin:0; font-size:{font_size_title};">{label}</h4>
        <h2 style="color:white; margin:0; font-size:{font_size_value};">{value}</h2>
    </div>
    """

# Colors
color_high = "#e74c3c"    # red
color_medium = "#f39c12"  # orange
color_low = "#27ae60"     # green




######### BY PRODUCTS



# Count the product 
product_counts = df_nc_filtered['product'].value_counts().reset_index()
product_counts.columns = ['product', 'Count']

# Bar Plot
fig5 = px.pie(product_counts, 
             names='product', 
             values='Count', 
             title='Product Distribution')
             
             
fig5.update_traces(textinfo='percent+label',
                  pull=[0.05]*len(product_counts))


fig5.update_layout(
    title_font=dict(size=17, color='black'),
    font=dict(size=16,color='#4B3621'),
    paper_bgcolor='white'
)



########### 

country_counts = df_nc_filtered['customer'].value_counts().reset_index()
country_counts.columns = ['Country', 'Count']

fig10 = px.choropleth(
    country_counts,
    locations="Country",
    locationmode="country names",
    color="Count",
    color_continuous_scale="Blues",
    title="Country Distribution",
    height=700
)

fig10.update_layout(margin=dict(l=0, r=0, t=30, b=0))

#########

# Assure that the column Severity exists
severity_order = ['High', 'Medium', 'Low']
df_nc_filtered['severity'] = pd.Categorical(df_nc_filtered['severity'], categories=severity_order, ordered=True)

# Order DataFrame
df_severity_sorted = df_nc_filtered.sort_values(by='severity')

def color_severity(val):
    if val == 'High':
        return 'background-color: #ff4d4d; color: white'
    elif val == 'Medium':
        return 'background-color: #ffd633'
    elif val == 'Low':
        return 'background-color: #85e085'
    return ''

styled_df = df_severity_sorted.style.applymap(color_severity, subset=['severity'])

#######

# Inicializa a lista de ações, se ainda não existir
if 'acoes' not in st.session_state or len(st.session_state.acoes) != len(df_nc_filtered):
    st.session_state.acoes = [''] * len(df_nc_filtered)



########################################

with tab2:
    st.subheader("Quality Control")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(fig3)

    with col2:
        with st.container():
            st.markdown(
    """
    <h3 style="color:black; font-size:17px; font-weight:bold;">
        Nonconformities by Severity
    </h3>
    """,
    unsafe_allow_html=True
)
            st.markdown(metric_card("🔴 High Severity", high, color_high), unsafe_allow_html=True)
            st.markdown(metric_card("🟠 Medium Severity", medium, color_medium), unsafe_allow_html=True)
            st.markdown(metric_card("🟢 Low Severity", low, color_low), unsafe_allow_html=True)

    with col3:
        st.plotly_chart(fig5)

    col4, col5 = st.columns(2)

    with col4:
        st.plotly_chart(fig10)

    with col5:
        st.dataframe(styled_df, use_container_width=True, height=600)
    
    
    st.markdown("---")
    st.subheader("✏️ Add Corrective Action")

    # Select line through ID
    id_selecionado = st.selectbox("Select ID:", df_nc_filtered['id'])

    # Text box to write corrective action
    index = df_nc_filtered[df_nc_filtered['id'] == id_selecionado].index[0]
    acao_input = st.text_area("Describe Corrective Action :", value=st.session_state.acoes[index])

    # Save button
    if st.button("Submit Action"):
        st.session_state.acoes[index] = acao_input
        st.success("Successfully saved!")

    # Update column with actions
    df_nc_filtered['Corrective Action'] = st.session_state.acoes

    st.markdown("---")
    st.subheader("📑 Dataframe with Corrective Action")
    st.dataframe(df_nc_filtered, use_container_width=True)





