import streamlit as st
import requests


BACKEND_URL = "http://127.0.0.1:5000"  # Adjust this as needed for your backend

# Function to fetch prompt templates from the backend
def fetch_prompt_templates():
    try:
        response = requests.get(f"{BACKEND_URL}/prompts/default")
        if response.status_code == 200:
            return response.json().get('prompt', [])
        else:
            st.error(f"Failed to fetch prompt templates. Status code: {response.status_code}")
            return []
    except requests.RequestException as e:
        st.error(f"Error fetching prompt templates: {e}")
        return []

# Function to update prompt templates in the backend
def update_prompt_template(prompt_name, new_prompt):
    try:
        response = requests.put(f"{BACKEND_URL}/prompts/{prompt_name}", json={"prompt": new_prompt})
        return response.status_code == 200
    except requests.RequestException as e:
        st.error(f"Error updating prompt template: {e}")
        return False

# Function to manage prompt library
def manage_prompt_library():
    st.subheader('Manage Prompt Library:')
    
    prompt_templates = fetch_prompt_templates()
    
    if isinstance(prompt_templates, str):
        prompt_templates = [prompt_templates]

    if prompt_templates:
        # Display current prompt templates
        for template in prompt_templates:
            st.write(template)
    else:
        st.info('No prompt templates found.')

    # Option to add new prompt template
    new_prompt = st.text_input('Add New Prompt Template:')
    if st.button('Add'):
        if new_prompt:
            prompt_templates.append(new_prompt)
            if update_prompt_template('default', '\n'.join(prompt_templates)):
                st.success('Template added successfully!')
            else:
                st.error('Failed to add template.')

    # Option to edit or delete prompt templates
    selected_template = st.selectbox('Select a template to edit/delete:', prompt_templates)
    if st.button('Edit'):
        edited_prompt = st.text_input('Edit Prompt Template:', value=selected_template)
        index = prompt_templates.index(selected_template)
        if st.button('Confirm Edit'):
            if edited_prompt:
                prompt_templates[index] = edited_prompt
                if update_prompt_template('default', '\n'.join(prompt_templates)):
                    st.success('Template edited successfully!')
                else:
                    st.error('Failed to edit template.')
            else:
                st.warning('Please provide a valid template.')
    if st.button('Delete'):
        if st.button('Confirm Delete'):
            prompt_templates.remove(selected_template)
            if update_prompt_template('default', '\n'.join(prompt_templates)):
                st.success('Template deleted successfully.')
            else:
                st.error('Failed to delete template.')

# Function to handle requirements file upload
def upload_requirements():
    uploaded_file = st.file_uploader("Upload a requirements file (txt, pdf)", type=["txt", "pdf"])
    if uploaded_file is not None:
        # Display uploaded file details
        st.subheader('Uploaded Requirements File:')
        st.write(uploaded_file)
        # You can add more processing here if needed

# Function to handle chat interactions
def handle_chat(user_input, chatbot_type):
    try:
        response = requests.post(f"{BACKEND_URL}/chat", json={"user_input": user_input, "chatbot_type": chatbot_type})
        if response.status_code == 200:
            return response.json().get('response', '')
        else:
            return f"Error: Unable to get response from the backend. Status code: {response.status_code}"
    except requests.RequestException as e:
        return f"Error: Unable to get response from the backend. Exception: {e}"

# Function to select chatbot model
def select_models():
    st.subheader('Select Chatbot Model:')
    model_options = ['ChatGPT', 'Other Chatbot Model']  # Adjust options as needed
    selected_model = st.selectbox('Choose a model:', model_options)
    return selected_model

# Main function to run the application
def main():
    st.title('Welcome to RAD-Chatbot ')

    # Sidebar navigation for Settings and Prompt Library
    st.sidebar.title('OPTIONS')
    page = st.sidebar.radio('Go to:', ['Upload File','Prompt Library', 'Settings'])

    if page == 'Upload File':
        upload_requirements()
    elif page == 'Prompt Library':
        st.header('Prompt Library')
        manage_prompt_library()
    elif page == 'Settings':
        st.header('Settings')
        select_models()

if __name__ == "__main__":
    main()
