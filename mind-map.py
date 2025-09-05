from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import requests
import fitz
import json
import textwrap
import logging
import base64
import re
from openai import OpenAI
from json_repair import repair_json

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Set your OpenAI API key as environment variable
# MODEL_ID = "openai/gpt-oss-20b"  # Using the only available model on your RunPod endpoint
MODEL_ID = "gpt-4o-mini-2024-07-18"
# Initialize OpenAI client with shorter timeout for better error handling
client = OpenAI(api_key=OPENAI_API_KEY, 
                # base_url="https://mw68d46ydpbo0a-8000.proxy.runpod.net/v1",
                timeout=1000.0)  # Reduced timeout to 2 minutes


def extract_content_from_file(file):
    if file.filename.endswith('.pdf'):
        return extract_text_from_pdf(file)
    elif file.filename.endswith('.txt'):
        return file.read().decode('utf-8')
    else:
        raise ValueError("Unsupported file type")
    

def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        for page_num in range(min(len(pdf_document), 10)):  # Limit to first 10 pages for performance
            page = pdf_document.load_page(page_num)
            page_text = page.get_text()
            text += page_text
            
        # Clean up common PDF extraction artifacts
        text = text.replace('\uf020', ' ').replace('\uf047', '')
        # Remove other Unicode artifacts that commonly appear in PDFs
        import re
        text = re.sub(r'[\uf000-\uf8ff]', '', text)  # Remove private use area characters
        text = ' '.join(text.split())  # Normalize whitespace
        
        logger.debug(f"Extracted {len(text)} characters from {min(len(pdf_document), 10)} pages")
        return text
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        raise


def clean_and_parse_json(response_text):
    """
    Clean and parse JSON response from OpenAI API with multiple fallback strategies
    """
    logger.debug(f"Original response: {response_text[:200]}...")
    
    # Strategy 1: Remove markdown code blocks
    cleaned_text = re.sub(r'```json\s*', '', response_text)
    cleaned_text = re.sub(r'```\s*$', '', cleaned_text, flags=re.MULTILINE)
    
    # Strategy 2: Extract JSON from response if it contains other text
    json_match = re.search(r'(\{.*\})', cleaned_text, re.DOTALL)
    if json_match:
        cleaned_text = json_match.group(1)
    
    # Strategy 3: Remove any leading/trailing whitespace and non-JSON characters
    cleaned_text = cleaned_text.strip()
    
    # Strategy 4: Try to find the start and end of JSON object
    start_idx = cleaned_text.find('{')
    end_idx = cleaned_text.rfind('}')
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        cleaned_text = cleaned_text[start_idx:end_idx + 1]
    
    logger.debug(f"Cleaned text: {cleaned_text[:200]}...")
    
    # Try parsing strategies in order of preference
    parsing_strategies = [
        # Strategy 1: Direct JSON parsing
        lambda text: json.loads(text),
        
        # Strategy 2: Use json-repair library
        lambda text: json.loads(repair_json(text)),
        
        # Strategy 3: Remove common formatting issues and try again
        lambda text: json.loads(
            text.replace('\n', ' ')
                .replace('\t', ' ')
                .replace('  ', ' ')
                .strip()
        ),
        
        # Strategy 4: Use json-repair on cleaned text
        lambda text: json.loads(repair_json(
            text.replace('\n', ' ')
                .replace('\t', ' ')
                .replace('  ', ' ')
                .strip()
        )),
    ]
    
    for i, strategy in enumerate(parsing_strategies):
        try:
            result = strategy(cleaned_text)
            logger.debug(f"Successfully parsed JSON using strategy {i + 1}")
            return result
        except (json.JSONDecodeError, ValueError) as e:
            logger.debug(f"Strategy {i + 1} failed: {e}")
            continue
    
    # If all strategies fail, log the error and raise exception
    logger.error(f"All JSON parsing strategies failed for text: {cleaned_text[:500]}")
    raise ValueError("Unable to parse response as valid JSON after trying multiple strategies")


