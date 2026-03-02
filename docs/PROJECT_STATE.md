What I recommend for your next backend step (small but critical)

Right now /rag/answer returns:

answer (plain text)

sources (blocks)

To enable hover citations properly, we need the answer output to include citation mapping.

Option 1 (Fastest, good enough)

Frontend shows answer text + a “Sources” panel under it.
When user hovers a source chip, show the preview.

Example:
Answer bubble
Below it: chips: [1] Page 1 Text, [2] Page 1 Table

This avoids rewriting answer text.

Option 2 (Best UX)

Backend returns answer + citations inserted:

answer text includes [1] [2]

plus citations: { "1": sourceObj, "2": sourceObj }

This is what you described.

We can implement Option 2 with a small prompt rule:
“After every sentence, add citation like [1] [2] using the provided numbered sources.”

What we’ll build in Next.js

A single page app:

UI pieces

Upload area (only if no document_id yet)

Chat history area

Chat input

Assistant message component that supports:

markdown rendering

citation hover cards

table rendering

later image thumbnails

Libraries (minimal)

react-markdown (render markdown)

remark-gfm (tables)

simple Tailwind styling

custom hover popover (no heavy UI lib needed)

Multimodal Roadmap (what I understand you want later)
Phase 1 (now)

✅ Text + table retrieval usable
✅ Chat UI + hover citations
✅ Answer generation endpoint

Phase 2

🔜 Image extraction + storage + image_blocks table
🔜 image embeddings + retrieval
🔜 UI: show image thumbnails in hover / sources

Phase 3

🔜 Page preview highlight (bbox overlay on PDF page image)
This is the “best” version of your hover view.

Next action (I will proceed without asking more)

I will generate:

A Next.js (TypeScript) frontend skeleton:

/ single page

upload + chat

calls your endpoints:

/documents/upload

/documents/{id}/parse

/documents/{id}/embed

/rag/answer

UI behavior:

After upload → automatically trigger parse → embed (with status)

Chat disabled until embedded (or allow but warn)

Each assistant message shows “Sources” chips

Hover chip shows preview card

Table source renders as table in preview