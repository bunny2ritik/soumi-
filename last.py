import streamlit as st
import base64
import requests
from textblob import TextBlob

# Function to decode the complaint ID from the URL query parameters
def decode_complaint_id_from_url():
    # Get query parameters from the URL
    query_params = st.experimental_get_query_params()

    # Base64-encoded parameter key for 'complaintid'
    param_key_encoded = 'Y29tcGxhaW50aWQ='

    # Decode the base64 encoded parameter key to 'complaintid'
    param_key = base64.b64decode(param_key_encoded).decode('utf-8')

    # Access the parameter using the decoded key
    if param_key in query_params:
        # The parameter value is returned as a list, so we take the first element
        encoded_complaint_id = query_params[param_key][0]

        try:
            # Decode the base64-encoded string to obtain the original complaint ID
            decoded_bytes = base64.b64decode(encoded_complaint_id)
            complaint_id = decoded_bytes.decode('utf-8')
            return complaint_id

        except Exception as e:
            st.error(f"Error decoding complaint ID: {e}")
            return None

    # If parameter is not found, or if there is an error decoding the ID
    st.error("Complaint ID not found in URL query parameters.")
    return None

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

# Function to derive ratings from sentiment categories
def derive_rating(sentiment_category):
    if sentiment_category == 'Very Bad':
        return 1.0
    elif sentiment_category == 'Bad':
        return 2.5
    elif sentiment_category == 'Good':
        return 4.0
    else:  # 'Excellent'
        return 5.0

# Function to submit feedback and handle API request
def submit_feedback(complaint_id, engineer_review, coordinator_review):
    # Perform sentiment analysis for engineer review
    engineer_sentiment = perform_sentiment_analysis(engineer_review)
    engineer_rating = derive_rating(engineer_sentiment)

    # Perform sentiment analysis for coordinator review
    coordinator_sentiment = perform_sentiment_analysis(coordinator_review)
    coordinator_rating = derive_rating(coordinator_sentiment)

    # API data to submit feedback
    feedback_data = {
        'apiKey': 'RnVqaXlhbWEgUG93ZXIgU3lzdGVtcyBQdnQuIEx0ZC4=.$2y$10$sd9eji2d1mc8i1nd1xsalefYiroiLa46/X0U9ihoGeOU7FaWDg30a.',
        'complaint_id': complaint_id,
        'engineer_feedback': {
            'feedback': engineer_review,
            'rating': engineer_rating,
            'output': engineer_sentiment
        },
        'coordinator_feedback': {
            'feedback': coordinator_review,
            'rating': coordinator_rating,
            'output': coordinator_sentiment
        }
    }

    # API endpoint
    api_url = 'https://staging.utlsolar.net/tracker/production/public/utlmtlapis/getCustomerFeedback'

    # Send POST request to the API
    response = requests.post(api_url, json=feedback_data)

    # Check response and provide feedback to user
    if response.status_code == 200:
        st.success('Feedback submitted successfully!')
    else:
        st.error('Failed to submit feedback. Please try again later.')

# Style and layout of the feedback form
def style_feedback_form(complaint_id):
    # Add logo
    logo_image = "https://github.com/bunny2ritik/Utl-feedback/blob/main/newlogo.png?raw=true"  # Path to your logo image
    st.image(logo_image, use_column_width=True)

    # Display the title for the complaint ID
    st.markdown(f"<h3 style='text-align: center;'>Feedback for Complaint ID: {complaint_id}</h3>", unsafe_allow_html=True)

    # Engineer review input
    st.header('Service Engineer')
    engineer_review = st.text_area('Write your feedback for the Service Engineer here:')

    # Coordinator review input
    st.header('Service Executive Coordinator')
    coordinator_review = st.text_area('Write your feedback for the Service Executive Coordinator here:')

    return engineer_review, coordinator_review

# Main application code
def main():
    # Decode complaint ID from the URL query parameters
    complaint_id_decoded = decode_complaint_id_from_url()

    # Ensure complaint_id_decoded is not None before proceeding
    if complaint_id_decoded:
        # Style the feedback form
        engineer_review, coordinator_review = style_feedback_form(complaint_id_decoded)
        
        # Add a submit button
        submit_button = st.button('Submit')

        # If the submit button is clicked, handle the submission
        if submit_button:
            submit_feedback(complaint_id_decoded, engineer_review, coordinator_review)

# Run the Streamlit app
if __name__ == "__main__":
    main()