def generate_mind_map(content):
    # Truncate content more aggressively for Arabic text which can be token-heavy
    max_content_length = 2000  # Reduced from 3000 for better performance with Arabic text
    if len(content) > max_content_length:
        content = content[:max_content_length] + "..."
        logger.debug(f"Content truncated to {max_content_length} characters")
    
    # Clean the content but don't escape braces since we're using f-strings
    content = content.strip()
    
    # Filter out some problematic characters that might cause issues
    import re
    content = re.sub(r'[\uf000-\uf8ff]', '', content)  # Remove private use area characters
    
    prompt = f"""
أنت أستاذ في علم الإدراك وخبير في إنشاء الخرائط الذهنية التفصيلية. مهمتك هي توليد خريطة ذهنية شاملة بصيغة JSON مناسبة لمكتبة GoJS من النص المقدم.

⚠️ مهم جدًا: يجب أن يحتوي ردك فقط على JSON صالح. لا تقم بتضمين أي نصوص تفسيرية أو تنسيقات Markdown أو كتل كود. ابدأ مباشرة بالقوس المعقوف الافتتاحي {{ وأنهِ بالقوس المعقوف الختامي }}.

ينبغي أن تكون الخريطة الذهنية مفصلة وتشمل جميع النقاط المهمة دون إغفال أي تفاصيل. التقط الأفكار الرئيسية وكذلك التفاصيل الداعمة. قم بترتيب الخريطة الذهنية في شكل هرمي يُظهر العلاقات والارتباطات بين المفاهيم المختلفة.

فيما يلي مثال على الصيغة المتوقعة لـ GoJS JSON الخاصة بالخريطة الذهنية:
{{
    "class": "go.TreeModel",
    "nodeDataArray": [
        {{"key":0, "text":"Mind Map", "loc":"0 0"}},
        {{"key":1, "parent":0, "text":"Getting more time", "brush":"skyblue", "dir":"right"}},
        {{"key":11, "parent":1, "text":"Wake up early", "brush":"skyblue", "dir":"right"}},
        {{"key":12, "parent":1, "text":"Delegate", "brush":"skyblue", "dir":"right"}},
        {{"key":2, "parent":0, "text":"More effective use", "brush":"darkseagreen", "dir":"right"}},
        {{"key":21, "parent":2, "text":"Planning", "brush":"darkseagreen", "dir":"right"}},
        {{"key":3, "parent":0, "text":"Time wasting", "brush":"palevioletred", "dir":"left"}},
        {{"key":31, "parent":3, "text":"Too many meetings", "brush":"palevioletred", "dir":"left"}}
    ]
}}

⚠️ مهم جدًا: حلّل النص التالي وأنشئ خريطة ذهنية استنادًا إلى محتواه الفعلي.
لا تُنشئ خريطة ذهنية عن "إدارة الوقت" أو تستخدم المثال أعلاه. أنشئ خريطة ذهنية استنادًا فقط إلى المحتوى المحدد أدناه:

{content}

التعليمات:

1. تحديد الأفكار الرئيسية: استخرج الأفكار الرئيسية من النص المقدم أعلاه وضعها كعُقد أساسية.
2. التقاط التفاصيل الداعمة: قم بتضمين جميع التفاصيل الداعمة والنقاط الفرعية كعُقد فرعية تحت الفكرة الرئيسية المناسبة.
3. الحفاظ على الهيكل الهرمي: تأكد أن الخريطة الذهنية تحافظ على هيكل هرمي واضح.
4. عدم إغفال التفاصيل: لا تهمل أي معلومة مهمة.
5. استخدام الألوان المناسبة: استعمل ألوانًا مختلفة للتمييز بين مستويات التسلسل الهرمي.
6. صيغة JSON صالحة فقط: أعد فقط JSON صالحًا بدون أي تنسيقات Markdown أو نصوص تفسيرية.
7. حرج: يجب أن تُبنى الخريطة الذهنية فقط على محتوى النص المقدم أعلاه، وليس على أي مثال.

📌 أعد الخريطة الذهنية بصيغة JSON المطلوبة استنادًا إلى المحتوى الفعلي المقدم.
"""

    
    try:
        logger.debug(f"Sending request to model: {MODEL_ID}")
        logger.debug(f"Content being processed: {content[:300]}...")
        logger.debug(f"Full prompt length: {len(prompt)} characters")
        
        # Log a snippet to verify content is included
        logger.debug(f"Prompt includes actual content: {'=== IMPORTANT:' in prompt}")
        
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": "You are an expert at creating detailed mind maps in JSON format. You must analyze the PROVIDED TEXT CONTENT and create a mind map based on that specific content, not on any examples given."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Reduced temperature for more consistent results
            top_p=0.9,       # Reduced top_p for more focused responses
            max_tokens=8192  # Limit response length to prevent timeouts
        )
        response_text = response.choices[0].message.content
        logger.debug(f"Raw API response: {response_text[:200]}...")
        print(response_text)
        # Use the enhanced parsing function
        mind_map_data = clean_and_parse_json(response_text)
        logger.debug(f"Successfully parsed mind map data with {len(mind_map_data.get('nodeDataArray', []))} nodes")
        
        return mind_map_data
    except Exception as e:
        logger.error(f"Error generating mind map: {e}")
        logger.error(f"Full error details: {str(e)}")
        raise

