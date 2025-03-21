import requests
import os

def upload_pdf(file_path, password):
    # Ensure the file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return
    
    # Prepare the files and data
    files = {
        'file': (os.path.basename(file_path), open(file_path, 'rb'), 'application/pdf')
    }
    data = {
        'password': password
    }
    
    # Make the request
    response = requests.post(
        'https://password-decrypter.vercel.app/decrypt-pdf',
        files=files,
        data=data
    )
    
    # Handle the response
    if response.status_code == 200:
        # Save the decrypted file
        with open('decrypted.pdf', 'wb') as f:
            f.write(response.content)
        print("PDF decrypted successfully! Saved as 'decrypted.pdf'")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

if __name__ == '__main__':
    # Your file path
    file_path = r"C:\Users\DELL\Desktop\James Temporary\document-trainer-and-many-more\PASSWORD DECRYPTER\2024 - 01 - ABSA - USD - 2046469480 - SIMSTEL CONNECT LIMITED - PW- 2019SI9480.pdf"
    password = "2019SI9480"
    
    upload_pdf(file_path, password)