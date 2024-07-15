from flask import Flask, request, jsonify, send_file
from reportlab.lib.pagesizes import letter,A4
from reportlab.pdfgen import canvas
import json
from flask_cors import CORS
import base64
import PyPDF2 as pypdf
from io import BytesIO
import secrets
import string

app = Flask(__name__)


cors  = CORS(app, origins=["http://localhost:3000", "localhost:3000"])


@app.route("/", methods=["GET"])
def home():
    return 'Hey yo brosky what up'

@app.route("/upload_file", methods=["POST"])
def upload_pdf():
    print('backend hit')
    if 'file' not in request.files:

        return jsonify({
            'message': 'You need to provide a file'
        }), 404
    file = request.files['file']
    if file.filename == '':
        return jsonify('file needs to have a name')
    
    if file.mimetype == 'application/pdf':

        try:
            read_files = pypdf.PdfReader(file, strict=False)
            pages = extract_text(read_files)
            images = extract_image(read_files)
            print(len(images))
            return jsonify({
                "pages": pages,
                "images": images
            }), 200
        except Exception as e:
            print(str(e))
            return jsonify({
                "error": True,
                "Message": "Something went wrong",
                "reason": "Pdf needs fixing",
                "done": False
            })
    else:
        jsonify('Invalid file type')

    return jsonify('Yoyo')


@app.route("/download_note", methods=["GET"])
def download_note():
    data = request.get_json()
    if not data or 'notes' not in data:
        return jsonify({
            "error": True,
            "message": 'Notes not provided'
        })
    
    notes = data["notes"]
    print(notes)
    pdf_buffer = strings_to_buffer(notes)
    name = f'{generate_secure_random_string(15)}.pdf'
    print(name)
    print(pdf_buffer)
    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=name
    )

   
   

def extract_text(file_stream):
    pages = []
    for index in range(len(file_stream.pages)):
            page = file_stream.pages[index]
            text = page.extract_text();
            pages.append(text)
            #pages.append(page.extract_text())
            

    return pages


def extract_image(file_stream):
    imgs = []
    # get all the pages in the pdf
    pages =  file_stream.pages

    # loop through all the pages and convert the images on each 
    for page_index in range(len(pages)):
        # get a single page
        page = pages[page_index]
        images = page.images
        for image_index in range(len(images)):
            # get the current image
            cur_image = images[image_index]
            b64 = base64.b64encode(cur_image.data)
            name = cur_image.name.split('.')
            
            img_type = name[-1]
            data = {
                "img_type": img_type,
                "base_64_data": str(b64).split('\'')[1]
            }
            imgs.append(data)

    return imgs  
    # return images


def strings_to_buffer(note_lists):
    try:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4,)
        width, height = A4
        y_position = height - 40
        text = c.beginText()
        text.setTextOrigin(40, y_position)

        for note in note_lists:

            text.textLine(note)
            y_position -= 20
            if y_position < 40:
                c.showPage()
                y_position = height - 40

        
        
        c.drawText(text)
    
        c.save()
        buffer.seek(0)
        return buffer
    except Exception as e:
        print('Something broke')
        print(e)


def generate_secure_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(secrets.choice(letters_and_digits) for i in range(length))