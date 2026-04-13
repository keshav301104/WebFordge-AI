import base64
import os
import httpx
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

# 1. The Output Contract
class AdContext(BaseModel):
    primary_value_prop: str = Field(description="The main offer, discount, or benefit presented in the ad.")
    target_audience: str = Field(description="The assumed demographic or persona this ad is targeting.")
    tone: str = Field(description="The emotional tone of the ad (e.g., Urgent, Professional, Playful, Trustworthy).")
    color_palette: list[str] = Field(description="List of 2-3 dominant hex color codes found in the ad.")

def encode_image(image_path: str) -> str:
    """Helper function to convert local image files to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

async def analyze_ad_creative(file_path: str = None, image_url: str = None) -> dict:
    """Analyzes an ad creative using Gemini 3.1 Flash Lite."""
    
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", temperature=0)
    structured_llm = llm.with_structured_output(AdContext)

    image_content = []
    
    if file_path and os.path.exists(file_path):
        base64_image = encode_image(file_path)
        image_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        })
    elif image_url:
        # NEW FIX: Download the image from the URL and convert it to Base64 for Gemini
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(image_url)
            response.raise_for_status()
            base64_image = base64.b64encode(response.content).decode('utf-8')
            image_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            })
    else:
        raise ValueError("Must provide either a valid file_path or image_url.")

    image_content.insert(0, {
        "type": "text", 
        "text": "You are an expert marketing analyst. Analyze this ad creative. Extract the primary value proposition, the target audience, the overall tone, and the 2-3 dominant brand colors (as hex codes)."
    })

    # Use asynchronous invocation
    response = await structured_llm.ainvoke([HumanMessage(content=image_content)])
    
    # Return standard dictionary
    return response.dict()