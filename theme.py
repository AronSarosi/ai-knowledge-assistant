"""Visual theme matched to aronsarosi.com and the other tools.

Warm sand base, terracotta accent, Newsreader serif headings + Inter body. This
is the REFERENCE implementation of the shared "hero formula" applied across all
four portfolio tools: eyebrow (tool name) -> H1 value prop -> one-line subhead ->
trust chips -> a framed demonstration of the real result. One modular type scale
(H1 clamp(2.5rem,5vw,3.75rem)) is used everywhere so the tools look like a family.
"""

from __future__ import annotations

import streamlit as st

BASE = "#F2ECE3"        # warm sand / page
SURFACE = "#FBF8F2"     # soft card surface
WHITE = "#FFFFFF"       # inputs
INK = "#221E19"         # headings
INK_DIM = "#5B544B"     # body
INK_MUTE = "#8A8175"    # muted captions / footer
LINE = "#E0D8CB"        # hairline
ACCENT = "#B5532E"      # terracotta
ACCENT_DEEP = "#99431F"  # terracotta hover

CARD_SHADOW = "0 1px 2px rgba(34,30,25,0.03), 0 18px 44px -34px rgba(34,30,25,0.22)"


_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600&family=Inter:wght@400;500;600&display=swap');

/* Shared modular type scale (Perfect Fourth ~1.333), used across all 4 tools. */
:root {{
  --h1: clamp(2.5rem, 5vw, 3.75rem);
  --h2: 1.5rem;
  --subhead: 1.15rem;
  --body: 1.02rem;
  --eyebrow: 0.8rem;
  --caption: 0.85rem;
}}

.stApp {{
  background-color: {BASE};
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  color: {INK_DIM};
}}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stBottom"] {{ background: {BASE}; }}
/* Match the bottom chat bar to the page content: the bottom container spans the
   full viewport, so constrain its inner block-container to the SAME max-width as
   the main column (1360px) and centre it (margin auto) so it lines up exactly
   with the content above, rather than a full-width bar. */
[data-testid="stBottom"] > div {{
  max-width: 1360px;
  margin-left: auto;
  margin-right: auto;
}}
[data-testid="stBottom"] .block-container {{
  max-width: 1360px;
  margin-left: auto;
  margin-right: auto;
}}
[data-testid="stBottom"] [data-testid="stChatInput"] {{
  max-width: 100%;
}}

.block-container {{
  max-width: 1360px;
  padding-top: 1.1rem;
  padding-bottom: 3rem;
}}

.stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
  font-family: 'Newsreader', Georgia, 'Times New Roman', serif;
  color: {INK};
  letter-spacing: -0.01em;
}}

.stApp p, .stApp li {{ color: {INK_DIM}; font-size: var(--body); }}
.stApp label, .stApp label p {{ color: {INK} !important; font-weight: 500; }}
.stApp [data-testid="stCaptionContainer"], .stApp small {{ color: {INK_MUTE} !important; }}

/* Text inputs */
.stTextInput input, .stTextArea textarea {{
  background-color: {WHITE};
  border: 1px solid {LINE} !important;
  border-radius: 10px !important;
  color: {INK};
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
  border-color: {ACCENT} !important;
  box-shadow: 0 0 0 3px rgba(181,83,46,0.16) !important;
}}

/* Chat input: ONE clean pill (no nested boxes), text vertically centred. */
[data-testid="stChatInput"] {{
  background: {WHITE};
  border: 1px solid {LINE};
  border-radius: 14px;
  box-shadow: {CARD_SHADOW};
}}
[data-testid="stChatInput"]:focus-within {{
  border-color: {ACCENT};
  box-shadow: 0 0 0 3px rgba(181,83,46,0.16);
}}
[data-testid="stChatInput"] textarea {{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: {INK};
}}
[data-testid="stChatInput"] button {{
  background: {ACCENT} !important;
  border-radius: 9px !important;
}}
[data-testid="stChatInput"] button svg {{ color: {WHITE} !important; fill: {WHITE} !important; }}

