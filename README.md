# 🍼 Baby Maker 5000

An AI-powered application that generates adorable baby photos and family portraits by blending facial features from two parent images.

## 🤖 AI Model Used

This application uses **PhotoMaker** from Replicate, which is currently the best model available for identity-preserving image generation:

### PhotoMaker Model Details
- **Model**: `tencentarc/photomaker:ddfc2b08d209f9fa8c1eca692712918bd449f695dabb4a958da31802a9570fe4`
- **Provider**: Replicate (TencentARC)
- **Specialization**: Identity preservation with multiple input images
- **Cost**: ~$0.007 per image
- **Generation Time**: ~8-15 seconds
- **Max Input Images**: 4 parent photos
- **Output Quality**: Photorealistic with excellent feature blending

### Why PhotoMaker?
PhotoMaker was chosen over other AI models because it:
- ✅ **Accepts multiple input images** (up to 4 parent photos)
- ✅ **Preserves facial identity** while blending features naturally
- ✅ **Generates realistic babies** that inherit parent characteristics
- ✅ **Cost-effective** compared to alternatives
- ✅ **Fast generation** with high-quality results
- ✅ **Multiple style options** (photographic, cinematic, artistic, etc.)

### Alternative Models Considered
- **DALL-E 3**: ❌ Text-to-image only, no photo input support
- **InstantID**: ❌ Limited to single face input
- **Midjourney**: ❌ No direct API, limited identity preservation
- **Stable Diffusion**: ❌ Requires complex setup for identity preservation

## 🚀 Features

### Core Functionality
- **Baby Generation**: Creates realistic baby photos from two parent images
- **Family Portraits**: Generates cohesive family photos with parents + baby
- **Identity Preservation**: Maintains and blends facial features from parent photos
- **Multiple Variations**: Generate 1-4 different baby options simultaneously

### Advanced Controls
- **Identity Preservation** (15-50): Control feature inheritance vs artistic freedom
- **Photo Styles**: 10+ styles including Photographic, Cinematic, Disney, Digital Art
- **Quality Steps** (20-100): Balance between quality and generation speed
- **Prompt Adherence** (1-10): How closely AI follows text descriptions
- **Age Ranges**: Newborn, Infant, Baby, or Toddler
- **Expressions**: Smiling, Peaceful, Curious, Laughing, Natural
- **Poses**: Classic, Casual, Parents holding baby, Outdoor, Studio
- **Backgrounds**: Studio, Neutral, Outdoor, Home, Professional

### Technical Features
- **Seed Control**: Reproducible results with custom seeds
- **Safety Filtering**: Optional content safety checker
- **Local Storage**: Images saved locally with download options
- **Progress Tracking**: Real-time generation progress
- **Error Handling**: Graceful fallbacks and detailed error messages

## 📋 Requirements

- Python 3.8+
- Replicate API Token (required)
- ~2GB disk space for dependencies
- Internet connection for API calls

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd babymaker5000
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   ```
   
   Edit `.env` and add your Replicate API token:
   ```
   REPLICATE_API_TOKEN=your_replicate_api_token_here
   ```

5. **Get Replicate API Token**
   - Visit [https://replicate.com/account/api-tokens](https://replicate.com/account/api-tokens)
   - Create an account if needed
   - Generate an API token
   - Add it to your `.env` file

## 🎮 Usage

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **Open in browser**
   - Navigate to `http://localhost:8501`

3. **Generate baby photos**
   - Upload two parent photos (PNG/JPG)
   - Adjust settings in the sidebar
   - Click "Generate Baby & Family Portrait"
   - Wait 20-30 seconds for both images
   - Download your results!

## 🎛️ Settings Guide

### Identity Preservation (15-50)
- **15-25**: Maximum parent feature preservation
- **25-35**: Balanced blending (recommended)
- **35-50**: More artistic interpretation

### Quality Steps (20-100)
- **20-30**: Fast generation, good quality
- **40-60**: Balanced quality/speed (recommended)
- **70-100**: Maximum quality, slower generation

### Photo Styles
- **Photographic**: Realistic, professional photos
- **Cinematic**: Movie-like lighting and composition
- **Disney Character**: Animated, cartoon-like style
- **Digital Art**: Modern digital artwork style

## 📁 Project Structure

```
babymaker5000/
├── app.py                 # Main Streamlit application
├── config/
│   ├── settings.py        # Configuration management
│   └── prompts.py         # AI prompts for generation
├── src/
│   ├── services/
│   │   └── replicate_service.py  # PhotoMaker API integration
│   └── ui/
│       └── main_page.py   # Streamlit user interface
├── generated_images/      # Local image storage
├── temp_uploads/         # Temporary file storage
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 💰 Cost Estimation

- **Baby Generation**: ~$0.007 per image
- **Family Portrait**: ~$0.007 per image
- **Complete Generation**: ~$0.014 per baby + family set
- **Multiple Variations**: Cost scales with number of outputs

Example costs:
- 10 baby generations: ~$0.14
- 50 baby generations: ~$0.70
- 100 baby generations: ~$1.40

## 🔧 Troubleshooting

### Common Issues

**"Replicate not configured"**
- Ensure `REPLICATE_API_TOKEN` is set in `.env`
- Check token is valid at replicate.com
- Restart the application after adding token

**"Parameter validation errors"**
- Update to latest version (parameters auto-constrained)
- Check internet connection
- Verify image files are valid PNG/JPG

**"Generation failed"**
- Check Replicate account has credits
- Ensure parent photos show clear faces
- Try reducing quality steps for faster generation

**Slow generation**
- Reduce quality steps (20-40)
- Generate single images instead of multiple
- Check internet connection speed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

[Add your license information here]

## 🙏 Acknowledgments

- **TencentARC** for the PhotoMaker model
- **Replicate** for the API platform
- **Streamlit** for the web framework
- **OpenAI** for inspiration and comparison

## 📞 Support

For issues, questions, or feature requests, please:
1. Check the troubleshooting section
2. Search existing issues
3. Create a new issue with detailed information

---

**⚠️ Disclaimer**: This application is for entertainment purposes only. Generated images are AI-created and do not represent real people. Results may vary based on input photo quality and settings. 