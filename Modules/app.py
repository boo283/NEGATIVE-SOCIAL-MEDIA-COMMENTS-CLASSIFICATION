import streamlit as st
import pandas as pd
import plotly.express as px
import json
from kafka import KafkaConsumer
from producer import get_data, produce_comments, create_producer
import threading
import queue
import time
from classification import predict

threshold = 150  # Base on the Internet speed (300 - 400)
ite = 15  # Use to check whether it reaches the end of the page (Should be 20 - 30)

# Function to add custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Apply custom CSS
local_css("style.css")

# DataFrame to store comments
if 'comments_df' not in st.session_state:
    st.session_state['comments_df'] = pd.DataFrame(columns=['id', 'text', 'tag_name', 'is_spam', 'label', 'username'])

# Set to track processed message ids
processed_ids = set()

# Queue to hold comments from consumer thread
comment_queue = queue.Queue()

def consume_classified_comments():
    consumer = KafkaConsumer(
        'StreamComments',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='streamlit-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    for message in consumer:
        comment = message.value
        print(comment)
        comment_id = comment['id']
        prediction = predict(comment["text"])
        
        pred = ''
        if prediction == 0:
            pred = "Others"
        elif prediction == 1:
            pred = "Hate speech"
        elif prediction == 2:
            pred = "Personal attack"
        else:
            pred = "Discrimination"

        comment["label"] = pred
        if comment_id not in processed_ids:
            comment_queue.put(comment)
            processed_ids.add(comment_id)

def update_comments_from_queue():
    while not comment_queue.empty():
        comment = comment_queue.get()
        comment_df = pd.DataFrame([comment])
        st.session_state['comments_df'] = pd.concat([st.session_state['comments_df'], comment_df], ignore_index=True)

# Initialize Streamlit app
st.title("Facebook Comment Classification")

# Input for Facebook post URL
with st.sidebar:
    url = st.text_input("Enter the Facebook post URL")
    username = st.text_input("Enter your Facebook username")
    password = st.text_input("Enter your Facebook password", type="password")

    if st.button("Fetch and Analyze Comments"):
        if url and username and password:
            with st.spinner('Fetching and analyzing comments...'):
                data, cnt = get_data(url, username, password, threshold, ite)

                producer = create_producer()

                # Start consumer thread
                consumer_thread = threading.Thread(target=consume_classified_comments, daemon=True)
                consumer_thread.start()

                # Start producer to send comments to Kafka
                st.write("Starting to produce comments...")
                produce_comments(producer, data)

                st.success("Fetching and analyzing complete.")
        else:
            st.error("Please enter all required fields.")

# Update comments from queue
update_comments_from_queue()

# Layout for displaying comments and charts
if not st.session_state['comments_df'].empty:
    # Comment and Sentiment Distribution
    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("Total Comments:", st.session_state['comments_df'].shape[0])
        # Display limited number of comments with pagination and limited columns
        comments_per_page = 5
        total_comments = len(st.session_state['comments_df'])
        total_pages = (total_comments // comments_per_page) + 1
        page = st.number_input('Page', min_value=1, max_value=total_pages, step=1)
        start_idx = (page - 1) * comments_per_page
        end_idx = start_idx + comments_per_page
        comments_display = st.session_state['comments_df'][['id', 'text', 'label', 'username']].iloc[start_idx:end_idx]
        st.table(comments_display)

        with st.expander("Show more details"):
            st.table(st.session_state['comments_df'][['id', 'text', 'tag_name', 'is_spam', 'label', 'username']])

    with col2:
        st.write("Comment Sentiment Distribution:")
        sentiment_counts = st.session_state['comments_df']['label'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        fig = px.pie(sentiment_counts, names='Sentiment', values='Count',
                     title='Distribution of Comments',
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(
            legend=dict(
                font=dict(size=13)
            )
        )
        st.plotly_chart(fig)

    st.write("---")

    # Top 3 usernames with the most negative comments by label
    st.write("Top 3 usernames with the most negative comments by label:")
    negative_labels = ["Hate speech", "Personal attack", "Discrimination"]
    top_users = (
        st.session_state['comments_df'][st.session_state['comments_df']['label'].isin(negative_labels)]
        .groupby(['username', 'label'])
        .size()
        .reset_index(name='count')
        .sort_values(by=['label', 'count'], ascending=[True, False])
        .groupby('label')
        .head(3)
    )
    st.table(top_users)

    st.write("---")

    # Interactive chart to show comments by username
    st.write("Comments by Username:")
    user_comment_counts = st.session_state['comments_df']['username'].value_counts().reset_index()
    user_comment_counts.columns = ['username', 'count']

    selected_user = st.selectbox('Select a username to view comments', user_comment_counts['username'])

    if selected_user:
        user_comments = st.session_state['comments_df'][st.session_state['comments_df']['username'] == selected_user].head(10)
        st.write(f"Comments by {selected_user}:")
        st.table(user_comments)
        
    limit = st.number_input('Enter the number of users to display', min_value=1, value=15)
    user_fig = px.bar(user_comment_counts.head(limit), x='username', y='count', title=f'Top {limit} Comments by Username',
                      color='count', color_continuous_scale=px.colors.sequential.Viridis)
    st.plotly_chart(user_fig)

    st.write("---")

    # Spam comment statistics
    st.write("Spam Comment Statistics:")
    spam_count = st.session_state['comments_df'][st.session_state['comments_df']['is_spam'] == 1].shape[0]
    total_count = st.session_state['comments_df'].shape[0]
    spam_data = pd.DataFrame({
        'Type': ['Spam', 'Non-Spam'],
        'Count': [spam_count, total_count - spam_count]
    })
    spam_fig = px.pie(spam_data, names='Type', values='Count', title='Spam vs Non-Spam Comments',
                      color_discrete_sequence=px.colors.qualitative.Set3)
    spam_fig.update_layout(
            legend=dict(
                font=dict(size=20)
            )
        )
    st.plotly_chart(spam_fig)

    st.write("---")

    # List usernames with spam comments
    st.write("Usernames with Spam Comments and Their Content:")
    spam_comments = st.session_state['comments_df'][st.session_state['comments_df']['is_spam'] == 1][['username', 'text']]
    st.table(spam_comments)
