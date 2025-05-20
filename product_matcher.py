import csv
from tqdm import tqdm
from sentence_transformers import util

from db_loader import load_products_from_db
from matcher_utils import (
    extract_volume,
    weighted_score,
    normalize_text,
    model,
    token_overlap,
    price_difference_score
)

def group_products_by_volume(products):
    grouped = {}
    for product in products:
        vol = extract_volume(product['name'])
        if vol:
            grouped.setdefault(vol, []).append(product)
    return grouped

def find_matches_in_group(group):
    matches = []

    # Precompute normalized names and embeddings
    names = [normalize_text(p['name']) for p in group]
    embeddings = model.encode(names, convert_to_tensor=True)

    # Outer loop with progress bar
    for i, p1 in enumerate(tqdm(group, desc="Comparing products")):
        for j, p2 in enumerate(group):
            if i >= j or p1['market'] == p2['market']:
                continue

            # Use precomputed embeddings
            semantic_sim = util.pytorch_cos_sim(embeddings[i], embeddings[j]).item()

            vol1 = extract_volume(p1['name'])
            vol2 = extract_volume(p2['name'])
            volume_score = 1.0 if vol1 == vol2 else 0.0

            overlap_score = token_overlap(p1['name'], p2['name'])
            price_score = price_difference_score(p1['price'], p2['price'])

            score = (0.35 * volume_score) + (0.25 * overlap_score) + (0.25 * semantic_sim) + (0.15 * price_score)

            if score >= 0.85:
                matches.append({
                    "product1": p1['name'],
                    "price1": p1['price'],
                    "market1": p1['market'],
                    "product2": p2['name'],
                    "price2": p2['price'],
                    "market2": p2['market'],
                    "score": round(score, 2)
                })
    return matches

def process_all_products():
    products = load_products_from_db()
    grouped_products = group_products_by_volume(products)

    with open('matched_products.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['product1', 'price1', 'market1', 'product2', 'price2', 'market2', 'score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for volume, group in grouped_products.items():
            print(f"Processing volume group: {volume} with {len(group)} products")
            matches = find_matches_in_group(group)
            for match in matches:
                writer.writerow(match)

    print("✅ Processing complete. Results saved to matched_products.csv")

if __name__ == "__main__":
    process_all_products()
