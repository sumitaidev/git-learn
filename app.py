import streamlit as st
from google import genai
from google.genai import types

# 1. Page Configuration
st.set_page_config(page_title="AI Study Companion", page_icon="📚", layout="centered")
st.title("📚 AI-Powered Study Companion & Quiz Generator")
st.write("Paste your lecture notes below to get an instant summary and a custom quiz!")

# 2. Securely input API Key in the UI sidebar
with st.sidebar:
    st.header("Setup")
    api_key = st.text_input("Enter your Gemini API Key:", type="password")
    st.info("Get a key from Google AI Studio")

# 3. App Core Logic
if api_key:
    # Initialize the standard Google GenAI client
    client = genai.Client(api_key=api_key)
    
    # Input area for study material
    user_text = st.text_area("Paste your study material/lecture notes here:", height=250)
    
    if st.button("Generate Summary & Quiz", type="primary"):
        if user_text.strip() == "":
            st.warning("Please paste some text first!")
        else:
            with st.spinner("AI is analyzing and generating your content..."):
                try:
                    # Construct the structured prompt
                    master_prompt = f"""
                    You are an expert AI Study Assistant. Analyze the following text and provide:
                    1. A concise, bulleted 'Summary' of the key concepts.
                    2. A '5-Question Multiple-Choice Quiz' based only on the text. Each question must have 4 options (A, B, C, D).
                    3. At the very end, provide an expandable 'Answer Key' with brief explanations.
                    
                    Text:
                    {user_text}
                    """
                    
                    # Call the recommended gemini-2.5-flash model
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=master_prompt,
                    )
                    
                    # Display the output nicely in the app
                    st.success("Generation Complete!")
                    st.markdown("---")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")
else:
    st.warning("Please enter your Gemini API Key in the sidebar to start the application.")