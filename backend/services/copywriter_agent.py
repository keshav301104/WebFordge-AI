import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic.v1 import BaseModel, Field

class ElementMapping(BaseModel):
    element_id: str = Field(description="The exact data-tpd-id from the original scraped elements.")
    new_value: str = Field(description="The rewritten text OR the new image URL for this specific element.")

class Variant(BaseModel):
    variant_name: str = Field(description="Must be 'Urgency', 'Trust', or 'Logical'.")
    element_mappings: list[ElementMapping] = Field(description="List of text/image updates mapped exactly to the original IDs.")

class CopywriterOutput(BaseModel):
    variants: list[Variant] = Field(description="Exactly 3 variants: Urgency, Trust, and Logical.")

# Add custom_prompt and creative_image_url to the parameters
async def generate_variants(scraped_json_str: str, ad_context: dict, creative_image_url: str = "", custom_prompt: str = "") -> dict:
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", temperature=0.5)
    structured_llm = llm.with_structured_output(CopywriterOutput)

    # Format the optional user instructions
    user_steering = f"\nUSER CUSTOM INSTRUCTIONS (PRIORITY OVERRIDE):\n{custom_prompt}" if custom_prompt else ""
    
    # Format the image injection mandate
    image_mandate = f"\nMANDATORY ASSET: You MUST assign this exact URL ({creative_image_url}) to the largest, most prominent hero/header image on the page." if creative_image_url else ""

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are an elite autonomous conversion rate optimization agent. 
        Your job is to take original landing page assets and rewrite/replace them.
        
        You MUST generate exactly three strategic variants:
        1. Urgency: Focus on FOMO, limited time, and fast action.
        2. Trust: Focus on reliability, social proof, and authority.
        3. Logical: Focus on direct features, metrics, and clear benefits.
        
        ASSET REPLACEMENT RULES:
        - For 'text' types: Rewrite to match the Ad Context.
        - For 'image' types: Use highly relevant Unsplash URLs (https://source.unsplash.com/featured/?<keyword>).{image_mandate}
        {user_steering}
        
        CRITICAL: Retain exact element IDs (data-tpd-id). Do not skip elements."""),
        
        ("human", """Here is the Ad Context derived from the uploaded image:
        {ad_context}
        
        Here are the extracted assets:
        {scraped_elements}
        
        Generate the 3 customized variants.""")
    ])

    chain = prompt | structured_llm
    
    try:
        result = await chain.ainvoke({
            "ad_context": json.dumps(ad_context, indent=2),
            "scraped_elements": scraped_json_str
        })
        return result.dict()
    except Exception as e:
        print(f"Copywriter Agent failed: {str(e)}")
        raise Exception("Failed to generate variants.")