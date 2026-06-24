"""Plain-English Privacy Notice and Terms of Use shown from the app footer.

Kept honest and specific to how the Knowledge Assistant actually handles data: the documents
you upload are indexed transiently into an in-session knowledge base, only the small passages
relevant to your question (plus the question itself) are sent to the model to compose a cited
answer, and nothing is added to any long-term store. This is a demo, not professional or legal
advice, but it accurately describes how the app behaves.
"""

# Shown in the policies below. Change freely.
CONTACT_EMAIL = "aron.sarosi13@gmail.com"

PRIVACY_MD = f"""
**Last updated: June 2026**

This is a **free demonstration application** built to showcase an AI document Q&A system.
Please read how your data is handled before uploading anything.

**What we process**
- **Documents you upload** (PDF / Word / text / markdown). Used only to build a temporary,
  in-session knowledge base so the assistant can answer your questions during your visit.
- **The questions you type**, used to find the relevant passages and compose an answer.

**How your data is used**
- Your documents are split into passages and indexed so the relevant ones can be retrieved.
  **Your full documents are never sent to the AI model.** Only the handful of passages that
  match your question, together with the question itself, are sent to the language-model
  provider (OpenAI) to write a grounded, cited answer.
- The provider processes this under its own API data policy. OpenAI does **not** train its
  models on data submitted via the API and retains it only briefly for abuse monitoring.

**Retention**
- Uploads are processed **transiently**: the index lives only in your session and is rebuilt
  whenever the document set changes. On the hosted demo the underlying instance is ephemeral
  and its storage is wiped when it recycles.
- We do not build user profiles, and we do not sell or share your data with anyone other than
  the AI provider above.

**Your responsibilities**
- Because this is a public demo, **please do not upload personal, confidential, regulated, or
  otherwise sensitive documents.** Use the bundled sample or non-sensitive documents only.

Questions about privacy: {CONTACT_EMAIL}
"""

TERMS_MD = f"""
**Last updated: June 2026**

By using this free demonstration application ("the Demo"), you agree to the following.

**The Demo is provided "as is"**
- It is for **evaluation and demonstration only**, without warranties of any kind (including
  accuracy, fitness for a particular purpose, or availability).
- AI-generated answers may contain errors. **This is not professional, legal, financial, or
  HR advice.** Every answer is shown with its source - always check the cited passage before
  relying on an answer for anything important.

**Fair use**
- To keep the Demo free and available, usage is limited to **15 questions per visit**,
  **at most 5 uploaded files**, and **10 MB per file**.
- Please don't try to circumvent these limits, overload the service, upload malicious files,
  or use the Demo for unlawful purposes. Want more, or a version built for your team? Get in
  touch.

**Your content**
- You keep all rights to the documents you upload, and you're responsible for having the right
  to upload them and for ensuring they contain no sensitive or personal data (see the Privacy
  Notice).
- The Demo's code and design remain the property of its author.

**Limitation of liability**
- To the maximum extent permitted by law, the author is not liable for any damages arising
  from your use of the Demo, including any loss arising from reliance on its output.

Contact: {CONTACT_EMAIL}
"""
