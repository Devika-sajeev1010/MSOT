import json
import os
import urllib.parse
from io import BytesIO

import requests
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from gtts import gTTS

# ------------------------------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES FROM .env
# ------------------------------------------------------------------------------
load_dotenv()

# ------------------------------------------------------------------------------
# APP CONFIGURATION
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Multi-Modal Visual Novel Engine",
    page_icon="📖",
    layout="wide"
)

# ------------------------------------------------------------------------------
# PHASE 1: DIRECTORS CUT (UI & CONFIGURATION)
# ------------------------------------------------------------------------------
@st.cache_resource
def get_gemini_client():
    """Caches and returns the Gemini client using st.cache_resource."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("Missing GEMINI_API_KEY! Please add it to your .env file.")
        st.stop()
    return genai.Client(api_key=api_key)

client = get_gemini_client()

# Sidebar Setup
st.sidebar.title("🎮 Story Settings")
genre = st.sidebar.selectbox(
    "Story Genre",
    ["Cyberpunk Noir", "High Fantasy", "Cosmic Horror", "Post-Apocalyptic", "Sci-Fi Exploration"]
)
art_style = st.sidebar.selectbox(
    "Art Style",
    ["Anime / Manga", "Pixel Art", "Digital Concept Art", "Watercolor", "Photorealistic"]
)

if st.sidebar.button("🔄 Restart Adventure"):
    st.session_state.clear()
    st.rerun()

# ------------------------------------------------------------------------------
# SYSTEM PROMPT (STRICT JSON OUTPUT REQUIREMENT)
# ------------------------------------------------------------------------------
SYSTEM_PROMPT = f"""
You are the Game Master for an interactive Choose-Your-Own-Adventure visual novel.
Genre: {genre}
Art Style for visual prompt engineering: {art_style}

You MUST ALWAYS respond with a SINGLE, VALID JSON object without markdown formatting outside of it.
The JSON object must have EXACTLY these 3 keys:
1. "story_text": The narrative paragraph continuing the story (2-4 vivid sentences).
2. "image_prompt": A highly detailed visual prompt suited for an image generation model that captures the current scene, specifying style '{art_style}'.
3. "options": A JSON array containing 2 to 3 distinct text choices for the player's next move.

Example format:
{{
  "story_text": "You step into the neon-lit alleyway, rain dripping off your trench coat.",
  "image_prompt": "A neon-lit futuristic alleyway at night, rain glistening on wet pavement, cibachrome style, {art_style}",
  "options": [
    "Investigate the glowing door on the right.",
    "Follow the suspicious figure in the shadow.",
    "Check your pocket comms for updates."
  ]
}}
"""

# Initialize Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Stores rendered turns: {text, image_url, audio_bytes, options}

if "game_started" not in st.session_state:
    st.session_state.game_started = False

if "chat_session" not in st.session_state:
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7,
            response_mime_type="application/json"
        )
    )

# ------------------------------------------------------------------------------
# HELPER FUNCTIONS (TTS & POLLINATIONS WITH TRY...EXCEPT)
# ------------------------------------------------------------------------------
def generate_audio(text: str) -> bytes | None:
    """Phase 4 & 5: Generates TTS audio using gTTS with error handling."""
    try:
        tts = gTTS(text=text, lang="en")
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.getvalue()
    except Exception as e:
        st.toast(f"⚠️ Could not generate audio narration: {e}", icon="🎙️")
        return None

def fetch_image(prompt: str) -> str | None:
    """Phase 4 & 5: Fetches visual asset from Pollinations API with fail-safe error handling."""
    encoded_prompt = urllib.parse.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=450&nologo=true"
    
    try:
        response = requests.get(image_url, timeout=10)
        if response.status_code == 200:
            return image_url
        else:
            st.toast("⚠️ Image server busy. Skipping visual rendering.", icon="🖼️")
            return None
    except Exception:
        st.toast("⚠️ Network error while fetching image. Continuing story...", icon="⚠️")
        return None

def process_turn(player_input: str):
    """Executes the pipeline: AI -> Parse JSON -> TTS -> Pollinations Image -> Update State."""
    with st.spinner("The AI Game Master is crafting the next scene..."):
        try:
            # 1. Send input to Gemini
            response = st.session_state.chat_session.send_message(player_input)
            
            # 2. Phase 2: Parse Structured JSON
            parsed_data = json.loads(response.text)
            story_text = parsed_data.get("story_text", "")
            image_prompt = parsed_data.get("image_prompt", "")
            options = parsed_data.get("options", [])

            # 3. Phase 4 & 5: Audio Generation
            audio_bytes = generate_audio(story_text)

            # 4. Phase 4 & 5: Image Generation via Pollinations
            image_url = fetch_image(image_prompt) if image_prompt else None

            # 5. Save turn into history
            st.session_state.chat_history.append({
                "story_text": story_text,
                "image_url": image_url,
                "audio_bytes": audio_bytes,
                "options": options
            })
            st.session_state.game_started = True

        except json.JSONDecodeError:
            st.error("Failed to parse JSON response from AI. Please try restarting.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# ------------------------------------------------------------------------------
# MAIN UI & RENDER ENGINE
# ------------------------------------------------------------------------------
st.title("🎬 Multi-Modal Visual Novel Engine")
st.caption(f"Currently Playing: **{genre}** | Style: **{art_style}**")

# Start Game Trigger
if not st.session_state.game_started:
    st.info("Click below to start your adventure!")
    if st.button("🚀 Begin Story", type="primary", use_container_width=True):
        process_turn("Start the story! Describe the opening scene and give me initial choices.")
        st.rerun()

# Render Story History
for index, turn in enumerate(st.session_state.chat_history):
    st.markdown("---")
    col1, col2 = st.columns([1, 1], gap="medium")
    
    with col1:
        st.markdown(f"### Chapter {index + 1}")
        st.write(turn["story_text"])
        
        # Audio Player
        if turn["audio_bytes"]:
            st.audio(turn["audio_bytes"], format="audio/mp3")

    with col2:
        # Visual Rendering
        if turn["image_url"]:
            st.image(turn["image_url"], use_container_width=True)
        else:
            st.info("🖼️ Visual artwork unavailable for this scene.")

# Phase 3: Dynamic UI Generation (Action Choices)
if st.session_state.chat_history:
    latest_turn = st.session_state.chat_history[-1]
    options = latest_turn.get("options", [])

    st.markdown("---")
    st.subheader("What do you do next?")
    
    # Dynamically generate buttons for choices
    cols = st.columns(len(options)) if options else []
    for idx, choice in enumerate(options):
        with cols[idx]:
            if st.button(choice, key=f"btn_{len(st.session_state.chat_history)}_{idx}", use_container_width=True):
                process_turn(choice)
                st.rerun()