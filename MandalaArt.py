import streamlit as st
import openai
import requests
from PIL import Image
import io
import base64
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Mandala Art Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E2E2E;
        font-size: 3rem;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }
    .stButton > button {
        background: linear-gradient(45deg, #2E2E2E, #4A4A4A);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        border-radius: 25px;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .download-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def create_openai_client(api_key):
    """Create OpenAI client with provided API key"""
    try:
        client = openai.OpenAI(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"❌ Error with API key: {str(e)}")
        return None

def generate_mandala_prompt(inspiration_word):
    """Generate a detailed prompt for DALL-E 3 based on the inspiration word"""
    prompt = f"""Create a beautiful, intricate black and white mandala design inspired by the word '{inspiration_word}'. 
    The mandala should be:
    - Completely black and white (no colors, no grayscale - pure black lines on white background)
    - Perfectly symmetrical and circular
    - Featuring intricate geometric patterns, sacred geometry, and detailed ornamental elements
    - Incorporating symbolic elements related to '{inspiration_word}'
    - High contrast with crisp, clean lines
    - Suitable for meditation and coloring
    - Professional quality with fine details
    - Centered on a pure white background
    
    Style: Traditional mandala art, spiritual, meditative, geometric, ornate, detailed line art"""
    
    return prompt

def generate_mandala_image(api_key, inspiration_word):
    """Generate mandala image using DALL-E 3"""
    try:
        client = create_openai_client(api_key)
        if not client:
            return None, None
            
        prompt = generate_mandala_prompt(inspiration_word)
        
        with st.spinner(f"🎨 Creating your '{inspiration_word}' mandala... This may take a few moments"):
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
        
        image_url = response.data[0].url
        
        # Download the image
        img_response = requests.get(image_url)
        img_response.raise_for_status()
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(img_response.content))
        
        return image, prompt
        
    except Exception as e:
        st.error(f"❌ Error generating image: {str(e)}")
        return None, None

def get_image_download_link(image, filename):
    """Generate download link for the image"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f'<a href="data:image/png;base64,{img_str}" download="{filename}" style="text-decoration: none;"><button style="background: linear-gradient(45deg, #28a745, #20c997); color: white; border: none; padding: 0.75rem 2rem; font-size: 1.1rem; border-radius: 25px; cursor: pointer; transition: all 0.3s ease;">📥 Download Mandala</button></a>'

def main():
    # Header
    st.markdown('<h1 class="main-header">🎨 Mandala Art Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Transform any word into a beautiful black and white mandala using AI</p>', unsafe_allow_html=True)
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 💭 Your Inspiration")
        
        # API Key input
        api_key = st.text_input(
            "🔑 Enter your OpenAI API Key:",
            type="password",
            placeholder="sk-...",
            help="Get your API key from https://platform.openai.com/api-keys"
        )
        
        # Word input
        inspiration_word = st.text_input(
            "💡 Enter a word that inspires you:",
            placeholder="e.g., peace, love, nature, wisdom, strength...",
            max_chars=50
        )
        
        # Generate button
        can_generate = api_key.strip() and inspiration_word.strip()
        
        if st.button("🎨 Generate Mandala", disabled=not can_generate):
            if can_generate:
                # Generate image without storing API key
                image, prompt = generate_mandala_image(api_key, inspiration_word.strip())
                
                if image:
                    st.session_state.current_image = image
                    st.session_state.current_prompt = prompt
                    st.session_state.current_word = inspiration_word.strip()
                    st.success(f"✨ Your '{inspiration_word}' mandala is ready!")
                    st.rerun()
        
        # Show requirements if missing
        if not api_key.strip() or not inspiration_word.strip():
            st.info("👆 Please enter both your API key and inspiration word to generate a mandala")
        
        # API Key help section
        with st.expander("🔧 How to get your OpenAI API Key"):
            st.markdown("""
            1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
            2. Sign in or create an account
            3. Click "Create new secret key"
            4. Copy the key and paste it above
            5. Make sure you have credits in your OpenAI account
            
            **Note:** Your API key is never stored and is only used for this generation.
            """)
        
        # Display generation settings
        with st.expander("⚙️ Generation Settings"):
            st.markdown("""
            **Model:** DALL-E 3  
            **Size:** 1024x1024 pixels  
            **Style:** Black and white mandala  
            **Quality:** Standard  
            """)
    
    with col2:
        st.markdown("### 🖼️ Your Mandala")
        
        # Display generated image
        if hasattr(st.session_state, 'current_image') and st.session_state.current_image:
            image = st.session_state.current_image
            word = st.session_state.current_word
            
            # Display image
            st.image(image, caption=f"Mandala inspired by: {word}", use_container_width=True)
            
            # Download section
            st.markdown('<div class="download-section">', unsafe_allow_html=True)
            st.markdown("### 📥 Download Your Mandala")
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mandala_{word}_{timestamp}.png"
            
            # Download button
            download_link = get_image_download_link(image, filename)
            st.markdown(download_link, unsafe_allow_html=True)
            
            # Image info
            st.markdown(f"""
            **Filename:** {filename}  
            **Format:** PNG  
            **Size:** {image.size[0]}x{image.size[1]} pixels  
            **Inspiration:** {word}
            """)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Show prompt used (expandable)
            if hasattr(st.session_state, 'current_prompt'):
                with st.expander("🔍 View AI Prompt Used"):
                    st.text_area("Prompt sent to DALL-E 3:", st.session_state.current_prompt, height=150)
        else:
            st.info("👈 Enter your API key and inspiration word, then click 'Generate Mandala' to create your artwork")
            
            # Show example
            st.markdown("### 🌟 Example Mandalas")
            st.markdown("""
            Try these inspiring words:
            - **Peace** - Flowing, calm patterns
            - **Nature** - Organic, leaf-like designs  
            - **Wisdom** - Ancient, symbolic elements
            - **Love** - Heart-centered, warm patterns
            - **Strength** - Bold, powerful geometry
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("### 💡 Tips for Better Results")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🎯 Choose Meaningful Words**
        - Abstract concepts work well
        - Emotions and feelings
        - Nature elements
        """)
    
    with col2:
        st.markdown("""
        **🖨️ Printing Tips**
        - Use high-quality paper
        - Print in actual size
        - Perfect for coloring books
        """)
    
    with col3:
        st.markdown("""
        **💝 Usage Ideas**
        - Meditation and mindfulness
        - Adult coloring books
        - Wall art and decoration
        """)
    
    # Security note
    st.markdown("---")
    st.markdown("🔒 **Privacy Note:** Your API key is never stored and is only used temporarily for image generation.")

if __name__ == "__main__":
    main()