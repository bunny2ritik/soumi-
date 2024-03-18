import streamlit as st
import base64

# Function to decode complaint ID from URL query parameters
def decode_complaint_id():
    # Get the current URL
    current_url = st.query_params.get('current_url', '')

    # Print the current URL for debugging
    print("Current URL:", current_url)

    # Check if the current URL is empty or doesn't contain query parameters
    if not current_url:
        st.error("Invalid URL format: URL is empty.")
        return None

    # Split the URL to get the query string
    split_url = current_url.split("?")

    if len(split_url) == 2:
        # Get the query string and decode it
        query_string = split_url[1]
        try:
            decoded_query = base64.b64decode(query_string).decode('utf-8')
            print("Decoded Query:", decoded_query)
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
    else:
        st.error("Error decoding complaint ID or complaint ID not found.")

# Run the main function
if __name__ == "__main__":
    main()
