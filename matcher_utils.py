import re
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def normalize_text(text):
    translations = {"кока кола": "coca cola", "скопско": "skopsko", "пиво": "beer"}
    text = text.lower()
    for mk, en in translations.items():
        text = text.replace(mk, en)
    return text

def extract_volume(text):
    text = text.lower()
    match_liters = re.search(r'(\d+([.,]\d+)?)(\s*л|л|l)', text)
    match_ml = re.search(r'(\d+)(\s*мл|ml|гр|g)', text)
    if match_liters:
        return match_liters.group(1).replace(',', '.')
    if match_ml:
        return str(float(match_ml.group(1)) / 1000)  # Treat grams and ml as liters for grouping
    return None

def token_overlap(name1, name2):
    tokens1 = set(name1.lower().split())
    tokens2 = set(name2.lower().split())
    intersection = tokens1.intersection(tokens2)
    return len(intersection) / max(len(tokens1), len(tokens2), 1)

def is_valid_category_match(name1, name2):
    blocked_pairs = [(["смути", "smooth"], ["пиво", "beer", "radler"])]
    n1 = name1.lower()
    n2 = name2.lower()
    for block1, block2 in blocked_pairs:
        if any(kw in n1 for kw in block1) and any(kw in n2 for kw in block2):
            return False
        if any(kw in n2 for kw in block1) and any(kw in n1 for kw in block2):
            return False
    return True

def price_difference_score(price1, price2, tolerance_percent=5):
    try:
        price1 = float(price1)
        price2 = float(price2)
    except ValueError:
        return 0.0

    lower_bound = price1 * (1 - tolerance_percent / 100)
    upper_bound = price1 * (1 + tolerance_percent / 100)
    return 1.0 if lower_bound <= price2 <= upper_bound else 0.0

def weighted_score(name1, price1, name2, price2):
    if not is_valid_category_match(name1, name2):
        return 0.0

    name1 = normalize_text(name1)
    name2 = normalize_text(name2)

    emb1 = model.encode(name1, convert_to_tensor=True)
    emb2 = model.encode(name2, convert_to_tensor=True)
    semantic_sim = util.pytorch_cos_sim(emb1, emb2).item()

    vol1 = extract_volume(name1)
    vol2 = extract_volume(name2)
    volume_score = 1.0 if vol1 == vol2 else 0.0

    overlap_score = token_overlap(name1, name2)
    price_score = price_difference_score(price1, price2)

    score = (0.35 * volume_score) + (0.25 * overlap_score) + (0.25 * semantic_sim) + (0.15 * price_score)
    return score
