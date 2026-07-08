import streamlit as st
st.title("The void")
st.write("Fill out the details below")
user_name = st.text_input("Enter your name")
user_message = st.text_input("Enter your message")
if st.button("Transmit"):
    if not user_name.strip():
        st.error("Please provide your name")
    elif not user_message.strip():
        st.warning("Please type a message to transmit")
    else:
        st.success(f"Transmission successful! Greetings,{user_name}. We received your message: {user_message}")

        char_count = len(user_message)
        token_count = char_count//4
        st.info(f"System Check: Your message will consume approximately {token_count} tokens from our context window.")
