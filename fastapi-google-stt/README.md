# FastAPI Google Speech-to-Text

This project is a FastAPI application that integrates with Google Cloud Speech-to-Text API to provide real-time audio transcription services.

## Project Structure

```
fastapi-google-stt
├── app
│   ├── main.py          # Entry point of the FastAPI application
│   ├── api
│   │   └── stt.py       # API endpoints for speech-to-text functionality
│   ├── services
│   │   └── google_stt.py # Logic for interacting with Google Cloud Speech-to-Text API
│   └── models
│       └── __init__.py  # Initialization of models package
├── requirements.txt      # Project dependencies
├── .env                  # Environment variables
└── README.md             # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd fastapi-google-stt
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory and add your Google Cloud project ID and any other necessary configuration settings.

5. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

## Usage

- The API provides endpoints for uploading audio files and receiving transcriptions.
- Refer to the API documentation in `app/api/stt.py` for specific endpoint details and request formats.

## License

This project is licensed under the MIT License.