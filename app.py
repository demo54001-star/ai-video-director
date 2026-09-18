import streamlit as st
import google.generativeai as genai
import yt_dlp
import time
import os

st.set_page_config(page_title="AI Video Director")
st.title("🎬 AI Video Director")

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

video_url = st.text_input("Paste the Video Link (YouTube, Insta, TikTok):")
custom_change = st.text_area("Director's Notes (What do you want to change?):", 
                             placeholder="e.g., Make it raining, change the car to a boat...")

if st.button("Generate New Prompt"):
    if not video_url or not custom_change:
        st.warning("Please provide both a video link and your director's notes.")
    else:
        with st.spinner("Downloading video..."):
            ydl_opts = {'outtmpl': 'temp_video.mp4', 'format': 'mp4'}
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
            except Exception as e:
                st.error("Error downloading video. Make sure the link is public.")
                st.stop()

        with st.spinner("Uploading to Gemini's brain..."):
            video_file = genai.upload_file(path="temp_video.mp4")

            while video_file.state.name == "PROCESSING":
                time.sleep(2)
                video_file = genai.get_file(video_file.name)

        with st.spinner("Analyzing visuals and writing prompt..."):
            model = genai.GenerativeModel("gemini-1.5-pro")

            prompt_instructions = f"""
            1. Provide a detailed bulleted breakdown of what you see in this video (camera movement, lighting, subjects, setting).
            2. Under a heading called 'FINAL PROMPT', write a highly detailed text-to-video prompt that perfectly recreates this style.
            3. CRITICAL INSTRUCTION: You must apply this custom change to the final prompt: {custom_change}
            """

            response = model.generate_content([prompt_instructions, video_file])
            st.success("Done!")
            st.markdown(response.text)

            if os.path.exists("temp_video.mp4"):
                os.remove("temp_video.mp4")
              
