import requests
import json
import logging
import os

logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")  # Default to smaller model


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
        influencer_topics.extend(inf.get("topics", []))

    prompt = f"""
You are a professional YouTube content strategist.

Brand:
- Name: {brand_name}
- Category: {category}
- Region: {region}
- Tone: {style}

Influencer styles: {", ".join(influencer_styles) or "mixed"}
Influencer topics: {", ".join(influencer_topics) or "general"}

Trending topics:
{", ".join(trends) if trends else "general trending topics"}

TASK:
Create 3–5 high-quality YouTube content ideas.

Each idea must include:
- Title
- Hook
- Short script (30–45 seconds)
- Caption
- CTA
- Why it works

Write naturally like a human creator.
Do NOT use JSON.
Return clean readable text.
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": True
    }

    try:
        print(f"🚀 [Ollama] Calling {OLLAMA_URL} for model {MODEL}...")
        logger.info(f"Calling Ollama API: {OLLAMA_URL} with model: {MODEL}")
        logger.debug(f"Prompt length: {len(prompt)} characters")
        
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            stream=True,
            timeout=300
        )
        
        # Check if the request was successful
        response.raise_for_status()
        print(f"📥 [Ollama] Response status {response.status_code}. Reading stream...")
        logger.info(f"Ollama API responded with status: {response.status_code}")
        
        output = ""
        done = False
        chunk_count = 0

        for line in response.iter_lines():
            if not line:
                continue

            try:
                line_text = line.decode("utf-8")
                data = json.loads(line_text)
                chunk_count += 1
                
                # Log first chunk for debugging
                if chunk_count == 1:
                    logger.debug(f"First chunk keys: {list(data.keys())}")
                
                # Accumulate response text
                if "response" in data:
                    response_text = data["response"]
                    if response_text:
                        output += response_text
                
                # Check if this is the final chunk
                if data.get("done", False):
                    done = True
                    logger.debug(f"Received done flag after {chunk_count} chunks")
                    break
                    
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON line: {e}, line: {line_text[:100] if 'line_text' in locals() else 'N/A'}")
                continue
            except Exception as e:
                logger.warning(f"Error processing line: {e}")
                continue

        logger.info(f"Processed {chunk_count} chunks, output length: {len(output)} characters, done: {done}")
        
        if not output:
            logger.error("No content generated from Ollama. Response received but no content found.")
            logger.error(f"Response status: {response.status_code}, Done flag: {done}, Chunks processed: {chunk_count}")
            return "Error: Failed to generate content. Ollama responded but no content was generated. Please check the logs for details."

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
        error_text = "Unknown error"
        error_details = {}
        
        if e.response:
            try:
                # Try to parse JSON error response
                error_details = e.response.json() if e.response.content else {}
                if "error" in error_details:
                    error_text = error_details["error"]
                elif e.response.text:
                    error_text = e.response.text
            except (json.JSONDecodeError, ValueError):
                # If not JSON, use raw text
                error_text = e.response.text or str(e.response.reason) or "Unknown error"
            
            logger.error(f"Ollama HTTP {e.response.status_code} error: {error_text}")
            logger.error(f"Response headers: {dict(e.response.headers)}")
            if e.response.content:
                logger.error(f"Response content: {e.response.content[:500]}")
        else:
            logger.error(f"HTTP error with no response object: {e}")
        
        error_msg = f"HTTP error from Ollama: {e.response.status_code if e.response else 'N/A'} - {error_text}"
        
        # Check for memory-related errors and provide helpful suggestions
        error_lower = error_text.lower()
        if "memory" in error_lower or "system memory" in error_lower:
            suggestion = (
                f"\n\n💡 Solution: The model '{MODEL}' requires more memory than available.\n"
                f"Options:\n"
                f"1. Use a smaller model: Set OLLAMA_MODEL environment variable to 'llama3.2:3b' or 'llama3.2:1b'\n"
                f"2. Free up system memory by closing other applications\n"
                f"3. Pull a smaller model: Run 'ollama pull llama3.2:3b'\n"
                f"4. Check available models: Run 'ollama list'"
            )
            return f"Error: {error_msg}{suggestion}"
        
        # Check for model not found errors
        if "model" in error_lower and ("not found" in error_lower or "does not exist" in error_lower):
            suggestion = (
                f"\n\n💡 Solution: The model '{MODEL}' is not available.\n"
                f"Run: ollama pull {MODEL}"
            )
            return f"Error: {error_msg}{suggestion}"
        
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error during content generation: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return f"Error: {error_msg}"
def generate_influencer_ideas(influencer, trends, user_prompt=None):
    channel_name = influencer.get("channel_name") or "Creator"
    category = influencer.get("category") or "general"
    description = influencer.get("description") or ""

    user_direction_block = ""
    if user_prompt:
        user_direction_block = f"\nUSER DIRECTION: The creator specifically wants to focus on: {user_prompt}\n"

    prompt = f"""
You are an expert YouTube growth strategist and talent manager.

Creator Profile:
- Name: {channel_name}
- Category: {category}
- Context: {description[:400]}
{user_direction_block}
Relevant Trends:
{", ".join(trends) if trends else "general YouTube viral trends"}

TASK:
Generate 3 high-potential content ideas that will help this creator grow AND attract premium brand sponsorships.
"""
    if user_prompt:
        prompt += f"Ensure the ideas align with the following direction: {user_prompt}\n"
    
    prompt += """
For each idea include:
1. Viral Title Idea
2. Content Hook & Concept
3. Brand Pitch (Why a brand would want to sponsor this specific video)

Write in a motivating, professional tone. Return clean readable text.
"""
    # Reuse payload logic
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False # Simple for studio
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        response.raise_for_status()
        return response.json().get("response", "AI was unable to generate ideas at this time.").strip()
    except Exception as e:
        logger.error(f"Creator Studio AI Error: {e}")
        return f"Error: Failed to connect to AI engine. ({str(e)})"
