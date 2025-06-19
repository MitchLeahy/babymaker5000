"""
OpenAI service for DALL-E image generation
"""

import base64
import io
import requests
from typing import Optional, List, Union
from PIL import Image
from openai import OpenAI

from config.settings import settings


class OpenAIService:
    """Service for OpenAI DALL-E image generation"""
    
    def __init__(self):
        """Initialize the OpenAI service"""
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def _validate_client(self) -> bool:
        """Check if OpenAI client is properly initialized"""
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please check your API key.")
        return True
    
    def _image_to_base64(self, image: Union[Image.Image, str, bytes]) -> str:
        """
        Convert image to base64 string
        
        Args:
            image: PIL Image, file path, or bytes
            
        Returns:
            Base64 encoded string
        """
        if isinstance(image, str):
            # If it's a file path
            with open(image, 'rb') as f:
                image_data = f.read()
        elif isinstance(image, bytes):
            # If it's already bytes
            image_data = image
        elif isinstance(image, Image.Image):
            # If it's a PIL Image
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            image_data = buffered.getvalue()
        else:
            raise ValueError("Unsupported image type")
        
        return base64.b64encode(image_data).decode('utf-8')
    
    def _download_image(self, url: str) -> Optional[Image.Image]:
        """
        Download image from URL and return as PIL Image
        
        Args:
            url: Image URL
            
        Returns:
            PIL Image object or None if failed
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content))
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None
    
    def generate_image(
        self, 
        prompt: str, 
        input_images: Optional[List[Union[Image.Image, str, bytes]]] = None,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "natural"
    ) -> Optional[str]:
        """
        Generate an image using DALL-E
        
        Args:
            prompt: Text description for image generation
            input_images: List of input images (for reference/inspiration)
            size: Image size ("1024x1024", "1792x1024", "1024x1792")
            quality: Image quality ("standard", "hd")
            style: Image style ("natural", "vivid")
            
        Returns:
            URL of generated image or None if failed
        """
        self._validate_client()
        
        try:
            # Note: DALL-E 3 doesn't directly support image input for conditioning
            # We'll enhance the prompt with image descriptions if images are provided
            enhanced_prompt = prompt
            
            if input_images:
                # For now, we'll add a note about the input images to the prompt
                # In a real implementation, you might want to use GPT-4 Vision to analyze the images
                enhanced_prompt += f"\n\nGenerate based on the characteristics and features from {len(input_images)} reference image(s)."
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size=size,
                quality=quality,
                style=style,
                n=1
            )
            
            if response.data and len(response.data) > 0:
                return response.data[0].url
            
            return None
            
        except Exception as e:
            print(f"Error generating image: {e}")
            return None
    
    def generate_baby_image(
        self, 
        parent1_image: Union[Image.Image, str, bytes],
        parent2_image: Union[Image.Image, str, bytes],
        custom_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate a baby image from two parent images
        
        Args:
            parent1_image: First parent image
            parent2_image: Second parent image
            custom_prompt: Optional custom prompt (uses default if not provided)
            
        Returns:
            URL of generated baby image or None if failed
        """
        from config.prompts import Prompts
        
        # Use custom prompt or default baby generation prompt
        prompt = custom_prompt or Prompts.get_baby_prompt()
        
        # Generate baby image with parent images as reference
        return self.generate_image(
            prompt=prompt,
            input_images=[parent1_image, parent2_image],
            size="1024x1024",
            quality="standard",
            style="natural"
        )
    
    def generate_family_portrait(
        self,
        parent1_image: Union[Image.Image, str, bytes],
        parent2_image: Union[Image.Image, str, bytes],
        baby_image: Union[Image.Image, str, bytes],
        custom_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate a family portrait with parents and baby
        
        Args:
            parent1_image: First parent image
            parent2_image: Second parent image
            baby_image: Baby image
            custom_prompt: Optional custom prompt (uses default if not provided)
            
        Returns:
            URL of generated family portrait or None if failed
        """
        from config.prompts import Prompts
        
        # Use custom prompt or default family portrait prompt
        prompt = custom_prompt or Prompts.get_family_prompt()
        
        # Generate family portrait with all images as reference
        return self.generate_image(
            prompt=prompt,
            input_images=[parent1_image, parent2_image, baby_image],
            size="1024x1024",
            quality="standard",
            style="natural"
        )
    
    def generate_with_enhanced_prompt(
        self,
        base_prompt: str,
        input_images: List[Union[Image.Image, str, bytes]],
        image_descriptions: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Generate image with enhanced prompt based on input images
        
        Args:
            base_prompt: Base prompt for generation
            input_images: List of input images
            image_descriptions: Optional descriptions of the input images
            
        Returns:
            URL of generated image or None if failed
        """
        enhanced_prompt = base_prompt
        
        if image_descriptions:
            enhanced_prompt += "\n\nReference characteristics:"
            for i, description in enumerate(image_descriptions, 1):
                enhanced_prompt += f"\nImage {i}: {description}"
        
        return self.generate_image(
            prompt=enhanced_prompt,
            input_images=input_images
        )
    
    def test_connection(self) -> bool:
        """
        Test if OpenAI connection is working
        
        Returns:
            True if connection works, False otherwise
        """
        try:
            self._validate_client()
            
            # Try a simple API call
            response = self.client.images.generate(
                model="dall-e-3",
                prompt="A simple test image of a cute puppy",
                size="1024x1024",
                n=1
            )
            return True
        except Exception as e:
            print(f"OpenAI connection test failed: {e}")
            return False


# Create a singleton instance
openai_service = OpenAIService() 