from flask import Flask, render_template, request, redirect, url_for, jsonify
from transformers import BartForConditionalGeneration, BartTokenizer
import subprocess
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
import PyPDF2
import pdfplumber
import pdfminer
import pdfminer.pdfparser
import pdfminer.pdfdocument
import pdfminer.pdfpage
import pdfminer.pdfinterp
import pdfminer.converter
import pdfminer.layout
from docx import Document
import io
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
import re
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from gtts import gTTS
from transformers import MarianMTModel, MarianTokenizer

# Load English to Hindi model
model_name_hindi = 'Helsinki-NLP/opus-mt-en-hi'
tokenizer_hindi = MarianTokenizer.from_pretrained(model_name_hindi)
model_hindi = MarianMTModel.from_pretrained(model_name_hindi)

def translate_text(text, model, tokenizer):
    # Tokenize the input text
    inputs = tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
    # Translate the input text
    translated = model.generate(**inputs)
    # Decode the translated text
    translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
    return translated_text

def translate_text_chunked(text, model, tokenizer, max_chunk_size):
    # Chunk the input text
    chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    
    # Translate each chunk and concatenate the translations
    translated_text = ""
    for chunk in chunks:
        # Translate the chunk
        translated_chunk = translate_text(chunk, model, tokenizer)
        # Append the translated chunk to the final translation
        translated_text += translated_chunk + " "
    
    return translated_text.strip()  # Remove leading/trailing whitespace





# Utility function to read PDF files
def read_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        resource_manager = PDFResourceManager()
        fake_file_handle = io.StringIO()
        converter = TextConverter(resource_manager, fake_file_handle, laparams=pdfminer.layout.LAParams())
        interpreter = PDFPageInterpreter(resource_manager, converter)
        
        for page in PDFPage.get_pages(file, check_extractable=True):
            interpreter.process_page(page)
            text += fake_file_handle.getvalue()

        converter.close()
        fake_file_handle.close()
        
    return text
    
# Utility function to read DOCX files
def read_docx(file_path):
    doc = Document(file_path)
    text = []
    for para in doc.paragraphs:
        text.append(para.text)
    return "\n".join(text)

# Utility function to read text files
def read_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# model = BartForConditionalGeneration.from_pretrained("legal_ease_model")
# tokenizer = BartTokenizer.from_pretrained("legal_ease_model")

# def ML_Model(inputText):
#     legal_document = inputText
#     input_ids = tokenizer.encode(legal_document, return_tensors="pt", max_length=1024, truncation=True)
#     summary_ids = model.generate(input_ids, max_length=150, length_penalty=2.0, num_beams=4, early_stopping=True)
#     generated_summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
#     return generated_summary


def ML_Model(text, model_path = 'saved_model', max_chunk_size=950):
    try:
        # Load model and tokenizer
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)
        # Function to generate summary for a single chunk
        def generate_summary(chunk):
            inputs = tokenizer.encode("summarize: " + chunk, return_tensors="pt", max_length=512, truncation=True)
            outputs = model.generate(inputs, max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
            return tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Function to chunk the text
        def chunk_document_flexible(text, max_chunk_size):
            chunks = []
            current_chunk = []
            current_size = 0

            sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)  # Split text into sentences
            for sentence in sentences:
                sentence_size = len(sentence.split())
                if current_size + sentence_size > max_chunk_size and current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_size = 0
                current_chunk.append(sentence)
                current_size += sentence_size
            if current_chunk:
                chunks.append(' '.join(current_chunk))

            return chunks

        # Generate summaries for each chunk
        chunks = chunk_document_flexible(text, max_chunk_size)
        summaries = [generate_summary(chunk) for chunk in chunks]

        # Combine summaries
        final_summary = ' '.join(summaries)

        return final_summary

    except Exception as e:
        print(f"Error: {str(e)}")
        return None
    

STREAMLIT_PORT = 8501  # Port for the Streamlit app
# Define the full path to the chatbot.py file
CHATBOT_PATH = 'GEMINI_chatbot/chatbot.py'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/page2', methods=['GET',"POST"])
def page2():
    form_ = UploadFileForm()

    if form_.validate_on_submit():
        file = form_.file.data
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Determine the file type and process accordingly
        if filename.endswith('.pdf'):
            content = read_pdf(file_path)
            content = content.replace("\n", " ")
        elif filename.endswith('.docx'):
            content = read_docx(file_path)
            content = content.replace("\n", " ")
        elif filename.endswith('.txt'):
            content = read_txt(file_path)
            content = content.replace("\n", " ")
        else:
            input_text = "Enter a valid value"
            return redirect(url_for('page2', input_text=input_text))

        generated_summary = ML_Model(content)
        
        input_text = generated_summary
        # processed_text = generated_summary
        return redirect(url_for('page2', input_text=input_text))
    
    return render_template('page2.html', form_ = form_)

@app.route('/run_streamlit')
def run_streamlit():
    # Run the Streamlit command in a subprocess
    subprocess.Popen(['streamlit', 'run', '--server.port', str(STREAMLIT_PORT), CHATBOT_PATH])
    return 'Redirecting'



@app.route('/process_summary', methods=['POST', 'GET'])
def process_summary():
    input_text = next(request.form.values())


    generated_summary = ML_Model(input_text)


    input_text = generated_summary
    # processed_text = generated_summary
    return redirect(url_for('page2', input_text=input_text))

@app.route('/play_audio/<filename>')
def play_audio(filename):
    # Render a template that includes an HTML5 audio player
    return render_template('play_audio.html', filename=filename)

@app.route('/text2audio', methods=['POST', 'GET'])
def text_to_audio():
    if request.method == 'POST' and 'text_data' in request.form:
        text = request.form['text_data']
        filename = 'summary_english.mp3'
        tts = gTTS(text=text, lang='en')
        tts.save('static/' + filename)
        return redirect(url_for('play_audio', filename=filename))
    else:
        # Handle the case where the correct data isn't provided
        return "No text provided for audio generation", 400
    
@app.route('/translate', methods=['POST', 'GET'])
def translate():

    if 'text_data' in request.form:
        text = request.form['text_data']
        translated_text_hindi_chunked = translate_text_chunked(text, model_hindi, tokenizer_hindi, max_chunk_size=512)
        return redirect(url_for('page2', input_text=translated_text_hindi_chunked))
    else:
        # If text_data is not in request.form, it means no data was sent
        return "No text provided for translation", 400

if __name__ == '__main__':
    app.run(debug=True, port = 9000)
