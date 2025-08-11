# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Chinese-language MapleStory trading opportunity monitoring system that uses AI/OCR to analyze game chat windows and detect trading opportunities. The system can automatically identify when players are looking to buy items you want to sell, using either Gemini AI or local OCR analysis.

## Common Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Setup OCR (first time use, downloads ~100MB language models)
python install_ocr.py

# Check if EasyOCR is properly installed
python -c "import easyocr; print('EasyOCR available')"
```

### Running the Application
```bash
# Start main monitoring program
python screen_monitor.py

# Run integration tests (recommended for development)
python integration_test.py

# Run specific test modules
python test_improved_ocr.py
python test_player_name_extraction.py
python test_new_html_format.py
```

### Testing and Development
```bash
# Integration testing with automatic result merging
python integration_test.py
# Choose 20-50 tests for development, 100+ for thorough testing
# Select analysis method: 1 (Gemini AI), 2 (Traditional OCR), or 3 (Rectangle-based OCR)

# Merge historical test results
python test_results_merger.py

# Debug OCR functionality
python diagnose_ocr_issue.py
python debug_ocr_filtering.py

# Debug rectangle detection (when enabled in config.py)
# Check rectangle_debug/ folder for visual analysis results
```

## Architecture Overview

### Core Components
- **`screen_monitor.py`**: Main monitoring application using strategy pattern
- **`roi_selector.py`**: Interactive ROI selection tool for game chat window
- **`config.py`**: Configuration file containing API keys and item keywords
- **Analyzers**: Strategy and Template pattern implementation for different text analysis methods
  - **`gemini_analyzer.py`**: High-precision AI analysis using Google Gemini API
  - **`ocr_analyzer.py`**: Contains multiple OCR analysis implementations:
    - **`OCRAnalyzer`**: Traditional text-based segmentation OCR
    - **`RectangleBasedOCRAnalyzer`**: New white rectangle boundary-based OCR with visual detection
  - **`text_analyzer.py`**: Base classes including Template Pattern foundation (`BaseOCRAnalyzer`)
  - **`rectangle_detector.py`**: White rectangle detection strategy using OpenCV

### Key Architectural Patterns

#### Strategy and Template Pattern for Text Analysis
```python
# Strategy Pattern Base
class TextAnalyzer:  # Base class in text_analyzer.py
    def analyze_and_parse(self, image)  # Main entry point
    def get_error_type(self, error_message)  # Error classification for auto-switching
    def parse_result(self, result)  # Parse analysis results

# Template Pattern for OCR
class BaseOCRAnalyzer(TextAnalyzer):  # Template method base class
    def analyze_image(self, image)  # Template method defining OCR flow
    def segment_text_regions(self, image, ocr_results)  # Abstract: text segmentation strategy
    def extract_target_segments(self, segments)  # Abstract: segment extraction strategy
```

#### Automatic Fallback System
The system automatically switches from Gemini AI to OCR when API quota is exceeded:
- Monitors API errors in real-time
- Classifies error types (API_QUOTA_EXCEEDED, NETWORK_ERROR, etc.)
- Seamlessly switches to backup analyzer
- Tracks fallback usage statistics

### Testing Framework
- **`integration_test.py`**: Comprehensive testing with batch execution (1-1000 tests)
- **`real_time_merger.py`**: Real-time test result merging and HTML report generation
- **`test_results_merger.py`**: Post-processing tool for historical test data

## Configuration

### API Configuration (`config.py`)
```python
# Required: Set your Gemini API key
GEMINI_API_KEY = "your_gemini_api_key_here"

# Monitoring settings
SCAN_INTERVAL = 2  # seconds between scans

# Item keywords - core business logic
SELLING_ITEMS = {
    "item_name": ["keyword1", "keyword2", "abbreviation"],
    # Add items you want to monitor for buying opportunities
}

