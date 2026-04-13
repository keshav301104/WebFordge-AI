from bs4 import BeautifulSoup

def rebuild_html_variants(original_html: str, variants_data: dict, ad_context: dict) -> list[dict]:
    """
    Takes the base HTML, the 3 copy/image variants, and the ad colors.
    Returns a list of dictionaries containing the final HTML strings.
    """
    completed_variants = []
    
    # Extract the dominant color from the Vision Agent (fallback to a sleek blue if missing)
    colors = ad_context.get("color_palette", ["#0052FF"])
    primary_color = colors[0] if colors else "#0052FF"
    
    # We dynamically inject a CSS block to theme the landing page's buttons 
    # to perfectly match the uploaded Ad Creative.
    color_injection = f"""
    <style>
        /* Troopod AI Injection: Aligning UI with Ad Creative */
        button, .button, .btn, input[type="submit"] {{
            background-color: {primary_color} !important;
            color: #ffffff !important;
            border: none !important;
        }}
    </style>
    """

    for variant in variants_data.get("variants", []):
        # 1. Parse a fresh copy of the original HTML for each variant
        soup = BeautifulSoup(original_html, "html.parser")
        
        # 2. Inject the custom color styles into the <head>
        if soup.head:
            soup.head.append(BeautifulSoup(color_injection, "html.parser"))
            
        # 3. Map the new text AND images perfectly to the tracked IDs
        for mapping in variant.get("element_mappings", []):
            element_id = mapping.get("element_id")
            new_value = mapping.get("new_value")  # CHANGED: Now using new_value for both text and urls
            
            if not element_id or not new_value:
                continue
            
            # Find the exact element we tagged during scraping
            target_element = soup.find(attrs={"data-tpd-id": element_id})
            
            if target_element:
                # ROUTING LOGIC: Handle Images vs. Text
                if target_element.name == 'img':
                    # Inject the new Unsplash URL
                    target_element['src'] = new_value
                    
                    # CRITICAL FIX: Delete srcset so it doesn't override our new src on mobile devices
                    if target_element.has_attr('srcset'):
                        del target_element['srcset']
                else:
                    # Replace the text while keeping the exact HTML tags intact
                    target_element.string = new_value
        
        # 4. Cleanup: Remove our custom tracking IDs so the final code looks completely native
        for tag in soup.find_all(attrs={"data-tpd-id": True}):
            del tag["data-tpd-id"]
            
        # 5. Save the finished variant
        completed_variants.append({
            "variant_name": variant.get("variant_name", "Unknown"),
            "html_content": str(soup),
            "confidence_score": 100 # Default to 100 before the QA Auditor runs
        })
        
    return completed_variants