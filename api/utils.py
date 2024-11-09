from groq import Groq
from django.conf import settings


def send_code_to_groq(_input):
    client = Groq(api_key=settings.GROQ_API_KEY)
    try:
        # Create the completion request
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "Give medical advice to patients."
                },
                {
                    "role": "user",
                    "content": _input
                }
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )

        # Initialize an empty response content string
        response_content = ""

        # Loop through each chunk to capture content
        for chunk in completion:
            print("Chunk received:", chunk)  # Print each chunk to inspect
            # Assuming chunk contains 'delta' with 'content', adjust if needed
            if hasattr(chunk, 'choices') and chunk.choices[0].delta.content:
                response_content += chunk.choices[0].delta.content

        # Return the assembled content
        if response_content:
            return {"output": response_content}
        else:
            return {"error": "Unexpected response structure, no content found."}
       
    except Exception as e:
        return {"error": str(e)}
