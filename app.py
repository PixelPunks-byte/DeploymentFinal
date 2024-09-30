import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# Configure the Gemini API with your API key
genai.configure(api_key="AIzaSyC5xrWL9ElndG119DoZdIVtenf76i89uzk")

# Initialize the Gemini models
flash_model = genai.GenerativeModel('gemini-1.5-flash')
pro_model = genai.GenerativeModel('gemini-1.5-pro')

# Store conversation history
conversation_history = {}

# Create a Streamlit app interface
st.title("AI Image Analysis and Chatbot")

# Upload Image Section
uploaded_image = st.file_uploader("Upload an image for analysis", type=["png", "jpg", "jpeg"])

if uploaded_image:
    # Convert the uploaded image to a PIL Image
    try:
        image = Image.open(io.BytesIO(uploaded_image.read()))  # Convert UploadedFile to PIL Image
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Initial prompt to analyze the image
        initial_prompt = "Analyze this image in detail. Note down what you see, including objects, colors, and any notable features. Describe the image in 2 lines."

        # Get initial analysis from Gemini Flash
        response = flash_model.generate_content([initial_prompt, image])  # Pass the image in the correct format
        analysis = response.text
        st.write(f"Image Analysis: {analysis}")

        # Store analysis in conversation history
        session_id = str(st.session_state.get('session_id', len(conversation_history) + 1))
        conversation_history[session_id] = {
            'image_analysis': analysis,
            'image_uploaded': True,  # Mark that an image was uploaded
            'chat_history': f"Image analysis: {analysis}\n\n"
        }

    except Exception as e:
        st.error(f"Error during image upload: {e}")

# Chat Section
user_input = st.text_input("Ask a question about the image or chat with the bot")

if user_input:
    session_id = str(st.session_state.get('session_id', len(conversation_history) + 1))

    # Retrieve session data
    session_data = conversation_history.get(session_id, {})
    chat_history = session_data.get('chat_history', '')
    image_uploaded = session_data.get('image_uploaded', False)  # Check if image was uploaded
    image_analysis = session_data.get('image_analysis', '')

    if image_uploaded and user_input.lower() in image_analysis.lower():
        # Generate response using the Flash model
        prompt = f"{chat_history}Human: {user_input}\n"
        response = flash_model.generate_content(prompt)
        bot_response = response.text.strip()
    else:
        # Generate response using the Pro model for general queries
        prompt = f"{chat_history}Human: {user_input}\n"
        response = pro_model.generate_content(prompt)
        bot_response = response.text.strip()

    # Display bot response
    st.write(f"Bot: {bot_response}")

    # Update conversation history
    if session_id not in conversation_history:
        conversation_history[session_id] = {'chat_history': ''}
    conversation_history[session_id]['chat_history'] += f"Human: {user_input}\nAI: {bot_response}\n"
