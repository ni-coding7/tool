import anthropic
import json
import re

PAGE_PROMPTS = {
    "home": """Scrivi contenuti HOME PAGE. Rispondi SOLO JSON:
{{
  "meta_title": "{company_block} - {geo_block}",
  "meta_description": "Descrizione SEO",
  "h1": "Headline",
  "intro": "Intro",
  "services_overview": "Servizi",
  "trust_block": "Trust",
  "cta_text": "CTA",
  "faqs": [{{"question": "Q1", "answer": "A1"}}]
}}""",
    "chi_siamo": """Scrivi CHI SIAMO. Rispondi SOLO JSON:
{{
  "meta_title": "Titolo",
  "meta_description": "Desc",
  "h1": "H1",
  "storia": "Storia",
  "missione": "Missione",
  "team_intro": "Team",
  "perche_noi": "USP",
  "faqs": [{{"question": "Q1", "answer": "A1"}}]
}}""",
    "servizio": """Scrivi SERVIZIO {service_name}. Rispondi SOLO JSON:
{{
  "meta_title": "Titolo",
  "meta_description": "Desc",
  "h1": "H1",
  "intro": "Intro",
  "cosa_offriamo": "Cosa",
  "perche_sceglierci": "Vantaggi",
  "processo": "Step",
  "faqs": [{{"question": "Q1", "answer": "A1"}}]
}}""",
    "city_page": """Scrivi CITY PAGE per {city}. Rispondi SOLO JSON:
{{
  "meta_title": "Titolo",
  "meta_description": "Desc",
  "h1": "H1",
  "intro_locale": "Intro",
  "servizi_in_citta": "Servizi",
  "contesto_territoriale": "Context",
  "perche_noi_locale": "Why",
  "faqs": [{{"question": "Q1", "answer": "A1"}}]
}}"""
}

def build_company_block(company: dict) -> str:
    if not company: return "N/D"
    s = company.get("services", [])
    s_str = ", ".join(s) if isinstance(s, list) else str(s)
    return f"Nome: {company.get('name', 'N/D')}\nServizi: {s_str}"

def generate_page_content(api_key, model, page_type, context_data, company=None, **kwargs):
    client = anthropic.Anthropic(api_key=api_key)
    prompt_template = PAGE_PROMPTS.get(page_type, PAGE_PROMPTS["home"])
    if company:
        context_data["company_block"] = build_company_block(company)
    if "geo_context" in kwargs and kwargs["geo_context"]:
        context_data["geo_block"] = str(kwargs["geo_context"])
    defaults = {"company_block": "N/D", "geo_block": "", "existing_block": "", "service_name": "Servizio", "city": "Città", "region": "", "climate": "N/D", "pois": "N/D", "services": ""}
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
