import streamlit as st
import pandas as pd
import random

CLOUDFRONT_PREFIX = "https://d2uc42tkny8gik.cloudfront.net/instagram/post_images/"

@st.cache_data
def load_influencer_data():
    df = pd.read_csv("resampled_posts_with_captions.csv")
    df['Followers'] = pd.to_numeric(df['Followers'], errors='coerce')
    df.dropna(subset=['influencer_name', 'Category', 'Followers', 'caption'], inplace=True)
    df["Image_file_name"] = df["Image_file_name"].str.strip("'").str.strip('"')
    return df

df = load_influencer_data()

def get_post_display(row):
    image_url = f"{CLOUDFRONT_PREFIX}{row['Image_file_name']}"
    caption = row["caption"]
    return image_url, caption

def get_influencer_info(name):
    rows = df[df["influencer_name"] == name]
    if rows.empty:
        return None
    return {
        "name": name,
        "followers": int(rows.iloc[0]["Followers"]),
        "category": rows.iloc[0]["Category"],
        "posts": rows.sample(n=min(3, len(rows)))
    }

def generate_questions():
    categories = df['Category'].unique()
    questions = []
    for _ in range(20):
        cat = random.choice(categories)
        same_cat = df[df['Category'] == cat]['influencer_name'].unique()
        if len(same_cat) < 2: continue
        ref, a = random.sample(list(same_cat), 2)
        b = random.choice(df['influencer_name'].unique())
        while b in [ref, a]:
            b = random.choice(df['influencer_name'].unique())
        questions.append((ref, a, b))
    for _ in range(10):
        chosen_cats = random.sample(list(categories), 3)
        selected = []
        for cat in chosen_cats:
            candidates = df[df['Category'] == cat]['influencer_name'].unique()
            if len(candidates) == 0: break
            selected.append(random.choice(candidates))
        if len(selected) == 3:
            questions.append(tuple(selected))
    return questions

def run_influencer_survey():
    if "influencer_questions" not in st.session_state:
        st.session_state.influencer_questions = generate_questions()
        st.session_state.influencer_index = 0
        st.session_state.influencer_responses = []

    i = st.session_state.influencer_index
    if i >= len(st.session_state.influencer_questions):
        return True

    q = st.session_state.influencer_questions[i]
    ref_info = get_influencer_info(q[0])
    a_info = get_influencer_info(q[1])
    b_info = get_influencer_info(q[2])

    if not all([ref_info, a_info, b_info]):
        st.session_state.influencer_index += 1
        st.rerun()

    # Centered title and progress indicator
    st.markdown(f"""
        <div style='text-align:center;'>
            <h3>Influencer Question {i + 1} of 30</h3>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr style='margin-top:0; margin-bottom:20px;'>", unsafe_allow_html=True)

    # Reference Block with shaded background (no category)
    st.markdown(f"""
        <div style='text-align:center; margin-bottom: 16px; max-width: 85%; 
                    margin-left:auto; margin-right:auto; padding: 16px;
                    background-color: rgba(235, 235, 235, 0.7);
                    border-radius: 8px;'>
            <h4 style='margin-bottom:8px;'>Reference: @{ref_info['name']}</h4>
            <p style='color:#555; margin-top:0;'>{ref_info['followers']:,} followers</p>
        </div>
    """, unsafe_allow_html=True)

    # Reference images
    ref_cols = st.columns(3)
    for idx, (_, row) in enumerate(ref_info["posts"].iterrows()):
        with ref_cols[idx]:
            image_url, caption = get_post_display(row)
            st.markdown(f'''
                <div style='height: 230px; display: flex; flex-direction: column; 
                            align-items: center; justify-content: space-between;'>
                    <img src="{image_url}" style="max-height: 160px; max-width: 100%; 
                              border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />
                    <p style="font-size: 12px; margin-top: 8px; text-align: center; 
                              color: #444; overflow-wrap: break-word; line-height: 1.3;">{caption[:250]}</p>
                </div>
            ''', unsafe_allow_html=True)

    st.markdown("<hr style='margin:20px 0;'>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align:center; margin-bottom:20px;'>Which influencer is more similar to @{ref_info['name']}?</h4>", unsafe_allow_html=True)

    # Comparison options
    col1, col2 = st.columns(2)
    for col, key, info in zip([col1, col2], ['a', 'b'], [a_info, b_info]):
        with col:
            # Option container (no category shown)
            st.markdown(f"""
                <div style='padding: 16px; margin-bottom: 12px; 
                            background-color: rgba(235, 235, 235, 0.7);
                            border-radius: 8px;
                            text-align: center;'>
                    <div style='margin-bottom: 12px;'>
                        <strong style='font-size: 16px;'>@{info['name']}</strong><br/>
                        <p style='color:#555; margin-top:0; margin-bottom:0;'>{info['followers']:,} followers</p>
                    </div>
            """, unsafe_allow_html=True)

            # Images grid
            cols = st.columns(3)
            for idx, (_, row) in enumerate(info["posts"].iterrows()):
                with cols[idx]:
                    image_url, caption = get_post_display(row)
                    st.markdown(f'''
                        <div style='height: auto; display: flex; flex-direction: column; 
                                    align-items: center; justify-content: flex-start;
                                    margin-bottom: 12px;'>
                            <img src="{image_url}" style="max-height: 160px; max-width: 100%; 
                                      border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />
                            <p style="font-size: 12px; margin-top: 8px; text-align: center; 
                                      color: #444; overflow-wrap: break-word; line-height: 1.3;">{caption[:250]}</p>
                        </div>
                    ''', unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
            
            # Centered selection button
            st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
            if st.button(f"Select @{info['name']}", 
                        key=f"{key}_{i}",
                        use_container_width=True,
                        type="secondary"):
                st.session_state.influencer_responses.append({
                    "question": i + 1,
                    "reference": ref_info["name"],
                    "selected": info["name"],
                    "other": a_info["name"] if key == "b" else b_info["name"]
                })
                st.session_state.influencer_index += 1
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    return False
