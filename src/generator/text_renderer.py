
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def create_text_image(text, font_path, font_size, max_width, color=(255, 255, 255), stroke_color=(0, 0, 0), stroke_width=2):
    """
    Creates a numpy array representing the text image (RGBA) using Pillow.
    Handles wrapping and stroking.
    """
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        # Fallback if font path is bad
        font = ImageFont.load_default()

    # Wrap text
    lines = []
    words = text.split()
    current_line = []
    
    # Simple word wrap
    # Note: For more precise wrapping we'd need to measure text, but this is an estimation loop
    # We'll measure the current line width
    
    dummy_draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    
    for word in words:
        current_line.append(word)
        line_str = " ".join(current_line)
        bbox = dummy_draw.textbbox((0, 0), line_str, font=font, stroke_width=stroke_width)
        w = bbox[2] - bbox[0]
        
        if w > max_width:
            # Pop the last word and finalize the previous line
            if len(current_line) > 1:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                # If a single word is too long, we keep it (or force break, but let's keep it)
                lines.append(line_str)
                current_line = []
    
    if current_line:
        lines.append(" ".join(current_line))

    # Calculate image size
    line_heights = []
    max_line_width = 0
    
    for line in lines:
        bbox = dummy_draw.textbbox((0, 0), line, font=font, stroke_width=stroke_width)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        max_line_width = max(max_line_width, w)
        line_heights.append(h + 10) # Add some line spacing/padding

    total_h = sum(line_heights) + 20 # Padding
    final_w = int(max(max_width, max_line_width)) + 20 

    # Draw
    img = Image.new('RGBA', (final_w, total_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    y = 10
    for i, line in enumerate(lines):
        # Center text
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=stroke_width)
        lw = bbox[2] - bbox[0]
        x = (final_w - lw) // 2
        
        # Draw Drop Shadow (offset +5, +5)
        shadow_color = (0, 0, 0, 255)
        shadow_offset = (5, 5)
        draw.text((x + shadow_offset[0], y + shadow_offset[1]), line, font=font, fill=shadow_color, stroke_width=stroke_width+2)

        # Draw stroke
        draw.text((x, y), line, font=font, fill=stroke_color, stroke_width=stroke_width)
        # Draw fill
        draw.text((x, y), line, font=font, fill=color, stroke_width=0)
        
        y += line_heights[i]

    return np.array(img)
