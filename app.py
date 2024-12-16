from flask import Flask, request, jsonify
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure the Generative AI API
genai_api_key = os.getenv("GENAI_API_KEY")
if not genai_api_key:
    raise ValueError("API key not found. Please set GENAI_API_KEY in your .env file.")
genai.configure(api_key=genai_api_key)

# File to store templates
TEMPLATE_FILE = "templates.json"

# Ensure the templates file exists
if not os.path.exists(TEMPLATE_FILE):
    with open(TEMPLATE_FILE, "w") as file:
        json.dump({}, file)

# Load templates from file
def load_templates():
    with open(TEMPLATE_FILE, "r") as file:
        return json.load(file)

# Save templates to file
def save_templates(templates):
    with open(TEMPLATE_FILE, "w") as file:
        json.dump(templates, file, indent=4)

@app.route('/add-template', methods=['POST'])
def add_template():
    try:
        data = request.json
        template_name = data.get('template_name')
        input_template = data.get('input_template')

        if not template_name or not input_template:
            return jsonify({"error": "Both 'template_name' and 'input_template' are required."}), 400

        templates = load_templates()
        templates[template_name] = input_template
        save_templates(templates)

        return jsonify({"message": f"Template '{template_name}' added successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/extract-variables', methods=['POST'])
def extract_variables():
    try:
        data = request.json
        template_name = data.get('template_name')
        output_text = data.get('input_text')

        if not template_name or not output_text:
            return jsonify({"error": "Both 'template_name' and 'input_text' are required."}), 400

        templates = load_templates()
        input_template = templates.get(template_name)

        if not input_template:
            return jsonify({"error": f"Template '{template_name}' not found."}), 404

        # Use the Generative AI API to process the input
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (f"your are variable extractor assistance from two text phrases ,here have input and output you need the match input and output and return the varibale for example match {input_template} and {output_text} and return variable and thier matching data\n"
                  "i give you example how you extract the variable take the example as reference for example input is Dear Parents,{{1}} of class {{2}} is absent from {{3}} on {{4}}.Regards, Desalite Connect. and output is Dear Parents.ABHINAB of class I JASMINE Roll no. 1 is absent from SFS School on 01-04-2024.Regards, Desalite Connect then the variable is 1 is ABHINAB,2 is  I JASMINE Roll no. 1, 3 is SFS School, 4 is 01-04-2024"
                  "example format :\n"
                  " 1:data,2:data \n\n"
                  "Extract variable and data accurately"
                  "Do not use \n tag and also json taq on your response ,write human readble, clean\n"
                  "Do not send unusual writing,send only variable \n"
                  "If input and output doesnot match then return text is not match ,do not explain write direct word so if text is not match you can not extract variable")

        response = model.generate_content(prompt)

        # Preprocess and format the response into JSON
        raw_variables = response.text.strip()
        variables = {}
        
        for pair in raw_variables.split(','):
            key, value = pair.split(':', 1)
            variables[key.strip()] = value.strip()

        return jsonify(variables), 200

    except Exception as e:
        return jsonify({"error": "input data is not match kindly check the template name"}), 500

@app.route('/show-templates', methods=['GET'])
def show_templates():
    try:
        templates = load_templates()
        return jsonify({"templates": templates}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/delete-template', methods=['DELETE'])
def delete_template():
    try:
        data = request.json
        template_name = data.get('template_name')

        if not template_name:
            return jsonify({"error": "'template_name' is required."}), 400

        templates = load_templates()

        if template_name not in templates:
            return jsonify({"error": f"Template '{template_name}' not found."}), 404

        del templates[template_name]
        save_templates(templates)

        return jsonify({"message": f"Template '{template_name}' deleted successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update-template', methods=['PUT'])
def update_template():
    try:
        data = request.json
        template_name = data.get('template_name')
        new_template_name = data.get('new_template_name')
        new_input_template = data.get('new_input_template')

        if not template_name or not new_template_name or not new_input_template:
            return jsonify({"error": "'template_name', 'new_template_name', and 'new_input_template' are required."}), 400

        templates = load_templates()

        if template_name not in templates:
            return jsonify({"error": f"Template '{template_name}' not found."}), 404

        # Update template
        del templates[template_name]
        templates[new_template_name] = new_input_template
        save_templates(templates)

        return jsonify({"message": f"Template '{template_name}' updated successfully to '{new_template_name}' with new content."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
