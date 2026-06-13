import streamlit as st
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

# 1. Page Configuration
st.set_page_config(page_title="PyTorch Career Predictor", page_icon="🧠", layout="centered")
st.title("🧠 Deep Learning Career Path Predictor")
st.write("This app uses a locally trained **PyTorch Neural Network Classifier** to predict your ideal career path!")

# 2. Define the PyTorch Neural Network Architecture
class CareerClassifier(nn.Module):
    def __init__(self, input_dim, num_classes):
        super(CareerClassifier, self).__init__()
        # 3-Layer Dense Feedforward Architecture
        self.fc1 = nn.Linear(input_dim, 16)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(16, 8)
        self.fc3 = nn.Linear(8, num_classes)
        
    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        out = self.relu(out)
        out = self.fc3(out)
        return out

# 3. Create Synthetic Training Data (Mock Data History)
# Features order: [Math, Science, Coding, English, Management]
X_train_raw = np.array([
    [95, 90, 95, 70, 60], [90, 85, 92, 65, 55], [88, 92, 90, 75, 50], # Data Scientists / Software Eng (Class 0)
    [60, 85, 55, 70, 65], [55, 90, 50, 75, 60], [62, 88, 52, 80, 70], # Medical / Bio Researchers (Class 1)
    [70, 60, 65, 90, 95], [65, 55, 60, 95, 90], [55, 65, 50, 88, 92], # Management / Marketing Experts (Class 2)
])
# Labels matching the profiles above
y_train_raw = np.array([0, 0, 0, 1, 1, 1, 2, 2, 2])
classes_map = {0: "Data Science & Software Engineering", 1: "Biomedical & Healthcare Research", 2: "Product Management & Marketing Analytics"}

# Scale features for the neural network
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_raw)

# Convert arrays to PyTorch Tensors
X_tensor = torch.FloatTensor(X_train_scaled)
y_tensor = torch.LongTensor(y_train_raw)

# 4. Train the Model Natively
@st.cache_resource
def train_pytorch_model():
    model = CareerClassifier(input_dim=5, num_classes=3)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.05)
    
    # Train for 100 epochs
    for epoch in range(100):
        optimizer.zero_grad()
        outputs = model(X_tensor)
        loss = criterion(outputs, y_tensor)
        loss.backward()
        optimizer.step()
    return model

model = train_pytorch_model()

# 5. UI Fields Input Structure
st.subheader("Enter Your Marks (0 - 100)")
col1, col2 = st.columns(2)
with col1:
    m1 = st.number_input("Mathematics:", min_value=0, max_value=100, value=85)
    m2 = st.number_input("Science/Physics:", min_value=0, max_value=100, value=80)
    m3 = st.number_input("Computer Programming:", min_value=0, max_value=100, value=90)
with col2:
    m4 = st.number_input("English/Communication:", min_value=0, max_value=100, value=70)
    m5 = st.number_input("Social Sciences/Management:", min_value=0, max_value=100, value=60)

if st.button("Predict Career Path with PyTorch", type="primary"):
    # Format current user metrics input array
    user_features = np.array([[m1, m2, m3, m4, m5]])
    user_features_scaled = scaler.transform(user_features)
    user_tensor = torch.FloatTensor(user_features_scaled)
    
    # Run Inference
    model.eval()
    with torch.no_grad():
        predictions = model(user_tensor)
        predicted_class_idx = torch.argmax(predictions, dim=1).item()
        probabilities = torch.softmax(predictions, dim=1).numpy()[0]
        
    predicted_career = classes_map[predicted_class_idx]
    
    st.markdown("---")
    st.subheader("🎯 Model Prediction Result")
    st.success(f"The PyTorch Neural Network recommends: **{predicted_career}**")
    
    # Render Prediction Confidence/Probability Bar Chart
    fig, ax = plt.subplots(figsize=(6, 2.5))
    y_pos = np.arange(len(classes_map))
    ax.barh(y_pos, probabilities, color='#4CAF50', height=0.4)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(list(classes_map.values()), fontsize=8)
    ax.set_xlabel('Model Confidence Probability Score')
    ax.set_xlim(0, 1.1)
    
    for i, v in enumerate(probabilities):
        ax.text(v + 0.02, i, f"{v*100:.1f}%", va='center', fontsize=8, fontweight='bold')
        
    st.pyplot(fig)
    
    # Generate downloadable PDF report
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", "B", 16)
pdf.cell(0, 10, "Neural Network Classification Career Analysis Report", ln=True, align='C')
pdf.ln(10)
pdf.set_font("Arial", size=12)
pdf.cell(0, 10, f"Input Subject Parameters Matrix: Math={m1}, Sci={m2}, Code={m3}, Eng={m4}, Mgmt={m5}", ln=True)
pdf.cell(0, 10, f"Classified Output Vector Target: {predicted_career}", ln=True)

# --- FIX: Pass 'PNG' format explicitly to prevent the rfind error ---
img_buf.seek(0)
pdf.image(img_buf, x=15, w=180, type='PNG')