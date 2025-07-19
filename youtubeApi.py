from googleapiclient.discovery import build #for building youtube api
from googleapiclient.errors import HttpError

yt_api_key = "AIzaSyBGs99uf_4CeicXoTp37qdYEoZXatKFApQ"
youtube = build('youtube','v3',developerKey = yt_api_key)

def clean_video_id(video_id):
    """Clean the video ID by removing any additional parameters"""
    # Split on first occurrence of '&' or '?' and take the first part
    video_id = video_id.split('&')[0]
    video_id = video_id.split('?')[0]
    # If the ID contains '=', take the part after it
    if '=' in video_id:
        video_id = video_id.split('=')[-1]
    return video_id
def fetch_video(video_id):
    try:
        clean_vid_id = clean_video_id(video_id)
        request = youtube.videos().list(
            part='snippet',
            id=clean_vid_id
        )
        response = request.execute()
        
        # Check if the response contains items
        if not response['items']:
            print(f"No video found with ID: {video_id}")
            return None
        
        video_details = response['items'][0]['snippet']
        return {
            'video_id': clean_vid_id,
            'title': video_details['title'],
            'thumbnail_url': video_details['thumbnails']['high']['url']
        }
    except HttpError as e:
        print(f"An error occurred: {e}")
        return None
    

# ans = fetch_video('dFsh2KYov8w')
# print(ans)