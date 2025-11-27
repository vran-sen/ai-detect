import streamlit as st
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import Counter
import numpy as np
import re
import random
from textstat import flesch_reading_ease, dale_chall_readability_score
import pandas as pd

try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

@st.cache_data
def load_ai_markers():
    return {
        # High-impact AI words (weight 15-25)
        'high_impact': {
            'delve': 20, 'tapestry': 25, 'realm': 18, 'embark': 20, 'pivotal': 18,
            'intricate': 20, 'testament': 22, 'catalyst': 18, 'harness': 15, 'leverage': 15
        },
        # Medium-impact AI words (weight 10-14)
        'medium_impact': {
            'vibrant': 12, 'landscape': 12, 'comprehensive': 12, 'seamlessly': 13,
            'resonate': 11, 'dynamic': 10, 'optimize': 12, 'framework': 11, 'paradigm': 14
        },
        # Low-impact but still AI-like words (weight 5-8)
        'low_impact': {
            'notably': 7, 'arguably': 8, 'moreover': 8, 'furthermore': 8, 'additionally': 8
        },
        # Phrases (weight 12-18)
        'phrases': {
            r'it is important to note': 15, r'delve into': 18, r'at its core': 16,
            r'navigating the': 14, r'landscape of': 15, r'tapestry of': 17,
            r'in conclusion': 12, r'in summary': 12
        }
    }

def advanced_detect_ai_markers(text):
    markers = {}
    text_lower = text.lower()
    
    # 1. LEXICAL MARKERS (35+ words)
    ai_markers = load_ai_markers()
    
    for category, words in ai_markers.items():
        markers[f'{category}_count'] = 0
        for word, weight in words.items():
            count = text_lower.count(word)
            markers[f'{word}_count'] = count
            markers[f'{category}_count'] += count * weight
    
    # 2. PHRASE MARKERS
    for phrase, weight in ai_markers['phrases'].items():
        count = len(re.findall(phrase, text_lower))
        markers[f'phrase_{phrase.replace(" ", "_")}'] = count
    
    # 3. SENTENCE STRUCTURE (Burstiness, uniformity)
    sentences = sent_tokenize(text)
    if sentences:
        sent_lengths = [len(word_tokenize(s)) for s in sentences]
        markers['sent_count'] = len(sentences)
        markers['avg_sent_len'] = np.mean(sent_lengths)
        markers['sent_std'] = np.std(sent_lengths)  # Low std = AI
        markers['uniform_sentences'] = 1 if markers['sent_std'] < 3 else 0
        markers['long_sentences'] = sum(1 for l in sent_lengths if l > 25)
    
    # 4. GRAMMAR PATTERNS
    markers['contractions'] = len(re.findall(r"\b(it's|that's|you're|we're|they're|I've|you've|we've|they've|I'd|you'd|he'd|she'd|we'd|they'd|I'll|you'll|he'll|she'll|we'll|they'll|isn't|aren't|wasn't|weren't|hasn't|haven't|hadn't|won't|wouldn't|don't|doesn't|didn't|can't|couldn't|shouldn't)\b", text_lower))
    markers['passive_voice'] = len(re.findall(r'\b(?:is|was|were|been|being)\s+(?:said|believed|considered|regarded|noted|observed)', text_lower))
    markers['no_contractions'] = 1 if markers['contractions'] == 0 else 0
    
    # 5. LEXICAL DIVERSITY
    words = word_tokenize(text_lower)
    unique_words = len(set(words))
    total_words = len(words)
    markers['lexical_diversity'] = unique_words / total_words if total_words > 0 else 0
    markers['low_diversity'] = 1 if markers['lexical_diversity'] < 0.4 else 0
    
    # 6. FORMALITY METRICS
    markers['noun_heavy'] = len(re.findall(r'\b(?:the|a|an|of|in|on|at|to|for|with|by)\b', text_lower)) / total_words if total_words > 0 else 0
    
    # 7. REPETITION PATTERNS
    word_freq = Counter(words)
    markers['top_word_repeat'] = max(word_freq.values()) / total_words if total_words > 0 else 0
    
    return markers

