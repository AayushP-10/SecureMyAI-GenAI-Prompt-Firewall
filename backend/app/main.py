from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal
from dotenv import load_dotenv

# Load environment variables from .env file.
load_dotenv()

# Import the LLM and firewall logic
from app.llm.groq import call_groq
from app.llm.gemini import call_gemini
from app.firewall.classifier import classify_risk

# Create the FastAPI app
app = FastAPI()

# Define the request body schema
class PromptRequest(BaseModel):
    prompt: str
    llm: Literal["groq", "gemini"]

# Define the response schema
class PromptResponse(BaseModel):
    risk: str
    llm_response: str

@app.post("/prompt", response_model=PromptResponse)
def check_prompt(request: PromptRequest):
    """
    Accepts a prompt and LLM choice, returns risk and LLM response.
    """
    risk = classify_risk(request.prompt)

    if request.llm == "groq":
        llm_response = call_groq(request.prompt)
    elif request.llm == "gemini":
        llm_response = call_gemini(request.prompt)
    else:
        raise HTTPException(status_code=400, detail="Invalid LLM choice.")

    return {"risk": risk, "llm_response": llm_response} 