def translate_mind_map(content):
    # Truncate content if it's too long to prevent token overflow
    max_content_length = 3000  # Adjust based on model's context window
    if len(content) > max_content_length:
        content = content[:max_content_length] + "..."
        logger.debug(f"Translation content truncated to {max_content_length} characters")
    
    prompt = """Jesteś profesorem nauk lingwistycznych, twoich zadaniem jest przetłumaczyć zawartość tekstową podanej mapy myśli na język Polski, nie naruszając struktury mapy.
    
    KRYTYCZNE: Twoja odpowiedź musi zawierać TYLKO poprawny JSON. Nie dołączaj żadnego tekstu wyjaśniającego, formatowania markdown, ani bloków kodu. Zacznij bezpośrednio od otwierającego nawiasu klamrowego {{ i zakończ zamykającym nawiasem klamrowym }}.
    
    Wykorzystane słownictwo powinno posiadać wydźwięk podobny do oryginalnego tekstu. Zwróć nienaruszoną w strukturze mapę myśli z przetumaczoną zawartością w formacie JSON.
    Oryginalne, angielskie wersje nazw własnych i naukowych pozostawiaj w nawiasach obok tłumaczenia. 

    Mapa myśli do przetłumaczenia:
    {content}
    """

    formatted_prompt = textwrap.dedent(prompt).format(content=content)
    logger.debug(f"Formatted translation prompt length: {len(formatted_prompt)} characters")
    
    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": "You are an expert linguist specializing in Polish translation while preserving JSON structure."},
                {"role": "user", "content": formatted_prompt}
            ],
            temperature=0.3,
            top_p=0.95
        )
        response_text = response.choices[0].message.content
        logger.debug(f"Raw translation response: {response_text[:200]}...")
        
        # Use the enhanced parsing function
        translated_data = clean_and_parse_json(response_text)
        logger.debug(f"Successfully parsed translated mind map data with {len(translated_data.get('nodeDataArray', []))} nodes")
        
        return translated_data
    except Exception as e:
        logger.error(f"Error translating mind map: {e}")
        raise
    

