from flask import Flask, request, send_file
import PyPDF2
import os
import tempfile

app = Flask(__name__)

@app.route('/decrypt-pdf', methods=['POST'])
def decrypt_pdf_endpoint():
    if 'file' not in request.files:
        return {"error": "No file provided"}, 400
    
    pdf_file = request.files['file']
    password = request.form.get('password', '')

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_input_path = os.path.join(temp_dir, "input.pdf")
        temp_output_path = os.path.join(temp_dir, "output.pdf")

        pdf_file.save(temp_input_path)

        success = remove_password(temp_input_path, temp_output_path, password)

        if not success:
            return {"error": "Failed to decrypt PDF. Incorrect password or PDF is not encrypted."}, 400

        return send_file(
            temp_output_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='decrypted.pdf'
        )

def remove_password(input_pdf, output_pdf, password):
    try:
        with open(input_pdf, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if reader.is_encrypted:
                reader.decrypt(password)
            writer = PyPDF2.PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            with open(output_pdf, 'wb') as output_file:
                writer.write(output_file)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


@app.route('/encrypt-pdf', methods=['POST'])
def encrypt_pdf_endpoint():
    if 'file' not in request.files:
        return {"error": "No file provided"}, 400
    
    pdf_file = request.files['file']
    password = request.form.get('password', '')

    if not password:
        return {"error": "No password provided"}, 400

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_input_path = os.path.join(temp_dir, "input.pdf")
        temp_output_path = os.path.join(temp_dir, "output.pdf")

        pdf_file.save(temp_input_path)

        success = encrypt_pdf(temp_input_path, temp_output_path, password)

        if not success:
            return {"error": "Failed to encrypt PDF."}, 500

        return send_file(
            temp_output_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='encrypted.pdf'
        )

def encrypt_pdf(input_pdf, output_pdf, password):
    try:
        reader = PyPDF2.PdfReader(input_pdf)
        writer = PyPDF2.PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.encrypt(password)

        with open(output_pdf, 'wb') as output_file:
            writer.write(output_file)

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


# Export the Flask app as the WSGI application
app = app
