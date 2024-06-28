from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import PyPDF2 as pypdf
app = Flask(__name__)

cors  = CORS(app, origins=["http://localhost:3000", "localhost:3000", "https://www.rafikiai.app", "rafikiai.app", "www.rafikiai.app"])


@app.route("/", methods=["GET"])
def home():
    return 'Hey yo brosky what up'

@app.route("/upload_file", methods=["POST"])
def upload_pdf():
    if 'file' not in request.files:

        return jsonify({
            'message': 'You need to provide a file'
        }), 404
    file = request.files['file']
    if file.filename == '':
        return jsonify('file needs to have a name')
    
    if file.mimetype == 'application/pdf':

        try:
            read_files = pypdf.PdfReader(file)
            text = extract_text(read_files)
            
            return jsonify({
                "extracted_text": text,
            }), 200
        except Exception as e:
            return jsonify({
                "Message": e
            })
    else:
        jsonify('Invalid file type')

    return jsonify('Yoyo')
   
   

def extract_text(file_stream):
    text = "";
    print(len(file_stream.pages))
    for index in range(len(file_stream.pages)):
            page = file_stream.pages[index]
            text += page.extract_text()
            text += '\n\n'

    return text;

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)


