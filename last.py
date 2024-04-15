import streamlit as st
import base64
import requests
from textblob import TextBlob

# Function to decode a base64-encoded string from a URL query parameter
def decode_q_parameter():
    # Get query parameters from the URL
    query_params = st.experimental_get_query_params()

    # Check if 'q' parameter is present in query parameters
    if 'q' in query_params:
        # 'q' parameter value is returned as a list, so we take the first element
        encoded_q_param = query_params['q'][0]

        try:
            # Base64-decode the 'q' parameter
            decoded_bytes = base64.b64decode(encoded_q_param)
            decoded_q = decoded_bytes.decode('utf-8')

            # Store the decoded parameter in session state
            st.session_state.decoded_q = decoded_q

            # Redirect the user to remove the query parameter from the URL
            st.experimental_rerun()

        except Exception as e:
            # Error handling for decoding issues
            st.error(f"Error decoding 'q' parameter: {str(e)}. Ensure the 'q' parameter contains a valid base64-encoded value.")
            return None
    else:
        # Error message if 'q' parameter is not found in query parameters
        st.error("Query parameter 'q' not found in URL. Ensure the URL contains a base64-encoded 'q' parameter.")
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
def submit_feedback(decoded_q, engineer_review, coordinator_review):
    # Perform sentiment analysis for engineer review
    engineer_sentiment = perform_sentiment_analysis(engineer_review)
    engineer_rating = derive_rating(engineer_sentiment)

    # Perform sentiment analysis for coordinator review
    coordinator_sentiment = perform_sentiment_analysis(coordinator_review)
    coordinator_rating = derive_rating(coordinator_sentiment)

    # API data to submit feedback
    feedback_data = {
        'apiKey': 'RnVqaXlhbWEgUG93ZXIgU3lzdGVtcyBQdnQuIEx0ZC4=.$2y$10$sd9eji2d1mc8i1nd1xsalefYiroiLa46/X0U9ihoGeOU7FaWDg30a',
        'decoded_q': decoded_q,
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

    # Check response and provide feedback to the user
    if response.status_code == 200:
        st.success('Feedback submitted successfully!')
    else:
        st.error(f'Failed to submit feedback. HTTP status code: {response.status_code}. Please try again later.')

# Style and layout of the feedback form
def style_feedback_form():
    # Add logo
    logo_image = "https://github.com/bunny2ritik/Utl-feedback/blob/main/newlogo.png?raw=true"
    st.image(logo_image, use_column_width=True, width=400)

    # Display title for the decoded 'q' parameter
    decoded_q = st.session_state.get('decoded_q')
    st.markdown(f"<h3 style='text-align: center;'>Feedback for Complaint ID: {decoded_q}</h3>", unsafe_allow_html=True)

    # Engineer review input
    st.header('Service Engineer')
    engineer_review = st.text_area('Write your feedback for the Service Engineer here:')

    # Coordinator review input
    st.header('Service Executive Coordinator')
    coordinator_review = st.text_area('Write your feedback for the Service Executive Coordinator here:')

    return engineer_review, coordinator_review

# Main application code
def main():
    # Check if the decoded 'q' parameter is already in session state
    if 'decoded_q' not in st.session_state:
        # Decode 'q' parameter from the URL query parameters
        decode_q_parameter()

    # If the decoded 'q' parameter is available in session state, proceed with the form
    if 'decoded_q' in st.session_state:
        # Style the feedback form
        engineer_review, coordinator_review = style_feedback_form()
        
        # Add a submit button
        submit_button = st.button('Submit')

        # If the submit button is clicked, handle the submission
        if submit_button:
            submit_feedback(st.session_state.decoded_q, engineer_review, coordinator_review)

# Run the Streamlit app
if __name__ == "__main__":
    main()
