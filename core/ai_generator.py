import anthropic
import json
import re

# --- CONFIGURAZIONE PROMPT ---
PAGE_PROMPTS = {
    "home": """Sei un copywriter SEO esperto. Scrivi i contenuti ottimizzati per la HOME PAGE.
Rispondi SOLO con JSON valido, nessun testo extra, nessun markdown.

Dati azienda: {company_block}
Contesto geo: {geo_block}
{existing_block}

Genera un JSON con questa struttura esatta:
{{
  "meta_title": "titolo SEO max 60 caratteri con keyword principale e città",
  "meta_description": "descrizione SEO max 155 caratteri con call to action",
  "h1": "headline principale della pagina",
  "intro": "paragrafo introduttivo 80-100 parole, con keyword geografica naturale",
  "services_overview": "paragrafo 60-80 parole che elenca i servizi principali",
  "trust_block": "paragrafo 50-70 parole su esperienza, valori, EEAT (esperienza reale, autorevolezza)",
  "cta_text": "testo call to action 15-20 parole",
  "faqs": [
    {{"question": "domanda frequente 1 specifica per settore e geo", "answer": "risposta 40-60 parole"}},
    {{"question": "domanda frequente 2", "answer": "risposta 40-60 parole"}},
    {{"question": "domanda frequente 3", "answer": "risposta 40-60 parole"}}
  ]
}}"""
}

def build_company_block(company: dict) -> str:
    if not company: return "N/D"
    s = company.get("services", [])
    s_str = ", ".join(s) if isinstance(s, list) else str(s)
    return f"Nome: {company.get('name', 'N/D')}\nServizi: {s_str}"

def generate_page_content(api_key, model, page_type, context_data, company=None):
    client = anthropic.Anthropic(api_key=api_key)
    prompt_template = PAGE_PROMPTS.get(page_type, PAGE_PROMPTS["home"])
    if company:
        context_data["company_block"] = build_company_block(company)
    
    defaults = {"company_block": "N/D", "geo_block": "", "existing_block": "", "service_name": "", "city": "", "region": "", "climate": "", "pois": "", "services": ""}
    full_context = {**defaults, **context_data}
    
    try:
        response = client.messages.create(
            model=model,
            max_tokens=2500,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt_template.format(**full_context)}]
        )
        raw_text = response.content[0].text
        clean_json = re.sub(r'```json\s*|\s*```', '', raw_text).strip()
        return json.loads(clean_json)
    except Exception as e:
        raise Exception(f"Errore AI: {str(e)}")
