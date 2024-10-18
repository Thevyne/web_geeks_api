import openai
from django.conf import settings

# Set the OpenAI API key from your Django settings
openai.api_key = settings.APIKEY

def send_code_to_api(complaint):
    try:
        # Create the Chat Completion with the old version of the API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can use other models like "gpt-3.5-turbo" if available
            messages=[
                {"role": "system", "content": "You are a helpful and professional medical assistant."},
                {"role": "user", "content": f"My complaint is: {complaint}"},
            ],
        )
        # Extract and return the message content from the AI response
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        # In case of an error, log the exception and return a default error message
        return f"Error: {str(e)}"