/* Buttons. */
.stButton > button, .stDownloadButton > button {{
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  border-radius: 10px;
  border: 1px solid {LINE};
  padding: 0.6rem 1.4rem;
  transition: transform .2s ease, border-color .2s ease, color .2s ease, background .2s ease, box-shadow .3s ease;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
  border-color: {ACCENT};
  color: {ACCENT};
}}
[data-testid="stBaseButton-primary"] {{
  background: {ACCENT} !important;
  border: none !important;
  color: {WHITE} !important;
  box-shadow: 0 10px 26px -10px rgba(181,83,46,0.75);
}}
[data-testid="stBaseButton-primary"]:hover {{
  background: {ACCENT_DEEP} !important;
  color: {WHITE} !important;
  transform: translateY(-2px);
}}

/* Chat bubbles as soft cards. */
[data-testid="stChatMessage"] {{
  background: {SURFACE};
  border: 1px solid {LINE};
  border-radius: 16px;
  padding: 0.4rem 1.1rem;
  box-shadow: {CARD_SHADOW};
}}

/* Citation expander. */
[data-testid="stExpander"] {{
  border: 1px solid {LINE};
  border-radius: 12px;
  background: {WHITE};
}}

[data-testid="stFileUploaderDropzone"] {{
  background: {SURFACE};
  border: 1px dashed {LINE};
  border-radius: 14px;
}}
[data-testid="stAlert"] {{ border-radius: 12px; }}
.stApp hr {{ border-color: {LINE}; }}

/* --- Hero (shared formula) --------------------------------------------- */
/* Wide enough that the H1 ("Drop your docs. Get the answers.") sits on ONE
   line at the largest clamp size; the subhead keeps its own narrower max-width. */
.hero {{ text-align: center; margin: 0.6rem auto 1.6rem; max-width: 960px; }}
.hero .kicker {{
  font-size: var(--eyebrow);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  color: {ACCENT};
}}
.hero h1 {{
  font-family: 'Newsreader', Georgia, serif;
  font-weight: 500;
  font-size: var(--h1);
  line-height: 1.07;
  letter-spacing: -0.02em;
  color: {INK};
  margin: 0.7rem 0 0;
  /* Keep the value prop on a single line on desktop. On a narrow viewport the
     clamp shrinks the type and the wider .hero gives it room, but allow a wrap
     as a last resort on very small screens so it never overflows. */
  white-space: nowrap;
}}
@media (max-width: 640px) {{
  .hero h1 {{ white-space: normal; }}
}}
.hero h1 .accent {{ color: {ACCENT}; font-style: italic; }}
.hero p {{
  color: {INK_DIM};
  font-size: var(--subhead);
  line-height: 1.6;
  max-width: 600px;
  margin: 1.1rem auto 0;
}}
.hero p b {{ color: {ACCENT_DEEP}; font-weight: 600; }}

/* Trust chips (the missing credibility cue). */
.trust {{
  display: flex; flex-wrap: wrap; justify-content: center;
  gap: 0.6rem; margin: 1.3rem auto 0; max-width: 760px;
}}
.trust .chip {{
  display: inline-flex; align-items: center; gap: 0.5rem;
  background: {WHITE}; border: 1px solid {LINE};
  border-radius: 999px; padding: 0.4rem 0.9rem;
  font-size: var(--caption); color: {INK_DIM}; font-weight: 500;
}}
.trust .chip::before {{
  content: ""; width: 7px; height: 7px; border-radius: 50%;
  background: {ACCENT}; flex: none;
}}

/* Demonstration: a three-column 'input -> prompt + arrow -> output' illustration.
   Matched to the Report Generator hero. Fixed-width blocks + one uniform gap keep
   equal space on both sides of the middle; flex-wrap keeps it responsive. */
.demo {{ max-width: 960px; margin: 2.2rem auto 0.5rem; }}
.hero-il {{
  display: flex; align-items: center; justify-content: center;
  gap: 2.6rem; flex-wrap: wrap;
}}
.hero-col {{
  flex: 0 0 auto; width: 320px;
  display: flex; flex-direction: column; align-items: center; text-align: center;
}}
.hero-cap {{
  letter-spacing: 0.1em; font-size: 0.78rem; color: {INK_MUTE};
  font-weight: 700; text-transform: uppercase; margin-bottom: 0.6rem;
}}
.hero-mid {{
  display: flex; flex-direction: column; align-items: center;
  gap: 0.8rem; flex: 0 0 auto; width: 220px;
}}
.hero-prompt {{
  background: {SURFACE}; border: 1px solid {LINE}; border-radius: 11px;
  padding: 0.65rem 0.85rem; font-size: 0.95rem; color: {INK_DIM};
  text-align: left; line-height: 1.45;
}}
.straight-arrow {{ line-height: 0; }}

