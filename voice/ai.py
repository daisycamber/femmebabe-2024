def get_ai_response(text):
    from openai import OpenAI
    from django.conf import settings
    client = OpenAI(api_key=settings.OPENAI_KEY)
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": text}
        ]
    )
    return completion