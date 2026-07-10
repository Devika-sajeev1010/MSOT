            
import streamlit as st

 

st.title("The MULTIVERSE OF CHATBOTS")

 

personality=st.selectbox("Who do you want to talk to?",[

    "Iron man","Spider man","Doctor strange","Captain america"

])

 

from google import genai

import os 

from dotenv import load_dotenv

 

load_dotenv()

client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

 

user_message=st.text_input("Say something: ")

if st.button("SEND"):

    if user_message:

        ai_instructions= f"You are acting as {personality}.Respond to the message sent by the user staying completely in character: {user_message} "

        

        with st.spinner("Connecting to the multiverse!......"):

            response=client.models.generate_content(

                model="gemini-2.5-flash",

                contents=ai_instructions

            )
            st.success("Message Received")
            st.write(response.text)