/* Stack of two overlapping document cards (PDF / Word). */
.stack {{ position: relative; width: 300px; height: 210px; margin: 0 auto; }}
.filecard {{
  position: absolute; left: 50%; top: 6px; width: 284px;
  background: {WHITE}; border: 1px solid {LINE}; border-radius: 9px;
  box-shadow: 0 10px 26px rgba(34,30,25,.16);
  padding: 0.6rem 0.7rem 0.55rem;
}}
.filecard.back {{ transform: translate(-64%, 32px) rotate(-5deg); }}
.filecard.front {{ transform: translate(-50%, 0); }}
.fc-tag {{
  display: inline-block; font-size: 0.82rem; font-weight: 700; color: {WHITE};
  border-radius: 3px; padding: 0.08rem 0.5rem; margin-bottom: 0.5rem;
}}
.tag-pdf {{ background: {ACCENT}; }}
.tag-doc {{ background: {INK}; }}
.fc-lines {{ display: flex; flex-direction: column; gap: 0.45rem; }}
.fc-lines .ln {{
  font-size: 0.8rem; line-height: 1.35; color: {INK_DIM}; text-align: left;
}}
.fc-lines .ln b {{ color: {INK}; font-weight: 600; }}

/* Result thumbnail (the cited answer). */
.report-thumb {{
  width: 300px; margin: 0 auto; background: {WHITE}; border: 1px solid {LINE};
  border-radius: 9px; box-shadow: 0 10px 26px rgba(34,30,25,.16);
  padding: 0.7rem 0.75rem; text-align: left;
}}
.rt-kicker {{
  font-size: 0.74rem; color: {ACCENT}; font-weight: 700; letter-spacing: 0.1em;
  text-transform: uppercase;
}}
.rt-title {{
  font-family: 'Newsreader', Georgia, serif; color: {INK}; font-weight: 600;
  font-size: 1.04rem; line-height: 1.3; margin: 0.35rem 0 0.55rem;
}}
.rt-title .cite {{
  color: {ACCENT}; font-weight: 700; font-size: 0.66rem;
  vertical-align: super; margin-left: 1px;
}}
.rt-take {{
  margin-top: 0.55rem; background: rgba(181,83,46,0.07);
  border-left: 3px solid {ACCENT}; border-radius: 3px;
  padding: 0.5rem 0.6rem; font-size: 0.82rem; color: {INK_DIM}; line-height: 1.4;
}}
.demo-cap {{
  text-align: center; color: {INK_MUTE}; font-style: italic;
  font-size: var(--caption); margin-top: 1.2rem;
}}

/* Section step headings (shared scale). */
.step {{
  font-family: 'Newsreader', Georgia, serif;
  font-size: var(--h2);
  font-weight: 600;
  color: {INK};
  margin: 0 0 0.25rem;
}}
.step-sub {{ color: {INK_DIM}; font-size: 0.95rem; margin: 0 0 0.9rem; }}

.footer {{ border-top: 1px solid {LINE}; margin-top: 3rem; padding-top: 1.4rem; }}
.footer .discl {{
  color: {INK_MUTE}; font-style: italic;
  font-size: 0.86rem; line-height: 1.55; max-width: 760px;
}}
.footer .built {{ color: {INK_MUTE}; font-size: 0.86rem; margin-top: 0.6rem; }}

