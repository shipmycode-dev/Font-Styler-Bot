# style.py
from font import NORMAL, FONTS

def apply_style(text: str, style_index: int) -> str:
    """
    Applies the selected English font style to the input text 
    by mapping standard characters to the target font Unicode table.
    """
    if style_index < 0 or style_index >= len(FONTS):
        return text
        
    target_font = FONTS[style_index]
    
    # Map uppercase and lowercase alphabets (52 characters total)
    table = str.maketrans(NORMAL, target_font[:52])
    return text.translate(table)

def get_total_styles() -> int:
    return len(FONTS)
