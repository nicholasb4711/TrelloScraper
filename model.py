import os
from openai import OpenAI

def get_resume_points(prompt):
    """Get resume points from OpenAI."""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {
                "role": "system",
                "content": "You are a professional resume writer who excels at creating impactful bullet points that highlight technical achievements and skills."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    return response.choices[0].message.content