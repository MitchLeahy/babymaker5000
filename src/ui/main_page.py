"""
Main page UI component for Baby Maker 5000
"""

import streamlit as st
import io
from PIL import Image
import os
from datetime import datetime

# Import our services
from src.services.replicate_service import replicate_service

def save_uploaded_file(uploaded_file, folder="temp_uploads"):
    """Save uploaded file temporarily and return path"""
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    file_path = os.path.join(folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def save_generated_image(image_url, filename, folder="generated_images"):
    """Download and save generated image locally"""
    import requests
    
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        
        file_path = os.path.join(folder, filename)
        with open(file_path, "wb") as f:
            f.write(response.content)
        return file_path
    except Exception as e:
        st.error(f"Error saving image: {e}")
        return None

def main_page():
    """Main page layout and functionality"""
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(90deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%); border-radius: 10px; margin-bottom: 2rem;">
        <h1>🍼 Baby Maker 5000 🍼</h1>
        <p style="font-size: 1.2em; margin: 0;">Create adorable baby photos and family portraits with AI!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("ℹ️ About")
        st.write("""
        Baby Maker 5000 uses advanced AI to:
        - Generate baby photos from parent images
        - Create beautiful family portraits
        - Store all images securely
        """)
        
        st.header("🔧 Status")
        # Test Replicate connection
        if replicate_service.test_connection():
            st.success("✅ Replicate AI Ready!")
        else:
            st.error("❌ Replicate not configured. Please set REPLICATE_API_TOKEN in your .env file.")
        
        st.header("⚙️ Generation Settings")
        
        # Identity Preservation Settings
        st.subheader("🎭 Identity & Style")
        style_strength = st.slider(
            "Identity Preservation", 
            min_value=15, max_value=50, value=25,
            help="Lower = more parent features preserved, Higher = more artistic freedom"
        )
        
        style_name = st.selectbox(
            "Photo Style",
            options=[
                "Photographic (Default)",
                "Cinematic",
                "Disney Charactor",
                "Digital Art",
                "Fantasy art",
                "Neonpunk",
                "Enhance",
                "Comic book",
                "Lowpoly",
                "Line art"
            ],
            index=0,
            help="Choose the artistic style for generation"
        )
        
        # Quality Settings
        st.subheader("🎨 Quality Controls")
        num_steps = st.slider(
            "Quality Steps", 
            min_value=20, max_value=100, value=50,
            help="More steps = higher quality but slower generation"
        )
        
        guidance_scale = st.slider(
            "Prompt Adherence",
            min_value=1.0, max_value=10.0, value=5.0, step=0.5,
            help="How closely to follow the text prompt (higher = more literal)"
        )
        
        num_outputs = st.selectbox(
            "Number of Images",
            options=[1, 2, 3, 4],
            index=0,
            help="Generate multiple variations (costs more)"
        )
        
        # Advanced Settings
        with st.expander("🔬 Advanced Settings"):
            seed = st.number_input(
                "Seed (for reproducibility)",
                min_value=-1, max_value=2147483647, value=-1,
                help="Use -1 for random, or set a number for reproducible results"
            )
            
            enable_safety_checker = st.checkbox(
                "Enable Safety Checker",
                value=True,
                help="Filter potentially inappropriate content"
            )
            
            disable_safety_checker = not enable_safety_checker
        
        # Baby-specific settings
        st.subheader("👶 Baby Settings")
        baby_age = st.selectbox(
            "Baby Age Range",
            options=[
                "Newborn (0-3 months)",
                "Infant (3-6 months)", 
                "Baby (6-12 months)",
                "Toddler (12-24 months)"
            ],
            index=2,
            help="Preferred age range for the generated baby"
        )
        
        baby_expression = st.selectbox(
            "Baby Expression",
            options=[
                "Smiling",
                "Peaceful/Sleeping",
                "Curious/Alert",
                "Laughing",
                "Natural/Candid"
            ],
            index=0,
            help="Preferred facial expression for the baby"
        )
        
        # Family Portrait Settings
        st.subheader("👨‍👩‍👧‍👦 Family Settings")
        family_pose = st.selectbox(
            "Family Pose Style",
            options=[
                "Classic Portrait (formal)",
                "Casual & Natural",
                "Parents holding baby",
                "Outdoor family shot",
                "Studio portrait"
            ],
            index=1,
            help="Style of family portrait composition"
        )
        
        background_style = st.selectbox(
            "Background Style",
            options=[
                "Clean white studio",
                "Soft neutral colors",
                "Natural outdoor setting",
                "Warm home environment",
                "Professional studio"
            ],
            index=0,
            help="Background setting for the portraits"
        )
    
    # Main content
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("👨 Parent 1")
        parent1_file = st.file_uploader(
            "Upload first parent's photo",
            type=['png', 'jpg', 'jpeg'],
            key="parent1"
        )
        
        if parent1_file:
            st.image(parent1_file, caption="Parent 1", use_column_width=True)
    
    with col2:
        st.header("👩 Parent 2")
        parent2_file = st.file_uploader(
            "Upload second parent's photo",
            type=['png', 'jpg', 'jpeg'],
            key="parent2"
        )
        
        if parent2_file:
            st.image(parent2_file, caption="Parent 2", use_column_width=True)
    
    # Generation section
    if parent1_file and parent2_file:
        st.markdown("---")
        
        # Custom prompt option
        with st.expander("🎨 Customize Generation (Optional)"):
            custom_baby_prompt = st.text_area(
                "Custom baby prompt (leave empty for default)",
                placeholder="e.g., smiling, outdoor setting, wearing cute outfit..."
            )
            custom_family_prompt = st.text_area(
                "Custom family portrait prompt (leave empty for default)",
                placeholder="e.g., parents holding baby in a park, professional studio portrait, casual outdoor setting..."
            )
        
        # Generation buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            generate_all = st.button("🎨 Generate Baby & Family Portrait", use_container_width=True, type="primary")
        
        # Handle complete generation workflow
        if generate_all:
            if not replicate_service.test_connection():
                st.error("❌ Please configure your REPLICATE_API_TOKEN in the .env file first!")
            else:
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Save uploaded files temporarily
                    parent1_path = save_uploaded_file(parent1_file)
                    parent2_path = save_uploaded_file(parent2_file)
                    
                    # Step 1: Generate Baby
                    status_text.text("🎨 Step 1/2: Creating your baby... (10-15 seconds)")
                    progress_bar.progress(25)
                    
                    # Build enhanced baby prompt
                    baby_age_text = {
                        "Newborn (0-3 months)": "newborn baby (0-3 months old)",
                        "Infant (3-6 months)": "infant baby (3-6 months old)", 
                        "Baby (6-12 months)": "baby (6-12 months old)",
                        "Toddler (12-24 months)": "toddler (12-24 months old)"
                    }[baby_age]
                    
                    expression_text = {
                        "Smiling": "with a bright, happy smile",
                        "Peaceful/Sleeping": "with a peaceful, serene expression",
                        "Curious/Alert": "with curious, alert eyes",
                        "Laughing": "laughing joyfully",
                        "Natural/Candid": "with a natural, candid expression"
                    }[baby_expression]
                    
                    background_text = {
                        "Clean white studio": "clean white studio background",
                        "Soft neutral colors": "soft, neutral colored background",
                        "Natural outdoor setting": "natural outdoor setting",
                        "Warm home environment": "warm, cozy home environment",
                        "Professional studio": "professional studio setting"
                    }[background_style]
                    
                    enhanced_baby_prompt = f"a cute {baby_age_text} img {expression_text}, {background_text}"
                    if custom_baby_prompt.strip():
                        enhanced_baby_prompt += f", {custom_baby_prompt.strip()}"
                    
                    baby_url = replicate_service.generate_with_photomaker(
                        input_images=[parent1_path, parent2_path],
                        prompt=enhanced_baby_prompt,
                        style_strength=style_strength,
                        num_steps=num_steps,
                        style_name=style_name,
                        num_outputs=num_outputs,
                        guidance_scale=guidance_scale,
                        seed=seed if seed != -1 else None,
                        disable_safety_checker=disable_safety_checker
                    )
                    
                    if not baby_url:
                        st.error("❌ Failed to generate baby. Please try again.")
                        return
                    
                    # Handle multiple outputs
                    if isinstance(baby_url, list):
                        baby_urls = baby_url
                        baby_url = baby_urls[0]  # Use first one for family portrait
                    else:
                        baby_urls = [baby_url]
                    
                    progress_bar.progress(50)
                    
                    # Save baby image(s)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    baby_paths = []
                    for i, url in enumerate(baby_urls):
                        baby_filename = f"baby_{timestamp}_{i+1}.png" if len(baby_urls) > 1 else f"baby_{timestamp}.png"
                        baby_path = save_generated_image(url, baby_filename)
                        baby_paths.append((url, baby_path, baby_filename))
                    
                    # Store in session state
                    st.session_state.baby_urls = baby_urls
                    st.session_state.baby_paths = baby_paths
                    
                    # Step 2: Generate Family Portrait
                    status_text.text("🎨 Step 2/2: Creating family portrait... (10-15 seconds)")
                    progress_bar.progress(75)
                    
                    # Build enhanced family prompt
                    pose_text = {
                        "Classic Portrait (formal)": "classic formal family portrait",
                        "Casual & Natural": "casual, natural family photo",
                        "Parents holding baby": "parents lovingly holding their baby",
                        "Outdoor family shot": "outdoor family photograph",
                        "Studio portrait": "professional studio family portrait"
                    }[family_pose]
                    
                    enhanced_family_prompt = f"a beautiful {pose_text} with people img, {background_text}"
                    if custom_family_prompt.strip():
                        enhanced_family_prompt += f", {custom_family_prompt.strip()}"
                    
                    family_url = replicate_service.generate_with_photomaker(
                        input_images=[parent1_path, parent2_path, baby_url],
                        prompt=enhanced_family_prompt,
                        style_strength=style_strength,
                        num_steps=num_steps,
                        style_name=style_name,
                        num_outputs=1,  # Always generate 1 family portrait
                        guidance_scale=guidance_scale,
                        seed=seed if seed != -1 else None,
                        disable_safety_checker=disable_safety_checker
                    )
                    
                    if family_url:
                        if isinstance(family_url, list):
                            family_url = family_url[0]
                            
                        # Save family image
                        family_filename = f"family_{timestamp}.png"
                        family_path = save_generated_image(family_url, family_filename)
                        
                        # Store in session state
                        st.session_state.family_url = family_url
                        st.session_state.family_path = (family_url, family_path, family_filename)
                        
                        progress_bar.progress(100)
                        status_text.text("🎉 Generation complete!")
                        
                        # Display results
                        st.success("🎉 Baby and family portrait generated successfully!")
                        
                        # Show results
                        if len(baby_urls) == 1:
                            # Single baby + family portrait
                            col1, col2 = st.columns(2)
                            with col1:
                                st.subheader("👶 Your AI Baby")
                                st.image(baby_urls[0], use_column_width=True)
                                
                                # Download button for baby
                                _, baby_path, baby_filename = baby_paths[0]
                                if baby_path and os.path.exists(baby_path):
                                    with open(baby_path, "rb") as file:
                                        st.download_button(
                                            label="📥 Download Baby Photo",
                                            data=file.read(),
                                            file_name=baby_filename,
                                            mime="image/png",
                                            key="download_baby"
                                        )
                            
                            with col2:
                                st.subheader("👨‍👩‍👧‍👦 Family Portrait")
                                st.image(family_url, use_column_width=True)
                                
                                # Download button for family
                                if family_path and os.path.exists(family_path):
                                    with open(family_path, "rb") as file:
                                        st.download_button(
                                            label="📥 Download Family Portrait",
                                            data=file.read(),
                                            file_name=family_filename,
                                            mime="image/png",
                                            key="download_family"
                                        )
                        else:
                            # Multiple baby variations + family portrait
                            st.subheader("👶 Your AI Baby Variations")
                            cols = st.columns(len(baby_urls))
                            for i, (url, (_, baby_path, baby_filename)) in enumerate(zip(baby_urls, baby_paths)):
                                with cols[i]:
                                    st.image(url, caption=f"Baby #{i+1}", use_column_width=True)
                                    if baby_path and os.path.exists(baby_path):
                                        with open(baby_path, "rb") as file:
                                            st.download_button(
                                                label=f"📥 Download #{i+1}",
                                                data=file.read(),
                                                file_name=baby_filename,
                                                mime="image/png",
                                                key=f"download_baby_{i}"
                                            )
                            
                            st.subheader("👨‍👩‍👧‍👦 Family Portrait")
                            st.image(family_url, use_column_width=True)
                            
                            # Download button for family
                            if family_path and os.path.exists(family_path):
                                with open(family_path, "rb") as file:
                                    st.download_button(
                                        label="📥 Download Family Portrait",
                                        data=file.read(),
                                        file_name=family_filename,
                                        mime="image/png",
                                        key="download_family"
                                    )
                    else:
                        st.error("❌ Failed to generate family portrait, but baby was created successfully!")
                        # Still show the baby(ies)
                        if len(baby_urls) == 1:
                            st.subheader("👶 Your AI Baby")
                            st.image(baby_urls[0], use_column_width=True)
                        else:
                            st.subheader("👶 Your AI Baby Variations")
                            cols = st.columns(len(baby_urls))
                            for i, url in enumerate(baby_urls):
                                with cols[i]:
                                    st.image(url, caption=f"Baby #{i+1}", use_column_width=True)
                    
                    # Clean up temp files
                    try:
                        os.remove(parent1_path)
                        os.remove(parent2_path)
                    except:
                        pass
                        
                except Exception as e:
                    st.error(f"❌ Error during generation: {str(e)}")
                    progress_bar.empty()
                    status_text.empty()
    
    else:
        st.info("👆 Please upload photos of both parents to get started!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🍼 Baby Maker 5000 - Powered by Replicate PhotoMaker AI</p>
        <p><small>For entertainment purposes only. Results may vary.</small></p>
    </div>
    """, unsafe_allow_html=True) 