from flask import Flask, request, send_file
import PyPDF2
import os
import tempfile

app = Flask(__name__)

@app.route('/decrypt-pdfs', methods=['POST'])
def decrypt_pdfs_endpoint():
    if 'files' not in request.files:
        return {"error": "No files provided"}, 400

    pdf_files = request.files.getlist('files')
    password = request.form.get('password', '')

    processed_files = []

    for pdf_file in pdf_files:
        original_filename = pdf_file.filename
        temp_input_path = os.path.join(tempfile.gettempdir(), original_filename)
        temp_output_path = os.path.join(tempfile.gettempdir(), f"decrypted_{original_filename}")

        pdf_file.save(temp_input_path)
        success = remove_password(temp_input_path, temp_output_path, password)

        if success:
            processed_files.append((temp_output_path, original_filename))

    if not processed_files:
        return {"error": "Failed to decrypt PDFs. Incorrect password or files not encrypted."}, 400

    return [
        send_file(f, mimetype='application/pdf', as_attachment=True, download_name=filename)
        for f, filename in processed_files
    ]

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


@app.route('/encrypt-pdfs', methods=['POST'])
def encrypt_pdfs_endpoint():
    if 'files' not in request.files:
        return {"error": "No files provided"}, 400

    pdf_files = request.files.getlist('files')
    password = request.form.get('password', '')

    if not password:
        return {"error": "No password provided"}, 400

    processed_files = []

    for pdf_file in pdf_files:
        original_filename = pdf_file.filename
        temp_input_path = os.path.join(tempfile.gettempdir(), original_filename)
        temp_output_path = os.path.join(tempfile.gettempdir(), f"encrypted_{original_filename}")

        pdf_file.save(temp_input_path)
        success = encrypt_pdf(temp_input_path, temp_output_path, password)

        if success:
            processed_files.append((temp_output_path, original_filename))

    if not processed_files:
        return {"error": "Failed to encrypt PDFs."}, 500

    return [
        send_file(f, mimetype='application/pdf', as_attachment=True, download_name=filename)
        for f, filename in processed_files
    ]

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

if __name__ == '__main__':
    app.run(debug=True)
