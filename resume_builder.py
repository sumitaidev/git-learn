import streamlit as st
import requests
from google import genai
from fpdf import FPDF

# 1. Page Configuration
st.set_page_config(page_title="AI Resume Builder", page_icon="📝", layout="centered")
st.title("📝 AI & GitHub Powered Resume Builder")
st.write("Generate a professional, downloadable PDF CV from your GitHub repositories and text inputs.")

# 2. Sidebar for Configuration
with st.sidebar:
    st.header("Setup")
    api_key = st.text_input("Enter your Gemini API Key:", type="password")
    st.info("Get an API key from Google AI Studio")

# 3. Core Logic: Fetch Public Projects from GitHub API
def fetch_github_projects(username):
    """
    Fetches the user's public repositories from GitHub and sorts them by star count
    to mimic 'pinned' or highly relevant showcase projects.
    """
    url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=5"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            repos = response.json()
            projects = []
            for repo in repos:
                projects.append({
                    "name": repo.get("name"),
                    "description": repo.get("description") or "No description provided.",
                    "language": repo.get("language") or "Tech Stack unspecified",
                    "url": repo.get("html_url")
                })
            return projects
        else:
            return None
    except Exception:
        return None

# 4. Core Logic: PDF Generating Engine Class
class PDFResume(FPDF):
    def header(self):
        self.set_font("Arial", "B", 18)
        self.set_text_color(33, 37, 41) # Dark gray header text
        
    def add_section_header(self, title):
        self.set_font("Arial", "B", 12)
        self.set_text_color(0, 51, 102) # Clean business blue color
        self.cell(0, 10, title, ln=True)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y()) # Clean partition line
        self.ln(3)

# 5. UI Fields Input Structure
if api_key:
    client = genai.Client(api_key=api_key)
    
    st.subheader("1. Developer Networks Context")
    github_user = st.text_input("Enter GitHub Username (e.g., torvalds):")
    
    st.subheader("2. Profile Summary Data")
    linkedin_raw_text = st.text_area(
        "Paste your LinkedIn Profile text content (Go to your profile page, press Ctrl+A, then copy-paste everything here):",
        height=200,
        placeholder="Paste Name, Headline, About Section, and Work Experience text blocks directly..."
    )
    
    if st.button("Compile Professional CV & PDF", type="primary"):
        if not github_user or not linkedin_raw_text.strip():
            st.warning("Please fill out both the GitHub username and paste your LinkedIn data block.")
        else:
            # Step A: Fetch GitHub data
            with st.spinner("Fetching public repository metadata from GitHub API..."):
                git_projects = fetch_github_projects(github_user)
            
            # Step B: Restructure and optimize data layout using Gemini
            with st.spinner("Structuring profile with Gemini optimization layers..."):
                git_context_str = ""
                if git_projects:
                    for p in git_projects:
                        git_context_str += f"- Project Name: {p['name']}\n  Description: {p['description']}\n  Tech Stack: {p['language']}\n"
                
                ai_prompt = f"""
                You are a senior professional resume writer. Take the raw LinkedIn text dump and public GitHub projects below and restructure them into a clean, concise standard resume format.
                
                CRITICAL RULE: Return ONLY the raw textual sections exactly as requested below. Do not use markdown backticks (```) or bold markers (**) anywhere in your response. Keep descriptions brief so it fits cleanly.
                
                Follow this exact output structure template:
                [NAME]
                [CONTACT EMAIL / PHONE / LINKEDIN LINK]
                ---
                SUMMARY
                [Write a compelling 2-sentence developer bio here]
                ---
                EXPERIENCE
                [Summarize work experience cleanly in bullet points]
                ---
                EDUCATION
                [Summarize education cleanly]
                """
                
                full_payload = f"{ai_prompt}\n\nRAW LINKEDIN DATA:\n{linkedin_raw_text}\n\nGITHUB PROJECTS:\n{git_context_str}"
                
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=full_payload,
                    )
                    resume_text = response.text
                    
                    # Step C: Render Data Context into PDF Structure
                    pdf = PDFResume()
                    pdf.add_page()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    
                    # Add standard ASCII clean encoding parsing parameters
                    pdf.set_font("Arial", size=10)
                    pdf.set_text_color(50, 50, 50)
                    
                    # Parse rows generated from the AI payload text safely
                    for line in resume_text.split("\n"):
                        clean_line = line.encode('latin-1', 'ignore').decode('latin-1')
                        if "---" in clean_line:
                            pdf.ln(4)
                            continue
                        if clean_line.isupper() and len(clean_line) < 30:
                            pdf.add_section_header(clean_line)
                        else:
                            pdf.multi_cell(0, 6, clean_line)
                    
                    # Explicitly append GitHub Projects fetched programmatically via API
                    if git_projects:
                        pdf.ln(4)
                        pdf.add_section_header("GITHUB SHOWCASE PROJECTS")
                        for p in git_projects:
                            pdf.set_font("Arial", "B", 10)
                            pdf.cell(0, 6, f"{p['name']} ({p['language']})", ln=True)
                            pdf.set_font("Arial", size=10)
                            pdf.multi_cell(0, 5, f"Description: {p['description']}\nURL: {p['url']}")
                            pdf.ln(2)
                    
                    # Convert generated binary payload layout into interactive download action hook
                    pdf_bytes = pdf.output(dest='S').encode('latin-1')
                    
                    st.success("🎉 CV Successfully compiled!")
                    st.download_button(
                        label="⬇️ Download Your CV PDF",
                        data=pdf_bytes,
                        file_name=f"{github_user}_professional_resume.pdf",
                        mime="application/pdf"
                    )
                    
                except Exception as e:
                    st.error(f"Execution Error during AI processing: {e}")
else:
    st.warning("Please enter your Gemini API Key in the sidebar to unlock the application workspace.")