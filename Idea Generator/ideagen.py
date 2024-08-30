import praw
from praw.exceptions import RedditAPIException
import time

# Initialize with your credentials
reddit = praw.Reddit(
    client_id='CLIENT_ID',
    client_secret='CLIENT_SECRET',
    user_agent='Platform:AppID:Version (by /u/USERNAME) ',
)

# Select the subreddit to scrape
subreddit = reddit.subreddit('sidehustle')

# Open a text file to write the post contents and comments
with open('sidehustle_posts_with_comments.txt', 'w', encoding='utf-8') as file:

    try:
        # Fetch the top 10 hot posts from the subreddit
        for post in subreddit.hot(limit=50):
            # Write the post details to the file
            file.write(f"Title: {post.title}\n")
            file.write(f"Score: {post.score}\n")
            file.write(f"Upvote Ratio: {post.upvote_ratio}\n")
            file.write(f"ID: {post.id}\n")
            file.write(f"URL: {post.url}\n")
            file.write(f"Comments: {post.num_comments}\n")
            file.write(f"Created: {post.created_utc}\n")
            file.write(f"Author: {post.author}\n")

            # Check if the post is a text post and write its body content
            if post.selftext:
                file.write(f"Content: {post.selftext}\n")
            else:
                file.write("Content: [Link Post - No Text Content]\n")

            # Fetch and write the comments
            file.write("Comments:\n")
            post.comments.replace_more(limit=0)  # Remove "MoreComments" objects for easier traversal
            for comment in post.comments.list():
                file.write(f"Comment by {comment.author}: {comment.body}\n")
                file.write(f"Score: {comment.score}\n")
                file.write(f"Created: {comment.created_utc}\n")
                file.write("-" * 40 + "\n")  # Separator between comments

            # Add a separator between posts
            file.write("="*80 + "\n\n")

            # Sleep for 2 seconds between requests to comply with rate limits
            time.sleep(2)

    except RedditAPIException as e:
        print(f"An error occurred: {e}")

print("Scraping complete. The posts and comments have been saved to 'sidehustle_posts_with_comments.txt'.")
