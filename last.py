import streamlit as st
import base64
import requests
from textblob import TextBlob

# Add custom CSS to hide Streamlit elements except the submit button
hide_elements_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            div.stButton>button {
                visibility: visible !important;
            }
            div.stDocument > div.stApp > div:nth-child(1) > div:nth-child(2) > div {
                visibility: hidden;
            }
            a[href^="https://github.com/streamlit/"][class^="stAppGotoGithubButton"] {
                display: none !important;
            }
            </style>
            """
st.markdown(hide_elements_style, unsafe_allow_html=True) 

# Function to decode the complaint ID from the URL query parameters
def decode_complaint_id_from_url():
    query_params = st.experimental_get_query_params()
    if 'q' in query_params:
        encoded_complaint_id = query_params['q'][0]
        try:
            decoded_bytes = base64.b64decode(encoded_complaint_id)
            complaint_id = decoded_bytes.decode('utf-8')
            if complaint_id.startswith('complaintId='):
                complaint_id = complaint_id.replace('complaintId=', '')
            return complaint_id
        except Exception as e:
            st.error(f"Error decoding complaint ID: {e}")
            return None
    return None

# Function to perform sentiment analysis using TextBlob
def perform_sentiment_analysis(review_text):
    sentiment_analysis = TextBlob(review_text).sentiment
    polarity_score = sentiment_analysis.polarity
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
    else:
        return 5.0

# Function to submit feedback and handle API request
def submit_feedback(complaint_id, engineer_review, coordinator_review):
    engineer_sentiment = perform_sentiment_analysis(engineer_review)
    engineer_rating = derive_rating(engineer_sentiment)
    coordinator_sentiment = perform_sentiment_analysis(coordinator_review)
    coordinator_rating = derive_rating(coordinator_sentiment)
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
    api_url = 'https://tracker.utlsolar.net/tracker/production/public/utlmtlapis/getCustomerFeedback'
    response = requests.post(api_url, json=feedback_data)
    if response.status_code == 200:
        return True, engineer_sentiment, coordinator_sentiment
    else:
        return False, None, None

# Style and layout of the feedback form
def style_feedback_form(complaint_id):
    logo_image = "https://imagizer.imageshack.com/img924/4894/eqE4eh.png"
    st.image(logo_image, use_column_width=True, width=400)
    st.markdown(f"<h3 style='text-align: center;'>Feedback for Complaint ID: {complaint_id}</h3>", unsafe_allow_html=True)
    st.header('Service Engineer')
    engineer_review = st.text_area('Write your feedback for the Service Engineer here:')
    st.header('Service Executive Coordinator')
    coordinator_review = st.text_area('Write your feedback for the Service Executive Coordinator here:')
    return engineer_review, coordinator_review

# Main application code
def main():
    query_params = st.experimental_get_query_params()
    if 'tab' in query_params and query_params['tab'] == ['results']:
        if 'engineer_sentiment' in st.session_state and 'coordinator_sentiment' in st.session_state:
            st.success('Feedback submitted successfully!')
            st.write('### Thank you for your valuable feedback!')
            st.write('### Sentiment Analysis Results:')
            st.write(f'- **Service Engineer Sentiment:** {st.session_state.engineer_sentiment}')
            st.write(f'- **Service Executive Coordinator Sentiment:** {st.session_state.coordinator_sentiment}')
        else:
            st.error('No feedback data available.')
    else:
        complaint_id_decoded = decode_complaint_id_from_url()
        if complaint_id_decoded:
            feedback_submitted = False
            if 'feedback_submitted' in st.session_state:
                feedback_submitted = st.session_state.feedback_submitted
            
            if not feedback_submitted:
                engineer_review, coordinator_review = style_feedback_form(complaint_id_decoded)
                submit_button = st.button('Submit')
                if submit_button:
                    success, engineer_sentiment, coordinator_sentiment = submit_feedback(complaint_id_decoded, engineer_review, coordinator_review)
                    if success:
                        st.session_state.feedback_submitted = True
                        st.session_state.engineer_sentiment = engineer_sentiment
                        st.session_state.coordinator_sentiment = coordinator_sentiment
                        st.experimental_set_query_params(tab='results')
                        st.experimental_rerun()
                    else:
                        st.error('Failed to submit feedback. Please try again later.')
        else:
            st.error("Complaint ID not found in URL query parameters.")

if __name__ == "__main__":
    main()
