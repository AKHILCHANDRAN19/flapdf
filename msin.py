from flask import Flask, render_template_string, request, send_file, redirect, url_for
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
import io

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# HTML Templates
HOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Tools</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { 
            font-family: 'Arial', sans-serif; 
            background: linear-gradient(135deg, #74ebd5, #acb6e5); 
            color: #333;
        }
        h1 {
            font-family: 'Montserrat', sans-serif; 
            font-weight: bold; 
            text-transform: uppercase;
            animation: fadeIn 2s ease;
        }
        h2 {
            font-family: 'Montserrat', sans-serif; 
            font-size: 1rem; 
            text-transform: uppercase;
            animation: fadeIn 2s ease;
        }
        .tool-card { 
            background-color: #fff; 
            box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
            border-radius: 10px; 
            transition: transform 0.3s; 
            padding: 20px;
        }
        .tool-card:hover { 
            transform: translateY(-5px); 
        }
        .card {
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            border-radius: 10px;
        }
        .fa-icon {
            font-size: 3rem;
            margin-bottom: 10px;
            animation: bounce 2s infinite;
        }
        .fa-eraser {
            color: #dc3545;
        }
        .fa-sync-alt {
            color: #ffc107;
        }
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(20px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
        }
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="header">
            <h1>PDF Tools</h1>
            <h2>Designed by Akhil Chandran</h2>
        </div>
        <div class="row g-4">
            <div class="col-md-6">
                <div class="card tool-card text-center">
                    <div class="card-body">
                        <i class="fas fa-cut fa-icon"></i>
                        <h5 class="card-title">PDF Splitter</h5>
                        <p class="card-text">Split your PDF files into smaller parts by selecting start and end pages.</p>
                        <a href="/splitter" class="btn btn-primary">Go to Splitter</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card tool-card text-center">
                    <div class="card-body">
                        <i class="fas fa-arrows-alt-h fa-icon"></i>
                        <h5 class="card-title">PDF Merger</h5>
                        <p class="card-text">Combine multiple PDF files into one single document.</p>
                        <a href="/merger" class="btn btn-primary">Go to Merger</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card tool-card text-center">
                    <div class="card-body">
                        <i class="fas fa-eraser fa-icon"></i>
                        <h5 class="card-title">Remove Pages</h5>
                        <p class="card-text">Remove specific pages or ranges from your PDF.</p>
                        <a href="/remove" class="btn btn-danger">Go to Remove</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card tool-card text-center">
                    <div class="card-body">
                        <i class="fas fa-sync-alt fa-icon"></i>
                        <h5 class="card-title">Rotate PDF</h5>
                        <p class="card-text">Rotate your PDF pages to the desired orientation.</p>
                        <a href="/rotate" class="btn btn-warning">Go to Rotate</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card tool-card text-center">
                    <div class="card-body">
                        <i class="fas fa-file-lines fa-icon"></i>
                        <h5 class="card-title">Extract Text from PDF</h5>
                        <p class="card-text">Upload a PDF to extract its text content.</p>
                        <a href="/extract" class="btn btn-custom">Go to Extract</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card tool-card text-center">
                    <div class="card-body">
                        <i class="fas fa-list-ol fa-icon" style="font-size: 40px;"></i>
                        <h5 class="card-title">Page Numbering</h5>
                        <p class="card-text">Add page numbers to your PDF files.</p>
                        <a href="/page-numbering" class="btn btn-primary">Go to Page Numbering</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card tool-card text-center">
                    <div class="card-body">
                        <i class="fas fa-file-pdf fa-icon"></i>
                        <h5 class="card-title">Extract PDF Pages</h5>
                        <p class="card-text">Extract specific pages or a range of pages from a PDF.</p>
                        <a href="/extract_pages" class="btn btn-primary">Go to Extract Pages</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card tool-card text-center">
                    <div class="card-body">
                        <i class="fas fa-image fa-icon"></i>
                        <h5 class="card-title">Create PDF from Images</h5>
                        <p class="card-text">Convert images to a PDF document.</p>
                        <a href="/combine_images" class="btn btn-primary">Go to Image to PDF</a>
                    </div>
                </div>
            </div>
        </div>
   </body>
   </html>
   """

SPLITTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Splitter</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #ff9a9e, #fad0c4);
            color: #333;
        }
        h1 {
            animation: fadeIn 1.5s ease;
            font-family: 'Montserrat', sans-serif; 
            text-transform: uppercase; 
            font-weight: bold; 
        }
        .form-container {
            animation: slideIn 1s ease;
            background: #fff;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
        }
        @keyframes slideIn {
            0% { transform: translateX(-100%); opacity: 0; }
            100% { transform: translateX(0); opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="container py-5">
        <h1 class="text-center mb-4">PDF Splitter</h1>
        <div class="form-container">
            <form method="POST" action="/splitter" enctype="multipart/form-data">
                <div class="mb-3">
                    <label for="file" class="form-label">Upload PDF</label>
                    <input type="file" class="form-control" name="file" accept=".pdf" required>
                </div>
                <div class="mb-3">
                    <label for="start_page" class="form-label">Start Page</label>
                    <input type="number" class="form-control" name="start_page" min="1" required>
                </div>
                <div class="mb-3">
                    <label for="end_page" class="form-label">End Page</label>
                    <input type="number" class="form-control" name="end_page" min="1" required>
                </div>
                <button type="submit" class="btn btn-primary">Split PDF</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

MERGER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Merger</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #74ebd5, #acb6e5);
            color: #333;
        }
        h1 {
            font-family: 'Montserrat', sans-serif; 
            text-transform: uppercase; 
            font-weight: bold; 
        }
        .form-container {
            background: #fff;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="container py-5">
        <h1 class="text-center mb-4">PDF Merger</h1>
        <div class="form-container">
            <form method="POST" action="/merger" enctype="multipart/form-data">
                <div class="mb-3">
                    <label for="files" class="form-label">Upload PDFs</label>
                    <input type="file" class="form-control" name="files" accept=".pdf" multiple required>
                </div>
                <button type="submit" class="btn btn-primary">Merge PDFs</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

# Other HTML and routes remain unchanged
REMOVE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Remove Pages</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container py-5">
        <h1 class="text-center mb-4">Remove Pages from PDF</h1>
        <div class="form-container">
            <form method="POST" action="/remove" enctype="multipart/form-data">
                <div class="mb-3">
                    <label for="file" class="form-label">Upload PDF</label>
                    <input type="file" class="form-control" name="file" accept=".pdf" required>
                </div>
                <div class="mb-3">
                    <label for="pages" class="form-label">Pages to Remove (e.g., 1,3,5 or 2-4)</label>
                    <input type="text" class="form-control" name="pages" required>
                </div>
                <button type="submit" class="btn btn-danger">Remove Pages</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

ROTATE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rotate PDF</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container py-5">
        <h1 class="text-center mb-4">Rotate PDF</h1>
        <div class="form-container">
            <form method="POST" action="/rotate" enctype="multipart/form-data">
                <div class="mb-3">
                    <label for="file" class="form-label">Upload PDF</label>
                    <input type="file" class="form-control" name="file" accept=".pdf" required>
                </div>
                <div class="mb-3">
                    <label for="degree" class="form-label">Rotate Degree (90, 180, 270)</label>
                    <input type="number" class="form-control" name="degree" required>
                </div>
                <button type="submit" class="btn btn-warning">Rotate PDF</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

EXTRACT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Extract Text</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #d4fc79, #96e6a1);
            color: #333;
        }
        h1 {
            text-align: center;
            margin-bottom: 20px;
            font-family: 'Montserrat', sans-serif; 
            text-transform: uppercase; 
            font-weight: bold; 
        }
        .form-container {
            background: #fff;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            padding: 20px;
            margin: 20px auto;
            max-width: 600px;
        }
        textarea {
            width: 100%;
            height: 300px;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="container py-5">
        <h1>Extract Text</h1>
        <div class="form-container">
            <form method="POST" action="/extract" enctype="multipart/form-data">
                <div class="mb-3">
                    <label for="file" class="form-label">Upload PDF</label>
                    <input type="file" class="form-control" name="file" accept=".pdf" required>
                </div>
                <button type="submit" class="btn btn-success">Extract Text</button>
            </form>
            {% if text %}
            <h3 class="mt-4">Extracted Text:</h3>
            <textarea readonly>{{ text }}</textarea>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

PAGE_NUMBERING_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Page Numbering</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #74ebd5, #acb6e5);
            color: #333;
        }
        .form-container {
            background: #fff;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="container py-5">
        <h1 class="text-center mb-4">PDF Page Numbering</h1>
        <div class="form-container">
            <form method="POST" action="/page-numbering" enctype="multipart/form-data">
                <div class="mb-3">
                    <label for="pdf_file" class="form-label">Upload PDF</label>
                    <input type="file" class="form-control" name="pdf_file" accept=".pdf" required>
                </div>
                <div class="mb-3">
                    <label for="numbering_method" class="form-label">Numbering Style</label>
                    <select class="form-select" name="numbering_method" required>
                        <option value="simple">1, 2, 3, ...</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label for="position" class="form-label">Position</label>
                    <select class="form-select" name="position" required>
                        <option value="left">Left</option>
                        <option value="middle">Middle</option>
                        <option value="right">Right</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary">Add Page Numbers</button>
            </form>
        </div>
    </div>
</body>
</html>
"""


# Extract Pages HTML Template
EXTRACT_PAGES_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Extract PDF Pages</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #ff9a9e, #fad0c4);
            color: #333;
        }
        h1 {
            font-family: 'Montserrat', sans-serif;
            text-transform: uppercase;
            font-weight: bold;
        }
        .form-container {
            background: #fff;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="container py-5">
        <h1 class="text-center mb-4">Extract PDF Pages</h1>
        <div class="form-container">
            <form method="POST" action="/extract_pages" enctype="multipart/form-data">
                <div class="mb-3">
                    <label for="file" class="form-label">Upload PDF</label>
                    <input type="file" class="form-control" name="file" accept=".pdf" required>
                </div>
                <div class="mb-3">
                    <label for="pages" class="form-label">Enter Pages (comma-separated or range)</label>
                    <input type="text" class="form-control" name="pages" placeholder="e.g., 1, 2, 5-7" required>
                </div>
                <button type="submit" class="btn btn-primary">Extract Pages</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

# Combine Images HTML Template
COMBINE_IMAGES_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Combine Images to PDF</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #ff9a9e, #fad0c4);
            color: #333;
        }
        h1 {
            font-family: 'Montserrat', sans-serif;
            text-transform: uppercase;
            font-weight: bold;
        }
        .form-container {
            background: #fff;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="container py-5">
        <h1 class="text-center mb-4">Combine Images to PDF</h1>
        <div class="form-container">
            <form method="POST" action="/combine_images" enctype="multipart/form-data">
                <div class="mb-3">
                    <label for="images" class="form-label">Upload Images</label>
                    <input type="file" class="form-control" name="images" accept="image/*" multiple required>
                </div>
                <button type="submit" class="btn btn-primary">Create PDF</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

# Routes
@app.route("/")
def home():
    return render_template_string(HOME_HTML)

@app.route("/splitter", methods=["GET", "POST"])
def splitter():
    if request.method == "POST":
        file = request.files["file"]
        start_page = int(request.form["start_page"])
        end_page = int(request.form["end_page"])

        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        output_path = os.path.join(OUTPUT_FOLDER, f"split_{file.filename}")
        file.save(input_path)

        reader = PdfReader(input_path)
        writer = PdfWriter()
        for page in range(start_page - 1, end_page):
            writer.add_page(reader.pages[page])

        with open(output_path, "wb") as output_pdf:
            writer.write(output_pdf)

        return send_file(output_path, as_attachment=True)
    return render_template_string(SPLITTER_HTML)

@app.route("/merger", methods=["GET", "POST"])
def merger():
    if request.method == "POST":
        files = request.files.getlist("files")
        output_path = os.path.join(OUTPUT_FOLDER, "merged.pdf")

        writer = PdfWriter()
        for file in files:
            input_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(input_path)
            reader = PdfReader(input_path)
            for page in reader.pages:
                writer.add_page(page)

        with open(output_path, "wb") as output_pdf:
            writer.write(output_pdf)

        return send_file(output_path, as_attachment=True)
    return render_template_string(MERGER_HTML)

@app.route("/remove", methods=["GET", "POST"])
def remove_pages():
    if request.method == "POST":
        pdf_file = request.files["file"]
        pages_to_remove = request.form["pages"]

        pdf_reader = PdfReader(pdf_file)
        pdf_writer = PdfWriter()
        total_pages = len(pdf_reader.pages)

        pages_to_remove_list = []
        for part in pages_to_remove.split(","):
            if "-" in part:
                start, end = map(int, part.split("-"))
                pages_to_remove_list.extend(range(start, end + 1))
            else:
                pages_to_remove_list.append(int(part))

        for i in range(total_pages):
            if i + 1 not in pages_to_remove_list:
                pdf_writer.add_page(pdf_reader.pages[i])

        output_pdf = io.BytesIO()
        pdf_writer.write(output_pdf)
        output_pdf.seek(0)
        return send_file(output_pdf, as_attachment=True, download_name="removed_pages.pdf", mimetype="application/pdf")
    return render_template_string(REMOVE_HTML)

@app.route("/rotate", methods=["GET", "POST"])
def rotate_pdf():
    if request.method == "POST":
        pdf_file = request.files["file"]
        degree = int(request.form["degree"])

        pdf_reader = PdfReader(pdf_file)
        pdf_writer = PdfWriter()

        for page in pdf_reader.pages:
            page.rotate(degree)
            pdf_writer.add_page(page)

        output_pdf = io.BytesIO()
        pdf_writer.write(output_pdf)
        output_pdf.seek(0)
        return send_file(output_pdf, as_attachment=True, download_name="rotated.pdf", mimetype="application/pdf")
    return render_template_string(ROTATE_HTML)

@app.route("/extract", methods=["GET", "POST"])
def extract():
    text = None
    if request.method == "POST":
        uploaded_file = request.files["file"]
        if uploaded_file:
            # Use the configured UPLOAD_FOLDER for saving the file
            file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
            uploaded_file.save(file_path)
            
            # Extract text from the uploaded PDF
            reader = PdfReader(file_path)
            text = "\n".join(page.extract_text() for page in reader.pages)
            
            # Cleanup: remove the uploaded file after processing
            os.remove(file_path)

    return render_template_string(EXTRACT_HTML, text=text)

# Add Page Numbers Function
def add_page_numbers(pdf_data, numbering_method, position):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    reader = PdfReader(io.BytesIO(pdf_data))
    total_pages = len(reader.pages)

    # Adjust vertical position for page numbers
    for i, page in enumerate(reader.pages, start=1):
        if numbering_method == "simple":
            text = f"{i}"
        elif numbering_method == "detailed":
            text = f"Page {i}"
        elif numbering_method == "total":
            text = f"{i} of {total_pages}"
        else:
            text = f"{i}"

        # Adjust position
        if position == "left":
            x = 50
        elif position == "middle":
            x = 300
        elif position == "right":
            x = 550
        else:
            x = 300
        
        y = 10  # Lower the position to avoid bottom gap
        can.setFont("Helvetica", 10)  # Ensure text fits
        can.drawString(x, y, text)
        can.showPage()

    can.save()
    packet.seek(0)
    overlay = PdfReader(packet)
    writer = PdfWriter()

    for original_page, overlay_page in zip(reader.pages, overlay.pages):
        original_page.merge_page(overlay_page)
        writer.add_page(original_page)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output

@app.route("/page-numbering", methods=["GET", "POST"])
def page_numbering():
    if request.method == "POST":
        pdf_file = request.files["pdf_file"]
        numbering_method = request.form["numbering_method"]
        position = request.form["position"]

        if pdf_file:
            pdf_data = pdf_file.read()
            output = add_page_numbers(pdf_data, numbering_method, position)

            return send_file(
                output,
                as_attachment=True,
                download_name="numbered_output.pdf",
                mimetype="application/pdf",
            )
    return render_template_string(PAGE_NUMBERING_TEMPLATE)

@app.route('/extract_pages', methods=['GET', 'POST'])
def extract_pages():
    if request.method == 'POST':
        # Get file and page range input
        file = request.files['file']
        pages_input = request.form['pages']

        # Save the uploaded file
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        # Parse page numbers and ranges
        pages = parse_page_range(pages_input)

        # Extract the specified pages
        extracted_pdf = extract_pdf_pages(file_path, pages)

        # Save the extracted pages as a new PDF
        output_path = os.path.join('outputs', 'extracted_pages.pdf')
        with open(output_path, 'wb') as output_file:
            extracted_pdf.write(output_file)

        return send_file(output_path, as_attachment=True)

    return render_template_string(EXTRACT_PAGES_HTML)

@app.route('/combine_images', methods=['GET', 'POST'])
def combine_images():
    if request.method == 'POST':
        # Get images
        images = request.files.getlist('images')
        image_paths = []
        
        for img in images:
            img_path = os.path.join('uploads', img.filename)
            img.save(img_path)
            image_paths.append(img_path)

        # Convert images to PDF
        output_pdf_path = os.path.join('outputs', 'combined_images.pdf')
        images = [Image.open(img_path).convert('RGB') for img_path in image_paths]
        images[0].save(output_pdf_path, save_all=True, append_images=images[1:], resolution=100.0)

        return send_file(output_pdf_path, as_attachment=True)

    return render_template_string(COMBINE_IMAGES_HTML)

def parse_page_range(pages_input):
    # Split input by commas, handle ranges
    page_list = []
    for part in pages_input.split(','):
        if '-' in part:
            start, end = part.split('-')
            page_list.extend(range(int(start), int(end) + 1))
        else:
            page_list.append(int(part))
    return sorted(set(page_list))

def extract_pdf_pages(file_path, pages):
    pdf_reader = PdfReader(file_path)
    pdf_writer = PdfWriter()

    # Adjust for 0-based indexing
    for page_num in pages:
        if 1 <= page_num <= len(pdf_reader.pages):
            pdf_writer.add_page(pdf_reader.pages[page_num - 1])

    return pdf_writer

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
