# Zara - Reactive Journal Companion 

# DISCLAIMER 

Disclaimer for Zara: A Reactive Journal/Therapy Bot

Please read this disclaimer carefully before using Zara, the reactive journal/therapy bot ("the Service") created by general-ai ("us", "we", or "our").

## 1. Not a Medical or Health Service

Zara is designed to provide support and enhance your journaling experience through conversational interaction and artificial intelligence. It is not a replacement for professional medical advice, diagnosis, or treatment. The Service is not a licensed healthcare provider, nor does it offer psychological therapy or mental health services.

## 2. No Professional Advice

The information and feedback provided by Zara are for general informational purposes only and are not intended to be a substitute for professional advice, diagnosis, or treatment. Always seek the advice of your physician, psychologist, therapist, or other qualified health provider with any questions you may have regarding a medical condition, mental health issue, or treatment, and never disregard professional medical advice or delay in seeking it because of something you have read on or through the Service.

## 3. Limitation of Liability

general-ai and its employees, contractors, and affiliates are not liable for any decisions, actions, or inactions you take based on the use of Zara, nor are we responsible for any harm or damage you may experience in relation to your use of the Service. Your use of Zara is at your sole risk.

## 4. No Endorsement

The Service may suggest resources or actions, but these suggestions should not be interpreted as endorsements of any specific therapy, healthcare provider, medication, or treatment plan.

## 5. Personal Responsibility

You are solely responsible for your interactions with Zara and the outcomes thereof. We encourage you to use the Service as a supplementary tool for self-reflection and journaling, not as a primary means of addressing psychological or medical needs.

## 6. Changes to This Disclaimer

We reserve the right to make changes to this disclaimer at any time without notice. Your continued use of Zara after any changes are made will be considered acceptance of those changes.

## 7. Contact Us

If you have any questions about this disclaimer, please contact us at jesse@general-ai.com.au.

By using Zara, you acknowledge and agree to the terms outlined in this disclaimer.

## Description

This project is a Streamlit-based web application that leverages OpenAI's GPT models for various functionalities, including chatbots, journaling, and document embedding. It incorporates a dynamic chat interface where users can interact with an AI assistant powered by GPT-3.5 and GPT-4 models. The application also features functionalities for creating and maintaining a journal, embedding journal entries for similarity searches, and managing user profiles.

## Features

- **AI-Driven Chat Interface**: Interact with a sophisticated chatbot powered by GPT-3.5 and GPT-4 models.
- **Journaling**: Automatically generate journal entries from chatlogs and embed them for future reference and similarity searches.
- **User Profiles**: Maintain and update user profiles based on interactions with the chatbot.
- **Document Embedding**: Use OpenAI embeddings and FAISS vector storage for efficient similarity searches within journal entries.

## Setup

### Prerequisites

- Python 3.11.x
- Streamlit
- OpenAI API key (for GPT-3.5 and GPT-4 access)
- python-dotenv (for environment variable management)
- Other dependencies listed in `requirements.txt`

### Installation

1. Clone the repository to your local machine.
2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   python -m spacy download en_core_web_md
   ```
3. Create a `.env` file at the root of the project directory, and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
4. Run the Streamlit application:
   ```
   streamlit run app.py
   ```

### Configuration

- **Environment Variables**: Ensure your OpenAI API key is stored in the `.env` file.
- **Directory Structure**: The application expects specific directories for `Memories`, `Personas`, `Portrait`, and `system prompts`. Make sure these exist and are structured as per the application's requirements.

## Usage

- **Starting the Application**: Access the web interface by running the Streamlit command and navigating to the provided URL.
- **Interacting with the Chatbot**: Type your queries or messages in the chat input box and receive responses from the AI assistant.
- **Journaling and Profiles**: The application automatically updates journal entries and user profiles based on your interactions with the chatbot.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests with your proposed changes.

## License

[MIT License](LICENSE.md)

## Acknowledgments

- OpenAI for the GPT models.
- Streamlit for the web application framework.

---

This README provides a basic overview and setup instructions for the project. Adjust the content as needed to better describe your project, how to set it up, use it, and contribute to it.
