from flask import Flask, request, send_file
import requests
import os
import tempfile

app = Flask(__name__)

# I Love PDF API Credentials
API_KEY = "secret_key_eae37c07cfe857b188cb3fdd6b85f77c_Nhi0s7362d1a6974b0986abc7172b092f708b"
BASE_URL = "https://api.ilovepdf.com/v1"

@app.route('/decrypt-pdfs', methods=['POST'])
def decrypt_pdfs_endpoint():
    if 'files' not in request.files:
        return {"error": "No files provided"}, 400

    pdf_files = request.files.getlist('files')
    password = request.form.get('password', '')

    if not password:
        return {"error": "No password provided"}, 400

    decrypted_files = []

    for pdf_file in pdf_files:
        original_filename = pdf_file.filename
        temp_input_path = os.path.join(tempfile.gettempdir(), original_filename)
        pdf_file.save(temp_input_path)

        decrypted_file_path = decrypt_with_ilovepdf(temp_input_path, password)
        if decrypted_file_path:
            decrypted_files.append((decrypted_file_path, original_filename))

    if not decrypted_files:
        return {"error": "Failed to decrypt PDFs. Incorrect password or API issue."}, 400

    return [
        send_file(f, mimetype='application/pdf', as_attachment=True, download_name=filename)
        for f, filename in decrypted_files
    ]

def decrypt_with_ilovepdf(file_path, password):
    """ Sends file to I Love PDF API for decryption and returns the decrypted file path """
    try:
        # Step 1: Start Decrypt Task
        response = requests.get(f"{BASE_URL}/start/decrypt", headers={"Authorization": f"Bearer {API_KEY}"})
        if response.status_code != 200:
            print(f"Error: {response.json()}")
            return None
        task_id = response.json()["task"]

        # Step 2: Upload File
        with open(file_path, "rb") as file:
            upload_response = requests.post(
                f"{BASE_URL}/upload/{task_id}", 
                headers={"Authorization": f"Bearer {API_KEY}"}, 
                files={"file": file}
            )

        if upload_response.status_code != 200:
            print(f"Upload Error: {upload_response.json()}")
            return None

        server_filename = upload_response.json()["server_filename"]

        # Step 3: Process Decryption
        process_response = requests.post(
            f"{BASE_URL}/process/{task_id}", 
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"files": [{"server_filename": server_filename}], "password": password}
        )

        if process_response.status_code != 200:
            print(f"Processing Error: {process_response.json()}")
            return None

        # Step 4: Download Decrypted File
        result_url = process_response.json()["download_url"]
        decrypted_file_path = file_path.replace(".pdf", "_decrypted.pdf")

        with requests.get(result_url, stream=True) as r:
            with open(decrypted_file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        return decrypted_file_path
    except Exception as e:
        print(f"Error: {e}")
        return None


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
        original_filename = pdf_file.filename
        temp_input_path = os.path.join(tempfile.gettempdir(), original_filename)
        pdf_file.save(temp_input_path)

        encrypted_file_path = encrypt_with_ilovepdf(temp_input_path, password)
        if encrypted_file_path:
            encrypted_files.append((encrypted_file_path, original_filename))

    if not encrypted_files:
        return {"error": "Failed to encrypt PDFs."}, 500

    return [
        send_file(f, mimetype='application/pdf', as_attachment=True, download_name=filename)
        for f, filename in encrypted_files
    ]

def encrypt_with_ilovepdf(file_path, password):
    """ Sends file to I Love PDF API for encryption and returns the encrypted file path """
    try:
        # Step 1: Start Encrypt Task
        response = requests.get(f"{BASE_URL}/start/protect", headers={"Authorization": f"Bearer {API_KEY}"})
        if response.status_code != 200:
            print(f"Error: {response.json()}")
            return None
        task_id = response.json()["task"]

        # Step 2: Upload File
        with open(file_path, "rb") as file:
            upload_response = requests.post(
                f"{BASE_URL}/upload/{task_id}", 
                headers={"Authorization": f"Bearer {API_KEY}"}, 
                files={"file": file}
            )

        if upload_response.status_code != 200:
            print(f"Upload Error: {upload_response.json()}")
            return None

        server_filename = upload_response.json()["server_filename"]

        # Step 3: Process Encryption
        process_response = requests.post(
            f"{BASE_URL}/process/{task_id}", 
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"files": [{"server_filename": server_filename}], "password": password}
        )

        if process_response.status_code != 200:
            print(f"Processing Error: {process_response.json()}")
            return None

        # Step 4: Download Encrypted File
        result_url = process_response.json()["download_url"]
        encrypted_file_path = file_path.replace(".pdf", "_encrypted.pdf")

        with requests.get(result_url, stream=True) as r:
            with open(encrypted_file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        return encrypted_file_path
    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == '__main__':
    app.run(debug=True)
