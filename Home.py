import streamlit as st
import base64
import warnings

def get_base64_of_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

image_base64 = get_base64_of_image('assets/iconizer-s.svg')
#

def show_home_page():
    image_base64 = get_base64_of_image('assets/iconizer-s.svg')
    st.markdown(f"""
    <head>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Smooch+Sans:wght@100..900&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="style.css">
    </head>
    <div class="header-container">
        <div class="logo-container">
            <img src="data:image/svg+xml;base64,{image_base64}" width="100%">
        </div>
        <div class="title-container">
            <h1>RAG DOLL</h1>
        </div>
    </div>
    <div class="container-title">
        <div class="text-section">
            <h1 style="font-size: 5rem;">&nbsp EU AI ACT<br> &nbsp COMPLIANCE CHECKER <br> &nbsp AND RISK ASSESSMENT</h1>
        </div>
        <div class="content-section">
            <p style="font-family: Mulish, sans-serif;">
    <strong>RAG DOLL</strong> is an intelligent compliance checker designed to evaluate the potential risks of AI systems by aligning them with the risk categories defined in the European AI Act, ranging from minimal to unacceptable. Using a RAG system and regulations-aware Large Language Models, it analyzes key aspects of an AI application and provides a structured <strong style="color: #1b2b5c;">Risk Assessment </strong>, <strong style="color: #1b2b5c;">Compliance Verification </strong>, and tailored <strong style="color: #1b2b5c;">Recommendations</strong>.
</p>
<p style="font-family: Mulish, sans-serif;">
    Users can assess their compliance by completing a customized questionnaire designed to align with the requirements of the EU AI Act.
</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def header():
    image_base64 = get_base64_of_image('assets/iconizer-s.svg')
    st.markdown(f"""
    <head>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Smooch+Sans:wght@100..900&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="style.css">
    </head>
    <div class="header-container">
        <div class="logo-container">
            <img src="data:image/svg+xml;base64,{image_base64}" width="100%">
        </div>
        <div class="title-container">
            <h1>RAG DOLL</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)
