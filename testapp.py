import streamlit as st
st.set_page_config(page_title="Brand & Influencer Similarity Survey", layout="wide")

import pandas as pd
from brand_logic import run_brand_survey
from influencer_logic import run_influencer_survey
from utils import save_to_google_sheet

# ----------------- CSS Styling ----------------- #
st.markdown("""
<style>
    /* Main centered container */
    .centered-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 60vh;
        text-align: center;
        padding: 20px;
    }
    
    /* Consistent button styling */
    .centered-button {
        margin-top: 40px;
        width: 200px;
    }
    
    /* Vertical divider for comparison pages */
    .vertical-divider {
        position: absolute;
        left: 50%;
        top: 0;
        bottom: 0;
        width: 1px;
        background-color: #e0e0e0;
        transform: translateX(-50%);
    }
    
    /* Comparison column styling */
    .comparison-column {
        flex: 1;
        display: flex;
        flex-direction: column;
        min-height: 420px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- Title Pages ----------------- #
def show_title_page():
    st.markdown("""
        <div class="centered-container">
            <h1 style="font-size: 48px; margin-bottom: 20px;">Influencer & Brand Similarity Survey</h1>
            <p style="font-size: 20px; max-width: 800px; margin: 0 auto 30px;">
                You'll be shown a reference influencer or brand and asked to choose which of two other options feels more similar. 
                Each question includes sample images, descriptions, and social/price context.
                The full survey takes about <strong>5–6 minutes</strong>.
            </p>
            <div class="centered-button">
    """, unsafe_allow_html=True)
    
    if st.button("Start Survey", key="title_start"):
        st.session_state.phase = "brand_intro"
        st.rerun()
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def show_brand_intro_page():
    st.markdown("""
        <div class="centered-container">
            <h1 style="font-size: 40px; margin-bottom: 20px;">Part 1: Brand Similarity</h1>
            <p style="font-size: 18px; max-width: 700px; margin: 0 auto 30px;">
                You'll be shown a reference clothing brand and asked to choose which of two other brands is more similar in style and price.
            </p>
            <div class="centered-button">
    """, unsafe_allow_html=True)
    
    if st.button("Start Brand Survey", key="brand_start"):
        st.session_state.phase = "brand_q"
        st.rerun()
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def show_influencer_intro_page():
    st.markdown("""
        <div class="centered-container">
            <h1 style="font-size: 40px; margin-bottom: 20px;">Part 2: Influencer Similarity</h1>
            <p style="font-size: 18px; max-width: 700px; margin: 0 auto 30px;">
                Now you'll see a reference influencer and be asked to select which of two other influencers aligns more closely in aesthetic and category.
            </p>
            <div class="centered-button">
    """, unsafe_allow_html=True)
    
    if st.button("Start Influencer Survey", key="influencer_start"):
        st.session_state.phase = "influencer_q"
        st.rerun()
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def show_end_page():
    st.markdown("""
        <div class="centered-container">
            <h1 style="font-size: 40px; margin-bottom: 20px;">🎉 Thank You!</h1>
            <p style="font-size: 18px; max-width: 700px; margin: 0 auto 30px;">
                You've completed the survey — we really appreciate your time and feedback.
                <br>
            </p>
    """, unsafe_allow_html=True)

    # Save responses to Google Sheets
    brand_responses = pd.DataFrame(st.session_state.get("brand_responses", []))
    influencer_responses = pd.DataFrame(st.session_state.get("influencer_responses", []))
    if not brand_responses.empty:
        save_to_google_sheet(brand_responses, "brand")
    if not influencer_responses.empty:
        save_to_google_sheet(influencer_responses, "influencer")
        st.success(f"Yay!")


# ----------------- Main App Flow ----------------- #
if "phase" not in st.session_state:
    st.session_state.phase = "title"
    st.session_state.brand_responses = []
    st.session_state.influencer_responses = []

if st.session_state.phase == "title":
    show_title_page()
elif st.session_state.phase == "brand_intro":
    show_brand_intro_page()
elif st.session_state.phase == "brand_q":
    done = run_brand_survey()
    if done:
        st.session_state.phase = "influencer_intro"
        st.rerun()
elif st.session_state.phase == "influencer_intro":
    show_influencer_intro_page()
elif st.session_state.phase == "influencer_q":
    done = run_influencer_survey()
    if done:
        st.session_state.phase = "end"
        st.rerun()
elif st.session_state.phase == "end":
    show_end_page()