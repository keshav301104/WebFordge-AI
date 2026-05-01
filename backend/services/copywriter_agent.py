from typing import List
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic.v1 import BaseModel, Field

class ElementMapping(BaseModel):
    element_id: str = Field(description="The exact data-tpd-id from the original scraped elements.")
    new_value: str = Field(description="The rewritten text OR the new image URL for this specific element.")

class Variant(BaseModel):
    variant_name: str = Field(description="Must be 'Urgency', 'Trust', or 'Logical'.")
    element_mappings: List[ElementMapping] = Field(description="List of text/image updates mapped exactly to the original IDs.")

class CopywriterOutput(BaseModel):
    variants: List[Variant] = Field(description="Exactly 3 variants: Urgency, Trust, and Logical.")

# Add custom_prompt and creative_image_url to the parameters
async def generate_variants(scraped_json_str: str, ad_context: dict, creative_image_url: str = "", custom_prompt: str = "") -> dict:
    
    # 1. Initialize the standard LLM (No more buggy structured output wrapper!)
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", temperature=0.5)
    
    # 2. The Lifesaver: LangChain's native JSON parser
    parser = JsonOutputParser(pydantic_object=CopywriterOutput)

    # 3. Format the optional user instructions
    user_steering = f"\nUSER CUSTOM INSTRUCTIONS (PRIORITY OVERRIDE):\n{custom_prompt}" if custom_prompt else ""
    
    # 4. Format the image injection mandate
    image_mandate = f"\nMANDATORY ASSET: You MUST assign this exact URL ({creative_image_url}) to the largest, most prominent hero/header image on the page." if creative_image_url else ""

    # 5. Build the Prompt (Notice {format_instructions} at the very bottom)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an elite autonomous conversion rate optimization agent.\n"
                   "Your job is to take original landing page assets and rewrite/replace them.\n\n"
                   "You MUST generate exactly three strategic variants:\n"
                   "1. Urgency: Focus on FOMO, limited time, and fast action.\n"
                   "2. Trust: Focus on reliability, social proof, and authority.\n"
                   "3. Logical: Focus on direct features, metrics, and clear benefits.\n\n"
                   "ASSET REPLACEMENT RULES:\n"
                   "- For 'text' types: Rewrite to match the Ad Context.\n"
                   "- For 'image' types: Use highly relevant Unsplash URLs."
                   f"{image_mandate}"
                   f"{user_steering}\n\n"
                   "CRITICAL: Retain exact element IDs (data-tpd-id). Do not skip elements.\n\n"
                   "FORMAT INSTRUCTIONS:\n"
                   "{format_instructions}"),
        
        ("human", "Here is the Ad Context derived from the uploaded image:\n"
                  "{ad_context}\n\n"
                  "Here are the extracted assets:\n"
                  "{scraped_elements}\n\n"
                  "Generate the 3 customized variants.")
    ])

    # 6. Pipe the Prompt -> LLM -> Parser
    chain = prompt | llm | parser
    
    try:
        # 7. Execute! The parser automatically forces JSON and returns a clean dictionary.
        result = await chain.ainvoke({
            "ad_context": json.dumps(ad_context, indent=2),
            "scraped_elements": scraped_json_str,
            "format_instructions": parser.get_format_instructions()
        })
        
        # Print the success to Render logs so we can see it working!
        print("\n\n====== PARSED JSON OUTPUT SUCCESS ======")
        print(json.dumps(result, indent=2))
        print("========================================\n\n")
            
        return result
        
    except Exception as e:
        print(f"Copywriter Agent failed: {str(e)}")
        raise Exception("Failed to generate variants.")