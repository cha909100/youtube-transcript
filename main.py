import os
import csv
import re
from datetime import datetime
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from docx import Document
from openai import OpenAI

# Set up the environment for OpenAI API
api_key = os.environ.get("YOUTUBE_API_KEY")  # Securely fetching the API key from environment variables
openai_api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

def get_channel_details(youtube, channel_id):
    """Retrieve details of a YouTube channel by ID."""
    response = youtube.channels().list(id=channel_id, part='snippet').execute()
    if not response.get('items'):
        return None
    return response['items'][0]['snippet']

def list_all_videos(api_key, channel_id):
    """List all videos from a YouTube channel and retrieve their transcripts and statistics."""
    youtube = build('youtube', 'v3', developerKey=api_key)
    videos = []
    count = 1

    channel_info = get_channel_details(youtube, channel_id)
    if not channel_info:
        return None, "Channel not found"

    channel_name = channel_info['title']
    uploads_playlist_id = channel_info['relatedPlaylists']['uploads']
    request = youtube.playlistItems().list(playlistId=uploads_playlist_id, part='snippet,contentDetails', maxResults=50)
    while request:
        response = request.execute()
        video_ids = [item['contentDetails']['videoId'] for item in response['items']]
        video_details_response = youtube.videos().list(id=','.join(video_ids), part='snippet,statistics').execute()
        for item in video_details_response['items']:
            video_id = item['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_title = item['snippet']['title']
            video_date = datetime.strptime(item['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d')
            likes = item['statistics'].get('likeCount', 'No likes data')
            views = item['statistics'].get('viewCount', 'No views data')
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                combined_text = ' '.join([entry['text'] for entry in transcript])
                summary, points = summarize_and_extract_points(combined_text)
                videos.append((count, video_title, video_url, video_date, likes, views, summary, points))
            except:
                videos.append((count, video_title, video_url, video_date, likes, views, "No transcript available", []))
            count += 1
        request = youtube.playlistItems().list_next(request, response)
    return videos, channel_name

def summarize_and_extract_points(text):
    """Generate a summary and key discussion points from a text using OpenAI's GPT model."""
    response = client.Completion.create(prompt=f"Summarize this text and provide 3-5 key discussion points: {text}", model="text-davinci-002", max_tokens=150)
    summary = response.choices[0].text.strip()
    points = summary.split('\n')[1:]  # Assuming points are returned in new lines after the summary
    return summary.split('\n')[0], points

def save_videos_to_csv(videos, filename):
    """Save video data to a CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['No.', 'Video Title', 'Video URL', 'Upload Date', 'Likes', 'Views', 'Summary', 'Discussion Points'])
        for video in videos:
            writer.writerow(video)

def save_summary_to_docx(videos, directory="summaries", prefix="OPENAI"):
    """Save video summaries and discussion points to DOCX files with a specified prefix."""
    if not os.path.exists(directory):
        os.makedirs(directory)
    for video in videos:
        doc = Document()
        doc.add_heading(video[1], 0)
        doc.add_paragraph(video[6])
        doc.add_heading('Discussion Points', level=1)
        for point in video[7]:
            doc.add_paragraph(point, style='ListBullet')
        filename = f"{prefix}_{re.sub(r'[\\/*?:"<>|]', '', video[1])}.docx"
        doc.save(os.path.join(directory, filename))

# Example usage setup
youtube_api_key = input("Please enter your YouTube API key: ")
youtube = build('youtube', 'v3', developerKey=youtube_api_key)
channel_url = input("Please enter the YouTube channel URL: ")
channel_id = get_channel_id(youtube, channel_url)
if channel_id:
    video_list, channel_name = list_all_videos(youtube_api_key, channel_id)
    if video_list:
        csv_filename = f"{channel_name.replace(' ', '_')}.csv"
        save_videos_to_csv(video_list, csv_filename)
        save_summary_to_docx(video_list)
    else:
        print("No videos found or channel not accessible.")
else:
    print("Channel ID not found.")
