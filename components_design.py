"""
Enhanced UI Components for OpenAI Usage Tracker
Aesthetic improvements while maintaining functionality
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List, Optional, Any

# Streamlit version compatibility utilities
def safe_dataframe(df: pd.DataFrame, **kwargs):
    """Safely render dataframe with version compatibility"""
    try:
        return st.dataframe(df, use_container_width=kwargs.get('use_container_width', True))
    except TypeError:
        # Remove unsupported parameters for older versions
        safe_kwargs = {k: v for k, v in kwargs.items() if k not in ['use_container_width']}
        return st.dataframe(df, **safe_kwargs)

def safe_plotly_chart(fig, **kwargs):
    """Safely render plotly chart with version compatibility"""
    try:
        return st.plotly_chart(fig, use_container_width=kwargs.get('use_container_width', True))
    except TypeError:
        # Remove unsupported parameters for older versions
        safe_kwargs = {k: v for k, v in kwargs.items() if k not in ['use_container_width']}
        return st.plotly_chart(fig, **safe_kwargs)

def load_apple_design_system():
    """Load Apple-style design system with premium aesthetics"""
    css = """
    <style>
    /* Apple System Fonts - San Francisco inspired */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Apple Design System Variables */
    :root {
        /* Apple Color Palette */
        --apple-blue: #007AFF;
        --apple-blue-rgb: 0, 122, 255;
        --apple-green: #34C759;
        --apple-orange: #FF9500;
        --apple-red: #FF3B30;
        --apple-purple: #AF52DE;
        --apple-teal: #5AC8FA;
        
        /* Apple Grayscale */
        --apple-gray-6: #1D1D1F;
        --apple-gray-5: #2C2C2E;
        --apple-gray-4: #48484A;
        --apple-gray-3: #6E6E73;
        --apple-gray-2: #AEAEB2;
        --apple-gray-1: #F2F2F7;
        
        /* Apple Radius System */
        --apple-radius-sm: 8px;
        --apple-radius-md: 12px;
        --apple-radius-lg: 16px;
        --apple-radius-xl: 20px;
        
        /* Apple Spacing System */
        --apple-space-4: 4px;
        --apple-space-8: 8px;
        --apple-space-16: 16px;
        --apple-space-24: 24px;
        --apple-space-32: 32px;
        --apple-space-48: 48px;
        --apple-space-64: 64px;
        --apple-space-96: 96px;
        --apple-space-128: 128px;
        
        /* Apple Shadows */
        --apple-shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
        --apple-shadow-md: 0 4px 12px rgba(0, 0, 0, 0.15), 0 2px 4px rgba(0, 0, 0, 0.12);
        --apple-shadow-lg: 0 10px 40px rgba(0, 0, 0, 0.16), 0 4px 12px rgba(0, 0, 0, 0.12);
    }
    
    /* Apple Light Theme (Default) */
    :root,
    [data-theme="light"] {
        --text-primary: var(--apple-gray-6);
        --text-secondary: var(--apple-gray-3);
        --text-tertiary: var(--apple-gray-2);
        
        --bg-primary: #FBFBFD;
        --bg-secondary: #FFFFFF;
        --bg-tertiary: var(--apple-gray-1);
        --bg-elevated: #FFFFFF;
        --border-color: rgba(0, 0, 0, 0.1);
        
        --shadow-card: var(--apple-shadow-md);
        --shadow-elevated: var(--apple-shadow-lg);
        
        /* Apple Semantic Colors */
        --accent-primary: var(--apple-blue);
        --accent-success: var(--apple-green);
        --accent-warning: var(--apple-orange);
        --accent-danger: var(--apple-red);
        --accent-info: var(--apple-teal);
    }
    
    /* Apple Dark Theme */
    @media (prefers-color-scheme: dark) {
        :root {
            --text-primary: #FFFFFF;
            --text-secondary: var(--apple-gray-2);
            --text-tertiary: var(--apple-gray-3);
            
            --bg-primary: #000000;
            --bg-secondary: var(--apple-gray-6);
            --bg-tertiary: var(--apple-gray-5);
            --bg-elevated: var(--apple-gray-5);
            --border-color: rgba(255, 255, 255, 0.1);
            
            --shadow-card: 0 4px 16px rgba(0, 0, 0, 0.4);
            --shadow-elevated: 0 8px 32px rgba(0, 0, 0, 0.6);
            
            /* Apple Dark Semantic Colors */
            --accent-primary: #0A84FF;
            --accent-success: #30D158;
            --accent-warning: #FF9F0A;
            --accent-danger: #FF453A;
            --accent-info: #64D2FF;
        }
    }
    
    /* Force Dark Theme for Streamlit Dark Mode */
    .stApp[data-theme="dark"],
    .stApp:has(.css-1d391kg[data-baseweb*="dark"]),
    body[data-theme="dark"] .stApp,
    [data-testid="stAppViewContainer"][data-theme="dark"] {
        --text-primary: #E9ECEF !important;
        --text-secondary: #ADB5BD !important;
        --text-light: #6C757D !important;
        
        --bg-primary: #212529 !important;
        --bg-secondary: #343A40 !important;
        --bg-tertiary: #495057 !important;
        --border-color: #495057 !important;
        
        --shadow-sm: 0 2px 4px rgba(0,0,0,0.3) !important;
        --shadow-md: 0 4px 8px rgba(0,0,0,0.4) !important;
        --shadow-lg: 0 8px 16px rgba(0,0,0,0.5) !important;
        
        background: linear-gradient(135deg, #343A40 0%, #495057 100%) !important;
        color: #E9ECEF !important;
    }
    
    /* Streamlit Dark Mode Text Elements */
    .stApp[data-theme="dark"] h1,
    .stApp[data-theme="dark"] h2, 
    .stApp[data-theme="dark"] h3,
    .stApp[data-theme="dark"] h4,
    .stApp[data-theme="dark"] h5,
    .stApp[data-theme="dark"] h6,
    body[data-theme="dark"] .stApp h1,
    body[data-theme="dark"] .stApp h2,
    body[data-theme="dark"] .stApp h3,
    body[data-theme="dark"] .stApp h4,
    body[data-theme="dark"] .stApp h5,
    body[data-theme="dark"] .stApp h6 {
        color: #E9ECEF !important;
    }
    
    /* Sidebar Dark Mode */
    .stApp[data-theme="dark"] .css-1d391kg *,
    body[data-theme="dark"] .stApp .css-1d391kg * {
        color: #E9ECEF !important;
    }
    
    /* Menu and Navigation Dark Mode */
    .stApp[data-theme="dark"] .stSelectbox label,
    .stApp[data-theme="dark"] .stSelectbox div,
    body[data-theme="dark"] .stApp .stSelectbox label,
    body[data-theme="dark"] .stApp .stSelectbox div {
        color: #E9ECEF !important;
    }
    
    /* Universal Dark Theme Text Fix */
    .dark-theme h1, .dark-theme h2, .dark-theme h3, 
    .dark-theme h4, .dark-theme h5, .dark-theme h6,
    .dark-theme p, .dark-theme span, .dark-theme div,
    .dark-theme label, .dark-theme .stMarkdown,
    .dark-theme .stText, .dark-theme .stCaption {
        color: #E9ECEF !important;
    }
    
    .dark-theme .css-1d391kg {
        background: #343A40 !important;
    }
    
    .dark-theme .stSelectbox > div > div {
        background: #495057 !important;
        color: #E9ECEF !important;
    }
    
    /* Apple Global Styles */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Display', 'SF Pro Text', sans-serif;
        background: var(--bg-primary);
        color: var(--text-primary) !important;
        line-height: 1.47059;
        font-weight: 400;
        letter-spacing: -0.022em;
    }
    
    /* Apple Typography Scale */
    h1, .apple-hero {
        font-size: 48px;
        line-height: 1.08349;
        font-weight: 700;
        letter-spacing: -0.003em;
        color: var(--text-primary);
        margin-bottom: var(--apple-space-24);
    }
    
    h2, .apple-title {
        font-size: 36px;
        line-height: 1.125;
        font-weight: 600;
        letter-spacing: -0.009em;
        color: var(--text-primary);
        margin-bottom: var(--apple-space-16);
    }
    
    h3, .apple-heading {
        font-size: 24px;
        line-height: 1.16667;
        font-weight: 600;
        letter-spacing: -0.016em;
        color: var(--text-primary);
        margin-bottom: var(--apple-space-16);
    }
    
    h4, .apple-subheading {
        font-size: 18px;
        line-height: 1.23;
        font-weight: 500;
        letter-spacing: -0.022em;
        color: var(--text-secondary);
        margin-bottom: var(--apple-space-8);
    }
    
    p, .apple-body {
        font-size: 16px;
        line-height: 1.47059;
        font-weight: 400;
        letter-spacing: -0.022em;
        color: var(--text-primary);
        margin-bottom: var(--apple-space-16);
    }
    
    .apple-caption {
        font-size: 14px;
        line-height: 1.42857;
        font-weight: 400;
        letter-spacing: -0.016em;
        color: var(--text-secondary);
    }
    
    .apple-label {
        font-size: 12px;
        line-height: 1.33337;
        font-weight: 500;
        letter-spacing: 0.066em;
        text-transform: uppercase;
        color: var(--text-tertiary);
    }
    
    /* Force Dark Theme Text Visibility */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background: linear-gradient(135deg, #343A40 0%, #495057 100%) !important;
            color: #E9ECEF !important;
        }
        
        /* Main titles and headers */
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
            color: #E9ECEF !important;
        }
        
        /* Sidebar text */
        .css-1d391kg * {
            color: #E9ECEF !important;
        }
        
        /* Menu items and navigation */
        .stSelectbox label, .stSelectbox div {
            color: #E9ECEF !important;
        }
        
        /* All text elements */
        .stMarkdown, .stText, .stCaption {
            color: #E9ECEF !important;
        }
    }
    
    /* Apple Container System */
    .main .block-container {
        padding-top: var(--apple-space-64);
        padding-bottom: var(--apple-space-64);
        padding-left: var(--apple-space-24);
        padding-right: var(--apple-space-24);
        max-width: 1024px;
        margin: 0 auto;
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
    
    /* Apple Grid System */
    .apple-grid {
        display: grid;
        gap: var(--apple-space-32);
        margin: var(--apple-space-48) 0;
    }
    
    .apple-grid-2 {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .apple-grid-3 {
        grid-template-columns: repeat(3, 1fr);
    }
    
    .apple-grid-4 {
        grid-template-columns: repeat(4, 1fr);
    }
    
    .apple-grid-auto {
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    }
    
    @media (max-width: 768px) {
        .apple-grid-2,
        .apple-grid-3,
        .apple-grid-4 {
            grid-template-columns: 1fr;
        }
    }
    
    /* Force Main Content Background */
    .stApp > .main,
    .stApp .main > .block-container,
    [data-testid="stAppViewContainer"] .main {
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
    
    /* Dark Theme Main Content */
    @media (prefers-color-scheme: dark) {
        .main .block-container {
            background: #212529 !important;
            color: #E9ECEF !important;
        }
        
        .stApp > .main,
        .stApp .main > .block-container {
            background: #212529 !important;
            color: #E9ECEF !important;
        }
    }
    
    .dark-theme .main .block-container,
    .dark-theme .stApp > .main,
    .dark-theme .stApp .main > .block-container {
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
    
    /* Centered Layout for Tables */
    .centered-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        margin: 0 auto;
    }
    
    .centered-table-container {
        width: 95%;
        max-width: 1100px;
        margin: 1rem auto;
        padding: 0 1rem;
    }
    
    /* Optimized Button Containers */
    .compact-button-container {
        display: flex;
        gap: 8px;
        justify-content: flex-start;
        align-items: center;
        margin: 0.5rem 0;
        flex-wrap: wrap;
    }
    
    .compact-button-container .stButton {
        margin: 0 !important;
    }
    
    .compact-button-container .stButton > button {
        padding: 0.5rem 1rem !important;
        margin: 0 !important;
        min-height: 2.5rem !important;
    }
    
    /* Header Styles */
    .page-header {
        background: var(--bg-primary);
        padding: 2rem;
        border-radius: var(--border-radius-lg);
        box-shadow: var(--shadow-sm);
        margin-bottom: 2rem;
        border-left: 4px solid var(--primary-color);
    }
    
    .page-title {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .page-description {
        font-size: 1.1rem;
        color: var(--text-secondary);
        margin-bottom: 0;
    }
    
    /* Apple Card System */
    .apple-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: var(--apple-radius-lg);
        padding: var(--apple-space-32);
        box-shadow: var(--shadow-card);
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        position: relative;
        overflow: hidden;
        backdrop-filter: saturate(180%) blur(20px);
        -webkit-backdrop-filter: saturate(180%) blur(20px);
    }
    
    .apple-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: var(--shadow-elevated);
    }
    
    .apple-card-hero {
        background: var(--bg-secondary);
        border-radius: var(--apple-radius-xl);
        padding: var(--apple-space-64) var(--apple-space-48);
        text-align: center;
        box-shadow: var(--shadow-card);
        margin: var(--apple-space-48) 0;
        position: relative;
    }
    
    .apple-card-hero::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-info) 100%);
        opacity: 0.05;
        border-radius: var(--apple-radius-xl);
    }
    
    /* Apple Metrics System */
    .apple-metric {
        text-align: center;
        padding: var(--apple-space-24);
    }
    
    .apple-metric-value {
        font-size: 56px;
        line-height: 1;
        font-weight: 700;
        letter-spacing: -0.005em;
        color: var(--accent-primary);
        margin-bottom: var(--apple-space-8);
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-info));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .apple-metric-label {
        font-size: 14px;
        line-height: 1.42857;
        font-weight: 500;
        letter-spacing: 0.066em;
        text-transform: uppercase;
        color: var(--text-secondary);
        margin-bottom: var(--apple-space-4);
    }
    
    .apple-metric-change {
        font-size: 12px;
        line-height: 1.33337;
        font-weight: 600;
        padding: var(--apple-space-4) var(--apple-space-8);
        border-radius: var(--apple-radius-sm);
        display: inline-block;
        margin-top: var(--apple-space-8);
    }
    
    .apple-metric-change.positive {
        background: rgba(52, 199, 89, 0.1);
        color: var(--accent-success);
    }
    
    .apple-metric-change.negative {
        background: rgba(255, 59, 48, 0.1);
        color: var(--accent-danger);
    }
    
    .metric-change {
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.5rem;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        display: inline-block;
    }
    
    .metric-change.positive {
        background: rgba(40, 167, 69, 0.1);
        color: var(--success-color);
    }
    
    .metric-change.negative {
        background: rgba(220, 53, 69, 0.1);
        color: var(--danger-color);
    }
    
    /* Enhanced Tables */
    .dataframe {
        border: 1px solid var(--border-color) !important;
        border-radius: var(--border-radius) !important;
        overflow: hidden !important;
        box-shadow: var(--shadow-sm) !important;
        background: var(--bg-primary) !important;
    }
    
    .dataframe th {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        padding: 1rem 0.75rem !important;
        border-bottom: 2px solid var(--border-color) !important;
    }
    
    .dataframe td {
        padding: 0.75rem !important;
        border-bottom: 1px solid var(--border-color) !important;
        font-size: 0.9rem !important;
    }
    
    .dataframe tbody tr:hover {
        background-color: rgba(0, 102, 204, 0.05) !important;
    }
    
    /* Status Indicators */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-success {
        background: rgba(40, 167, 69, 0.1);
        color: var(--success-color);
        border: 1px solid rgba(40, 167, 69, 0.2);
    }
    
    .status-warning {
        background: rgba(255, 193, 7, 0.1);
        color: #856404;
        border: 1px solid rgba(255, 193, 7, 0.2);
    }
    
    .status-danger {
        background: rgba(220, 53, 69, 0.1);
        color: var(--danger-color);
        border: 1px solid rgba(220, 53, 69, 0.2);
    }
    
    /* Apple-style File Upload */
    .apple-file-upload {
        background: var(--bg-secondary);
        border: 2px dashed var(--apple-blue);
        border-radius: var(--apple-radius-16);
        padding: var(--apple-space-32);
        text-align: center;
        transition: all 0.4s var(--apple-easing);
        cursor: pointer;
        position: relative;
        overflow: hidden;
        margin: var(--apple-space-16) 0;
    }
    
    .apple-file-upload:hover {
        border-color: var(--apple-blue-hover);
        background: rgba(0, 122, 255, 0.02);
        transform: translateY(-2px);
        box-shadow: var(--apple-shadow-medium);
    }
    
    .apple-file-upload.dragover {
        border-color: var(--apple-green);
        background: rgba(52, 199, 89, 0.05);
    }
    
    .apple-file-upload-icon {
        font-size: 48px;
        color: var(--apple-blue);
        margin-bottom: var(--apple-space-16);
        display: block;
    }
    
    .apple-file-upload-text {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--apple-space-8);
    }
    
    .apple-file-upload-subtext {
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin-bottom: var(--apple-space-24);
    }
    
    .apple-file-upload-button {
        display: inline-flex;
        align-items: center;
        gap: var(--apple-space-8);
        background: var(--apple-blue);
        color: white;
        padding: var(--apple-space-12) var(--apple-space-24);
        border-radius: var(--apple-radius-12);
        font-size: 0.9rem;
        font-weight: 600;
        text-decoration: none;
        border: none;
        cursor: pointer;
        transition: all 0.4s var(--apple-easing);
    }
    
    .apple-file-upload-button:hover {
        background: var(--apple-blue-hover);
        transform: scale(1.02);
    }
    
    .apple-file-status {
        margin-top: var(--apple-space-16);
        padding: var(--apple-space-16);
        border-radius: var(--apple-radius-12);
        text-align: left;
    }
    
    .apple-file-status.success {
        background: rgba(52, 199, 89, 0.1);
        border: 1px solid rgba(52, 199, 89, 0.3);
        color: var(--apple-green);
    }
    
    .apple-file-status.error {
        background: rgba(255, 59, 48, 0.1);
        border: 1px solid rgba(255, 59, 48, 0.3);
        color: var(--apple-red);
    }
    
    .apple-file-status-icon {
        display: inline-block;
        margin-right: var(--apple-space-8);
        font-size: 1.1rem;
    }
    
    /* Hide native Streamlit file uploader when using custom */
    .apple-file-upload-container .stFileUploader > label {
        display: none;
    }
    
    .apple-file-upload-container .stFileUploader > div {
        display: none;
    }
    
    /* Hide sidebar file uploader labels */
    .sidebar-file-upload .stFileUploader > label {
        display: none !important;
    }
    
    .sidebar-file-upload .stFileUploader > div[data-testid="stFileUploaderDropzone"] {
        display: none !important;
    }
    
    /* Make native uploader invisible but functional */
    .sidebar-file-upload .stFileUploader {
        display: none !important;
        position: absolute;
        opacity: 0;
        pointer-events: none;
        width: 1px;
        height: 1px;
        overflow: hidden;
    }
    
    .sidebar-file-upload .stFileUploader > div {
        display: none !important;
    }
    
    .sidebar-file-upload .stFileUploader label {
        display: none !important;
    }
    
    .sidebar-file-upload .stFileUploader input {
        position: absolute;
        left: -9999px;
        opacity: 0;
    }
    
    /* Apple Style File Upload Overrides */
    .stFileUploader {
        background: rgba(var(--apple-blue-rgb), 0.05) !important;
        border: 1px solid rgba(var(--apple-blue-rgb), 0.15) !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin: 12px 0 !important;
    }
    
    .stFileUploader > label {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: var(--apple-blue) !important;
        margin-bottom: 8px !important;
    }
    
    .stFileUploader > div[data-testid="stFileUploaderDropzone"] {
        border: 2px dashed rgba(var(--apple-blue-rgb), 0.3) !important;
        border-radius: 8px !important;
        padding: 24px 16px !important;
        text-align: center !important;
        background: var(--bg-primary) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
        cursor: pointer !important;
    }
    
    .stFileUploader > div[data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--apple-blue) !important;
        background: rgba(var(--apple-blue-rgb), 0.02) !important;
    }
    
    .stFileUploader > div[data-testid="stFileUploaderDropzone"] > div {
        color: var(--text-secondary) !important;
        font-size: 0.8rem !important;
    }
    
    .stFileUploader button {
        background: var(--apple-blue) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 6px 12px !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
    }
    
    .stFileUploader button:hover {
        background: var(--apple-blue-hover) !important;
        transform: scale(1.02) !important;
    }
    
    .sidebar-file-upload-header {
        display: flex;
        align-items: center;
        gap: var(--apple-space-8);
        margin-bottom: var(--apple-space-12);
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--apple-blue);
    }
    
    .sidebar-file-upload-area {
        border: 2px dashed rgba(var(--apple-blue-rgb), 0.3);
        border-radius: var(--apple-radius-8);
        padding: var(--apple-space-16);
        text-align: center;
        background: var(--bg-primary);
        transition: all 0.3s var(--apple-easing);
        cursor: pointer;
    }
    
    .sidebar-file-upload-area:hover {
        border-color: var(--apple-blue);
        background: rgba(var(--apple-blue-rgb), 0.02);
    }
    
    .sidebar-file-upload-icon {
        font-size: 24px;
        color: var(--apple-blue);
        margin-bottom: var(--apple-space-8);
    }
    
    .sidebar-file-upload-text {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-bottom: var(--apple-space-8);
    }
    
    .sidebar-file-upload-button {
        font-size: 0.75rem;
        padding: var(--apple-space-6) var(--apple-space-12);
        background: var(--apple-blue);
        color: white;
        border: none;
        border-radius: var(--apple-radius-8);
        font-weight: 500;
        cursor: pointer;
    }
    
    .status-info {
        background: rgba(23, 162, 184, 0.1);
        color: var(--info-color);
        border: 1px solid rgba(23, 162, 184, 0.2);
    }
    
    /* Apple Button System */
    .stButton > button,
    .apple-button {
        border-radius: var(--apple-radius-md) !important;
        border: none !important;
        padding: var(--apple-space-16) var(--apple-space-32) !important;
        font-size: 16px !important;
        line-height: 1.23 !important;
        font-weight: 500 !important;
        letter-spacing: -0.022em !important;
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
        cursor: pointer !important;
        position: relative !important;
        overflow: hidden !important;
        backdrop-filter: saturate(180%) blur(20px) !important;
        -webkit-backdrop-filter: saturate(180%) blur(20px) !important;
    }
    
    .stButton > button:hover,
    .apple-button:hover {
        transform: scale(1.05) !important;
        box-shadow: var(--shadow-elevated) !important;
    }
    
    .apple-button-primary {
        background: var(--accent-primary) !important;
        color: white !important;
    }
    
    .apple-button-secondary {
        background: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    .apple-button-ghost {
        background: transparent !important;
        color: var(--accent-primary) !important;
        border: 1px solid var(--accent-primary) !important;
    }
    
    /* Apple Navigation System */
    .css-1d391kg {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-color);
        backdrop-filter: saturate(180%) blur(20px);
        -webkit-backdrop-filter: saturate(180%) blur(20px);
    }
    
    /* Apple Top Navigation (Future Implementation) */
    .apple-nav {
        position: sticky;
        top: 0;
        z-index: 999;
        background: var(--bg-secondary);
        backdrop-filter: saturate(180%) blur(20px);
        -webkit-backdrop-filter: saturate(180%) blur(20px);
        border-bottom: 1px solid var(--border-color);
        padding: var(--apple-space-16) var(--apple-space-24);
        margin-bottom: var(--apple-space-48);
    }
    
    .apple-nav-container {
        max-width: 1024px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .apple-nav-logo {
        font-size: 24px;
        font-weight: 700;
        color: var(--text-primary);
        text-decoration: none;
    }
    
    .apple-nav-menu {
        display: flex;
        gap: var(--apple-space-32);
        align-items: center;
    }
    
    .apple-nav-item {
        color: var(--text-secondary);
        text-decoration: none;
        font-size: 16px;
        font-weight: 500;
        transition: color 0.3s ease;
    }
    
    .apple-nav-item:hover,
    .apple-nav-item.active {
        color: var(--accent-primary);
    }
    
    .css-1d391kg .stSelectbox > label {
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        font-size: 0.9rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    /* Compact Sidebar Messages */
    .sidebar-compact-status {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 4px 8px;
        margin: 4px 0;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .sidebar-compact-status.success {
        background: rgba(40, 167, 69, 0.1);
        color: var(--success-color);
        border: 1px solid rgba(40, 167, 69, 0.2);
    }
    
    .sidebar-compact-status.error {
        background: rgba(220, 53, 69, 0.1);
        color: var(--danger-color);
        border: 1px solid rgba(220, 53, 69, 0.2);
    }
    
    .sidebar-compact-status.info {
        background: rgba(23, 162, 184, 0.1);
        color: var(--info-color);
        border: 1px solid rgba(23, 162, 184, 0.2);
    }
    
    .sidebar-status-icon {
        font-size: 0.9rem;
        width: 12px;
        height: 12px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    
    .sidebar-section {
        margin-bottom: 1rem;
    }
    
    .sidebar-section-header {
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 8px;
        padding-left: 4px;
        border-left: 3px solid var(--primary-color);
    }
    
    /* Progress Indicators */
    .progress-container {
        background: var(--bg-tertiary);
        border-radius: 12px;
        padding: 4px;
        margin: 1rem 0;
    }
    
    .progress-bar {
        height: 8px;
        border-radius: 8px;
        background: linear-gradient(90deg, var(--primary-color), var(--info-color));
        transition: width 0.3s ease;
    }
    
    /* Apple Alert System */
    .apple-alert {
        display: flex;
        align-items: center;
        gap: var(--apple-space-16);
        padding: var(--apple-space-16) var(--apple-space-24);
        margin: var(--apple-space-16) 0;
        border-radius: var(--apple-radius-md);
        font-size: 16px;
        font-weight: 500;
        line-height: 1.47059;
        letter-spacing: -0.022em;
        box-shadow: var(--shadow-card);
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        position: relative;
        overflow: hidden;
        backdrop-filter: saturate(180%) blur(20px);
        -webkit-backdrop-filter: saturate(180%) blur(20px);
    }
    
    .custom-alert::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        opacity: 0.05;
        pointer-events: none;
    }
    
    .apple-alert.success {
        background: rgba(52, 199, 89, 0.1);
        border: 1px solid rgba(52, 199, 89, 0.2);
        color: var(--accent-success);
    }
    
    .apple-alert.error {
        background: rgba(255, 59, 48, 0.1);
        border: 1px solid rgba(255, 59, 48, 0.2);
        color: var(--accent-danger);
    }
    
    .apple-alert.warning {
        background: rgba(255, 149, 0, 0.1);
        border: 1px solid rgba(255, 149, 0, 0.2);
        color: var(--accent-warning);
    }
    
    .apple-alert.info {
        background: rgba(0, 122, 255, 0.1);
        border: 1px solid rgba(0, 122, 255, 0.2);
        color: var(--accent-primary);
    }
    
    .apple-alert-icon {
        font-size: 20px;
        min-width: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .apple-alert-content {
        flex: 1;
        line-height: 1.47059;
    }
    
    .alert-icon {
        font-size: 1.2rem;
        min-width: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .alert-content {
        flex: 1;
        line-height: 1.4;
    }
    
    .alert-title {
        font-weight: 600;
        margin-bottom: 4px;
    }
    
    .alert-message {
        font-size: 0.85rem;
        opacity: 0.9;
    }
    
    /* Compact Alert Variant */
    .custom-alert.compact {
        padding: 8px 12px;
        font-size: 0.8rem;
        margin: 4px 0;
    }
    
    .custom-alert.compact .alert-icon {
        font-size: 1rem;
        min-width: 16px;
    }
    
    /* Dark theme alert support */
    .dark-theme .custom-alert {
        background: var(--bg-secondary) !important;
        color: inherit !important;
    }
    
    .dark-theme .custom-alert.success {
        color: #4CAF50 !important;
        border-left-color: #4CAF50 !important;
    }
    
    .dark-theme .custom-alert.error {
        color: #F44336 !important;
        border-left-color: #F44336 !important;
    }
    
    .dark-theme .custom-alert.warning {
        color: #FF9800 !important;
        border-left-color: #FF9800 !important;
    }
    
    .dark-theme .custom-alert.info {
        color: #2196F3 !important;
        border-left-color: #2196F3 !important;
    }
    
    /* Form Enhancements */
    .stNumberInput > label,
    .stTextInput > label,
    .stSelectbox > label {
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div {
        border-radius: var(--border-radius) !important;
        border: 1px solid var(--border-color) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    /* Apple Responsive Design */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: var(--apple-space-16);
            padding-right: var(--apple-space-16);
            padding-top: var(--apple-space-32);
            padding-bottom: var(--apple-space-32);
        }
        
        .apple-card-hero {
            padding: var(--apple-space-32) var(--apple-space-24);
        }
        
        h1, .apple-hero {
            font-size: 36px;
            line-height: 1.125;
        }
        
        h2, .apple-title {
            font-size: 28px;
            line-height: 1.14;
        }
        
        .apple-metric-value {
            font-size: 42px;
        }
        
        .apple-nav-menu {
            display: none;
        }
        
        .apple-grid {
            gap: var(--apple-space-16);
        }
    }
    
    @media (max-width: 480px) {
        h1, .apple-hero {
            font-size: 28px;
        }
        
        .apple-card {
            padding: var(--apple-space-24);
        }
        
        .apple-metric-value {
            font-size: 32px;
        }
    }
    
    /* Apple Animations */
    @keyframes appleSlideUp {
        from {
            opacity: 0;
            transform: translateY(32px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes appleScale {
        from {
            opacity: 0;
            transform: scale(0.95);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes appleFloat {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-8px);
        }
    }
    
    .apple-animate-slideUp {
        animation: appleSlideUp 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }
    
    .apple-animate-scale {
        animation: appleScale 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }
    
    .apple-animate-float {
        animation: appleFloat 3s ease-in-out infinite;
    }
    
    /* Apple Micro-interactions */
    .apple-interactive {
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }
    
    .apple-interactive:hover {
        transform: translateY(-4px);
    }
    
    /* Custom Components */
    .data-card {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-lg);
        padding: 1.5rem;
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
        margin-bottom: 1.5rem;
    }
    
    .data-card:hover {
        box-shadow: var(--shadow-md);
    }
    
    .card-header {
        display: flex;
        justify-content: between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
    }
    
    .card-subtitle {
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin: 0.25rem 0 0 0;
    }
    </style>
    
    <script>
    // JavaScript for comprehensive dark theme detection
    (function() {
        function updateTheme() {
            const isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
            const streamlitRoot = document.querySelector('.stApp');
            const body = document.body;
            
            if (streamlitRoot) {
                if (isDark) {
                    streamlitRoot.classList.add('dark-theme');
                    body.classList.add('dark-theme');
                    
                    // Force dark theme styles
                    streamlitRoot.style.setProperty('--text-primary', '#E9ECEF', 'important');
                    streamlitRoot.style.setProperty('--bg-primary', '#212529', 'important');
                    streamlitRoot.style.background = 'linear-gradient(135deg, #343A40 0%, #495057 100%)';
                    streamlitRoot.style.color = '#E9ECEF';
                    
                    // Update all text elements
                    const textElements = streamlitRoot.querySelectorAll('h1, h2, h3, h4, h5, h6, p, span, div, label');
                    textElements.forEach(el => {
                        if (!el.style.color || el.style.color === 'rgb(33, 37, 41)' || el.style.color === '#212529') {
                            el.style.color = '#E9ECEF';
                        }
                    });
                    
                    // Fix main content background
                    const mainContent = streamlitRoot.querySelector('.main .block-container');
                    if (mainContent) {
                        mainContent.style.background = 'var(--bg-primary)';
                        mainContent.style.color = 'var(--text-primary)';
                    }
                } else {
                    streamlitRoot.classList.remove('dark-theme');
                    body.classList.remove('dark-theme');
                    
                    // Light theme main content
                    const mainContent = streamlitRoot.querySelector('.main .block-container');
                    if (mainContent) {
                        mainContent.style.background = '#FFFFFF';
                        mainContent.style.color = '#212529';
                    }
                }
            }
        }
        
        // Initial theme update
        updateTheme();
        
        // Listen for theme changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', updateTheme);
        }
        
        // Periodically check for new elements (Streamlit dynamic content)
        setInterval(updateTheme, 1000);
    })();
    </script>
    """
    st.markdown(css, unsafe_allow_html=True)


def load_enhanced_css():
    """Legacy function name for backward compatibility"""
    return load_apple_design_system()


class AppleComponents:
    """Apple-style UI components with premium aesthetics and smooth interactions"""
    
    @staticmethod
    def render_hero_section(title: str, description: str = None, icon: str = None):
        """Render Apple-style hero section with large typography"""
        icon_html = f'<span style="margin-right: var(--apple-space-16);">{icon}</span>' if icon else ''
        description_html = f'<p class="apple-body" style="font-size: 18px; color: var(--text-secondary); max-width: 600px; margin: 0 auto;">{description}</p>' if description else ''
        
        st.markdown(f"""
        <div class="apple-card-hero apple-animate-slideUp">
            <h1 class="apple-hero">{icon_html}{title}</h1>
            {description_html}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_apple_alert(message: str, alert_type: str = "info", icon: str = None):
        """Render Apple-style alert with beautiful styling"""
        if icon is None:
            icons = {
                "success": "✓",
                "error": "✕",
                "info": "ⓘ",
                "warning": "⚠"
            }
            icon = icons.get(alert_type, "ⓘ")
        
        st.markdown(f"""
        <div class="apple-alert {alert_type} apple-animate-scale">
            <div class="apple-alert-icon">{icon}</div>
            <div class="apple-alert-content">{message}</div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_section_header(title: str, subtitle: str = None):
        """Render Apple-style section header"""
        subtitle_html = f'<p class="apple-caption" style="margin-top: var(--apple-space-4);">{subtitle}</p>' if subtitle else ''
        
        st.markdown(f"""
        <div style="margin: var(--apple-space-64) 0 var(--apple-space-32) 0; text-align: center;">
            <h2 class="apple-title">{title}</h2>
            {subtitle_html}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_apple_grid(content_func, columns: int = 3, gap: str = "var(--apple-space-32)"):
        """Render content in Apple-style grid layout"""
        st.markdown(f'<div class="apple-grid apple-grid-{columns}" style="gap: {gap};">',
                   unsafe_allow_html=True)
        content_func()
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_apple_button_group(buttons: list, alignment: str = "left"):
        """Render Apple-style button group"""
        alignment_style = {
            "left": "justify-content: flex-start;",
            "center": "justify-content: center;",
            "right": "justify-content: flex-end;"
        }.get(alignment, "justify-content: flex-start;")
        
        st.markdown(f'<div style="display: flex; gap: var(--apple-space-16); {alignment_style} flex-wrap: wrap; margin: var(--apple-space-24) 0;">', unsafe_allow_html=True)
        cols = st.columns(len(buttons))
        for i, button_config in enumerate(buttons):
            with cols[i]:
                if isinstance(button_config, dict):
                    button_type = button_config.get('style', 'secondary')
                    css_class = f"apple-button-{button_type}"
                    st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                    st.button(
                        button_config.get('label', 'Button'),
                        key=button_config.get('key', f'apple_btn_{i}'),
                        help=button_config.get('help', ''),
                        disabled=button_config.get('disabled', False)
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.button(button_config, key=f'apple_btn_{i}')
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_apple_metrics(metrics: List[Dict[str, Any]], columns: int = 4):
        """Render metrics in Apple-style cards with premium aesthetics"""
        st.markdown(f'<div class="apple-grid apple-grid-{columns}">', unsafe_allow_html=True)
        
        cols = st.columns(columns)
        
        for i, metric in enumerate(metrics):
            with cols[i % columns]:
                value = metric.get('value', '0')
                label = metric.get('label', 'Metric')
                change = metric.get('change', None)
                change_type = metric.get('change_type', 'neutral')
                icon = metric.get('icon', '')
                
                change_html = ""
                if change:
                    change_class = f"apple-metric-change {change_type}"
                    change_symbol = "↗" if change_type == "positive" else "↘" if change_type == "negative" else "→"
                    change_html = f'<div class="{change_class}">{change_symbol} {change}</div>'
                
                icon_html = f'<div style="font-size: 24px; margin-bottom: var(--apple-space-8);">{icon}</div>' if icon else ''
                
                st.markdown(f"""
                <div class="apple-card apple-metric apple-interactive apple-animate-scale">
                    {icon_html}
                    <div class="apple-metric-value">{value}</div>
                    <div class="apple-metric-label">{label}</div>
                    {change_html}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_status_badge(status: str, text: str = None) -> str:
        """Generate HTML for status badge"""
        if text is None:
            text = status.title()
        
        status_class = f"status-badge status-{status}"
        return f'<span class="{status_class}">{text}</span>'
    
    @staticmethod
    def render_apple_card(title: str, content_func, subtitle: str = None, icon: str = None):
        """Render content in Apple-style card with beautiful styling"""
        icon_html = f'<span style="margin-right: var(--apple-space-8);">{icon}</span>' if icon else ''
        subtitle_html = f'<p class="apple-caption" style="margin-top: var(--apple-space-4);">{subtitle}</p>' if subtitle else ''
        
        st.markdown(f"""
        <div class="apple-card apple-interactive apple-animate-slideUp">
            <div style="margin-bottom: var(--apple-space-24);">
                <h3 class="apple-heading">{icon_html}{title}</h3>
                {subtitle_html}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Render the content
        content_func()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_enhanced_table(df: pd.DataFrame, title: str = None, searchable: bool = True):
        """Render enhanced data table with better styling"""
        if title:
            st.subheader(title)
        
        if searchable and not df.empty:
            search_term = st.text_input("🔍 Search", placeholder="Type to filter data...")
            if search_term:
                # Simple text-based filtering
                mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                df = df[mask]
        
        # Add custom styling to the dataframe
        if not df.empty:
            safe_dataframe(df, use_container_width=True)
        else:
            st.info("No data available")
    
    @staticmethod
    def render_progress_bar(value: float, max_value: float, label: str = "", color: str = "primary"):
        """Render enhanced progress bar"""
        percentage = min((value / max_value) * 100, 100) if max_value > 0 else 0
        
        color_map = {
            "primary": "#0066CC",
            "success": "#28A745", 
            "warning": "#FFC107",
            "danger": "#DC3545"
        }
        
        bar_color = color_map.get(color, color_map["primary"])
        
        st.markdown(f"""
        <div style="margin: 1rem 0;">
            {f'<div style="margin-bottom: 0.5rem; font-weight: 600;">{label}</div>' if label else ''}
            <div class="progress-container">
                <div class="progress-bar" style="width: {percentage}%; background: {bar_color};"></div>
            </div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.25rem;">
                {value:.2f} / {max_value:.2f} ({percentage:.1f}%)
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_alert_card(message: str, alert_type: str = "info", dismissible: bool = False):
        """Render enhanced alert card"""
        icons = {
            "success": "✅",
            "warning": "⚠️", 
            "error": "❌",
            "info": "ℹ️"
        }
        
        icon = icons.get(alert_type, "ℹ️")
        
        if alert_type == "success":
            st.success(f"{icon} {message}")
        elif alert_type == "warning":
            st.warning(f"{icon} {message}")
        elif alert_type == "error":
            st.error(f"{icon} {message}")
        else:
            st.info(f"{icon} {message}")
    
    @staticmethod
    def render_status_pill(text: str, status: str = "default", icon: str = None):
        """Render Apple-style status pill"""
        colors = {
            "success": "var(--accent-success)",
            "warning": "var(--accent-warning)",
            "error": "var(--accent-danger)",
            "info": "var(--accent-primary)",
            "default": "var(--text-tertiary)"
        }
        
        bg_colors = {
            "success": "rgba(52, 199, 89, 0.1)",
            "warning": "rgba(255, 149, 0, 0.1)",
            "error": "rgba(255, 59, 48, 0.1)",
            "info": "rgba(0, 122, 255, 0.1)",
            "default": "var(--bg-tertiary)"
        }
        
        color = colors.get(status, colors["default"])
        bg_color = bg_colors.get(status, bg_colors["default"])
        icon_html = f'<span style="margin-right: var(--apple-space-4);">{icon}</span>' if icon else ''
        
        st.markdown(f"""
        <span style="
            display: inline-flex;
            align-items: center;
            padding: var(--apple-space-4) var(--apple-space-8);
            border-radius: var(--apple-radius-sm);
            background: {bg_color};
            color: {color};
            font-size: 12px;
            font-weight: 500;
            letter-spacing: 0.066em;
            text-transform: uppercase;
        ">
            {icon_html}{text}
        </span>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_floating_action(icon: str, tooltip: str, onclick_key: str):
        """Render Apple-style floating action button"""
        st.markdown(f"""
        <style>
        .apple-fab {{
            position: fixed;
            bottom: var(--apple-space-32);
            right: var(--apple-space-32);
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: var(--accent-primary);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            box-shadow: var(--shadow-elevated);
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            z-index: 1000;
            backdrop-filter: saturate(180%) blur(20px);
            -webkit-backdrop-filter: saturate(180%) blur(20px);
        }}
        
        .apple-fab:hover {{
            transform: scale(1.1);
            box-shadow: 0 12px 48px rgba(0, 122, 255, 0.4);
        }}
        </style>
        <div class="apple-fab" title="{tooltip}">{icon}</div>
        """, unsafe_allow_html=True)
    
    @staticmethod 
    def render_apple_file_upload(title: str, description: str, file_type: str = "json", key: str = None):
        """Render Apple-style file upload component"""
        import streamlit as st
        
        # Create unique key if not provided
        if key is None:
            key = f"file_upload_{hash(title)}"
        
        # Create container with custom styling
        st.markdown(f"""
        <div class="apple-file-upload-container">
            <div class="apple-file-upload">
                <span class="apple-file-upload-icon">📁</span>
                <div class="apple-file-upload-text">{title}</div>
                <div class="apple-file-upload-subtext">{description}</div>
                <button class="apple-file-upload-button">
                    <span>📤</span>
                    파일 선택
                </button>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Hidden native uploader
        uploaded_file = st.file_uploader(
            label="",
            type=[file_type] if file_type else None,
            key=key
        )
        
        # Status display
        if uploaded_file is not None:
            st.markdown(f"""
            <div class="apple-file-status success">
                <span class="apple-file-status-icon">✅</span>
                <strong>{uploaded_file.name}</strong> ({uploaded_file.size:,} bytes)
            </div>
            """, unsafe_allow_html=True)
        
        return uploaded_file
    
    @staticmethod
    def render_sidebar_file_upload(title: str, description: str, file_type: str = "json", key: str = None, icon: str = "📁"):
        """Render compact Apple-style file upload for sidebar"""
        import streamlit as st
        
        # Create unique key if not provided  
        if key is None:
            key = f"sidebar_upload_{hash(title)}"
        
        # Apple style header
        st.markdown(f"""
        <div class="sidebar-file-upload-header" style="
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 12px;
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--apple-blue);
        ">
            <span>{icon}</span>
            <span>{title}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Native uploader with Apple styling
        uploaded_file = st.file_uploader(
            label=description,
            type=[file_type] if file_type else None, 
            key=key
        )
        
        # Show upload status with Apple styling
        if uploaded_file is not None:
            st.markdown(f"""
            <div style="
                margin-top: 8px; 
                padding: 8px 12px; 
                font-size: 0.75rem;
                background: rgba(52, 199, 89, 0.1);
                border: 1px solid rgba(52, 199, 89, 0.3);
                color: var(--apple-green);
                border-radius: 8px;
            ">
                <span style="margin-right: 8px;">✅</span>
                <strong>{uploaded_file.name}</strong>
                <span style="color: var(--text-secondary); margin-left: 4px;">
                    ({uploaded_file.size:,} bytes)
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        return uploaded_file


class EnhancedComponents(AppleComponents):
    """Legacy enhanced components - now inherits from AppleComponents for backward compatibility"""
    
    @staticmethod
    def render_sidebar_section_header(title: str):
        """Render compact sidebar section header - Legacy compatibility"""
        st.markdown(f"""
        <div class="apple-label" style="margin: var(--apple-space-16) 0 var(--apple-space-8) 0; padding-left: 4px; border-left: 3px solid var(--accent-primary); font-size: 0.9rem; font-weight: 600; color: var(--text-primary);">{title}</div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_compact_sidebar_status(message: str, status_type: str = "info", icon: str = None):
        """Render compact sidebar status message - Legacy compatibility"""
        if icon is None:
            icons = {
                "success": "✓",
                "error": "✗", 
                "info": "●",
                "warning": "⚠"
            }
            icon = icons.get(status_type, "●")
        
        colors = {
            "success": "var(--accent-success)",
            "error": "var(--accent-danger)",
            "warning": "var(--accent-warning)",
            "info": "var(--accent-primary)"
        }
        
        bg_colors = {
            "success": "rgba(52, 199, 89, 0.1)",
            "error": "rgba(255, 59, 48, 0.1)",
            "warning": "rgba(255, 149, 0, 0.1)",
            "info": "rgba(0, 122, 255, 0.1)"
        }
        
        color = colors.get(status_type, colors["info"])
        bg_color = bg_colors.get(status_type, bg_colors["info"])
        
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 4px 8px;
            margin: 4px 0;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 500;
            background: {bg_color};
            color: {color};
            border: 1px solid {color}33;
        ">
            <span style="font-size: 0.9rem; width: 12px; height: 12px; display: inline-flex; align-items: center; justify-content: center;">{icon}</span>
            <span>{message}</span>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_enhanced_table(df: pd.DataFrame, title: str = None, searchable: bool = True):
        """Render enhanced data table with better styling - Legacy compatibility"""
        if title:
            st.subheader(title)
        
        if searchable and not df.empty:
            search_term = st.text_input("🔍 Search", placeholder="Type to filter data...")
            if search_term:
                # Simple text-based filtering
                mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                df = df[mask]
        
        # Add custom styling to the dataframe
        if not df.empty:
            safe_dataframe(df, use_container_width=True)
        else:
            st.info("No data available")
    
    @staticmethod
    def render_alert_card(message: str, alert_type: str = "info", dismissible: bool = False):
        """Render enhanced alert card - Legacy compatibility"""
        AppleComponents.render_apple_alert(message, alert_type)
    
    @staticmethod
    def render_metric_cards(metrics: List[Dict[str, Any]], columns: int = 4):
        """Render metrics in beautiful card format - Legacy compatibility"""
        AppleComponents.render_apple_metrics(metrics, columns)
    
    @staticmethod
    def render_page_header(title: str, description: str, icon: str = "📊"):
        """Render enhanced page header with consistent styling - Legacy compatibility"""
        AppleComponents.render_section_header(title, description)
    
    @staticmethod
    def render_data_card(title: str, content_func, subtitle: str = None, actions: List[str] = None):
        """Render content in an enhanced card format - Legacy compatibility"""
        AppleComponents.render_apple_card(title, content_func, subtitle)
    
    @staticmethod
    def render_centered_container(content_func, max_width: str = "1100px"):
        """Render content in a centered container - Legacy compatibility"""
        st.markdown(f'<div style="max-width: {max_width}; margin: 0 auto; padding: 0 1rem;">', 
                   unsafe_allow_html=True)
        content_func()
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_custom_alert(message: str, alert_type: str = "info", title: str = None, compact: bool = False):
        """Render beautiful custom alert with better styling - Legacy compatibility"""
        AppleComponents.render_apple_alert(message, alert_type)
    
    @staticmethod
    def render_inline_alert(message: str, alert_type: str = "info"):
        """Render compact inline alert for forms and buttons - Legacy compatibility"""
        AppleComponents.render_apple_alert(message, alert_type)


class AppleCharts:
    """Enhanced chart components with better aesthetics"""
    
    @staticmethod
    def create_usage_dashboard_chart(data: pd.DataFrame, title: str = "Usage Overview") -> go.Figure:
        """Create enhanced usage dashboard chart"""
        fig = px.bar(
            data, 
            x="date", 
            y="Total Usage ($)",
            color="model",
            title=title,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        # Enhanced styling
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Inter",
            title_font_size=20,
            title_font_color="#212529",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=0, r=0, t=60, b=0)
        )
        
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.1)',
            showline=True,
            linewidth=1,
            linecolor='rgba(0,0,0,0.2)'
        )
        
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.1)',
            showline=True,
            linewidth=1,
            linecolor='rgba(0,0,0,0.2)'
        )
        
        return fig
    
    @staticmethod
    def create_budget_overview_chart(budget_data: Dict, usage_data: Dict) -> go.Figure:
        """Create enhanced budget vs usage chart"""
        projects = list(budget_data.keys())
        budgets = list(budget_data.values())
        usage = [usage_data.get(p, 0) for p in projects]
        
        fig = go.Figure()
        
        # Budget bars
        fig.add_trace(go.Bar(
            name='Budget',
            x=projects,
            y=budgets,
            marker_color='rgba(0, 102, 204, 0.7)',
            text=[f'${b:.2f}' for b in budgets],
            textposition='auto',
        ))
        
        # Usage bars
        fig.add_trace(go.Bar(
            name='Usage',
            x=projects,
            y=usage,
            marker_color='rgba(40, 167, 69, 0.7)',
            text=[f'${u:.2f}' for u in usage],
            textposition='auto',
        ))
        
        fig.update_layout(
            title="Budget vs Actual Usage",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Inter",
            title_font_size=20,
            title_font_color="#212529",
            barmode='group',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig


class AppleForms:
    """Enhanced form components with better UX"""
    
    @staticmethod
    def render_budget_form(projects: List[Dict], current_budgets: Dict):
        """Render enhanced budget setting form"""
        st.markdown("### 💳 Budget Configuration")
        
        with st.expander("🎯 Individual Project Budgets", expanded=True):
            for project in projects:
                if project.get("status") == "active" and project.get("name", "").lower() != "default project":
                    project_id = project["id"]
                    project_name = project["name"]
                    current_budget = current_budgets.get(project_id, 0.0)
                    
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.text(f"📋 {project_name}")
                        
                    with col2:
                        budget = st.number_input(
                            "Monthly Budget ($)",
                            min_value=0.0,
                            max_value=10000.0,
                            value=float(current_budget),
                            step=10.0,
                            key=f"budget_enhanced_{project_id}",
                            label_visibility="collapsed"
                        )
                        
                    with col3:
                        if st.button("💾", key=f"save_enhanced_{project_id}", help="Save budget"):
                            st.success(f"Budget saved: ${budget:.2f}")
                        
                        if st.button("🗑️", key=f"delete_enhanced_{project_id}", help="Delete budget"):
                            st.warning(f"Budget deleted for {project_name}")
    
    @staticmethod
    def render_confirmation_dialog(title: str, message: str, confirm_key: str, cancel_key: str):
        """Render enhanced confirmation dialog"""
        st.markdown(f"""
        <div class="data-card" style="border-left: 4px solid var(--danger-color); background: rgba(220, 53, 69, 0.05);">
            <div class="card-header">
                <h3 class="card-title">⚠️ {title}</h3>
            </div>
            <p>{message}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            confirm = st.button("✅ Confirm", key=confirm_key, type="primary")
        
        with col2:
            cancel = st.button("❌ Cancel", key=cancel_key)
        
        return confirm, cancel


# Example usage functions
def demo_apple_dashboard():
    """Demo function showing Apple-style dashboard"""
    load_apple_design_system()
    
    # Hero section
    AppleComponents.render_hero_section(
        "OpenAI Usage Tracker",
        "Monitor API usage, manage budgets, and optimize performance across your organization with enterprise-grade insights.",
        "🚀"
    )
    
    # Metric cards
    metrics = [
        {"value": "$2,431", "label": "Total Cost", "change": "+12.5%", "change_type": "positive", "icon": "💰"},
        {"value": "89%", "label": "Budget Used", "change": "+5%", "change_type": "warning", "icon": "📊"},
        {"value": "12", "label": "Active Projects", "change": "0", "change_type": "neutral", "icon": "📋"},
        {"value": "3.4K", "label": "API Requests", "change": "+23%", "change_type": "positive", "icon": "⚡"},
    ]
    
    AppleComponents.render_apple_metrics(metrics, columns=4)
    
    # Section header
    AppleComponents.render_section_header(
        "Project Overview",
        "Detailed breakdown of budget utilization and performance metrics across all active projects"
    )
    
    # Sample data in Apple card
    def render_sample_data():
        sample_data = pd.DataFrame({
            'Project': ['Project Alpha', 'Project Beta', 'Project Gamma'],
            'Budget': ['$500.00', '$300.00', '$200.00'],
            'Used': ['$480.00', '$150.00', '$220.00'],
            'Status': ['⚠️ Warning', '✅ Good', '🔴 Over'],
        })
        safe_dataframe(sample_data, use_container_width=True)
    
    AppleComponents.render_apple_card(
        "Budget Status",
        render_sample_data,
        subtitle="Real-time monitoring of budget utilization",
        icon="💳"
    )


def demo_enhanced_dashboard():
    """Legacy demo function - redirects to Apple demo"""
    return demo_apple_dashboard()


if __name__ == "__main__":
    demo_enhanced_dashboard()