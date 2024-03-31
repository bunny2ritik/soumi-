import streamlit as st
import requests
from textblob import TextBlob
import base64

# Function to submit feedback and handle API request
def submit_feedback(complaint_id, engineer_review, coordinator_review):
    # Perform sentiment analysis for engineer review
    engineer_sentiment = perform_sentiment_analysis(engineer_review)

    # Perform sentiment analysis for coordinator review
    coordinator_sentiment = perform_sentiment_analysis(coordinator_review)

    # Derive ratings from sentiment analysis
    engineer_rating = derive_rating(engineer_sentiment)
    coordinator_rating = derive_rating(coordinator_sentiment)

    # Save the feedback to the API database
    save_feedback_to_api(complaint_id, engineer_review, engineer_rating, coordinator_review, coordinator_rating, engineer_sentiment, coordinator_sentiment)
    
    # Display sentiment analysis results
    st.header('Sentiment Analysis Results:')
    st.write('Service Engineer Review Sentiment:', engineer_sentiment)
    st.write('Service Executive Coordinator Review Sentiment:', coordinator_sentiment)

# Function to decode the complaint ID from the URL query parameters
# Function to perform sentiment analysis using TextBlob
# Remaining functions stay the same as before

# Read the URL query parameters
url_query = st.experimental_get_query_params()

# Decode the complaint ID from the URL query parameters
complaint_id_decoded = decode_complaint_id_from_url(url_query)

if not complaint_id_decoded:
    st.error("Complaint ID not found in URL query parameters")
    st.stop()

# Style the feedback form
def style_feedback_form(complaint_id):
    # Remaining code for styling the feedback form stays the same

# Style the feedback form
engineer_review, coordinator_review = style_feedback_form(complaint_id_decoded)

# Remaining code for the submit button and feedback submission process remains the same

# Submit feedback and handle API request
if submit_button:
    # Submit feedback and handle API request
    if complaint_id_decoded:
        submit_feedback(complaint_id_decoded, engineer_review, coordinator_review)
