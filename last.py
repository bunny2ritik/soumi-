import streamlit as st
import base64
import requests
from textblob import TextBlob

# Function to adjust padding and decode a base64-encoded string
def decode_base64(encoded_string):
    # Calculate required padding
    padding_needed = 4 - len(encoded_string) % 4
    # Add required padding
    if padding_needed < 4:
        encoded_string += "=" * padding_needed
    # Decode the base64-encoded string
    decoded_bytes = base64.b64decode(encoded_string)
    return decoded_bytes.decode('utf-8')

# Function to decode the encoded query parameter name and value from the URL
def decode_encoded_query_parameter():
    # Get query parameters from the URL
    query_params = st.experimental_get_query_params()

    # Iterate over query parameters to find the encoded query parameter name
    for encoded_param_name, param_value in query_params.items():
        try:
            # Decode the encoded query parameter name using the decode_base64 function
            decoded_param_name = decode_base64(encoded_param_name)

            # Check if the decoded query parameter name is 'complaintId'
            if decoded_param_name == 'complaintId':
                # Decode the encoded parameter value using the decode_base64 function
                encoded_complaint_id = param_value[0]
                decoded_complaint_id = decode_base64(encoded_complaint_id)

                # Store the decoded complaint ID in session state
                st.session_state.decoded_complaint_id = decoded_complaint_id

                # Redirect the user to remove the query parameter from the URL
                st.experimental_rerun()

        except Exception as e:
            # Error handling for decoding issues
            st.error(f"Error decoding encoded query parameter name or value: {str(e)}. Ensure the query parameter name and value are base64-encoded and valid.")
            return None
    else:
        # Error message if 'complaintId' is not found in URL query parameters
        st.error("Query parameter 'complaintId' not found in URL. Ensure the URL contains a base64-encoded 'complaintId' parameter.")
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
def submit_feedback(decoded_complaint_id, engineer_review, coordinator_review):
    # Perform sentiment analysis for engineer review
    engineer_sentiment = perform_sentiment_analysis(engineer_review)
    engineer_rating = derive_rating(engineer_sentiment)

    # Perform sentiment analysis for coordinator review
    coordinator_sentiment = perform_sentiment_analysis(coordinator_review)
    coordinator_rating = derive_rating(coordinator_sentiment)

    # API data to submit feedback
    feedback_data = {
        'apiKey': 'RnVqaXlhbWEgUG93ZXIgU3lzdGVtcyBQdnQuIEx0ZC4=.$2y$10$sd9eji2d1mc8i1nd1xsalefYiroiLa46/X0U9ihoGeOU7FaWDg30a',
        'complaint_id': decoded_complaint_id,
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

    # Display title for the decoded 'complaintId' parameter
    decoded_complaint_id = st.session_state.get('decoded_complaint_id')
    st.markdown(f"<h3 style='text-align: center;'>Feedback for Complaint ID: {decoded_complaint_id}</h3>", unsafe_allow_html=True)

    # Engineer review input
    st.header('Service Engineer')
    engineer_review = st.text_area('Write your feedback for the Service Engineer here:')

    # Coordinator review input
    st.header('Service Executive Coordinator')
    coordinator_review = st.text_area('Write your feedback for the Service Executive Coordinator here:')

    return engineer_review, coordinator_review

# Main application code
def main():
    # Check if the decoded 'complaintId' parameter is already in session state
    if 'decoded_complaint_id' not in st.session_state:
        # Decode 'complaintId' parameter from the URL query parameters
        decode_encoded_query_parameter()

    # If the decoded 'complaintId' parameter is available in session state, proceed with the form
    if 'decoded_complaint_id' in st.session_state:
        # Style the feedback form
        engineer_review, coordinator_review = style_feedback_form()
        
        # Add a submit button
        submit_button = st.button('Submit')

        # If the submit button is clicked, handle the submission
        if submit_button:
            submit_feedback(st.session_state.decoded_complaint_id, engineer_review, coordinator_review)

# Run the Streamlit app
if __name__ == "__main__":
    main()

