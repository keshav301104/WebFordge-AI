import httpx
from bs4 import BeautifulSoup
import json

async def fetch_and_extract_content(url: str):
    """
    Fetches a URL, assigns unique tracking IDs to text AND image elements, 
    and returns both the modified HTML (for rebuilding) and a JSON map (for the LLM).
    """
    try:
        # 1. Fetch the raw HTML asynchronously
        async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            raw_html = response.text

        # Using html.parser as a safe default, you can keep lxml if it's installed
        soup = BeautifulSoup(raw_html, "html.parser")

        extracted_elements = []
        node_counter = 0 # Universal counter for IDs

        # 2. Extract meaningful TEXT elements
        target_text_tags = ['h1', 'h2', 'h3', 'h4', 'p', 'button', 'a', 'span', 'li']
        
        for element in soup.find_all(target_text_tags):
            text = element.get_text(strip=True)
            
            # Ignore empty tags or tiny artifacts
            if text and len(text) > 2: 
                tracking_id = f"tpd_node_{node_counter}"
                element['data-tpd-id'] = tracking_id
                
                extracted_elements.append({
                    "id": tracking_id,
                    "type": "text",
                    "tag": element.name,
                    "original_value": text
                })
                node_counter += 1

        # 3. Extract IMAGE elements
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                tracking_id = f"tpd_node_{node_counter}"
                img['data-tpd-id'] = tracking_id
                
                extracted_elements.append({
                    "id": tracking_id,
                    "type": "image",
                    "tag": "img",
                    "original_value": src
                })
                node_counter += 1

        # 4. The Blueprint and JSON Map
        # We no longer need to strip out scripts/styles for the LLM context
        # because we are ONLY sending the LLM the clean JSON array below.
        html_blueprint = str(soup) 
        llm_context_json = json.dumps(extracted_elements)

        return html_blueprint, llm_context_json

    except Exception as e:
        print(f"Scraping failed: {str(e)}")
        raise Exception(f"Failed to scrape the target URL: {str(e)}")