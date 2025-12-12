# app.py
import streamlit as st
import requests

API_URL = "http://localhost:8000/predict"  # backend URL

st.set_page_config(
    page_title="Mental Health Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding-bottom: 20px;
    }
    .risk-card {
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .emotion-bar {
        height: 25px;
        border-radius: 5px;
        margin: 8px 0;
        transition: width 0.5s ease;
    }
    .emotion-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
    }
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 50px;
        font-weight: bold;
        font-size: 16px;
    }
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
    }
    .info-box {
        background-color: #e8f4fd;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2196F3;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h1 class='main-header'>🧠 Mental Health Emotion & Risk Detector</h1>", unsafe_allow_html=True)

# Information Box
st.markdown("""
<div class="info-box">
    <b>📋 How it works:</b> Enter your thoughts or feelings in the text box below. 
    Our AI will analyze the emotional content and provide insights about potential risk levels.
    All analysis is confidential and anonymous.
</div>
""", unsafe_allow_html=True)

# Create two columns for layout
col_left, col_right = st.columns([2, 1], gap="large")

with col_left:
    # Input Section
    st.subheader("📝 Share Your Thoughts")
    user_text = st.text_area(
        "Express your feelings here:",
        height=180,
        placeholder="Example: I've been feeling overwhelmed lately and haven't been sleeping well. Work has been really stressful...",
        label_visibility="collapsed"
    )
    
    analyze_button = st.button("🔍 Analyze Emotional State", use_container_width=True)

with col_right:
    # Information Panel
    st.subheader("ℹ️ About Risk Levels")
    
    st.markdown("""
    <div style='padding: 15px; background-color: #f0f2f6; border-radius: 10px;'>
    <b>🟢 LOW RISK</b><br>
    <small>Normal emotional variation, healthy coping</small>
    
    <br><br>
    
    <b>🟠 MODERATE RISK</b><br>
    <small>Elevated distress, may benefit from support</small>
    
    <br><br>
    
    <b>🔴 HIGH RISK</b><br>
    <small>Severe distress, professional support recommended</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Resources Section
    with st.expander("📞 Crisis Resources"):
        st.markdown("""
        **If you're in crisis:**
        - National Suicide Prevention Lifeline: 988
        - Crisis Text Line: Text HOME to 741741
        - International Association for Suicide Prevention: [Find a crisis center](https://www.iasp.info/resources/Crisis_Centres/)
        
        *This tool is for informational purposes only and not a substitute for professional care.*
        """)

# Analysis Section
if analyze_button:
    if not user_text.strip():
        st.warning("⚠️ Please enter some text to analyze.")
    else:
        try:
            with st.spinner("🔮 Analyzing emotional patterns..."):
                response = requests.post(API_URL, json={"text": user_text}, timeout=20)
            
            if response.status_code != 200:
                st.error(f"❌ API Error: {response.status_code}")
            else:
                data = response.json()
                risk = data.get("risk", "unknown").lower()
                preds = data.get("predictions", [])
                
                st.markdown("---")
                st.markdown("<h2 style='text-align: center;'>📊 Analysis Results</h2>", unsafe_allow_html=True)
                
                # Risk Level Display
                col1, col2, col3 = st.columns(3)
                with col2:
                    risk_colors = {
                        "low": ("#4CAF50", "🟢"),
                        "moderate": ("#FF9800", "🟠"), 
                        "high": ("#F44336", "🔴"),
                        "unknown": ("#757575", "⚫")
                    }
                    color, icon = risk_colors.get(risk, ("#757575", "⚫"))
                    
                    st.markdown(f"""
                    <div class="risk-card" style="background-color: {color}20; border: 2px solid {color};">
                        <h3 style="color: {color}; margin-top: 0;">Risk Level</h3>
                        <h1 style="color: {color}; margin: 10px 0;">{icon} {risk.upper()}</h1>
                        <p style="color: {color}; font-size: 14px;">Emotional State Assessment</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Emotions Display
                st.subheader("🎭 Emotional Breakdown")
                
                if preds:
                    # Create two columns for emotions
                    emo_col1, emo_col2 = st.columns(2)
                    
                    for i, emotion_data in enumerate(preds):
                        emo = emotion_data["emotion"]
                        score = emotion_data["score"]
                        percentage = score * 100
                        
                        # Color mapping for different emotions
                        emotion_colors = {
                            "sadness": "#2196F3",
                            "joy": "#FFC107",
                            "anger": "#F44336",
                            "fear": "#9C27B0",
                            "surprise": "#009688",
                            "disgust": "#795548",
                            "neutral": "#9E9E9E"
                        }
                        
                        color = emotion_colors.get(emo.lower(), "#607D8B")
                        
                        # Alternate between columns
                        target_col = emo_col1 if i % 2 == 0 else emo_col2
                        
                        with target_col:
                            st.markdown(f"""
                            <div style="margin-bottom: 20px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                    <span><b>{emo.capitalize()}</b></span>
                                    <span><b>{percentage:.1f}%</b></span>
                                </div>
                                <div style="background-color: #e0e0e0; border-radius: 10px; height: 20px;">
                                    <div class="emotion-bar" style="width: {percentage}%; background-color: {color};"></div>
                                </div>
                                <div style="text-align: right; font-size: 12px; color: #666; margin-top: 2px;">
                                    Confidence: {score:.3f}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("📭 No strong emotions detected in the text.")
                
                # Text Preview
                with st.expander("📖 Text Preview"):
                    st.caption("This is what we analyzed:")
                    st.info(user_text[:500] + ("..." if len(user_text) > 500 else ""))
                
                # Disclaimer
                st.markdown("---")
                st.caption("💡 **Note**: This tool uses AI to detect emotional patterns and is not a diagnostic tool. Always consult with mental health professionals for clinical assessments.")
                
        except requests.exceptions.ConnectionError:
            st.error("🔌 Cannot connect to the analysis server. Please ensure the backend is running on localhost:8000")
        except requests.exceptions.Timeout:
            st.error("⏰ The analysis is taking too long. Please try again.")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

# Footer
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])
with footer_col2:
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 12px; padding-top: 20px;">
        <p>🧠 Mental Health Emotion & Risk Detector | v1.0 | Confidential & Anonymous Analysis</p>
        <p>This tool is for educational and supportive purposes only.</p>
    </div>
    """, unsafe_allow_html=True)