## Hack Melbourne 2026
## Project Name: AdaptED

# What it does
AdaptED is an AI-powered educational accessibility tool designed to help teachers adapt their existed lecture notes for different learning needs.

Instead of creating multiple versions of the same lesson, teachers can select an accessibility mode and AdaptED automatically modifies their notes using AI.

AdaptED currently supports four accessibility modes:
- Simplify Language
- Reduce Cognitive Load
- Improve Visual Accessibility
- Add Audio-Friendly Alternatives

After the notes are adapted, AdaptED evaluates the accessibility of the original and adapted versions using a rule-based scoring system, allowing teachers to see the improvement.

# Features
## 1. Lecture note adaptation
Teachers can enter or upload their existing lecture notes and choose how they want the material to be adapted.

## 2. Simplify language
Makes educational content easier to understand by:
- replace unnecessarily difficult wording with simpler language
- explain difficult terminology
- shorter and clearer sentences

## 3. Reduce cognitive load
Makes complex information easier to process by:
- one main idea at a time
- break complex instructions into clear steps
- make information into smaller sections
- headings and bullet points

## 4. Improve visual accessibility
Improves the structure and accessibility of written content by:
- descriptions for important images or diagrams
- no reliance on colour alone
- clear headings and lists
- a logical reading order

## 5. Add audio-friendly alternatives
Makes written material easier to follow when listened to by:
- shorter, natural sentences
- clear transitions between ideas
- explain technical terminology

## 6. Accessibility Scoring
AdaptED uses a transparent, rule-based scoring system to evaluate how well the notes follow the selected accessibility principles.

# How it works
Teacher --> Enter lecture notes --> Select accessibility mode (simplify language, reduce cognitive load, improve visual accessibility, add audio-friendly alternatives) --> AI adaptation --> Adapted lecture notes --> Accessibility scoring --> Before and after score
                 
# Tech Stack
Frontend: Streamlit
Backend: Python
AI: OpenAI API
Scoring: Python-based rule system

# Team
- Alice Sun (Frontend & UI)
- Elena Yu (AI Integration & Prompt)
- Yilia Sun (Accessibility Scoring & Evaluation）
