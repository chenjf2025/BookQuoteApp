import os
from zhipuai import ZhipuAI

# Zhipu AI GLM API Key
# Ensure ZHIPU_API_KEY is in your .env
zhipu_client = ZhipuAI(api_key=os.environ.get("ZHIPU_API_KEY", ""))

def generate_image(core_thought: str) -> str:
    """
    Uses ZhipuAI GLM-Image model (cogview-3 or later) to generate an image based on the core thought.
    Returns the URL string of the generated image.
    """
    try:
        response = zhipu_client.images.generations(
            model="cogview-3", # Use GLM image model CogView-3
            prompt=core_thought,
            size="1024x1024"
        )
        return response.data[0].url
    except Exception as e:
        print(f"Error during image generation: {e}")
        # Return a fallback or placeholder image URL
        return "https://via.placeholder.com/1024x1024.png?text=Image+Generation+Failed"
