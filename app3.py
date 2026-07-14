            
import streamlit as st
from google import genai
import os 
from dotenv import load_dotenv
load_dotenv()

client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
 

st.title("The MULTIVERSE OF CHATBOTS")

# sidebar


 

personality=st.sidebar.selectbox("Who do you want to talk to?",[

    "Iron man","Spider man","Doctor strange","Captain america"

])

intensity=st.sidebar.slider("Intensity level", min_value=1 , max_value=10 ,value =5)

if st.sidebar.button("Clear chat history"):
     st.session_state.messages = []
     st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if user_message := st.chat_input("Say something.."):
    with st.chat_message("user"):
        st.write(user_message)

    st.session_state.messages.append({"role": "user" , "content": user_message})


    ai_instructions= f"You are acting as {personality} with an intensity level of {intensity}.Respond to the message sent by the user staying completely in character: {user_message} "

        

    with st.spinner("Connecting to the multiverse!......"):

            response=client.models.generate_content(

                model="gemini-2.5-flash",

                contents=ai_instructions

            )
    
    with st.chat_message("assistant"):
         st.write(response.text)

    st.session_state.messages.append({"role": "assistant" , "content": response.text})