from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import re

app = Flask(__name__)
#tesseract path 
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def check_range(value, min_val, max_val):
    return min_val <= value <= max_val

@app.route('/', methods=['GET', 'POST', 'HEAD'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file attached'}), 400

    image_file = request.files['image']
    image = Image.open(image_file)
    
    # Perform OCR
    text = pytesseract.image_to_string(image)
    parameter_patterns = {
        'WBC': r'WBC\s*Count\s*([\d.]+)',
        'RBC': r'RBC\s*Count\s*([\d.]+)',
        'Hemoglobin': r'Hemoglobin\s*([\d.]+)',
        'Platelet Count': r'Platelet\s*Count\s*([\d.]+)'
    }

    features = {}
    for parameter, pattern in parameter_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        features[parameter] = float(match.group(1)) if match else None

    # Ranges 
    ranges = {
        "WBC Count": (4.0, 11.0),
        "RBC Count": (4.40, 6.00),
        "Hemoglobin": (13.5, 18.0),
        "Platelet Count": (150.0, 400.0)
    }

    # Check values normal ranges or not
    incorrect_params = []

    for parameter, value_range in ranges.items():
        value = features.get(parameter)
        if value is not None and not check_range(value, *value_range):
            incorrect_params.append(parameter)

    if incorrect_params:
        result = "Abnormal"
    else:
        result = "Normal"
    return jsonify({'result': result})

if __name__ == "__main__":
    app.run(debug=True)
