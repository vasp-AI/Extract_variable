from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configure the Generative AI API
genai.configure(api_key="AIzaSyBXg8ezkE2ZYhHzqc-VklWbiWCyiXSpXQ4")

@app.route('/extract-variables', methods=['POST'])
def extract_variables():
    try:
        # Get input data from the user
        data = request.json
        input_template = data.get('input_template')
        output_text = data.get('output_text')

        if not input_template or not output_text:
            return jsonify({"error": "Both 'input_template' and 'output_text' are required."}), 400

        # Use the Generative AI API to process the input
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (f"your are text extractor assistance ,here have input and output you need the match input and output and return the varibale for example match {input_template} and {output_text} and return variable and thier matching data\n"
                  "for example input is Dear Parents,{{1}} of class {{2}} is absent from {{3}} on {{4}}.Regards, Desalite Connect. and output is Dear Parents.ABHINAB of class I JASMINE Roll no. 1 is absent from SFS School on 01-04-2024.Regards, Desalite Connect then the variable is {{1}} is ABHINAB,{{2}} is  I JASMINE Roll no. 1,{{3}} is SFS School,{{4}} is 01-04-2024"
"example format :\n"
"{{{1}}:data,{{2}}:data}"
"Do not use \n tag and also json taq on your response ,write human readble, clean")

        response = model.generate_content(prompt)

        # Return the response directly
        return jsonify({"variables": response.text.strip()}), 200

    except Exception as e:
        return jsonify({"error": "Contact who developed this"}), 500

if __name__ == '__main__':
    app.run(debug=True)