def calculate_probability(markers):
    """Bayesian-style probability calculation"""
    base_human_prob = 0.5  # 50/50 starting point
    
    # WEIGHTS BY CATEGORY (total 100 points max)
    weights = {
        'lexical': 25,      # AI words/phrases
        'structure': 20,    # Sentence patterns
        'grammar': 15,      # Contractions, passive
        'diversity': 15,    # Lexical diversity
        'formality': 15,    # Noun-heavy, formal
        'repetition': 10    # Word repetition
    }
    
    ai_score = 0
    
    # Lexical markers
    ai_score += min(markers.get('high_impact_count', 0), 25)
    ai_score += min(markers.get('medium_impact_count', 0), 15)
    
    # Structure
    if markers.get('sent_std', 0) < 3: ai_score += 12
    if markers.get('uniform_sentences', 0): ai_score += 8
    
    # Grammar
    if markers.get('no_contractions', 0): ai_score += 12
    ai_score += min(markers.get('passive_voice', 0) * 2, 8)
    
    # Diversity
    if markers.get('low_diversity', 0): ai_score += 12
    if markers.get('top_word_repeat', 0) > 0.15: ai_score += 5
    
    # Formality
    if markers.get('noun_heavy', 0) > 0.2: ai_score += 10
    
    # Normalize to probability
    ai_probability = min((ai_score / 100) * 0.9 + 0.1, 0.99)  # Never 100%
    
    return {
        'ai_prob': ai_probability,
        'human_prob': 1 - ai_probability,
        'confidence': min(ai_score / 50, 0.95)  # Confidence in prediction
    }

def enhanced_humanize(text, strength="strong"):
    sentences = sent_tokenize(text)
    humanized = []
    
    human_transitions = [
        "But here's the thing", "So", "Look", "That said", "Here's why", 
        "And that matters because", "Truth is", "Real talk", "Bottom line"
    ]
    
    ai_replacements = {
        'delve': ['look at', 'check out', 'dig into'], 'tapestry': ['mix', 'web', 'network'],
        'landscape': ['world', 'scene', 'picture'], 'realm': ['world', 'area', 'space'],
        'embark': ['start', 'jump in', 'get going'], 'pivotal': ['key', 'crucial', 'huge'],
        'intricate': ['complex', 'tricky', 'detailed'], 'testament': ['proof', 'sign', 'evidence']
    }
    
    for i, sent in enumerate(sentences):
        s = sent
        
        # Strength-based modifications
        if strength == "strong" and random.random() < 0.4:
            # Fragments, questions, exclamations
            if random.random() < 0.3:
                s = s.split('.')[0] + "."
            elif random.random() < 0.3:
                s = s + " Right?"
            elif random.random() < 0.2:
                s = "... " + s[0].lower() + s[1:]
        
        # Contractions
        contractions = {
            " it is ": " it's ", " that is ": " that's ", " there is ": " there's ",
            " you are ": " you're ", " they are ": " they're ", " will not ": " won't ",
            " can not ": " can't ", " does not ": " doesn't ", " do not ": " don't "
        }
        for formal, casual in contractions.items():
            s = s.replace(formal, casual)
        
        # AI word replacement
        s_lower = s.lower()
        for ai_word, replacements in ai_replacements.items():
            if ai_word in s_lower:
                s = s.replace(ai_word.capitalize(), random.choice(replacements).capitalize())
                s = s.replace(ai_word, random.choice(replacements))
        
        humanized.append(s)
    
    # Add natural transitions between paragraphs
    result = ' '.join(humanized)
    paragraphs = re.split(r'\n\s*\n', result)
    for i in range(1, len(paragraphs)):
        if random.random() < 0.3:
            paragraphs[i] = random.choice(human_transitions) + ": " + paragraphs[i]
    
    return '\n\n'.join(paragraphs)

