%%writefile space_verification_web3.py
import panel as pn
import os
import base64
import time
import json
import random
from datetime import datetime
from PIL import Image
from PyPDF2 import PdfReader
import google.generativeai as genai
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

pn.extension(design="material", template="fast")

# Space theme CSS with animations
space_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Space+Mono&display=swap');

body {
    background: #000000;
    color: #00ff9d;
    font-family: 'Space Mono', monospace;
}

.special-span {
    animation: starGlow 2s infinite alternate;
    text-shadow: 0 0 15px #00ff9d;
}

@keyframes starGlow {
    from { opacity: 0.8; }
    to { opacity: 1; text-shadow: 0 0 25px #00ff9d; }
}

.planet {
    position: absolute;
    border-radius: 50%;
    animation: orbit 20s linear infinite;
}

@keyframes orbit {
    from { transform: rotate(0deg) translateX(150px) rotate(0deg); }
    to { transform: rotate(360deg) translateX(150px) rotate(-360deg); }
}

</style>
<div class="planet" style="width:50px;height:50px;background:radial-gradient(circle at 30% 30%, #6b00ff, #000);"></div>
"""

# Initialize APIs
os.environ["OPENAI_API_KEY"] = "sk-proj-..."  # Replace
GOOGLE_API_KEY = "AIzaSyCeoy..."              # Replace
UBER_API_KEY = "rt2iuBepkZJ43cOFDMy0ymVcxR1WnMnAxZtJtrcOamtRTdj5E0jneD6gdqhmhJY7"
genai.configure(api_key=GOOGLE_API_KEY)

# Blockchain components
class StellarLedger:
    def _init_(self):
        self.chain = []
        self.sellers = [
            {'id': 1, 'name': 'MoonMart', 'rating': 4.8, 'trips': 42},
            {'id': 2, 'name': 'NebulaNet', 'rating': 4.6, 'trips': 38},
            {'id': 3, 'name': 'QuantumQuik', 'rating': 4.9, 'trips': 45}
        ]
        
    def add_block(self, data):
        block = {
            'timestamp': datetime.now().isoformat(),
            'data': data,
            'hash': base64.b64encode(os.urandom(32)).decode(),
            'nonce': random.getrandbits(128)
        }
        self.chain.append(block)
        
    def update_ratings(self, success):
        for seller in self.sellers:
            if success:
                seller['rating'] = min(5, seller['rating'] + 0.1)
                seller['trips'] += 1
            else:
                seller['rating'] = max(4, seller['rating'] - 0.2)

ledger = StellarLedger()

class QuantumContract:
    def execute(self, invoice, validation):
        result = {
            'success': "Verified: Yes" in validation,
            'block': f"#{len(ledger.chain)+1}",
            'miner': f"0x{base64.b64encode(os.urandom(16)).decode()[:24]}"
        }
        ledger.add_block({'invoice': invoice, 'validation': validation})
        ledger.update_ratings(result['success'])
        return result

# Processing functions
def process_invoice(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = "\n".join([page.extract_text() for page in reader.pages])
    
    prompt = ChatPromptTemplate.from_template("""
    Extract from space invoice: {text}
    Return JSON with:
    - commodity (space product category)
    - model_numbers (list)
    - quantities (list)
    - specifications (list)
    """)
    
    chain = prompt | ChatOpenAI(model="gpt-4") | StrOutputParser()
    return chain.invoke({"text": text})

def validate_with_gemini(invoice_data, image):
    img = Image.open(image)
    prompt = f"""Analyze space tech image and compare with:
    {invoice_data}
    Check anti-gravity compatibility and quantum specs"""
    
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([prompt, img])
    return response.text

# Panel UI Components
contract = QuantumContract()
pdf_input = pn.widgets.FileInput(accept='.pdf')
image_input = pn.widgets.FileInput(accept='.png,.jpg,.jpeg', multiple=True)
results = pn.pane.JSON({}, theme='dark')
leaderboard = pn.pane.DataFrame([], theme='dark')

def update_leaderboard():
    df = pn.DataFrame(ledger.sellers).sort_values('rating', ascending=False)
    leaderboard.object = df.style.format({'rating': '{:.1f}'}).highlight_max(color='#00ff9d')

def process_event(event):
    invoice_data = process_invoice(pdf_input.value)
    results.object = {"invoice": invoice_data}
    
    for img in image_input.value:
        validation = validate_with_gemini(invoice_data, img)
        contract_result = contract.execute(invoice_data, validation)
        results.object.update({img: [validation, contract_result]})
    
    update_leaderboard()

# Build interface
dashboard = pn.Column(
    pn.pane.HTML(space_css),
    pn.Row(
        pn.Column(
            pn.pane.Markdown("# 🚀 Stellar Verification System", style={'color': '#00ff9d'}),
            pn.pane.Markdown("### Upload Space Invoice PDF"),
            pdf_input,
            pn.pane.Markdown("### Upload Quantum Product Images"),
            image_input,
            pn.widgets.Button(name="⚡ Execute Smart Contract", button_type="primary"),
        ),
        pn.Column(
            pn.pane.Markdown("## 🔭 Verification Results", style={'color': '#6b00ff'}),
            results,
            pn.pane.Markdown("## 🌌 Seller Leaderboard"),
            leaderboard
        )
    )
)

dashboard.servable()

# Run in Colab: 
# from space_verification_web3 import dashboard
# dashboard.show()
