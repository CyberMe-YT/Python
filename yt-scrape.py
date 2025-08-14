from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta, timezone
import dateutil.parser

API_KEY = "<GOOGLE_API_KEY>"  # Replace with your API key
CHANNELS_FILE = "/files/channels.txt"  # File with comma-separated channel IDs

youtube = build("youtube", "v3", developerKey=API_KEY)

# Define 6 months ago as timezone-aware datetime in UTC
six_months_ago = datetime.now(timezone.utc) - timedelta(days=30*6)

def get_uploads_playlist(channel_id):
    try:
        channel_info = youtube.channels().list(
            id=channel_id,
            part="contentDetails"
        ).execute()
    except HttpError as e:
        print(f"API error fetching channel {channel_id}: {e}")
        return None

    if "items" not in channel_info or len(channel_info["items"]) == 0:
        print(f"Warning: No channel found with ID: {channel_id}")
        return None

    return channel_info["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

def get_videos_from_playlist(playlist_id):
    videos_data = []
    next_page_token = None

    while True:
        try:
            videos = youtube.playlistItems().list(
                playlistId=playlist_id,
                part="snippet,contentDetails",
                maxResults=50,
                pageToken=next_page_token
            ).execute()
        except HttpError as e:
            print(f"API error fetching playlist {playlist_id}: {e}")
            break

        video_ids = [item["contentDetails"]["videoId"] for item in videos["items"]]

        if not video_ids:
            break

        try:
            stats_response = youtube.videos().list(
                id=",".join(video_ids),
                part="statistics,snippet"
            ).execute()
        except HttpError as e:
            print(f"API error fetching video stats: {e}")
            break

        for video in stats_response.get("items", []):
            title = video["snippet"]["title"]
            views = int(video["statistics"].get("viewCount", 0))

            # Parse published date as aware datetime
            published_at = dateutil.parser.isoparse(video["snippet"]["publishedAt"])

            if published_at >= six_months_ago:
                videos_data.append((title, views, published_at))

        next_page_token = videos.get("nextPageToken")
        if not next_page_token:
            break

    return videos_data

def main():
    try:
        with open(CHANNELS_FILE, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"File '{CHANNELS_FILE}' not found.")
        return

    channel_ids = [cid.strip() for cid in content.split(",") if cid.strip()]

    all_videos = []

    for channel_id in channel_ids:
        print(f"Processing channel: {channel_id}")
        uploads_playlist = get_uploads_playlist(channel_id)
        if not uploads_playlist:
            print(f"Skipping channel {channel_id} due to missing uploads playlist.")
            continue
        channel_videos = get_videos_from_playlist(uploads_playlist)
        all_videos.extend(channel_videos)

    if not all_videos:
        print("No recent videos found for the provided channels.")
        return

    # Sort combined list by views descending
    all_videos.sort(key=lambda x: x[1], reverse=True)

    print("\n=== Videos from the last 6 months sorted by views (descending) ===\n")
    for title, views, published_at in all_videos:
        pub_date_str = published_at.strftime("%Y-%m-%d")
        print(f"{title} - {views} views - Published on {pub_date_str}")

if __name__ == "__main__":
    main()