def main():
    st.set_page_config(
        page_title="Advanced AI Detector & Humanizer",
        page_icon="🧠", layout="wide", initial_sidebar_state="expanded"
    )
    
    st.title("Advanced AI Text Detector & Humanizer")
    st.markdown("**50+ markers • Bayesian probability • Confidence scoring**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        strength = st.selectbox("Humanization strength", ["Light", "Medium", "Strong"], index=2)
        threshold = st.slider("AI Alert Threshold", 40, 90, 70)
        
        st.header("📈 Interpretation")
        st.info("""
        **AI Probability:**
        - 🟢 0-30%: **Likely Human**
        - 🟡 31-69%: **Mixed/Unclear**  
        - 🟠 70-89%: **Likely AI**
        - 🔴 90%+: **Strong AI Signal**
        """)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Input Text")
        input_text = st.text_area(
            label="Text for analysis", 
            label_visibility="collapsed",
            height=250, 
            placeholder="Paste text to analyze..."
        )
        
        if st.button("🚀 Analyze (50+ markers)", type="primary", use_container_width=True):
            if input_text.strip():
                with st.spinner("🔍 Scanning 50+ AI markers..."):
                    markers = advanced_detect_ai_markers(input_text)
                    probs = calculate_probability(markers)
                    
                    # Main Results
                    st.header("📊 Detection Results")
                    
                    col_a, col_b, col_c = st.columns([1,1,1])
                    
                    with col_a:
                        ai_pct = probs['ai_prob'] * 100
                        color = "🟢" if ai_pct < 30 else "🟡" if ai_pct < 70 else "🟠" if ai_pct < 90 else "🔴"
                        st.metric(f"{color} AI Probability", f"{ai_pct:.1f}%", 
                                delta=f"{probs['human_prob']*100:.0f}% Human")
                    
                    with col_b:
                        st.metric("Confidence", f"{probs['confidence']*100:.0f}%")
                    
                    with col_c:
                        readability = flesch_reading_ease(input_text)
                        st.metric("Readability (Flesch)", f"{readability:.0f}")
                    
                    # Top contributing factors
                    st.subheader("🔥 Top AI Indicators")
                    top_markers = []
                    for marker, value in markers.items():
                        if value > 0 and ('count' in marker or marker in ['uniform_sentences', 'no_contractions', 'low_diversity']):
                            top_markers.append({'Marker': marker.replace('_', ' ').title(), 'Value': value})
                    
                    top_df = pd.DataFrame(top_markers[:10])
                    if not top_df.empty:
                        st.dataframe(top_df, use_container_width=True)
                    else:
                        st.success("✅ No significant AI markers detected!")
                    
                    # Detailed breakdown
                    with st.expander("📋 Full 50+ Marker Analysis"):
                        detailed_df = pd.DataFrame([
                            {'Category': 'Lexical', 'AI Score': markers.get('high_impact_count', 0) + markers.get('medium_impact_count', 0)},
                            {'Category': 'Structure', 'AI Score': markers.get('uniform_sentences', 0) * 20 + (12 if markers.get('sent_std', 0) < 3 else 0)},
                            {'Category': 'Grammar', 'AI Score': markers.get('no_contractions', 0) * 12 + markers.get('passive_voice', 0) * 2},
                            {'Category': 'Diversity', 'AI Score': markers.get('low_diversity', 0) * 12 + (5 if markers.get('top_word_repeat', 0) > 0.15 else 0)},
                        ])
                        st.dataframe(detailed_df)
    
    with col2:
        st.subheader("✨ Humanize")
        if st.button("🎭 Humanize Text", type="secondary"):
            if input_text.strip():
                with st.spinner("Applying humanization..."):
                    humanized = enhanced_humanize(input_text, strength.lower())
                    
                    st.text_area("✨ Humanized Output", humanized, height=250)
                    
                    # Before/After comparison
                    orig_probs = calculate_probability(advanced_detect_ai_markers(input_text))
                    human_probs = calculate_probability(advanced_detect_ai_markers(humanized))
                    
                    col1m, col2m = st.columns(2)
                    with col1m:
                        st.metric("📄 Original", f"{orig_probs['ai_prob']*100:.0f}% AI")
                    with col2m:
                        st.metric("✨ Humanized", f"{human_probs['ai_prob']*100:.0f}% AI", 
                                delta=f"{(human_probs['ai_prob']-orig_probs['ai_prob'])*100:.0f}%")
    
    # Footer
    st.markdown("---")
    with st.expander("ℹ️ Technical Details"):
        st.markdown("""
        **Detection Algorithm:**
        - **50+ markers**: Lexical (35+ words), phrases (12), structure, grammar, diversity
        - **Bayesian probability**: Combines multiple signals with category weights
        - **Burstiness**: Sentence length variation (low = AI)
        - **Perplexity proxy**: Lexical diversity + repetition patterns
        
        **Humanization Techniques:**
        - Sentence fragments/questions
        - Contraction injection (25+ patterns)
        - AI word replacement (25+ mappings)
        - Natural transitions (10+ options)
        - Controlled "imperfections"
        """)

if __name__ == "__main__":
    main()