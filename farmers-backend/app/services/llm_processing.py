from openai import OpenAI

client = OpenAI()

EXTRACTION_PROMPT = """Extract key farming information from this text:
{text}

Return JSON format with these fields:
- crops: list of crops grown
- livestock: list of livestock (empty if none)
- farm_size: number in hectares
- certifications: list of certifications
- years_experience: integer
- annual_capacity: string description
- farming_methods: list of techniques used
- challenges: list of mentioned challenges"""

def extract_structured_data(text: str):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": EXTRACTION_PROMPT.format(text=text)
            }],
            temperature=0.1
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

PROFILE_PROMPT = """Create a professional farmer profile from this data:
{data}

Guidelines:
- Use simple, clear language
- Highlight key production capabilities
- Mention years of experience
- Include certifications
- Keep under 200 words"""

def generate_profile(structured_data: dict):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": PROFILE_PROMPT.format(data=structured_data)
            }],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Profile generation error: {str(e)}"