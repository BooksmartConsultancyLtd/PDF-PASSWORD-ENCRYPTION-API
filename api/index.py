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

    decrypted_files = []

    for pdf_file in pdf_files:
        temp_input_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
        temp_output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name

        pdf_file.save(temp_input_path)
        success = remove_password(temp_input_path, temp_output_path, password)

        if success:
            decrypted_files.append(temp_output_path)

    if not decrypted_files:
        return {"error": "Failed to decrypt PDFs. Incorrect password or files not encrypted."}, 400

    # Return multiple files separately
    return [send_file(f, mimetype='application/pdf', as_attachment=True, download_name=os.path.basename(f)) for f in decrypted_files]

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

    encrypted_files = []

    for pdf_file in pdf_files:
        temp_input_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
        temp_output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name

        pdf_file.save(temp_input_path)
        success = encrypt_pdf(temp_input_path, temp_output_path, password)

        if success:
            encrypted_files.append(temp_output_path)

    if not encrypted_files:
        return {"error": "Failed to encrypt PDFs."}, 500

    # Return multiple files separately
    return [send_file(f, mimetype='application/pdf', as_attachment=True, download_name=os.path.basename(f)) for f in encrypted_files]

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
