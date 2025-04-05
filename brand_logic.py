import streamlit as st
import pandas as pd
import random
from collections import Counter

BRAND_CLUSTERS = {
    "GUCCI": 1, "SAINT LAURENT": 1, "ALEXANDER MCQUEEN": 1, "TOM FORD": 1, "MAISON MARGIELA": 1, "RICK OWENS": 1, "YOHJI YAMAMOTO": 1,
    "OFF-WHITE": 2, "SUPREME": 2, "PALM ANGELS": 2, "FEAR OF GOD": 2,
    "THE FRANKIE SHOP": 3, "A.P.C.": 3, "VINCE": 3, "NANUSHKA": 3, "RAG & BONE": 3, "POLO RALPH LAUREN": 3,
    "NIKE": 4, "ADIDAS": 4, "THE NORTH FACE": 4, "LULULEMON": 4,
    "LEVI'S": 5, "AGOLDE": 5, "7 FOR ALL MANKIND": 5, "CALVIN KLEIN JEANS": 5,
    "ZIMMERMANN": 6, "JOHANNA ORTIZ": 6, "SOLID & STRIPED": 6, "HUNZA G": 6,
    "MICHAEL KORS COLLECTION": 7, "VERSACE JEANS COUTURE": 7, "CALVIN KLEIN JEANS": 7, "POLO RALPH LAUREN": 7
}

@st.cache_data
def load_brand_data():
    prices = pd.read_excel("grafluence_data.xlsx", sheet_name="small_sample_prices")
    images = pd.read_excel("grafluence_data.xlsx", sheet_name="brand_images_real")
    prices["Brand"] = prices["Brand"].str.upper()
    images["Brand"] = images["Brand"].str.upper()
    images = images.dropna(subset=["Product image URL"])

    weighted_lookup = {}
    for brand, group in images.groupby("Brand"):
        weights = group["Category 2"].value_counts().to_dict()
        weighted_lookup[brand] = list(zip(group["Product image URL"], group["Category 2"].map(weights)))

    price_lookup = dict(zip(prices["Brand"], prices["Average Price"]))
    available_brands = list(set(price_lookup) & set(weighted_lookup))
    return available_brands, price_lookup, weighted_lookup

brands, price_lookup, image_lookup = load_brand_data()

def weighted_sample(images, k=6):
    urls, weights = zip(*images)
    return random.choices(urls, weights=weights, k=min(k, len(urls)))

def get_brand_data(brand):
    images = weighted_sample(image_lookup[brand])
    return {
        "Brand": brand,
        "Price": round(price_lookup[brand]),
        "Images": images
    }

def generate_cluster_question(verify_cluster, test_cluster):
    reference = random.choice([b for b in brands if BRAND_CLUSTERS.get(b) == verify_cluster])
    same = random.choice([b for b in brands if BRAND_CLUSTERS.get(b) == verify_cluster and b != reference])
    different = random.choice([b for b in brands if BRAND_CLUSTERS.get(b) == test_cluster])
    if random.random() < 0.5:
        return {"reference": get_brand_data(reference), "a": get_brand_data(same), "b": get_brand_data(different)}
    else:
        return {"reference": get_brand_data(reference), "a": get_brand_data(different), "b": get_brand_data(same)}

def generate_mixed_cluster_question():
    clusters = list(set(BRAND_CLUSTERS.values()))
    selected_clusters = random.sample(clusters, 3)
    selected_brands = [random.choice([b for b in brands if BRAND_CLUSTERS.get(b) == c]) for c in selected_clusters]
    random.shuffle(selected_brands)
    return {
        "reference": get_brand_data(selected_brands[0]),
        "a": get_brand_data(selected_brands[1]),
        "b": get_brand_data(selected_brands[2])
    }

def generate_all_questions():
    questions = []
    clusters = list(set(BRAND_CLUSTERS.values()))
    cluster_pairs = random.sample([(v, t) for v in clusters for t in clusters if v != t], 4)
    cluster_pairs += random.choices([(v, t) for v in clusters for t in clusters if v != t], k=16)
    for v, t in cluster_pairs:
        questions.append(generate_cluster_question(v, t))
    for _ in range(10):
        questions.append(generate_mixed_cluster_question())
    return questions

def run_brand_survey():
    if "brand_questions" not in st.session_state:
        st.session_state.brand_questions = generate_all_questions()
        st.session_state.brand_index = 0
        st.session_state.brand_responses = []

    i = st.session_state.brand_index
    if i >= 30:
        return True

    q = st.session_state.brand_questions[i]
    st.markdown(f"<h3 style='text-align:center;'>Brand Question {i + 1} of 30</h3>", unsafe_allow_html=True)

    st.markdown("---")
    ref_imgs = "".join([f"<img src='{url}' width='80' style='margin: 4px; border-radius: 6px;'/>" for url in q['reference']['Images']])
    st.markdown(f"""
    <div style='text-align: center;'>
        <h3>Reference Brand: {q['reference']['Brand']}</h3>
        <p><strong>Median Price:</strong> ${q['reference']['Price']}</p>
        {ref_imgs}
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"<h4 style='text-align:center;'>Which brand is more similar to {q['reference']['Brand']}?</h4>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    for col, key in zip([col1, col2], ['a', 'b']):
        with col:
            imgs = "".join([f"<img src='{url}' width='90' style='margin:4px; border-radius:6px;'/>" for url in q[key]['Images']])
            st.markdown(f"""
            <div style='display: flex; flex-direction: column; justify-content: space-between; height: 300px; padding: 16px; border: 2px solid #ccc; border-radius: 12px; text-align: center;'>
                <div>
                    <h4>{q[key]['Brand']}</h4>
                    <p><strong>Median Price:</strong> ${q[key]['Price']}</p>
                    {imgs}
                </div>
            </div>""", unsafe_allow_html=True)

    # Button row (aligned with respective brand)
    col1b, col2b = st.columns(2)
    if col1b.button(f"Select {q['a']['Brand']}", key=f"a_{i}"):
        st.session_state.brand_responses.append({
            "question": i + 1,
            "reference": q["reference"]["Brand"],
            "selected": q["a"]["Brand"],
            "other": q["b"]["Brand"]
        })
        st.session_state.brand_index += 1
        st.rerun()

    if col2b.button(f"Select {q['b']['Brand']}", key=f"b_{i}"):
        st.session_state.brand_responses.append({
            "question": i + 1,
            "reference": q["reference"]["Brand"],
            "selected": q["b"]["Brand"],
            "other": q["a"]["Brand"]
        })
        st.session_state.brand_index += 1
        st.rerun()

    return False

