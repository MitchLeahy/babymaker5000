"""
Internal prompts for Baby Maker 5000 image generation
"""

class Prompts:
    """Collection of prompts for different image generation tasks"""
    
    BABY_GENERATION_PROMPT = """
    Create a realistic, adorable baby photo that combines facial features from both parents. 
    The baby should be:
    - Approximately 6-12 months old
    - Smiling or with a peaceful expression
    - Well-lit with soft, natural lighting
    - High quality, professional photography style
    - Wearing cute baby clothes (pastel colors preferred)
    - Background should be simple and clean (white or soft colors)
    
    The baby should naturally blend characteristics from both parent images, including:
    - Eye color and shape
    - Hair color and texture
    - Facial structure
    - Skin tone
    
    Style: Professional baby portrait photography, high resolution, warm and loving atmosphere.
    """
    
    FAMILY_PORTRAIT_PROMPT = """
    Create a beautiful, professional family portrait featuring three people: two parents and their baby.
    The composition should be:
    - Warm, loving family atmosphere
    - Professional portrait photography style
    - Soft, natural lighting
    - Clean, simple background (studio or outdoor natural setting)
    - All three subjects should be clearly visible and well-positioned
    - Parents should be holding or positioned near the baby
    - Everyone should have happy, natural expressions
    - High quality, professional photography
    - Clothing should be coordinated but not matching (neutral or complementary colors)
    
    The family should look natural and connected, with the baby as the central focus.
    Style: Professional family portrait photography, high resolution, timeless and elegant.
    """
    
    @staticmethod
    def get_baby_prompt(additional_details=""):
        """Get baby generation prompt with optional additional details"""
        base_prompt = Prompts.BABY_GENERATION_PROMPT
        if additional_details:
            return f"{base_prompt}\n\nAdditional details: {additional_details}"
        return base_prompt
    
    @staticmethod
    def get_family_prompt(additional_details=""):
        """Get family portrait prompt with optional additional details"""
        base_prompt = Prompts.FAMILY_PORTRAIT_PROMPT
        if additional_details:
            return f"{base_prompt}\n\nAdditional details: {additional_details}"
        return base_prompt 