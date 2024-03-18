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

# Function to perform sentiment analysis using TextBlob
def perform_sentiment_analysis(review_text):
    sentiment_analysis = TextBlob(review_text).sentiment
    polarity_score = sentiment_analysis.polarity
    
    # Determine sentiment category based on polarity score
    if polarity_score <= -0.5:
        return 'Very Bad'
    elif polarity_score <= 0:
        return 'Bad'
    elif polarity_score <= 0.5:
        return 'Good'
    else:
        return 'Excellent'

# Function to derive ratings from sentiment polarity score
def derive_rating(sentiment_score):
    if sentiment_score == 'Very Bad':
        return 1.0
    elif sentiment_score == 'Bad':
        return 2.5
    elif sentiment_score == 'Good':
        return 4.0
    else:
        return 5.0

# Function to save feedback data to API
def save_feedback_to_api(complaint_id, engineer_review, engineer_rating, coordinator_review, coordinator_rating, engineer_sentiment, coordinator_sentiment):
    # Feedback data including complaint ID
    feedback_data = {
        'apiKey': 'RnVqaXlhbWEgUG93ZXIgU3lzdGVtcyBQdnQuIEx0ZC4=.$2y$10$sd9eji2d1mc8i1nd1xsalefYiroiLa46/X0U9ihoGeOU7FaWDg30a.',
        'complaint_id': complaint_id,
        'engineer_feedback': {
            'feedback': engineer_review,
            'rating': engineer_rating,
            'output': perform_sentiment_analysis(engineer_review)
        },
        'coordinator_feedback':  {
            'complaint_id': complaint_id,
            'feedback': coordinator_review,
            'rating': coordinator_rating,
            'output': perform_sentiment_analysis(coordinator_review)
        }
    }

    # API endpoint
    api_url = 'https://staging.utlsolar.net/tracker/production/public/utlmtlapis/getCustomerFeedback'

    # Make a POST request to the API endpoint
    response = requests.post(api_url, json=feedback_data)

    # Check if the request was successful
    if response.status_code == 200:
        st.success('Feedback submitted successfully!')
    else:
        st.error('Failed to submit feedback. Please try again later.')

# Function to decode complaint ID from URL query parameters
def decode_complaint_id():
    # Get the current URL
    current_url = st.query_params.get('current_url', '')

    # Split the URL to get the query string
    split_url = current_url.split("?")
    print("Split URL:", split_url)

    if len(split_url) == 2:
        # Get the query string and decode it
        decoded_url = base64.b64decode(split_url[1]).decode('utf-8')
        print("Decoded URL:", decoded_url)

        # Split the decoded URL to get the complaint ID
        complaint_str = decoded_url.split("=")
        print("Complaint String:", complaint_str)

        if len(complaint_str) == 2:
            complaint_id = complaint_str[1]
            return complaint_id

    # Return None if decoding fails or complaint ID not found
    return None

# Main function
def main():
    # Decode the complaint ID from URL query parameters
    complaint_id_decoded = decode_complaint_id()

    if complaint_id_decoded is not None:
        st.write("Decoded Complaint ID:", complaint_id_decoded)
    else:
        st.error("Error decoding complaint ID or complaint ID not found.")

# Run the main function
if __name__ == "__main__":
    main()



