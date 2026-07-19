import streamlit as st
import requests
import random  # Task 4: Import random module

st.title("The AI Image Studio")

# Sidebar - General Settings
st.sidebar.header("General Settings")
artstyle = st.sidebar.selectbox(
    "Select Art style",
    ["Photorealistic", "Anime", "Sketch", "3D Render"]
)

width = st.sidebar.slider("Image width", min_value=256, max_value=1024, value=768)
height = st.sidebar.slider("Image Height", min_value=256, max_value=1024, value=768)

# Task 3: Add the "Magic Enhance" toggle in the sidebar
magic_enhance = st.sidebar.checkbox(" ✨ Enable Magic Enhance")

# Main UI Prompts
user_prompt = st.text_input("Describe your masterpiece:")

# Task 4: Create a list of 5 creative surprise prompts
surprise_prompts = [
    "An astronaut riding a horse on Mars",
    "A cyberpunk street food vendor in Tokyo neon alley",
    "A cute baby dragon sleeping inside a teacup",
    "A majestic floating castle surrounded by waterfalls and clouds",
    "An ancient library where books are literally flying around"
]

# Create two columns so the buttons sit neatly side-by-side
col1, col2 = st.columns(2)

with col1:
    generate_clicked = st.button("Generate Image")

with col2:
    surprise_clicked = st.button("Surprise Me!")

# Set up the logic to determine which prompt to use
final_prompt = ""
should_generate = False

if generate_clicked:
    if user_prompt:
        final_prompt = f"{user_prompt}, art style: {artstyle}"
        should_generate = True
    else:
        st.warning("Please provide a description or click 'Surprise Me!'")

elif surprise_clicked:
    # Task 4: Pick a random prompt if "Surprise Me!" is clicked
    random_prompt = random.choice(surprise_prompts)
    final_prompt = f"{random_prompt}, art style: {artstyle}"
    st.info(f" Surprise prompt selected: **{random_prompt}**")
    should_generate = True

# Generation Logic Loop
if should_generate:
    with st.spinner("Rendering the image..."):
        # Task 3: Secretly append boost words if "Magic Enhance" is checked
        if magic_enhance:
            final_prompt += ", masterpiece, 8k resolution, highly detailed, trending on artstation, unreal engine 5 render"
        
        # Task 1: Append width and height to the end using standard HTTP parameters
        url = f"https://image.pollinations.ai/prompt/{final_prompt}?width={width}&height={height}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                st.success("Image generated successfully!")
                st.image(response.content, caption=final_prompt)
                
                # Task 2 & Bonus: Make the download file name dynamic with .png extension
                dynamic_file_name = f"{artstyle.lower().replace(' ', '_')}_image.png"
                
                st.download_button(
                    label="Download Image",
                    data=response.content,
                    file_name=dynamic_file_name,
                    mime="image/png"
                )
            else:
                st.error("API is currently unavailable. Please try again.")
        except Exception as e:
            st.error(f"An error occurred: {e}")