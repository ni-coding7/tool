import anthropic
import json
import re

# --- CONFIGURAZIONE PROMPT ---
# Usiamo i template senza le doppie graffe interne per evitare KeyError
PAGE_PROMPTS = {
    "home": "Scrivi contenuti HOME PAGE per l'azienda {company_block}. Contesto geo: {geo_block}. Rispondi SOLO in formato JSON con queste chiavi: meta_title, meta_description, h1, intro, services_overview, trust_block, cta_text, faqs (lista di question e answer).",
    "chi_siamo": "Scrivi pagina CHI SIAMO per {company_block}. Rispondi SOLO in formato JSON con queste chiavi: meta_title, meta_description, h1, storia, missione, team_intro, perche_noi, faqs.",
    "servizio": "Scrivi pagina SERVIZIO per {service_name} dell'azienda {company_block}. Rispondi SOLO in formato JSON con queste chiavi: meta_title, meta_description, h1, intro, cosa_offriamo, perche_sceglierci, processo, faqs.",
    "city_page": "Scrivi CITY PAGE per la città di {city} per l'azienda {company_block}. Rispondi SOLO in formato JSON con queste chiavi: meta_title, meta_description, h1, intro_locale, servizi_in_citta, contesto_territoriale, perche_noi_locale, faqs."
}

def build_company_block(company: dict) -> str:
    if not company: return "N/D"
    s = company.get("services", [])
    s_str = ", ".join(s) if isinstance(s, list) else str(s)
    return f"Nome: {company.get('name', 'N/D')}, Settore: {company.get('industry', 'N/D')}, Servizi: {s_str}"

def generate_page_content(api_key, **kwargs):
    model = kwargs.get('model', 'claude-3-5-sonnet-latest')
    page_type = kwargs.get('page_type', 'home')
    context_data = kwargs.get('context_data', {})
    company = kwargs.get('company')
    
    client = anthropic.Anthropic(api_key=api_key)
    prompt_template = PAGE_PROMPTS.get(page_type, PAGE_PROMPTS["home"])
    
    if company:
        context_data["company_block"] = build_company_block(company)
    if "geo_context" in kwargs and kwargs.get("geo_context"):
        context_data["geo_block"] = str(kwargs["geo_context"])
        
    defaults = {
        "company_block": "N/D", "geo_block": "N/D", "existing_block": "", 
        "service_name": "Servizio", "city": "Città", "region": "", 
        "climate": "N/D", "pois": "N/D", "services": ""
    }
    full_context = {**defaults, **context_data}
    
    try:
        # Formattiamo il prompt
        final_prompt = prompt_template.format(**full_context)
        
        response = client.messages.create(
            model=model,
            max_tokens=2500,
            temperature=0.7,
            messages=[{"role": "user", "content": final_prompt}]
        )
        
        raw_text = response.content[0].text
        # Pulizia rigorosa del JSON
        clean_json = re.sub(r'```json\s*|\s*```', '', raw_text).strip()
        # Se Claude aggiunge testo prima/dopo, cerchiamo solo la parte tra parentesi graffe
        json_match = re.search(r'\{.*\}', clean_json, re.DOTALL)
        if json_match:
            clean_json = json_match.group(0)
            
        return json.loads(clean_json)
    except Exception as e:
        raise Exception(f"Errore AI: {str(e)}")