# Rectangle detection parameters for new OCR analyzer
RECTANGLE_DETECTION_CONFIG = {
    "WHITE_THRESHOLD": 240,              # White detection threshold
    "MIN_RECTANGLE_AREA": 100,           # Minimum rectangle area
    "MAX_RECTANGLE_AREA": 5000,          # Maximum rectangle area
    "MIN_ASPECT_RATIO": 0.2,             # Minimum aspect ratio
    "MAX_ASPECT_RATIO": 10,              # Maximum aspect ratio
    "FILL_RATIO_THRESHOLD": 0.7,         # Rectangle fill ratio threshold
    "TEXT_ASSIGNMENT_TOLERANCE": 5,      # Text assignment tolerance in pixels
}

# OCR Debug settings
OCR_DEBUG_CONFIG = {
    "ENABLE_RECTANGLE_DEBUG": False,     # Enable rectangle detection debugging
    "DEBUG_OUTPUT_DIR": "rectangle_debug", # Debug output directory
}
```

### OCR Settings
- **Traditional OCR**: Text-based segmentation using content patterns
- **Rectangle-based OCR**: Visual boundary-based segmentation using white rectangles
- **Languages**: ['ch_tra', 'en'] (Traditional Chinese + English)
- **Debug Mode**: Visual detection results saved to `rectangle_debug/` when enabled

## Important Implementation Details

### Segmentation Algorithms
The system now supports two segmentation approaches:

1. **Traditional Text-based Segmentation** (`OCRAnalyzer`):
   - Uses text content patterns and logical rules
   - Segments based on spaces, punctuation, and content analysis
   - Legacy approach with good text-based recognition

2. **Rectangle-based Visual Segmentation** (`RectangleBasedOCRAnalyzer`):
   - Uses OpenCV to detect white rectangle boundaries in game interface
   - Segments based on visual UI elements rather than text content
   - Implements Template Pattern for extensible segmentation strategies
   - Focuses on extracting 1st segment (player name) and 3rd segment (channel number)
   - Includes visual debugging capabilities

### JSON Serialization
The system includes comprehensive JSON serialization handling for NumPy objects and complex data structures in `screen_monitor.py:convert_to_json_serializable()`.

### Error Handling Strategy
- API quota management with automatic fallback
- Detailed error classification and logging
- Debug files generated for JSON parsing failures: `*_debug.txt`

## Testing Workflow

1. **Setup**: Choose ROI region (game chat window)
2. **Configure**: Set item keywords in `config.py`
3. **Test**: Run `integration_test.py` with 10-50 iterations
4. **Review**: Open `integration_test_*/quick_view.html` for visual results
5. **Debug**: Check debug files if JSON parsing fails

## File Naming Conventions

- **Test files**: `test_*.py` for functional tests
- **Debug files**: `debug_*.py` for diagnostic tools  
- **Integration results**: `integration_test_YYYYMMDD_HHMMSS/`
- **HTML reports**: `quick_view.html` (filtered results), `combined_results.json`

## Dependencies

- **Core**: pyautogui, Pillow, numpy, tkinter
- **AI**: google-generativeai (Gemini API)
- **OCR**: easyocr (optional, installed via `install_ocr.py`)
- **Computer Vision**: opencv-python (for rectangle detection)
- **UI**: tkinter-tooltip

### New Dependencies for Rectangle-based OCR
```bash
pip install opencv-python>=4.8.0
# Already included in updated requirements.txt
```

## Development Notes

- All comments and variable names are in Chinese for maintainability
- Combined Strategy and Template patterns for flexible analyzer implementation
- Template Pattern in `BaseOCRAnalyzer` standardizes OCR processing flow
- Rectangle detection uses OpenCV for computer vision-based segmentation
- Visual debugging tools generate annotated images for development
- Real-time merging system provides immediate feedback during testing
- HTML reports filter to show only matching trading opportunities
- System supports three analysis modes: Gemini AI, Traditional OCR, and Rectangle-based OCR

### Rectangle-based OCR Workflow
1. **Image Preprocessing**: Enhance contrast and sharpness
2. **Rectangle Detection**: Use OpenCV to find white rectangular boundaries
3. **Text Assignment**: Map OCR results to detected rectangles
4. **Segment Extraction**: Extract 1st (player) and 3rd (channel) segments
5. **Visual Debugging**: Generate annotated output images (when enabled)