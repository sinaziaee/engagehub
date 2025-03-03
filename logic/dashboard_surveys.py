import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
from collections import Counter
import re

# Set page config
st.set_page_config(
    page_title="Park Survey Analysis",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        font-weight: 600;
    }
    h1, h2, h3 {
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .chart-container {
        background-color: white;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("📊 Park Survey Data Analysis Dashboard")
st.markdown("This dashboard analyzes responses from park visitors to improve park services and amenities.")

# Function to clean dataframe
@st.cache_data
def load_and_clean_data():
    data = pd.read_csv("form_responses.csv")
    
    # Clean text fields (remove newlines)
    text_columns = ['neighborhood', 'accessibility', 'improvements', 'event_experience', 'concerns', 'comments']
    for col in text_columns:
        data[col] = data[col].str.strip()
    
    # Convert ratings to numeric if needed
    numeric_cols = ['cleanliness_rating', 'safety_rating']
    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    
    return data

# Load data
df = load_and_clean_data()

# Sidebar filters
st.sidebar.header("Filters")

# Age group filter
age_groups = ["All"] + sorted(df['age_group'].unique().tolist())
selected_age = st.sidebar.selectbox("Age Group", age_groups)

# Gender filter
genders = ["All"] + sorted(df['gender'].unique().tolist())
selected_gender = st.sidebar.selectbox("Gender", genders)

# Visit frequency filter
frequencies = ["All"] + sorted(df['visit_frequency'].unique().tolist())
selected_frequency = st.sidebar.selectbox("Visit Frequency", frequencies)

# Apply filters
filtered_df = df.copy()
if selected_age != "All":
    filtered_df = filtered_df[filtered_df['age_group'] == selected_age]
if selected_gender != "All":
    filtered_df = filtered_df[filtered_df['gender'] == selected_gender]
if selected_frequency != "All":
    filtered_df = filtered_df[filtered_df['visit_frequency'] == selected_frequency]

# Create tabs
tabs = st.tabs([
    "📋 Overview", 
    "👥 Demographics", 
    "🚶 Usage Patterns", 
    "⭐ Satisfaction", 
    "🔍 Amenities", 
    # "💬 Text Analysis",
    # "📈 Correlation Analysis"
])

# Tab 1: Overview
with tabs[0]:
    st.header("Survey Overview")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Responses", len(filtered_df))
    with col2:
        avg_cleanliness = round(filtered_df['cleanliness_rating'].mean(), 2)
        st.metric("Avg. Cleanliness", avg_cleanliness)
    with col3:
        avg_safety = round(filtered_df['safety_rating'].mean(), 2)
        st.metric("Avg. Safety", avg_safety)
    
    # Summary statistics
    st.subheader("Quick Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        # Visit frequency distribution
        freq_counts = filtered_df['visit_frequency'].value_counts().reset_index()
        freq_counts.columns = ['Visit Frequency', 'Count']
        
        fig = px.bar(
            freq_counts, 
            x='Visit Frequency', 
            y='Count',
            color='Count',
            color_continuous_scale='Viridis',
            text='Count'
        )
        fig.update_layout(
            title='Visit Frequency Distribution',
            xaxis_title='',
            yaxis_title='Number of Respondents',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Parks visited distribution
        parks_counts = filtered_df['parks_visited'].value_counts().reset_index()
        parks_counts.columns = ['Park', 'Count']
        
        fig = px.pie(
            parks_counts, 
            values='Count', 
            names='Park',
            title='Parks Visited Distribution',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# Tab 2: Demographics
with tabs[1]:
    st.header("Demographic Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Age group distribution
        age_counts = filtered_df['age_group'].value_counts().reset_index()
        age_counts.columns = ['Age Group', 'Count']
        
        # Define the correct order for age groups
        age_order = ["Under 18", "18–24", "25–34", "35–44", "45–54", "55–64", "65+"]
        
        # Reorder the dataframe
        age_counts['Age Group'] = pd.Categorical(
            age_counts['Age Group'], 
            categories=age_order, 
            ordered=True
        )
        age_counts = age_counts.sort_values('Age Group')
        
        fig = px.bar(
            age_counts, 
            x='Age Group', 
            y='Count',
            color='Count',
            color_continuous_scale='Blues',
            text='Count'
        )
        fig.update_layout(
            title='Age Group Distribution',
            xaxis_title='',
            yaxis_title='Number of Respondents',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gender distribution
        gender_counts = filtered_df['gender'].value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']
        
        fig = px.pie(
            gender_counts, 
            values='Count', 
            names='Gender',
            title='Gender Distribution',
            color_discrete_sequence=px.colors.qualitative.Pastel1
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Neighborhood map or chart
    st.subheader("Neighborhood Distribution")
    neighborhood_counts = filtered_df['neighborhood'].value_counts().reset_index()
    neighborhood_counts.columns = ['Neighborhood', 'Count']
    
    fig = px.bar(
        neighborhood_counts.sort_values('Count', ascending=False).head(10), 
        x='Neighborhood', 
        y='Count',
        color='Count',
        color_continuous_scale='Greens',
        text='Count'
    )
    fig.update_layout(
        xaxis_title='',
        yaxis_title='Number of Respondents',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

# Tab 3: Usage Patterns
with tabs[2]:
    st.header("Park Usage Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Purpose of visit
        purpose_counts = filtered_df['purpose'].value_counts().reset_index()
        purpose_counts.columns = ['Purpose', 'Count']
        
        fig = px.bar(
            purpose_counts.sort_values('Count', ascending=False), 
            x='Purpose', 
            y='Count',
            color='Count',
            color_continuous_scale='Oranges',
            text='Count'
        )
        fig.update_layout(
            title='Purpose of Visit',
            xaxis_title='',
            yaxis_title='Number of Respondents',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Travel method
        travel_counts = filtered_df['travel_method'].value_counts().reset_index()
        travel_counts.columns = ['Travel Method', 'Count']
        
        fig = px.pie(
            travel_counts, 
            values='Count', 
            names='Travel Method',
            title='Travel Method to Parks',
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Cross tabulation: Age group vs Visit frequency
    st.subheader("Age Group vs. Visit Frequency")
    
    # Create cross tabulation
    cross_tab = pd.crosstab(
        filtered_df['age_group'], 
        filtered_df['visit_frequency']
    )
    
    # Sort index by age group order
    cross_tab = cross_tab.reindex(age_order)
    
    # Visit frequency order
    freq_order = ["Daily", "Weekly", "Monthly", "A few times a year", "Rarely/Never"]
    cross_tab = cross_tab[freq_order]
    
    # Create heatmap
    fig = px.imshow(
        cross_tab,
        labels=dict(x="Visit Frequency", y="Age Group", color="Count"),
        x=cross_tab.columns,
        y=cross_tab.index,
        color_continuous_scale='YlGnBu',
        aspect="auto",
        text_auto=True
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

# Tab 4: Satisfaction
with tabs[3]:
    st.header("Satisfaction Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Cleanliness rating distribution
        cleanliness_counts = filtered_df['cleanliness_rating'].value_counts().reset_index()
        cleanliness_counts.columns = ['Rating', 'Count']
        cleanliness_counts = cleanliness_counts.sort_values('Rating')
        
        fig = px.bar(
            cleanliness_counts, 
            x='Rating', 
            y='Count',
            color='Count',
            color_continuous_scale='RdYlGn',
            text='Count'
        )
        fig.update_layout(
            title='Cleanliness Rating Distribution',
            xaxis_title='Rating (1-5)',
            yaxis_title='Number of Respondents',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Average cleanliness by park
        st.subheader("Average Cleanliness by Park")
        clean_by_park = filtered_df.groupby('parks_visited')['cleanliness_rating'].mean().reset_index()
        clean_by_park.columns = ['Park', 'Average Cleanliness']
        
        fig = px.bar(
            clean_by_park.sort_values('Average Cleanliness', ascending=False), 
            x='Park', 
            y='Average Cleanliness',
            color='Average Cleanliness',
            color_continuous_scale='RdYlGn',
            text=clean_by_park['Average Cleanliness'].round(2)
        )
        fig.update_layout(
            xaxis_title='',
            yaxis_title='Average Rating (1-5)',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Safety rating distribution
        safety_counts = filtered_df['safety_rating'].value_counts().reset_index()
        safety_counts.columns = ['Rating', 'Count']
        safety_counts = safety_counts.sort_values('Rating')
        
        fig = px.bar(
            safety_counts, 
            x='Rating', 
            y='Count',
            color='Count',
            color_continuous_scale='RdYlGn',
            text='Count'
        )
        fig.update_layout(
            title='Safety Rating Distribution',
            xaxis_title='Rating (1-5)',
            yaxis_title='Number of Respondents',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Average safety by park
        st.subheader("Average Safety by Park")
        safety_by_park = filtered_df.groupby('parks_visited')['safety_rating'].mean().reset_index()
        safety_by_park.columns = ['Park', 'Average Safety']
        
        fig = px.bar(
            safety_by_park.sort_values('Average Safety', ascending=False), 
            x='Park', 
            y='Average Safety',
            color='Average Safety',
            color_continuous_scale='RdYlGn',
            text=safety_by_park['Average Safety'].round(2)
        )
        fig.update_layout(
            xaxis_title='',
            yaxis_title='Average Rating (1-5)',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Accessibility analysis
    st.subheader("Accessibility Analysis")
    
    accessibility_counts = filtered_df['accessibility'].value_counts().reset_index()
    accessibility_counts.columns = ['Accessibility', 'Count']
    
    fig = px.pie(
        accessibility_counts, 
        values='Count', 
        names='Accessibility',
        title='Accessibility Assessment',
        color_discrete_sequence=px.colors.sequential.Plasma_r
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

# Tab 5: Amenities
with tabs[4]:
    st.header("Amenities Analysis")
    
    # Amenities used
    amenities_counts = filtered_df['amenities_used'].value_counts().reset_index()
    amenities_counts.columns = ['Amenity', 'Count']
    
    fig = px.bar(
        amenities_counts.sort_values('Count', ascending=False), 
        x='Amenity', 
        y='Count',
        color='Count',
        color_continuous_scale='Viridis',
        text='Count'
    )
    fig.update_layout(
        title='Amenities Used by Visitors',
        xaxis_title='',
        yaxis_title='Number of Respondents',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Amenities by age group
    st.subheader("Amenities Used by Age Group")
    
    # Create cross tabulation of amenities by age group
    amenities_age = pd.crosstab(
        filtered_df['age_group'], 
        filtered_df['amenities_used']
    )
    
    # Sort index by age group order
    amenities_age = amenities_age.reindex(age_order)
    
    # Create heatmap
    fig = px.imshow(
        amenities_age,
        labels=dict(x="Amenity", y="Age Group", color="Count"),
        x=amenities_age.columns,
        y=amenities_age.index,
        color_continuous_scale='Purples',
        aspect="auto",
        text_auto=True
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Events analysis
    st.subheader("Event Participation and Experience")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Event participation
        event_counts = filtered_df['events_participated'].value_counts().reset_index()
        event_counts.columns = ['Participated', 'Count']
        
        fig = px.pie(
            event_counts, 
            values='Count', 
            names='Participated',
            title='Event Participation',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Event experience
        experience_counts = filtered_df['event_experience'].value_counts().reset_index()
        experience_counts.columns = ['Experience', 'Count']
        
        fig = px.pie(
            experience_counts, 
            values='Count', 
            names='Experience',
            title='Event Experience',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
