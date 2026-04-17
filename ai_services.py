from google import genai
import json
import os

# Client automatically picks up the GEMINI_API_KEY environment variable
client = genai.Client() 
MODEL_ID = "gemini-2.5-flash" 

def generate_resume(profile_data, role):
    prompt = f"Act as an expert ATS resume writer. Take this profile data and output a tailored Markdown resume for a {role} role. Focus on impact and keywords.\n\nProfile Data:\n{profile_data}"
    response = client.models.generate_content(model=MODEL_ID, contents=prompt)
    return response.text

def generate_study_plan(role, domain):
    prompt = f"Act as an expert technical mentor. Create a structured 3-day syllabus covering key concepts for a {role} specializing in {domain}. Format the output in Markdown."
    response = client.models.generate_content(model=MODEL_ID, contents=prompt)
    return response.text

def generate_qa(role, level):
    prompt = f"Generate 3 technical and 2 behavioral interview questions for a {level} {role}. Return ONLY a valid JSON array of objects, each with a 'question' and 'ideal_answer' key. Do not include markdown formatting."
    response = client.models.generate_content(model=MODEL_ID, contents=prompt)
    
    clean_json = response.text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(clean_json)
    except json.JSONDecodeError:
        return [{"question": "Failed to parse questions.", "ideal_answer": "Please try generating again."}]

def evaluate_answer(question, user_answer, role):
    prompt = f"Act as a technical interviewer for a {role}. The candidate was asked: '{question}'. They answered: '{user_answer}'. Evaluate their response. If the user provides garbage input, gibberish, or a completely irrelevant answer, score them a 0/10 and strictly tell them to take the interview seriously. Give a score out of 10 and exactly 2 sentences of constructive feedback on how to improve."
    response = client.models.generate_content(model=MODEL_ID, contents=prompt)
    return response.text
