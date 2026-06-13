import streamlit as st
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
from urllib.parse import urlparse, parse_qs

# 1. Page Configuration
st.set_page_config(page_title="Bulletproof YouTube Quizzer", page_icon="🎓", layout="centered")
st.title("🎓 Bulletproof YouTube Lecture Quizzer")
st.write("Generates quizzes using Transcripts. If transcripts are disabled, it automatically scans Title, Description, and Comments so it never fails!")

# 2. Sidebar for API Key Setup
with st.sidebar:
    st.header("Setup")
    api_key = st.text_input("Enter your Gemini API Key:", type="password")
    st.info("Get a key from Google AI Studio")

# 3. Helper Function to Extract Video ID
def get_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            p = parse_qs(parsed_url.query)
            return p.get('v', [None])[0]
        if parsed_url.path.startswith(('/embed/', '/v/')):
            return parsed_url.path.split('/')[2]
    return None

# 4. Core Metadata Extractor Function (The Fallback Engine)
def fetch_youtube_metadata(url):
    """
    Extracts Video Title, Description, and Top Comments when transcripts are unavailable.
    """
    ydl_opts = {
        'getcomments': True,
        'skip_download': True,
        'quiet': True,
        'extract_flat': False
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            title = info.get('title', 'Unknown Title')
            description = info.get('description', 'No description available.')
            
            # Extract top 10 comment texts safely
            comments_list = info.get('comments', [])
            top_comments = []
            for i, c in enumerate(comments_list):
                if i >= 10: break
                top_comments.append(c.get('text', ''))
                
            comments_text = "\n".join(top_comments)
            
            metadata_payload = f"""
            VIDEO TITLE: {title}
            
            VIDEO DESCRIPTION:
            {description}
            
            TOP VIEWER COMMENTS & DISCUSSIONS:
            {comments_text}
            """
            return metadata_payload, "Metadata (Title, Description, Comments)"
    except Exception as e:
        st.error(f"Metadata extraction engine encountered an issue: {e}")
        return None, None

# 5. Main Application Logic
if api_key:
    client = genai.Client(api_key=api_key)
    video_url = st.text_input("Paste YouTube Video URL:")
    
    if st.button("Generate Quiz", type="primary"):
        if not video_url:
            st.warning("Please enter a valid YouTube URL.")
        else:
            video_id = get_video_id(video_url)
            
            if not video_id:
                st.error("Invalid YouTube URL configuration.")
            else:
                data_source_used = None
                text_payload = None
                
                # --- TRY METHOD 1: TRANSCRIPTS ---
                with st.spinner("Attempting to extract video transcript..."):
                    try:
                        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                        text_snippets = []
                        for item in transcript_list:
                            if isinstance(item, dict):
                                text_snippets.append(item.get('text', ''))
                            else:
                                text_snippets.append(getattr(item, 'text', ''))
                        
                        text_payload = " ".join(text_snippets)
                        if text_payload.strip():
                            data_source_used = "Official Subtitles/Transcripts"
                            st.info("🎯 Found transcripts! Building quiz based directly on what the teacher said.")
                    except Exception:
                        # Silently pass to handle error via the metadata fallback structure
                        pass
                
                # --- TRY METHOD 2: METADATA FALLBACK (If Transcripts Failed) ---
                if not text_payload:
                    with st.spinner("⚠️ Transcripts disabled. Activating Fallback: Extracting Title, Description, and Comments..."):
                        text_payload, data_source_used = fetch_youtube_metadata(video_url)
                
                # --- GENERATE QUIZ WITH THE AVAILABLE PAYLOAD ---
                if text_payload:
                    with st.spinner(f"Sending data to Gemini (Source: {data_source_used})..."):
                        try:
                            quiz_prompt = f"""
                            You are an expert academic evaluator. Your task is to generate a comprehensive 5-question multiple-choice quiz.
                            Depending on the data available below, evaluate what the professor taught or discussed in this lecture.
                            
                            Data Context Source Type: {data_source_used}
                            
                            Provided Content Context:
                            {text_payload}
                            
                            Requirements:
                            1. Write a short abstract summarizing the core topic.
                            2. Create 5 distinct Multiple-Choice Questions with 4 options (A, B, C, D).
                            3. Add an expandable 'Answer Key' with justifications mapping back to the data context.
                            """
                            
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=quiz_prompt,
                            )
                            
                            st.success(f"Successfully generated quiz using {data_source_used}!")
                            st.markdown("---")
                            st.markdown(response.text)
                            
                        except Exception as gen_err:
                            st.error(f"Gemini evaluation engine error: {gen_err}")
                else:
                    st.error("Failed to extract any text strings from this link. Verify the video settings.")
else:
    st.warning("Please enter your Gemini API Key in the sidebar to unlock the application.")