"""
Replicate service for image-to-image generation
Better alternative to DALL-E for face/identity generation
"""

import io
import base64
import requests
from typing import Optional, List, Union, Dict, Any
from PIL import Image
import replicate

from config.settings import settings


class ReplicateService:
    """Service for Replicate image-to-image generation"""
    
    def __init__(self):
        """Initialize the Replicate service"""
        self.client = None
        # Replicate uses REPLICATE_API_TOKEN environment variable by default
        # You can also set it manually: replicate.api_token = "your_token"
    
    def _validate_client(self) -> bool:
        """Check if Replicate is properly configured"""
        try:
            # Test if we can access Replicate
            replicate.models.list()
            return True
        except Exception as e:
            print(f"Replicate not configured properly: {e}")
            return False
    
    def _prepare_image_input(self, image: Union[Image.Image, str, bytes]) -> str:
        """
        Prepare image for Replicate API (convert to URL or base64)
        
        Args:
            image: PIL Image, file path, or bytes
            
        Returns:
            Image URL or data URI
        """
        if isinstance(image, str):
            # If it's already a URL, return as is
            if image.startswith(('http://', 'https://')):
                return image
            # If it's a file path, convert to base64
            with open(image, 'rb') as f:
                image_data = f.read()
        elif isinstance(image, bytes):
            image_data = image
        elif isinstance(image, Image.Image):
            # Convert PIL Image to bytes
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            image_data = buffered.getvalue()
        else:
            raise ValueError("Unsupported image type")
        
        # Convert to base64 data URI
        base64_str = base64.b64encode(image_data).decode('utf-8')
        return f"data:image/png;base64,{base64_str}"
    
    def generate_with_photomaker(
        self,
        input_images: List[Union[Image.Image, str, bytes]],
        prompt: str,
        style_strength: int = 20,
        num_steps: int = 50,
        style_name: str = "Photographic (Default)",
        num_outputs: int = 1,
        guidance_scale: float = 5.0,
        seed: Optional[int] = None,
        disable_safety_checker: bool = False
    ) -> Optional[List[str]]:
        """
        Generate images using PhotoMaker (great for identity preservation)
        
        Args:
            input_images: List of input face images
            prompt: Text prompt (use 'img' as trigger word, e.g., "a baby img")
            style_strength: Style strength (0-100, lower = more ID fidelity)
            num_steps: Number of inference steps
            style_name: Style preset
            num_outputs: Number of images to generate
            guidance_scale: Guidance scale (how closely to follow prompt)
            seed: Random seed for reproducibility (None for random)
            disable_safety_checker: Whether to disable safety checker
            
        Returns:
            List of generated image URLs or None if failed
        """
        try:
            # Prepare input images
            prepared_images = [self._prepare_image_input(img) for img in input_images]
            
            # Build input dictionary with only the images we have
            input_dict = {
                "prompt": prompt,
                "num_steps": num_steps,
                "style_name": style_name,
                "num_outputs": num_outputs,
                "guidance_scale": guidance_scale,
                "negative_prompt": "nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry",
                "style_strength_ratio": style_strength,
                "disable_safety_checker": disable_safety_checker,
            }
            
            # Add seed if provided
            if seed is not None:
                input_dict["seed"] = seed
            
            # Add only the image parameters that have values
            if len(prepared_images) > 0:
                input_dict["input_image"] = prepared_images[0]
            if len(prepared_images) > 1:
                input_dict["input_image2"] = prepared_images[1]
            if len(prepared_images) > 2:
                input_dict["input_image3"] = prepared_images[2]
            if len(prepared_images) > 3:
                input_dict["input_image4"] = prepared_images[3]
            
            # Run PhotoMaker
            output = replicate.run(
                "tencentarc/photomaker:ddfc2b08d209f9fa8c1eca692712918bd449f695dabb4a958da31802a9570fe4",
                input=input_dict
            )
            
            return output if isinstance(output, list) else [output]
            
        except Exception as e:
            print(f"Error with PhotoMaker: {e}")
            return None
    
    def generate_with_instantid(
        self,
        face_image: Union[Image.Image, str, bytes],
        prompt: str,
        negative_prompt: str = "ugly, deformed, noisy, blurry, low contrast",
        num_steps: int = 30,
        guidance_scale: float = 5.0,
        ip_adapter_scale: float = 0.8,
        controlnet_conditioning_scale: float = 0.8
    ) -> Optional[str]:
        """
        Generate images using InstantID (excellent for single face identity preservation)
        
        Args:
            face_image: Single face image for identity
            prompt: Text prompt
            negative_prompt: Negative prompt
            num_steps: Number of inference steps
            guidance_scale: Guidance scale
            ip_adapter_scale: IP adapter scale (higher = more identity preservation)
            controlnet_conditioning_scale: ControlNet scale
            
        Returns:
            Generated image URL or None if failed
        """
        try:
            # Prepare face image
            prepared_image = self._prepare_image_input(face_image)
            
            # Run InstantID
            output = replicate.run(
                "zsxkib/instant-id:c2d1c2b7b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8",
                input={
                    "image": prepared_image,
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "num_inference_steps": num_steps,
                    "guidance_scale": guidance_scale,
                    "ip_adapter_scale": ip_adapter_scale,
                    "controlnet_conditioning_scale": controlnet_conditioning_scale,
                }
            )
            
            return output[0] if isinstance(output, list) else output
            
        except Exception as e:
            print(f"Error with InstantID: {e}")
            return None
    
    def generate_with_face_to_many(
        self,
        image: Union[Image.Image, str, bytes],
        style: str = "3D",
        prompt: str = "",
        negative_prompt: str = "ugly, deformed, noisy, blurry",
        num_inference_steps: int = 20
    ) -> Optional[str]:
        """
        Generate stylized versions using face-to-many
        
        Args:
            image: Input face image
            style: Style to apply ("3D", "Emoji", "Pixel art", "Video game", "Claymation", "Toy")
            prompt: Additional prompt
            negative_prompt: Negative prompt
            num_inference_steps: Number of steps
            
        Returns:
            Generated image URL or None if failed
        """
        try:
            prepared_image = self._prepare_image_input(image)
            
            output = replicate.run(
                "fofr/face-to-many:35cea9c3164d9fb7fbd48b51503eabdb39c9d04fdaef9a68f368bed8087ec5f9",
                input={
                    "image": prepared_image,
                    "style": style,
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "num_inference_steps": num_inference_steps,
                }
            )
            
            return output
            
        except Exception as e:
            print(f"Error with face-to-many: {e}")
            return None
    
    def generate_baby_with_photomaker(
        self,
        parent1_image: Union[Image.Image, str, bytes],
        parent2_image: Union[Image.Image, str, bytes],
        custom_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate baby image using PhotoMaker with two parent images
        
        Args:
            parent1_image: First parent image
            parent2_image: Second parent image
            custom_prompt: Optional custom prompt
            
        Returns:
            Generated baby image URL or None if failed
        """
        from config.prompts import Prompts
        
        # Use custom prompt or default, but adapt for PhotoMaker
        base_prompt = custom_prompt or Prompts.get_baby_prompt()
        # PhotoMaker needs 'img' trigger word
        photomaker_prompt = f"a cute baby img, {base_prompt}"
        
        result = self.generate_with_photomaker(
            input_images=[parent1_image, parent2_image],
            prompt=photomaker_prompt,
            style_strength=30,  # Lower for more ID fidelity
            num_steps=50,
            style_name="Photographic (Default)",
            num_outputs=1
        )
        
        return result[0] if result else None
    
    def generate_family_with_photomaker(
        self,
        parent1_image: Union[Image.Image, str, bytes],
        parent2_image: Union[Image.Image, str, bytes],
        baby_image: Union[Image.Image, str, bytes],
        custom_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate family portrait using PhotoMaker
        
        Args:
            parent1_image: First parent image
            parent2_image: Second parent image
            baby_image: Baby image
            custom_prompt: Optional custom prompt
            
        Returns:
            Generated family portrait URL or None if failed
        """
        from config.prompts import Prompts
        
        # Use custom prompt or default, but adapt for PhotoMaker
        base_prompt = custom_prompt or Prompts.get_family_prompt()
        photomaker_prompt = f"a family portrait with people img, {base_prompt}"
        
        result = self.generate_with_photomaker(
            input_images=[parent1_image, parent2_image, baby_image],
            prompt=photomaker_prompt,
            style_strength=20,  # Lower for more ID fidelity
            num_steps=50,
            style_name="Photographic (Default)",
            num_outputs=1
        )
        
        return result[0] if result else None
    
    def face_swap_simple(
        self,
        source_image: Union[Image.Image, str, bytes],
        target_image: Union[Image.Image, str, bytes]
    ) -> Optional[str]:
        """
        Simple face swap between two images
        
        Args:
            source_image: Source face image
            target_image: Target image to swap face into
            
        Returns:
            Face-swapped image URL or None if failed
        """
        try:
            source_prepared = self._prepare_image_input(source_image)
            target_prepared = self._prepare_image_input(target_image)
            
            output = replicate.run(
                "pikachupichu25/image-faceswap:latest",
                input={
                    "source_image": source_prepared,
                    "target_image": target_prepared,
                }
            )
            
            return output
            
        except Exception as e:
            print(f"Error with face swap: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        Test if Replicate connection is working
        
        Returns:
            True if connection works, False otherwise
        """
        return self._validate_client()
    
    def get_available_models(self) -> Dict[str, str]:
        """
        Get information about available models
        
        Returns:
            Dictionary of model names and descriptions
        """
        return {
            "photomaker": "Best for identity preservation with multiple input images. Great for baby generation from parents.",
            "instantid": "Excellent for single face identity preservation. Fast and high quality.",
            "face-to-many": "Transform faces into different styles (3D, emoji, pixel art, etc.)",
            "face-swap": "Simple face swapping between two images",
        }


# Create a singleton instance
replicate_service = ReplicateService() 