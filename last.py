import streamlit as st
import base64
import requests
from textblob import TextBlob

# Hide Streamlit toolbar and viewer badge using CSS
hide_elements_css = """
<style>
[data-testid="stToolbar"], [data-testid="stText"] div:first-child {
    visibility: hidden !important;
}
</style>
"""

# Apply the CSS styles
st.markdown(hide_elements_css, unsafe_allow_html=True)

# Function to decode the complaint ID from the URL query parameters
def decode_complaint_id_from_url():
    # Decode complaint ID from the URL query parameters
    encoded_complaint_id = st.query_params().get('q')

    # Access the 'q' parameter, if present
    if encoded_complaint_id:
        try:
            # Decode the base64-encoded string to obtain the original complaint ID
            decoded_bytes = base64.b64decode(encoded_complaint_id)
            complaint_id = decoded_bytes.decode('utf-8')

            # Extract only the complaint ID value without the parameter name
            if complaint_id.startswith('complaintId='):
                complaint_id = complaint_id.replace('complaintId=', '')

            return complaint_id

        except Exception as e:
            st.error("Error decoding complaint ID. Please check the URL.")
            st.stop()

    # If 'q' parameter is not found
    st.error("Complaint ID not found in URL query parameters.")
    st.stop()

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
    ratings = {'Very Bad': 1.0, 'Bad': 2.5, 'Good': 4.0, 'Excellent': 5.0}
    return ratings.get(sentiment_category, 0.0)

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

    # API endpoint for production
    api_url = 'https://tracker.utlsolar.net/tracker/production/public/utlmtlapis/getCustomerFeedback'

    # Send POST request to the API
    try:
        response = requests.post(api_url, json=feedback_data)
        response.raise_for_status()  # Raise error for non-200 status codes

        # Check response and provide feedback to user
        if response.status_code == 200:
            st.success('Feedback submitted successfully!')
            # Show sentiment analysis results
            st.write('### Sentiment Analysis Results:')
            st.write(f'- **Service Engineer Sentiment:** {engineer_sentiment}')
            st.write(f'- **Service Executive Coordinator Sentiment:** {coordinator_sentiment}')
        else:
            st.error('Failed to submit feedback. Please try again later.')
    
    except requests.exceptions.RequestException as e:
        st.error(f'Error submitting feedback: {e}')

# Style and layout of the feedback form
def style_feedback_form(complaint_id):
    # Add logo with increased size
    logo_image = "https://imagizer.imageshack.com/img924/4894/eqE4eh.png"  # Path to your logo image
    st.image(logo_image, use_column_width=True, width=400)

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

