from flask import Flask, request, jsonify
import os
from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI

app = Flask(__name__)

# Store different chatbot configurations
chatbot_configs = {
    'default': {'api_key': os.getenv('OPENAI_API_KEY', 'your_openai_api_key')},
    # Add other chatbot configurations here
}

# In-memory prompt library (use a database in production)
prompt_library = {
    'default': """
    Definition of ambiguity that the LLM will look for in the requirement:
    Examples of Ambiguities:
    - Lexical Ambiguity:
      - Homonyms: One word has the same written and phonetic presentation but different meanings.
      - Polysemy: One word has different meanings.
    - Syntactic Ambiguity:
      - Analytical Ambiguity: The role of constituents within a sentence can be interpreted in two distinct ways.
      - Attachment Ambiguity: A particular constituent can be attached to two parts of a sentence.
      - Coordination Ambiguity: More than one conjunction (and, or) is used in a sentence, or one conjunction is used with a modifier.
    - Semantic Ambiguity:
      - Coordination Ambiguity
      - Referential Ambiguity: Anaphora ambiguity where a pronoun has multiple antecedent options.
      - Scope Ambiguity: Operators like quantifiers and negation can enter into different scoping relations with other sentence constituents.
    - Anaphora Ambiguity: The text offers multiple antecedent options for a pronoun.
    - Modals and Adverbs: Ambiguity arising from modifiers that express quality associated with a predicate.
    - Passive Voice: Ambiguity when the passive verb is not followed by the subject that performs the action.
    
    Input: {user_input}
    
    Task:
    As an LLM, your task is to thoroughly analyze the requirement and point out any areas of ambiguity or potential unintended outcomes.
    Provide clear guidance or suggestions for how to address and resolve any ambiguities found, ensuring that the requirement is properly understood.
    
    Output:
    List of bullet points detailing any areas of ambiguity or potential unintended outcomes found in the requirement analysis.
    For each point listed, include suggestions or guidance on how to address and resolve any ambiguities or potential unintended outcomes.
    """
}

# Endpoint to get and update prompt templates
@app.route('/prompts/<prompt_name>', methods=['GET', 'PUT'])
def manage_prompts(prompt_name):
    if request.method == 'GET':
        prompt = prompt_library.get(prompt_name, None)
        if prompt is None:
            return jsonify({"error": "Prompt not found"}), 404
        return jsonify({"prompt": prompt})
    
    if request.method == 'PUT':
        data = request.json
        new_prompt = data.get('prompt')
        if not new_prompt:
            return jsonify({"error": "No prompt provided"}), 400
        prompt_library[prompt_name] = new_prompt
        return jsonify({"message": "Prompt updated successfully"})

# Endpoint for chatbot interaction
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_input = data.get('user_input')
        chatbot_type = data.get('chatbot_type', 'default')
        
        if not user_input:
            return jsonify({"error": "No user input provided"}), 400
        
        # Get the appropriate API key and prompt template
        api_key = chatbot_configs.get(chatbot_type, chatbot_configs['default'])['api_key']
        prompt_template = prompt_library.get('default')  # Extend to use specific templates if needed
        
        llm = OpenAI(api_key=api_key)
        prompt = PromptTemplate(template=prompt_template, input_variables=["user_input"])
        chain = LLMChain(prompt=prompt, llm=llm)
        
        # Send the prompt to the OpenAI model and get the response
        response = chain.run(user_input)
        
        # Return the model's analysis as the response
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to handle user interactions with ambiguities
@app.route('/resolve_ambiguity', methods=['POST'])
def resolve_ambiguity():
    try:
        data = request.json
        ambiguity = data.get('ambiguity')
        additional_context = data.get('additional_context')
        
        if not ambiguity or not additional_context:
            return jsonify({"error": "Ambiguity or additional context not provided"}), 400
        
        # Here you would process the ambiguity and additional context, 
        # update the prompt, and get a refined response from the LLM.
        
        # For simplicity, just echoing the inputs back in this example
        return jsonify({"message": "Ambiguity resolved", "ambiguity": ambiguity, "additional_context": additional_context})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
