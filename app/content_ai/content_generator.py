import requests
import json
import logging

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


def generate_content(brand, influencers, trends):
    brand_name = brand.get("title", "Brand")
    category = brand.get("category", "general")
    style = brand.get("required_style", "neutral")
    region = brand.get("target_region", "global")

    influencer_styles = []
    influencer_topics = []

    for inf in influencers:
        if inf.get("style"):
            influencer_styles.append(inf["style"])
        if inf.get("topics"):
            influencer_topics.extend(inf["topics"])

    prompt = f"""
You are a professional YouTube content strategist.

Brand:
- Name: {brand_name}
- Category: {category}
- Region: {region}
- Tone: {style}

Influencer styles: {", ".join(set(influencer_styles)) or "mixed"}
Influencer topics: {", ".join(set(influencer_topics)) or "general"}

Trending topics:
{", ".join(trends) if trends else "current trending YouTube topics"}

TASK:
Create 3–5 high-quality YouTube content ideas.

Each idea must include:
1. Title
2. Hook
3. 30–45 second script
4. Caption
5. CTA
6. Why it works

Write naturally like a human creator.
Do NOT use JSON.
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": True
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=180)
        
        # Check if the request was successful
        response.raise_for_status()
        
        output = ""

        for line in response.iter_lines():
            if not line:
                continue

            try:
                data = json.loads(line.decode("utf-8"))
                if "response" in data:
                    output += data["response"]
                # Check if this is the final chunk
                if data.get("done", False):
                    break
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON line: {e}")
                continue
            except Exception as e:
                logger.warning(f"Error processing line: {e}")
                continue

        if not output:
            logger.error("No content generated from Ollama. Check if Ollama is running and the model is available.")
            return "Error: Failed to generate content. Please ensure Ollama is running and the model 'llama3' is available."

        return output.strip()
        
    except requests.exceptions.ConnectionError:
        error_msg = f"Failed to connect to Ollama at {OLLAMA_URL}. Please ensure Ollama is running."
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except requests.exceptions.Timeout:
        error_msg = "Request to Ollama timed out."
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP error from Ollama: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error during content generation: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return f"Error: {error_msg}"
