import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from textblob import TextBlob
import plotly.express as px
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Calgary Parks Dashboard",
    page_icon="🌲",
    layout="wide"
)

# Custom CSS to improve the look and feel
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2c7fb8;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .section-header {
        font-size: 1.5rem;
        color: #2c7fb8;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .info-text {
        font-size: 1rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown("<h1 class='main-header'>Calgary Parks Review Dashboard</h1>", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("park_reviews.csv")
    # Add sentiment analysis
    df["Sentiment"] = df["Text"].apply(lambda text: TextBlob(str(text)).sentiment.polarity)
    df["Sentiment Category"] = df["Sentiment"].apply(
        lambda x: "Positive" if x > 0.1 else ("Negative" if x < -0.1 else "Neutral")
    )
    return df

# Loading message
with st.spinner('Loading data...'):
    df = load_data()

# Show dataframe sample in an expander
with st.expander("View sample data"):
    st.dataframe(df.head(10))

# Sidebar for filters
st.sidebar.markdown("<h2 class='section-header'>Filters</h2>", unsafe_allow_html=True)

# Filter by ratings
rating_filter = st.sidebar.multiselect(
    "Filter by Rating",
    options=sorted(df["Rating"].unique()),
    default=sorted(df["Rating"].unique())
)

# Filter by sentiment
sentiment_filter = st.sidebar.multiselect(
    "Filter by Sentiment",
    options=["Positive", "Neutral", "Negative"],
    default=["Positive", "Neutral", "Negative"]
)

# Filter by top N parks
top_n = st.sidebar.slider("Show Top N Parks", min_value=5, max_value=50, value=10, step=5)

# Apply filters
filtered_df = df[df["Rating"].isin(rating_filter) & df["Sentiment Category"].isin(sentiment_filter)]

# Main dashboard layout with tabs
tab1, tab3, tab4 = st.tabs(["Overview", "Review Text Analysis", "Advanced Analysis"])

with tab1:
    st.markdown("<h2 class='section-header'>Overview of Park Ratings</h2>", unsafe_allow_html=True)
    
    # Create two columns for the visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution of ratings
        st.markdown("<h3 class='section-header'>Rating Distribution</h3>", unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(filtered_df["Rating"], bins=5, kde=True, ax=ax)
        ax.set_xlabel("Rating")
        ax.set_ylabel("Count of Reviews")
        ax.set_title("Distribution of Park Ratings")
        st.pyplot(fig)
    
    with col2:
        # Sentiment distribution
        st.markdown("<h3 class='section-header'>Sentiment Distribution</h3>", unsafe_allow_html=True)
        sentiment_counts = filtered_df["Sentiment Category"].value_counts().reset_index()
        sentiment_counts.columns = ["Sentiment", "Count"]
        fig = px.pie(
            sentiment_counts, 
            values="Count", 
            names="Sentiment", 
            hole=0.4, 
            color="Sentiment",
            color_discrete_map={"Positive": "#2ecc71", "Neutral": "#f1c40f", "Negative": "#e74c3c"}
        )
        fig.update_layout(title_text="Review Sentiment Distribution")
        st.plotly_chart(fig)
    
    # Overall statistics
    st.markdown("<h3 class='section-header'>Key Statistics</h3>", unsafe_allow_html=True)
    
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.metric("Total Parks", filtered_df["Park Name"].nunique())
    
    with stat_col2:
        st.metric("Total Reviews", len(filtered_df))
    
    with stat_col3:
        st.metric("Average Rating", round(filtered_df["Rating"].mean(), 2))
    
    with stat_col4:
        positive_pct = (filtered_df["Sentiment Category"] == "Positive").mean() * 100
        st.metric("Positive Reviews", f"{positive_pct:.1f}%")

with tab3:
    st.markdown("<h2 class='section-header'>Review Text Analysis</h2>", unsafe_allow_html=True)
    
    # Word cloud options
    wc_col1, wc_col2 = st.columns([1, 2])
    
    with wc_col1:
        # Word cloud controls
        st.markdown("<h3 class='section-header'>Word Cloud Settings</h3>", unsafe_allow_html=True)
        
        wc_type = st.radio(
            "Select Word Cloud Type",
            ["All Reviews", "By Rating", "By Sentiment"]
        )
        
        if wc_type == "By Rating":
            selected_rating = st.select_slider(
                "Select Rating",
                options=sorted(filtered_df["Rating"].unique())
            )
            wc_data = filtered_df[filtered_df["Rating"] == selected_rating]
            wc_title = f"Word Cloud for {selected_rating}-Star Reviews"
        
        elif wc_type == "By Sentiment":
            selected_sentiment = st.selectbox(
                "Select Sentiment",
                options=["Positive", "Neutral", "Negative"]
            )
            wc_data = filtered_df[filtered_df["Sentiment Category"] == selected_sentiment]
            wc_title = f"Word Cloud for {selected_sentiment} Reviews"
        
        else:  # All Reviews
            wc_data = filtered_df
            wc_title = "Word Cloud for All Reviews"
    
    with wc_col2:
        # Generate and display word cloud
        if len(wc_data) > 0:
            text_data = " ".join(wc_data["Text"].astype(str))
            
            # Generate word cloud
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color="white",
                max_words=200,
                collocations=False
            ).generate(text_data)
            
            # Display
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            ax.set_title(wc_title)
            st.pyplot(fig)
        else:
            st.warning("Not enough data for the selected filters to generate a word cloud.")
    
    # Top words
    st.markdown("<h3 class='section-header'>Top Words by Category</h3>", unsafe_allow_html=True)
    
    def get_top_words(texts, n=10):
        """Extract top words from a series of texts"""
        # Join all texts
        all_text = " ".join(texts.astype(str)).lower()
        
        # Simple tokenization and counting (could be improved with nltk or spacy)
        words = all_text.split()
        # Filter out short words and common stopwords
        stopwords = ["the", "a", "and", "is", "in", "to", "of", "for", "with", "on", "at", "from", "by", "an", "this", "that", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them"]
        words = [word for word in words if len(word) > 3 and word.isalpha() and word not in stopwords]
        
        # Count words
        word_counts = pd.Series(words).value_counts().head(n)
        return word_counts
    
    # Create tabs for different word analyses
    word_tab1, word_tab2 = st.tabs(["Words by Rating", "Words by Sentiment"])
    
    with word_tab1:
        rating_cols = st.columns(len(rating_filter))
        
        for i, rating in enumerate(sorted(rating_filter)):
            with rating_cols[i % len(rating_cols)]:
                rating_df = filtered_df[filtered_df["Rating"] == rating]
                if len(rating_df) > 0:
                    top_words = get_top_words(rating_df["Text"])
                    
                    # Create bar chart
                    fig = px.bar(
                        x=top_words.values,
                        y=top_words.index,
                        orientation='h',
                        title=f"Top Words in {rating}-Star Reviews",
                        labels={"x": "Count", "y": "Word"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write(f"No {rating}-star reviews in the filtered data.")
    
    with word_tab2:
        sentiment_cols = st.columns(len(sentiment_filter))
        
        for i, sentiment in enumerate(sentiment_filter):
            with sentiment_cols[i % len(sentiment_cols)]:
                sentiment_df = filtered_df[filtered_df["Sentiment Category"] == sentiment]
                if len(sentiment_df) > 0:
                    top_words = get_top_words(sentiment_df["Text"])
                    
                    # Create bar chart
                    fig = px.bar(
                        x=top_words.values,
                        y=top_words.index,
                        orientation='h',
                        title=f"Top Words in {sentiment} Reviews",
                        labels={"x": "Count", "y": "Word"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write(f"No {sentiment} reviews in the filtered data.")

with tab4:
    st.markdown("<h2 class='section-header'>Advanced Analysis</h2>", unsafe_allow_html=True)
    
    # Correlation between sentiment and rating
    st.markdown("<h3 class='section-header'>Sentiment vs. Rating</h3>", unsafe_allow_html=True)
    
    # Create scatter plot
    fig = px.scatter(
        filtered_df,
        x="Rating",
        y="Sentiment",
        color="Sentiment Category",
        size="Rating",
        hover_data=["Park Name", "Text"],
        opacity=0.7,
        title="Correlation between Review Rating and Sentiment",
        color_discrete_map={"Positive": "#2ecc71", "Neutral": "#f1c40f", "Negative": "#e74c3c"}
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    # Park comparison
    st.markdown("<h3 class='section-header'>Park Comparison</h3>", unsafe_allow_html=True)
    
    # Allow selection of parks to compare
    top_parks = filtered_df["Park Name"].value_counts().head(20).index.tolist()
    selected_parks = st.multiselect(
        "Select parks to compare:",
        options=top_parks,
        default=top_parks[:3] if len(top_parks) >= 3 else top_parks
    )
    
    if selected_parks:
        # Filter data for selected parks
        parks_df = filtered_df[filtered_df["Park Name"].isin(selected_parks)]
        
        # Create comparison metrics
        comp_col1, comp_col2 = st.columns(2)
        
        with comp_col1:
            # Average ratings comparison
            avg_ratings = parks_df.groupby("Park Name")["Rating"].mean().reset_index()
            fig = px.bar(
                avg_ratings,
                x="Park Name",
                y="Rating",
                color="Park Name",
                title="Average Rating Comparison"
            )
            fig.update_layout(xaxis_title="Park", yaxis_title="Average Rating")
            st.plotly_chart(fig, use_container_width=True)
        
        with comp_col2:
            # Sentiment comparison
            sentiment_comp = pd.crosstab(
                parks_df["Park Name"], 
                parks_df["Sentiment Category"], 
                normalize="index"
            ).reset_index().melt(
                id_vars=["Park Name"],
                var_name="Sentiment",
                value_name="Percentage"
            )
            sentiment_comp["Percentage"] = sentiment_comp["Percentage"] * 100
            
            fig = px.bar(
                sentiment_comp,
                x="Park Name",
                y="Percentage",
                color="Sentiment",
                title="Sentiment Distribution Comparison",
                barmode="stack",
                color_discrete_map={"Positive": "#2ecc71", "Neutral": "#f1c40f", "Negative": "#e74c3c"}
            )
            fig.update_layout(xaxis_title="Park", yaxis_title="Percentage (%)")
            st.plotly_chart(fig, use_container_width=True)
        
        # Rating distribution by park
        rating_dist = pd.crosstab(
            parks_df["Park Name"],
            parks_df["Rating"]
        ).reset_index().melt(
            id_vars=["Park Name"],
            var_name="Rating",
            value_name="Count"
        )
        
        fig = px.bar(
            rating_dist,
            x="Park Name",
            y="Count",
            color="Rating",
            title="Rating Distribution by Park",
            barmode="group"
        )
        fig.update_layout(xaxis_title="Park", yaxis_title="Number of Reviews")
        st.plotly_chart(fig, use_container_width=True)
    
    # Time analysis (if date column exists in the data)
    if "Date" in df.columns:
        st.markdown("<h3 class='section-header'>Temporal Analysis</h3>", unsafe_allow_html=True)
        
        # Convert to datetime
        filtered_df["Date"] = pd.to_datetime(filtered_df["Date"])
        filtered_df["Month"] = filtered_df["Date"].dt.to_period("M")
        
        # Monthly trends
        monthly_ratings = filtered_df.groupby(filtered_df["Date"].dt.to_period("M"))["Rating"].mean().reset_index()
        monthly_ratings["Month"] = monthly_ratings["Date"].astype(str)
        
        fig = px.line(
            monthly_ratings,
            x="Month",
            y="Rating",
            markers=True,
            title="Average Rating Trend Over Time"
        )
        fig.update_layout(xaxis_title="Month", yaxis_title="Average Rating")
        st.plotly_chart(fig, use_container_width=True)

# Footer with information
st.markdown("""
---
<p class="info-text">This dashboard analyzes park reviews in Calgary. 
Use the sidebar filters to customize the view and the tabs to explore different aspects of the data.</p>
""", unsafe_allow_html=True)