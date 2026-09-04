# style.py
from font import NORMAL, FONTS

def apply_style(text: str, style_index: int) -> str:
    """
    User ke normal text ko select kiye hue font style me convert karega.
    """
    if style_index < 0 or style_index >= len(FONTS):
        return text # Fallback
        
    target_font = FONTS[style_index]
    
    # Create mapping dictionary mapping normal characters to styled characters
    table = str.maketrans(NORMAL, target_font[:52]) 
    styled_text = text.translate(table)
    
    # Text-Arts like Sparks, Strikethrough use combining marks.
    # Handle specific index patterns if they contain zero-width joiners (optional logic)
    
    return styled_text

def get_total_styles() -> int:
    return len(FONTS)
