import streamlit as st
import requests
from google import genai
from fpdf import FPDF
import io
import matplotlib.pyplot as plt

# 1. Page Configuration
st.set_page_config(page_title="AI Technical Doc Builder", page_icon="📖", layout="centered")
st.title("📖 AI Technical Documentation Generator")
st.write("Provide a source file to generate a structured, professional PDF technical manual complete with system flowcharts.")

# 2. Sidebar Configuration
with st.sidebar:
    st.header("Authentication")
    api_key = st.text_input("Enter your Gemini API Key:", type="password")
    st.info("Obtain a free key from Google AI Studio.")

# 3. Helper: Convert regular GitHub URL to Raw Content URL
def convert_to_raw_github_url(url):
    if "github.com" in url and "/blob/" in url:
        return url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    return url

# 4. Helper Engine: Programmatically Draw a Flowchart Image
def generate_flowchart_image():
    """
    Draws a highly detailed vector pipeline flowchart using matplotlib
    and converts it to an in-memory byte buffer for FPDF to parse.
    """
    fig, ax = plt.subplots(figsize=(7, 3.5), dpi=300)
    ax.axis('off')
    
    # Configure box formatting parameters
    box_blue = dict(boxstyle="round,pad=0.5", fc="#E1F5FE", ec="#0288D1", lw=1.5)
    box_amber = dict(boxstyle="darrow,pad=0.4", fc="#FFF8E1", ec="#FFA000", lw=1.5)
    box_green = dict(boxstyle="round,pad=0.5", fc="#E8F5E9", ec="#388E3C", lw=1.5)
    
    # Draw flowchart content blocks
    ax.text(0.15, 0.8, "Source Input\n(File/GitHub)", ha="center", va="center", bbox=box_blue, fontsize=9)
    ax.text(0.50, 0.8, "Gemini AI Core\n(Architecture Analysis)", ha="center", va="center", bbox=box_amber, fontsize=9)
    ax.text(0.85, 0.8, "FPDF Compiler\n(PDF Generation)", ha="center", va="center", bbox=box_green, fontsize=9)
    
    ax.text(0.50, 0.2, "Output Target:\nDownloadable Technical Manual PDF Document", ha="center", va="center", 
            bbox=dict(boxstyle="square,pad=0.6", fc="#ECEFF1", ec="#455A64", lw=1.5), fontsize=9)
    
    # Draw routing connection arrows
    arrow_props = dict(arrowstyle="->", lw=2, color="#37474F")
    ax.annotate("", xy=(0.34, 0.8), xytext=(0.28, 0.8), arrowprops=arrow_props)
    ax.annotate("", xy=(0.69, 0.8), xytext=(0.63, 0.8), arrowprops=arrow_props)
    ax.annotate("", xy=(0.50, 0.42), xytext=(0.50, 0.62), arrowprops=arrow_props)
    
    # Save chart directly into a byte array wrapper
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', bbox_inches='tight', pad_inches=0.1)
    img_buf.seek(0)
    plt.close(fig)
    return img_buf

# 5. Core Logic: PDF Style Setup
class TechnicalDocPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, "AUTOMATED TECHNICAL DOCUMENTATION MANUAL", border=0, ln=True, align="R")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", border=0, align="C")

    def add_custom_heading(self, text):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(12, 35, 64)  # Deep enterprise blue
        self.ln(5)
        self.cell(0, 10, text, ln=True)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(4)

# 6. Core Interface Flow
if api_key:
    client = genai.Client(api_key=api_key)
    input_mode = st.radio("Choose Input Source:", ("Option A: Paste GitHub File Link", "Option B: Upload Source Code File"))
    
    code_content = ""
    filename_context = "Source Code"
    
    if input_mode == "Option A: Paste GitHub File Link":
        github_url = st.text_input("Paste GitHub File URL:")
        if github_url:
            raw_target_url = convert_to_raw_github_url(github_url)
            with st.spinner("Fetching source data stream from GitHub..."):
                try:
                    res = requests.get(raw_target_url)
                    if res.status_code == 200:
                        code_content = res.text
                        filename_context = github_url.split("/")[-1]
                        st.success(f"Successfully fetched file: {filename_context}")
                except Exception as e:
                    st.error(f"Network processing failed: {e}")
                    
    else:
        uploaded_file = st.file_uploader("Upload Code File:", type=["py", "js", "cpp", "java"])
        if uploaded_file is not None:
            code_content = uploaded_file.getvalue().decode("utf-8")
            filename_context = uploaded_file.name
            st.success(f"Successfully staged: {filename_context}")

    # Process Action Output Row
    if code_content:
        if st.button("Generate Technical Documentation Manual", type="primary"):
            with st.spinner("Analyzing architecture and assembling document structure..."):
                
                doc_prompt = f"""
                You are an expert Solutions Architect. Analyze this source code and build a comprehensive Software Reference Manual.
                Do NOT include any Markdown bolding (**) or code backticks (```) in your response. Output raw clean lines.
                
                Generate content following these exact structural header tags:
                
                DOCUMENT TITLE
                Technical Reference Manual for {filename_context}
                
                SYSTEM ARCHITECTURE OVERVIEW
                [Provide a concise overview here]
                
                FUNCTIONAL COMPONENT BREAKDOWN
                [Detail primary methods and their responsibilities]
                
                DEPENDENCY AND ENVIRONMENT ANALYSIS
                [List required module frameworks here]
                """
                
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[doc_prompt, code_content],
                    )
                    generated_raw_doc = response.text
                    
                    # Initialize PDF Constructor Engine
                    pdf = TechnicalDocPDF()
                    pdf.add_page()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    pdf.set_font("Helvetica", size=10)
                    pdf.set_text_color(40, 40, 40)
                    
                    # 1. Parse and print the Title Section dynamically
                    pdf.add_custom_heading("SYSTEM RECONSTRUCT MANUAL")
                    
                    # 2. INJECT SYSTEM ARCHITECTURE FLOWCHART DYNAMICALLY INTO THE PDF
                    pdf.ln(2)
                    chart_bytes = generate_flowchart_image()
                    # We inject the byte array directly into FPDF's image channel
                    pdf.image(chart_bytes, x=15, w=180)
                    pdf.ln(5)
                    
                    # 3. Stream structural code data to text pages
                    sections_to_intercept = ["DOCUMENT TITLE", "SYSTEM ARCHITECTURE OVERVIEW", "FUNCTIONAL COMPONENT BREAKDOWN", "DEPENDENCY AND ENVIRONMENT ANALYSIS"]
                    
                    for line in generated_raw_doc.split("\n"):
                        clean_line = line.encode('latin-1', 'ignore').decode('latin-1').strip()
                        if not clean_line:
                            continue
                        
                        if any(clean_line.startswith(sec) for sec in sections_to_intercept):
                            pdf.add_custom_heading(clean_line)
                        else:
                            pdf.set_font("Helvetica", size=10)
                            pdf.multi_cell(0, 6, clean_line)
                    
                    # Compile buffer output profile 
                    pdf_output = pdf.output(dest='S').encode('latin-1')
                    
                    st.success("🎉 Document generated with native workflow chart maps!")
                    st.download_button(
                        label="⬇️ Download Document Manual PDF",
                        data=pdf_output,
                        file_name=f"Technical_Documentation_{filename_context.split('.')[0]}.pdf",
                        mime="application/pdf"
                    )
                    
                except Exception as e:
                    st.error(f"Documentation compiler error: {e}")
else:
    st.warning("Please input your Gemini API Key in the left sidebar setup window.")