import streamlit as st
import requests
from textblob import TextBlob
import base64
from urllib.parse import urlparse, parse_qs

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

    # Check if the current URL is empty
    if not current_url:
        st.error("URL is empty. Please make sure to provide a valid URL with query parameters.")
        return None

    # Split the URL to get the query string
    split_url = current_url.split("?")

    if len(split_url) == 2:
        # Get the query string and decode it
        query_string = split_url[1]
        try:
            decoded_query = base64.b64decode(query_string).decode('utf-8')
            complaint_id = decoded_query.split('=')[1]
            return complaint_id
        except Exception as e:
            st.error("Error decoding query string: {}".format(e))
            return None
    else:
        st.error("Invalid URL format: Query parameters not found.")
        return None

# Main function
def main():
    # Decode the complaint ID from URL query parameters
    complaint_id_decoded = decode_complaint_id()

    if complaint_id_decoded is not None:
        st.write("Decoded Complaint ID:", complaint_id_decoded)

        # Style the feedback form
        engineer_review, coordinator_review = style_feedback_form(complaint_id_decoded)

        # Add a submit button with custom style
        submit_button_style = """
            <style>
                div.stButton > button:first-child {
                    background-color: #4CAF50; /* Green */
                    color: white;
                }
            </style>
        """

        # Inject the submit button style into the Streamlit app
        st.markdown(submit_button_style, unsafe_allow_html=True)

        # Add a submit button
        submit_button = st.button('Submit')

        # Submit feedback and handle API request
        if submit_button:
            submit_feedback(complaint_id_decoded, engineer_review, coordinator_review)

# Function to style the feedback form
def style_feedback_form(complaint_id):
    # Add logo with increased size
    logo_image = "https://github.com/bunny2ritik/Utl-feedback/blob/main/newlogo.png?raw=true"  # Path to your logo image
    st.image(logo_image, use_column_width=True, width=400)
    
    # Display the title for the complaint ID without quotation marks
    st.markdown(f"<h3 style='text-align: center;'>Feedback for Complaint ID : {complaint_id}</h3>", unsafe_allow_html=True)

    # Set title for service engineer section
    st.header('Service Engineer ')

    # Add text area for engineer feedback
    engineer_review = st.text_area('Write your feedback for the Service Engineer here:')

    # Set title for service coordinator section
    st.header('Service Executive Coordinator' )

    # Add text area for coordinator feedback
    coordinator_review = st.text_area('Write your feedback for the Service Executive Coordinator here:')

    return engineer_review, coordinator_review

# Run the main function
if __name__ == "__main__":
    main()