/* Subtle legal links at the very bottom + the standalone policy pages. */
.footer .legal {{ margin-top: 1rem; }}
.footlink {{
  color: {INK_MUTE} !important; text-decoration: none !important;
  font-size: 0.85rem; margin: 0 0.55rem;
}}
.footlink:hover {{ color: {ACCENT} !important; text-decoration: none !important; }}
.footsep {{ color: #B7AD9E; }}
.policy-title {{
  text-align: center; font-family: 'Newsreader', Georgia, serif; color: {INK};
  font-weight: 500; font-size: 2.4rem; margin: 0.6rem 0 0.3rem;
}}
.policy-back {{ color: {INK_MUTE}; text-decoration: none; font-size: 0.95rem; }}
.policy-back:hover {{ color: {ACCENT}; text-decoration: underline; }}
</style>
"""


def inject_theme() -> None:
    """Inject fonts and styling. Call once, right after set_page_config."""
    st.markdown(_CSS, unsafe_allow_html=True)


def render_header() -> None:
    """Hero: eyebrow tool name, value-prop H1, one-line subhead, trust chips."""
    st.markdown(
        """
        <div class="hero">
          <div class="kicker">AI Knowledge Assistant</div>
          <h1>Drop your docs. <span class="accent">Get the answers.</span></h1>
          <p>Point it at your handbooks, policies and manuals. Your team asks in plain
          English and gets a straight answer, with the exact source quoted.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


_STRAIGHT_ARROW = (
    '<svg class="straight-arrow" width="150" height="30" viewBox="0 0 150 30" '
    'fill="none" stroke="#B5532E" stroke-width="5" stroke-linecap="round" '
    'stroke-linejoin="round"><path d="M6 15 L132 15"/>'
    '<path d="M132 15 L116 6"/><path d="M132 15 L116 24"/></svg>'
)


def render_demo() -> None:
    """A three-column 'input -> prompt + arrow -> output' illustration:
    your documents, the plain-English question, and the cited answer."""
    st.markdown(
        f"""
        <div class="demo">
          <div class="hero-il">
            <div class="hero-col">
              <div class="hero-cap">Your documents &middot; PDF / Word</div>
              <div class="stack">
                <div class="filecard back">
                  <span class="fc-tag tag-pdf">handbook.pdf</span>
                  <div class="fc-lines">
                    <span class="ln"><b>2. Annual leave.</b> Full-time staff receive 28
                    days of paid leave per year.</span>
                    <span class="ln">This is in addition to all UK public holidays.</span>
                    <span class="ln">Part-time entitlement is calculated pro rata.</span>
                  </div>
                </div>
                <div class="filecard front">
                  <span class="fc-tag tag-doc">policy.docx</span>
                  <div class="fc-lines">
                    <span class="ln"><b>Remote working.</b> Staff may work from home up
                    to three days each week.</span>
                    <span class="ln">Requests are approved by your line manager.</span>
                    <span class="ln">Core hours are 10am to 4pm, Monday to Friday.</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="hero-mid">
              <div class="hero-prompt">&ldquo;How many holiday days do I get?&rdquo;</div>
              {_STRAIGHT_ARROW}
            </div>
            <div class="hero-col">
              <div class="hero-cap">Cited answer</div>
              <div class="report-thumb">
                <div class="rt-kicker">Annual leave</div>
                <div class="rt-title">Full-time staff get 28 days of paid leave, plus
                all UK public holidays.<span class="cite">[1]</span></div>
                <div class="rt-take"><b>Source [1]</b><br>Lumen &amp; Co. handbook,
                section 2</div>
              </div>
            </div>
          </div>
          <div class="demo-cap">A real answer, traced to the exact source &ndash; never a guess.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_step(title: str, subtitle: str = "") -> None:
    html = f'<div class="step">{title}</div>'
    if subtitle:
        html += f'<div class="step-sub">{subtitle}</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_footer() -> None:
    st.markdown(
        """
        <div class="footer">
          <p style="text-align:center; font-size:1.02rem; color:#5B544B; margin:0 0 1.1rem;">
          Want this running on <b style="color:#B5532E;">your own</b> documents?
          <a class="footlink" href="https://aronsarosi.com/#contact" target="_blank">Let&rsquo;s talk</a>.</p>
          <p class="discl">Answers are generated from the documents you provide and
          are shown with their sources. Always check the cited passage before relying
          on an answer for anything important.</p>
          <div class="legal" style="text-align:center;">
            <a class="footlink" href="?page=terms" target="_blank">Terms of Use</a>
            <span class="footsep">&middot;</span>
            <a class="footlink" href="?page=privacy" target="_blank">Privacy Policy</a>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_policy_page(page: str) -> None:
    """Render a standalone, themed Terms / Privacy page (opened from the footer).

    Same warm background and brand as the main app; the caller follows this with
    st.stop() so the main UI does not also render underneath.
    """
    from legal import PRIVACY_MD, TERMS_MD

    title = "Privacy Policy" if page == "privacy" else "Terms of Use"
    body = PRIVACY_MD if page == "privacy" else TERMS_MD
    _left, mid, _right = st.columns([1, 3, 1])
    with mid:
        st.markdown(f"<div class='policy-title'>{title}</div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center; margin-bottom:1.4rem;'>"
            "<a class='policy-back' href='?'>&larr; Back to the app</a></div>",
            unsafe_allow_html=True,
        )
        st.markdown(body)
