# Advanced AI Text Detector & Humanizer

This Streamlit web application detects AI-generated content in text and humanizes it by rewriting for natural, human-like style. It uses an advanced set of 50+ linguistic, structural, and grammatical markers with Bayesian probability scoring and confidence estimates.

## Features

![Preview](prev.png)

- Detects over 35 AI-associated words and phrases including formal patterns and repetitive syntax.
- Analyzes sentence burstiness, lexical diversity, passive voice, contractions, and repetition.
- Calculates AI probability with human-readable scoring (0-30% likely human, 70-100% likely AI).
- Shows top contributing AI markers influencing the detection score.
- Humanizes input text using sentence variation, contractions, idiomatic replacements, and natural transitions.
- User-selectable humanization strength: Light, Medium, Strong.
- Real-time before and after AI probability comparison.
- Clean, intuitive UI with detailed marker analysis.

## Installation

```bash
pip install streamlit nltk numpy pandas textstat
```
## Usage

Run the app locally via:

```bash
streamlit run app.py
```

1. Paste or type your text in the input area.
2. Click **Analyze** to get AI detection results with detailed marker breakdown.
3. Use the **Humanize Text** button to rewrite the text to sound more natural.
4. Adjust humanization strength via the sidebar.

## How It Works

The detection module scans the text for AI markers such as overused AI jargon, passive voice, uniform sentence lengths, and low lexical diversity. It calculates a probabilistic AI score with confidence level based on weighted marker contributions.

The humanizer rewrites text by varying sentence lengths, adding conversational contractions, replacing AI-favored words with natural equivalents, and inserting natural-sounding transitions and rhetorical devices.

## Example AI Markers

- Overused words: "delve", "tapestry", "realm", "pivotal"
- Common phrases: "it is important to note", "delve into", "navigating the"
- Structural signs: low burstiness (sentence length variation), high passive voice
- Grammatical points: absence of contractions, formal tone

## Notes

- This tool is for educational and editorial purposes; detection results are probabilistic, not definitive.
- Complex, heavily human-edited AI text may evade detection.
- Humanized output aims for natural flow and plausibility, not exact content rewriting.


## Acknowledgments


Built with Streamlit, NLTK, Textstat, and inspired by state-of-the-art AI text detection research.