@app.route('/')
def index():
    logger.debug("Rendering index page")
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    logger.debug("Received a request to generate a mind map.")

    file = request.files.get('file')
    text = request.form.get('text')

    logger.debug(f"File received: {file.filename if file else 'None'}")
    logger.debug(f"Text received: {text[:100] if text else 'None'}...")

    if file:
        try:
            filename = secure_filename(file.filename)
            logger.debug(f"Processing file: {filename}")

            file_content = extract_content_from_file(file)
            logger.debug(f"Extracted content length: {len(file_content)} characters")
            logger.debug(f"Content preview: {file_content[:300]}...")
            
            mind_map_data = generate_mind_map(file_content)
            logger.debug(f"Generated mind map with {len(mind_map_data.get('nodeDataArray', []))} nodes")

            # Log the actual content of the first few nodes to verify it's from the uploaded file
            nodes = mind_map_data.get('nodeDataArray', [])
            if nodes:
                logger.debug(f"Root node text: {nodes[0].get('text', 'N/A')}")
                if len(nodes) > 1:
                    logger.debug(f"First child node text: {nodes[1].get('text', 'N/A')}")

            return jsonify(mind_map_data)
        except Exception as e:
            logger.error(f"Error processing uploaded file: {e}")
            return jsonify({'error': str(e)}), 500
    elif text:
        try:
            logger.debug(f"Processing text input: {text[:50]}...")
            mind_map_data = generate_mind_map(text)
            return jsonify(mind_map_data)
        except Exception as e:
            logger.error(f"Error processing text input: {e}")
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'No file or text input provided'}), 400
    

@app.route('/translate', methods=['POST'])
def translate():
    logger.debug("Received a request to translate a mind map.")

    try:
        request_data = request.get_json()
        mind_map_content = request_data.get('content')

        if not mind_map_content:
            return jsonify({'error': 'Mind map content not provided'}), 400

        # Convert the content to JSON string if it's a dict
        if isinstance(mind_map_content, dict):
            content_str = json.dumps(mind_map_content, ensure_ascii=False)
        else:
            content_str = str(mind_map_content)

        translated_data = translate_mind_map(content_str)
        logger.debug(f"Translated data with {len(translated_data.get('nodeDataArray', []))} nodes")

        return jsonify(translated_data)
    except Exception as e:
        logger.error(f"Error translating mind map: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    

@app.route('/load_map', methods=['POST'])
def load_map():
    file = request.files['file']
    if file:
        try:
            map_data = json.load(file)
            logger.debug(f"Loaded mind map data: {map_data}")
            return jsonify(map_data), 200
        except Exception as e:
            logger.error(f"Error loading mind map: {e}")
            return jsonify({'error': str(e)}), 500
    logger.warning("No file uploaded")
    return jsonify({'error': 'No file uploaded'}), 400


@app.route('/test_generate', methods=['GET'])
def test_generate():
    """Test endpoint to verify mind map generation with sample text"""
    logger.debug("Test generate endpoint called")
    
    sample_text = """
    Project Management Fundamentals
    
    Project management is the practice of initiating, planning, executing, controlling, and closing the work of a team to achieve specific goals and meet specific success criteria at the specified time.
    
    Key Areas:
    1. Project Planning - Defining scope, timeline, and resources
    2. Risk Management - Identifying and mitigating potential issues
    3. Team Leadership - Managing and motivating team members
    4. Quality Control - Ensuring deliverables meet standards
    5. Budget Management - Controlling costs and resource allocation
    
    Success Factors:
    - Clear communication
    - Stakeholder engagement
    - Regular monitoring and reporting
    - Adaptability to change
    """
    
    try:
        logger.debug(f"Generating mind map for sample text: {len(sample_text)} characters")
        mind_map_data = generate_mind_map(sample_text)
        logger.debug(f"Generated test mind map with {len(mind_map_data.get('nodeDataArray', []))} nodes")
        
        # Log some details about the generated map
        nodes = mind_map_data.get('nodeDataArray', [])
        if nodes:
            logger.debug(f"Root node: {nodes[0]}")
            
        return jsonify(mind_map_data)
    except Exception as e:
        logger.error(f"Error in test generate: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        exit(1)
    
    logger.debug(f"Initialized OpenAI client with model: {MODEL_ID}")
    app.run(host='0.0.0.0', port=8081, debug=False)
