# LegalEase Web Application

LegalEase is an innovative software solution designed to simplify the complexity of legal documents. With its advanced algorithms, it effortlessly processes legal documents in PDF or text format and delivers concise and easy-to-understand summaries. Our platform ensures accessibility to legal information for all, empowering individuals and businesses to navigate the legal landscape with confidence and clarity.

## Features

- **Document Upload and Summary Generation:** Users can upload documents and receive concise summaries.
- **Audio Playback of Text:** Text-to-audio conversion for accessible content delivery.
- **Multi-Page Interface:** Includes multiple pages for different functionalities.
- **Interactive Chat and Translation Services:** Integrated chatbot and translation for multilingual support.

## Prerequisites

Before you start, ensure you have the following installed:
- **Python 3.6 or higher**: Download it from [python.org](https://www.python.org/downloads/).
- **Conda**: This will be used to manage environments and install packages. Follow the installation guide [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/).

## Installation

1. **Clone the repository**:
Drive link of working prototype https://drive.google.com/file/d/1t4mN7fe9_lLbB8uiJws2kEwzizkG1ZoW/view?usp=sharing

Download the Repository and the open the repository folder


2. **Create and activate a Conda environment**:
    conda create --name legalease python=3.8
    conda activate legalease

3. **Install required Python packages**:
    *Install Flask and other necessary packages*:
    conda install flask
    *If there is a requirements.txt file, run*:
    pip install -r requirements.txt

## Configuring the Application

Ensure that all paths to static files (like CSS and images) and templates are correctly set in your Flask application script (app.py). The static files should be in a folder named static and HTML templates in a folder named templates unless specified otherwise in your Flask configuration.

## Running the Application
1. Run the Flask application:
Use Python to start the server directly.
    python app.py
2. This will start the server on http://127.0.0.1:9000/. Open this URL in a web browser to view your application.

## Navigating the Application
1. Home Page: Accessible by visiting http://127.0.0.1:9000/. This is the main page of your application.
2. Document Processing: Navigate to /page2 for document uploading and summarization functionalities.
3. Audio Playback: Go to /play_audio to listen to the text as audio.
4. Chatbot Interaction: The chatbot can be accessed through a dedicated icon or link, typically found on the bottom-right of the application interface.

## Contributing
Contributions to the LegalEase project are welcome! Please feel free to submit pull requests or open issues to discuss potential changes or improvements.

## Support
For support open an issue on the GitHub project page.




