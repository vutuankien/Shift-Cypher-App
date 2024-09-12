from flask import Flask, request, render_template, send_file, url_for
import os
import tempfile

app = Flask(__name__)

# Bảng ký tự cần mã hóa
special_chars = " @_."
special_chars_length = len(special_chars)

# Hàm mã hóa mở rộng
def encrypt(text, key):
    encrypted_text = ""
    for char in text:
        if char.isalpha():
            # Mã hóa các ký tự chữ cái
            ascii_offset = 65 if char.isupper() else 97
            encrypted_char = chr(((ord(char) - ascii_offset + key) % 26) + ascii_offset)
            encrypted_text += encrypted_char
        elif char in special_chars:
            # Mã hóa các ký tự đặc biệt " @ _ ."
            index = special_chars.index(char)
            new_index = (index + key) % special_chars_length
            encrypted_text += special_chars[new_index]
        else:
            encrypted_text += char
    return encrypted_text

# Hàm giải mã
def decrypt(text, key):
    decrypted_text = ""
    for char in text:
        if char.isalpha():
            # Giải mã các ký tự chữ cái
            ascii_offset = 65 if char.isupper() else 97
            decrypted_char = chr(((ord(char) - ascii_offset - key) % 26) + ascii_offset)
            decrypted_text += decrypted_char
        elif char in special_chars:
            # Giải mã các ký tự đặc biệt " @ _ ."
            index = special_chars.index(char)
            new_index = (index - key) % special_chars_length
            decrypted_text += special_chars[new_index]
        else:
            decrypted_text += char
    return decrypted_text

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    error = ""
    download_url = ""
    text = request.form.get("text", "")
    key = request.form.get("key", "")

    if request.method == "POST":
        try:
            key = int(key)
            if key < 0 or key > 25:
                error = "Vui lòng nhập giá trị dịch chuyển từ 0 đến 25."
            else:
                action = request.form["action"]
                
                if 'file' in request.files and request.files['file'].filename:
                    file = request.files['file']
                    filename = file.filename
                    file_text = file.read().decode('utf-8')
                    
                    if action == "encrypt":
                        result = encrypt(file_text, key)
                        output_filename = f"encrypted_{filename}"
                    elif action == "decrypt":
                        result = decrypt(file_text, key)
                        output_filename = f"decrypted_{filename}"
                    
                    # Lưu kết quả vào file tạm thời
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8') as temp_file:
                        temp_file.write(f"\n{result}")
                        temp_file_path = temp_file.name
                    
                    download_url = f"/download/{os.path.basename(temp_file_path)}"
                
                else:
                    if action == "encrypt":
                        result = encrypt(text, key)
                    elif action == "decrypt":
                        result = decrypt(text, key)
                    
                    # Lưu kết quả vào file tạm thời
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8') as temp_file:
                        temp_file.write(f"\n{result}")
                        temp_file_path = temp_file.name
                    
                    download_url = f"/download/{os.path.basename(temp_file_path)}"

        except ValueError:
            error = "Vui lòng nhập số nguyên cho giá trị dịch chuyển."
    
    return render_template("index.html", result=result, error=error, text=text, key=key if key else '', download_url=download_url)

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    temp_file_path = os.path.join(tempfile.gettempdir(), filename)
    return send_file(temp_file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
