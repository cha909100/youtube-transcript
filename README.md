# YouTube Transcript Downloader

A Python application that retrieves video details and transcripts from a specified YouTube channel, summarises the content using OpenAI's GPT model, and saves the data in CSV and DOCX formats.

---

## **Features**
- Fetches video metadata (title, URL, upload date, likes, views) from a YouTube channel.
- Retrieves transcripts for videos using the YouTube Transcript API.
- Summarises transcripts and extracts key discussion points using OpenAI GPT.
- Saves video data to a CSV file.
- Exports summaries and key points to individual DOCX files.

---

## **Requirements**
1. **Python 3.7+**
2. **APIs**:
   - [YouTube Data API](https://developers.google.com/youtube/registering_an_application)
   - [YouTube Transcript API](https://pypi.org/project/youtube-transcript-api/)
   - [OpenAI GPT API](https://platform.openai.com/signup/)
3. **Dependencies**:
   - `google-api-python-client`
   - `youtube-transcript-api`
   - `python-docx`
   - `openai`

   
