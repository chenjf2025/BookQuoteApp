import os
from PIL import Image, ImageDraw, ImageFont
import httpx
import io
import textwrap

async def create_poster_image(book_title: str, texts: list[str], bg_image_url: str = None) -> str:
    """
    Downloads the background image (or uses a beige solid color), nicely overlays the quotes 
    and book title, saves the poster locally (in a 'static' dir), and returns the local file path/URL.
    """
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    width, height = 1024, 1024
    
    # 1. Background image handling
    if bg_image_url:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(bg_image_url)
                response.raise_for_status()
                image_data = response.content
                base_image = Image.open(io.BytesIO(image_data)).convert('RGBA')
                # Resize if needed
                if base_image.size != (width, height):
                    base_image = base_image.resize((width, height), Image.Resampling.LANCZOS)
        except Exception as e:
            print(f"Error downloading image: {e}")
            bg_image_url = None # Fallback to solid color
            
    if not bg_image_url:
        # Create a beige background: #F5F5DC (Beige) or #FAF0E6 (Linen)
        base_image = Image.new('RGBA', (width, height), (250, 240, 230, 255))
    
    # 2. Add an overlay for better text readability (only if using image)
    if bg_image_url:
        overlay = Image.new('RGBA', base_image.size, (0, 0, 0, int(255 * 0.4)))
        composite = Image.alpha_composite(base_image, overlay).convert('RGB')
        text_color = (255, 255, 255) # White
    else:
        composite = base_image.convert('RGB')
        text_color = (60, 50, 50) # Dark brown/gray for beige bg
        
    draw = ImageDraw.Draw(composite)
    
    # 3. Load Fonts & Dynamic Sizing
    font_path = os.path.join(base_dir, "fonts", "SourceHanSansCN-Regular.otf")
    base_font_size = int(width * 0.035)
    
    # Heuristic: If there's a lot of text, scale down the font size.
    total_chars = sum(len(t) for t in texts)
    if total_chars > 150:
        base_font_size = int(width * 0.028)
    elif total_chars > 80:
        base_font_size = int(width * 0.032)
        
    try:
        quote_font = ImageFont.truetype(font_path, size=base_font_size)
        title_font = ImageFont.truetype(font_path, size=int(width * 0.03))
    except Exception as e:
        print(f"Font error: {e}, attempting system fonts...")
        quote_font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    
    # 4. Wrap text and draw Quotes
    blocks = []
    total_text_height = 0
    line_spacing = int(height * 0.015)
    paragraph_spacing = int(height * 0.03)
    
    # Adjust wrap width based on text length to make it look blockier
    wrap_width = 22 if total_chars < 150 else 30
    
    for text in texts:
        wrapped_text = textwrap.fill(text, width=wrap_width)
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=quote_font, spacing=line_spacing)
        block_height = bbox[3] - bbox[1]
        blocks.append((wrapped_text, block_height))
        total_text_height += block_height + paragraph_spacing
        
    if len(blocks) > 0:
        total_text_height -= paragraph_spacing
        
    # Starting Y position (centered minus some offset for the title)
    current_y = (height - total_text_height) / 2 - (height * 0.05)
    
    for wrapped_text, block_height in blocks:
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=quote_font, spacing=line_spacing)
        block_width = bbox[2] - bbox[0]
        x = (width - block_width) / 2
        
        # Center-align text within the block
        draw.multiline_text((x, current_y), wrapped_text, font=quote_font, fill=text_color, align='center', spacing=line_spacing)
        current_y += block_height + paragraph_spacing
    
    # 5. Draw Book Title and Author signature at the bottom
    signature = f"—— 《{book_title}》"
    bbox_t = draw.textbbox((0, 0), signature, font=title_font)
    text_width_t = bbox_t[2] - bbox_t[0]
    
    draw.text(((width - text_width_t) / 2, height - (height * 0.15)), signature, font=title_font, fill=text_color)
    
    # 6. Save image
    static_dir = os.path.join(base_dir, "static")
    os.makedirs(static_dir, exist_ok=True)
    
    import time
    filename = f"poster_{book_title.replace(' ', '_')}_{int(time.time())}.jpg"
    file_path = os.path.join(static_dir, filename)
    
    composite.save(file_path, "JPEG", quality=95)
    
    return f"/static/{filename}"
