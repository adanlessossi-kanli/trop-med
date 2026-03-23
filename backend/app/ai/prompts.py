SYSTEM_PROMPT = (
    "You are a medical AI assistant specialized in tropical medicine. "
    "Always provide evidence-based answers with confidence levels. "
    "Never make autonomous clinical decisions. "
    "If uncertain, explicitly state your uncertainty."
)

PROMPTS = {
    "query": {
        "system": SYSTEM_PROMPT,
        "template": "Medical question ({locale}): {question}",
        "mode": "direct",
    },
    "differential": {
        "system": SYSTEM_PROMPT + " Provide a ranked differential diagnosis with probability estimates.",
        "template": (
            "Patient demographics: {demographics}\n"
            "Symptoms: {symptoms}\n"
            "Vitals: {vitals}\n"
            "History: {history}\n\n"
            "Provide a ranked differential diagnosis with suggested investigations."
        ),
        "mode": "thinking",
    },
    "literature": {
        "system": SYSTEM_PROMPT + " Synthesize research findings with methodology notes and clinical implications.",
        "template": "Literature review on: {topic}",
        "mode": "thinking",
    },
    "translate": {
        "system": "You simplify medical text for patients at a 6th-grade reading level while maintaining accuracy.",
        "template": "Simplify the following medical text into {target_language}:\n\n{text}",
        "mode": "direct",
    },
}


def build_prompt(prompt_type: str, **kwargs) -> dict:
    cfg = PROMPTS[prompt_type]
    return {
        "system": cfg["system"],
        "prompt": cfg["template"].format(**kwargs),
        "mode": cfg["mode"],
    }
