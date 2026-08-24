import streamlit as st

from prompts import build_prompt
from ai_service import generate_adapted_lesson
from scoring import MODES, calculate_score, compare_scores, compare_multiple_scores

st.set_page_config(
    page_title="AdaptEd",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Styling

st.markdown(
    """
    <style>

        /* Main page */

        .stApp {
            background-color: var(--st-background-color);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2.2rem;
            padding-bottom: 3rem;
        }


        /* Main font */

        html, body, [class*="css"] {
            font-family: "Avenir Next", "Helvetica Neue", Arial, sans-serif;
            font-style: normal;
            color: var(--st-text-color);
        }


        /* Headings */

        h1 {
            font-family: "Avenir Next", "Helvetica Neue", Arial, sans-serif;
            font-weight: 700;
            letter-spacing: -0.04em;
            color: var(--st-text-color);
        }

        h2, h3 {
            font-family: "Helvetica Neue", Arial, sans-serif;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: var(--st-text-color);
        }


        /* Small captions */

        div[data-testid="stCaptionContainer"],
        div[data-testid="stCaptionContainer"] * {
            color: var(--st-text-color) !important;
            opacity: 0.65;
            font-size: 0.88rem !important;
        }


        /* Homepage hero section */

        .hero {
            padding: 4rem 2rem 1.5rem 2rem;
            text-align: center;
            border-radius: 24px;
            margin-bottom: 2rem;
        }

        .eyebrow {
            font-size: 0.9rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--st-primary-color);
            margin-bottom: 0.5rem;
        }

        .hero-title {
            font-family: "Avenir Next", "Helvetica Neue", Arial, sans-serif;
            font-size: clamp(2.7rem, 6vw, 5rem);
            line-height: 1.02;
            font-weight: 700;
            letter-spacing: -0.04em;
            color: var(--st-text-color);
            margin-bottom: 1rem;
        }

        .hero-copy {
            max-width: 720px;
            margin: 0 auto 0.5rem auto;
            text-align: center;
            font-size: 1.12rem;
            line-height: 1.7;
            color: var(--st-text-color);
            opacity: 0.7;
        }


        /* Small labels */

        .mini-label {
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--st-text-color);
            opacity: 0.65;
            margin-bottom: 0.75rem;
        }


        /* Accessibility scores */

        .score {
            font-size: 3.2rem;
            font-weight: 700;
            line-height: 1;
            color: var(--st-text-color);
            margin: 0.2rem 0 0.6rem 0;
        }

        .muted {
            color: var(--st-text-color);
            opacity: 0.65;
        }


        /* Buttons */

        div.stButton > button {
            border-radius: 12px;
            min-height: 3rem;
            font-weight: 600;
        }

        div.stButton > button[kind="primary"] {
            background-color: #3B5CCC !important;
            color: #FFFFFF !important;
            border: none !important;
        }

        div.stButton > button[kind="primary"]:hover {
            background-color: #304BA8 !important;
            color: #FFFFFF !important;
            border: none !important;
        }


        /* Homepage feature captions */

        .feature-caption {
            font-style: italic;
            color: var(--st-text-color);
            opacity: 0.68;
            font-size: 0.95rem;
            line-height: 1.55;
            margin-bottom: 0;
        }


        /* Cards */

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 16px;
            background-color: var(--st-secondary-background-color);
            border-color: var(--st-border-color);
        }

    </style>
    """,
    unsafe_allow_html=True,
)

# State
if "page" not in st.session_state:
    st.session_state.page = "home"

if "lesson_text" not in st.session_state:
    st.session_state.lesson_text = ""

if "profile" not in st.session_state:
    st.session_state.profile = {}


def go(page_name):
    st.session_state.page = page_name
    st.rerun()


# MOCK BACKEND (replace later)
def mock_analysis():
    """Replace later with Person 2/3 backend functions."""
    return [
        {
            "title": "Dense instructions",
            "detail": "Long blocks of information may be difficult for some learners to process.",
        },
        {
            "title": "Advanced vocabulary",
            "detail": "Several terms may need simpler explanations or vocabulary support.",
        },
        {
            "title": "Connectivity dependency",
            "detail": "The lesson includes activities that may require reliable internet access.",
        },
        {
            "title": "Visual-only information",
            "detail": "Important meaning may depend on a diagram or visual without a text alternative.",
        },
    ]


def mock_adapted_lesson():
    return """
### Topic: The Water Cycle

#### Key idea
Water continuously moves between Earth's surface and the atmosphere.

#### Step 1 — Evaporation
Heat from the sun changes liquid water into water vapour.

**Important word:** *Evaporation* — when liquid water becomes a gas.

#### Step 2 — Condensation
Water vapour cools and forms tiny droplets. These droplets can form clouds.

#### Step 3 — Precipitation
Water falls from clouds as rain, snow, sleet, or hail.

#### Check your understanding
**Where does the energy for evaporation come from?**

*Hint: Think about what heats the Earth's surface.*
"""


def mock_teacher_guide():
    profile = st.session_state.profile
    internet = profile.get("internet", "Limited")
    devices = profile.get("devices", 0)
    printer = profile.get("printer", False)

    suggestions = [
        "Read the key idea aloud before students begin.",
        "Teach the three stages one at a time instead of presenting all instructions at once.",
        "Keep scientific vocabulary, but explain each term in plain language.",
    ]

    if internet in ["Limited", "None"]:
        suggestions.append("Use an offline activity instead of requiring students to stream a video.")

    if devices < 5:
        suggestions.append("Use pairs or small groups rather than one-device-per-student activities.")

    if printer:
        suggestions.append("Provide a print-friendly worksheet for students who benefit from a physical copy.")

    return suggestions


# Page 1 — Home page
if st.session_state.page == "home":
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">Make learning accessible to everyone</div>
            <div class="hero-title">One lesson.<br>For all learners.</div>
            <div class="hero-copy">
                Adapt existing teaching materials to your learners' needs and
                the resources your classroom actually has.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, middle, right = st.columns([1.25, 1, 1.25])
    with middle:
        if st.button("Adapt your lesson →", type="primary", use_container_width=True):
            go("setup")

    st.write("")

    c1, c2, c3 = st.columns(3)

    with c1:
        with st.container(border=True, height = 150):
            st.subheader("🧠 Learner needs")
            st.markdown(
                """
                <p class="feature-caption">
                    Support different levels of focus, literacy,
                    language, and visual accessibility.
                </p>
                """,
                unsafe_allow_html=True,
            )

    with c2:
        with st.container(border=True, height = 150):
            st.subheader("🏫 Classroom reality")
            st.markdown(
                """
                <p class="feature-caption">
                    Consider internet access, devices, printers,
                    class size, and other practical constraints.
                </p>
                """,
                unsafe_allow_html=True,
            )

    with c3:
        with st.container(border=True, height = 150):
            st.subheader("⚡ Less preparation")
            st.markdown(
                """
                <p class="feature-caption">
                    Turn one lesson into practical alternatives
                    without rewriting everything manually.
                </p>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    with st.container(border=True, height = 200):
        st.subheader("Accessibility is not one-size-fits-all")
        st.markdown(
                """
                <p class="feature-caption">
                    Learners may often face several barriers simultaneously, compromising 
                    their ability to learn, study, and refine themselves.
                    AdaptEd is therefore designed around overlapping support and the
                    classroom reality individuals are learning in, where we aim to provide all
                    educators with the opportunity to study and to become the best of themselves.
                </p>
                """,
                unsafe_allow_html=True,
            )

# Page 2 — Lesson Setup
elif st.session_state.page == "setup":
    top_left, top_right = st.columns([5, 1])
    with top_left:
        st.title("Adapt a lesson")
        st.caption("Tell AdaptEd about the material, classroom, and learner support needs.")
    with top_right:
        if st.button("← Home", use_container_width=True):
            go("home")

    st.divider()

    left, right = st.columns([1.35, 1], gap="large")

    with left:
        st.subheader("1. Your lesson")
        with st.container(border=True, height = 500):
            # uploaded = st.file_uploader(
            #     "Upload a lesson",
            #     type=["pdf", "txt"],
            #     help="Upload your lesson here for analysis and simplification.",
            # )

            lesson = st.text_area(
                "Paste lesson content",
                value=st.session_state.lesson_text,
                height=350,
                placeholder=(
                    "Paste your worksheet, lesson instructions, activity, "
                    "or teaching notes here..."
                ),
            )

            st.session_state.lesson_text = lesson

    with right:
        st.subheader("2. Classroom resources")
        with st.container(border=True, height = 500):
            internet = st.selectbox(
                "Internet access",
                ["Reliable", "Limited", "None"],
                index=1,
            )

            class_size = st.number_input(
                "Class size (Max 500)",
                min_value=1,
                max_value=500,
                value=30,
            )

            devices = st.number_input(
                "Number of student devices (Max 500)",
                min_value=0,
                max_value=500,
                value=4,
            )

            printer = st.toggle("Printer available", value=True)
            projector = st.toggle("Projector available", value=False)

            headphones = st.selectbox(
                "Headphones",
                ["None", "Some", "Enough for everyone"],
            )

    st.write("")
    st.subheader("3. Learner support needs")
    st.caption("Please select all that apply.")

    target_modifications = st.multiselect(
        "How would you like to adapt this lesson?",
        MODES,
        default=st.session_state.get(
            "target_modifications",
            []
        ),
        placeholder="Select one or more options",
    )

    st.session_state.target_modifications = target_modifications

    focus = "Reduce cognitive load" in target_modifications
    language = "Simplify language" in target_modifications
    audio = "Audio accessibility" in target_modifications
    visual = "Improve visual accessibility" in target_modifications

    st.write("")

    button_left, button_mid, button_right = st.columns([1, 1.2, 1])

    with button_mid:
        analyse_clicked = st.button(
            "Analyse my lesson →",
            type="primary",
            use_container_width=True,
        )

    if analyse_clicked:
        if not lesson.strip():
            st.error("Please paste lesson content above.")
    
        elif not target_modifications:
            st.error("Please select at least one learner support need.")

        else:
            st.session_state.profile = {
                "internet": internet,
                "class_size": class_size,
                "devices": devices,
                "printer": printer,
                "projector": projector,
                "headphones": headphones,
                "focus": focus,
                "language": language,
                "audio": audio,
                "visual": visual,
            }
            go("analysis")


# Page 3 — Analysis
elif st.session_state.page == "analysis":
    top_left, top_right = st.columns([5, 1])
    with top_left:
        st.title("Accessibility analysis")
        st.caption("Mock results for your UI prototype — connect the real analysis later.")
    with top_right:
        if st.button("← Edit", use_container_width=True):
            go("setup")

    st.divider()

    score_col, summary_col = st.columns([1, 2], gap="large")

    with score_col:
        with st.container(border=True):
            st.markdown('<div class="mini-label">Accessibility score</div>', unsafe_allow_html=True)
            st.markdown('<div class="score">58 / 100</div>', unsafe_allow_html=True)
            st.progress(58)
            st.caption("Prototype score — your backend can calculate this later.")

    with summary_col:
        with st.container(border=True):
            st.subheader("Classroom snapshot")
            p = st.session_state.profile
            a, b, c = st.columns(3)
            a.metric("Students", p.get("class_size", 30))
            b.metric("Devices", p.get("devices", 4))
            c.metric("Internet", p.get("internet", "Limited"))

            selected = [
                label
                for key, label in [
                    ("focus", "Cognitive Load"),
                    ("language", "Language"),
                    ("audio", "Audio"),
                    ("visual", "Visual"),
                ]
                if p.get(key)
            ]

            if selected:
                st.write("**Selected support:** " + " • ".join(selected))
            else:
                st.write("**Selected support:** General accessibility")

    st.write("")
    st.subheader("Potential barriers")

    issues = mock_analysis()

    for i in range(0, len(issues), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(issues):
                with col:
                    with st.container(border=True, height = 150):
                        st.markdown(f"### ⚠️ {issues[idx]['title']}")
                        st.write(issues[idx]["detail"])

    # st.write("")
    # st.subheader("Classroom-aware recommendations")

    # r1, r2 = st.columns(2)
    # with r1:
    #     with st.container(border=True):
    #         st.markdown("### ✅ Adapt the material")
    #         st.write(
    #             "Break instructions into smaller steps, explain difficult vocabulary, "
    #             "and create a print-friendly version."
    #         )

    # with r2:
    #     with st.container(border=True):
    #         st.markdown("### 🧩 Resource-aware adjustment")
    #         p = st.session_state.profile
    #         if p.get("devices", 0) < 5:
    #             st.write(
    #                 "There are too few devices for individual digital activities. "
    #                 "Prefer paired/group work and printable resources."
    #             )
    #         elif p.get("internet") in ["Limited", "None"]:
    #             st.write(
    #                 "Avoid activities that depend on streaming or constant internet access."
    #             )
    #         else:
    #             st.write(
    #                 "Digital activities are feasible, but provide a printable alternative where possible."
    #             )

    st.write("")
    c1, c2, c3 = st.columns([1, 1.2, 1])
    
    with c2:
        if st.button(
            "Generate accessible version →",
            type="primary",
            use_container_width=True,
        ):
            try:
                with st.spinner("Adapting your lesson..."):
                    prompt = build_prompt(
                        st.session_state.lesson_text,
                        st.session_state.target_modifications
                    )
    
                    result = generate_adapted_lesson(prompt)
    
                    score_result = compare_multiple_scores(
                        st.session_state.lesson_text,
                        result,
                        st.session_state.target_modifications
                    )
    
                    st.session_state.adapted_result = result
                    st.session_state.score_result = score_result
    
                go("result")
    
            except Exception as error:
                st.error(
                    "We couldn't generate the accessible version. "
                    "Please try again."
                )
                st.caption(f"Technical details: {error}")

# Page 4 - Result
elif st.session_state.page == "result":
    top_left, top_right = st.columns([5, 1])
    with top_left:
        st.title("Your adapted lesson")
        st.caption("A classroom-ready version generated around the selected needs and constraints.")
    with top_right:
        if st.button("← Analysis", use_container_width=True):
            go("analysis")

    st.divider()
    # if "adapted_result" in st.session_state:
    #     st.markdown(st.session_state.adapted_result)

    full_result = st.session_state.adapted_result

    score_result = st.session_state.get(
        "score_result",
        {
            "before": 0,
            "after": 0,
            "improvement": 0
        }
    )

    before = score_result["before"]
    after = score_result["after"]
    improvement = score_result["improvement"]

    st.subheader("Accessibility improvement")

    score_col1, score_col2, score_col3 = st.columns(3)

    with score_col1:
        st.metric(
            "Before",
            f"{before}/100"
        )

    with score_col2:
        st.metric(
            "After",
            f"{after}/100",
            f"+{improvement}"
        )

    with score_col3:
        st.metric(
            "Improvement",
            f"{improvement} points"
        )

    st.progress(after)

    if "## Accessibility Notes" in full_result:
        adapted_lesson, accessibility_notes = full_result.split(
            "## Accessibility Notes",
        1
    )
    else:
        adapted_lesson = full_result
        accessibility_notes = "No additional accessibility notes."


    accessible_tab, guide_tab, original_tab = st.tabs(
        ["Accessible version", "Teacher guide", "Original"]
    )

    with accessible_tab:
        with st.container(border=True):
            st.markdown(adapted_lesson)

        st.download_button(
            "Download printable version",
            data=adapted_lesson,
            file_name="adapted_lesson.txt",
            mime="text/plain",
            use_container_width=False,
        )

    with guide_tab:
        with st.container(border=True):
            st.markdown("## Accessibility Notes")
            st.markdown(accessibility_notes)
        

        st.subheader("Suggested classroom delivery")
        for item in mock_teacher_guide():
            st.write(f"✓ {item}")

    with original_tab:
        with st.container(border=True):
            if st.session_state.lesson_text.strip():
                st.write(st.session_state.lesson_text)
            else:
                st.info("Uploaded-file text extraction will be connected later.")

    st.write("")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("Start another lesson", use_container_width=True):
            st.session_state.lesson_text = ""
            st.session_state.profile = {}
            st.session_state.target_modifications = []
            st.session_state.pop("adapted_result", None)
            st.session_state.pop("score_result", None)
            go("setup")
