"use client";

import { useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type Source = {
  block_type: "text" | "table" | "image";
  block_id: string;
  page_number: number;
  content: string;
  bbox?: any;
  score?: number;
};

type ChatMsg =
  | { role: "user"; content: string }
  | { role: "assistant"; content: string; sources: Source[] };

const API_BASE = process.env.NEXT_PUBLIC_API_BASE!;

function extractCitationNumbers(text: string): number[] {
  const matches = text.match(/\[(\d+)\]/g) ?? [];
  const nums = matches
    .map((m) => Number(m.replace("[", "").replace("]", "")))
    .filter((n) => Number.isFinite(n) && n > 0);
  return Array.from(new Set(nums));
}

function SourcePreview({ src }: { src: Source }) {
  const isTable = src.block_type === "table";
  return (
    <div className="w-[420px] max-w-[80vw] rounded-xl border border-slate-700 bg-slate-900 p-3 shadow-xl">
      <div className="text-xs text-slate-300">
        <span className="font-semibold">Page {src.page_number}</span>{" "}
        <span className="ml-2 rounded-md bg-slate-800 px-2 py-0.5">
          {src.block_type}
        </span>
      </div>

      <div className="mt-2 max-h-64 overflow-auto rounded-lg bg-slate-950 p-2 text-sm text-slate-100">
        {isTable ? (
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {src.content}
          </ReactMarkdown>
        ) : (
          <pre className="whitespace-pre-wrap">{src.content}</pre>
        )}
      </div>
    </div>
  );
}

function CitationInline({
  n,
  source,
}: {
  n: number;
  source?: Source;
}) {
  const [open, setOpen] = useState(false);

  return (
    <span
      className="relative inline-block"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      <span className="mx-0.5 cursor-help rounded bg-slate-800 px-1.5 py-0.5 text-xs text-slate-200">
        [{n}]
      </span>

      {open && source && (
        <div className="absolute left-0 top-6 z-50">
          <SourcePreview src={source} />
        </div>
      )}
    </span>
  );
}

function AssistantMessage({
  content,
  sources,
}: {
  content: string;
  sources: Source[];
}) {
  const citedNums = useMemo(() => extractCitationNumbers(content), [content]);

  const sourceMap = useMemo(() => {
    const map = new Map<number, Source>();
    sources.forEach((s, idx) => map.set(idx + 1, s));
    return map;
  }, [sources]);

  const parts = useMemo(() => {
    const tokens = content.split(/(\[\d+\])/g);
    return tokens.map((t, i) => {
      const m = t.match(/^\[(\d+)\]$/);
      if (m) {
        const n = Number(m[1]);
        return <CitationInline key={i} n={n} source={sourceMap.get(n)} />;
      }
      return (
        <span key={i}>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{t}</ReactMarkdown>
        </span>
      );
    });
  }, [content, sourceMap]);

  return (
    <div className="rounded-2xl bg-slate-900 p-4 text-slate-100">
      <div className="prose prose-invert max-w-none">{parts}</div>

      {citedNums.length === 0 && sources.length > 0 && (
        <div className="mt-3 text-xs text-slate-300">
          No inline citations found. Sources available below.
        </div>
      )}

      {sources.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {sources.map((s, idx) => (
            <div key={s.block_id} className="relative group">
              <div className="rounded-lg bg-slate-800 px-2 py-1 text-xs text-slate-200">
                [{idx + 1}] Page {s.page_number} · {s.block_type}
              </div>
              <div className="invisible absolute left-0 top-7 z-50 group-hover:visible">
                <SourcePreview src={s} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function Page() {
  const [documentId, setDocumentId] = useState<string>("");
  const [busy, setBusy] = useState(false);
  const [uploadName, setUploadName] = useState<string>("");
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [input, setInput] = useState("");

  async function uploadAndProcess(file: File) {
    setBusy(true);
    try {
      const form = new FormData();
      form.append("file", file);

      const up = await fetch(`${API_BASE}/documents/upload`, {
        method: "POST",
        body: form,
      });
      if (!up.ok) throw new Error(await up.text());
      const upJson = await up.json();
      const docId = upJson.document_id as string;

      setDocumentId(docId);
      setUploadName(file.name);

      await fetch(`${API_BASE}/documents/${docId}/parse`, { method: "POST" });
      await fetch(`${API_BASE}/documents/${docId}/embed`, { method: "POST" });

      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content:
            `PDF uploaded and processing started.\n\nDocument ID: ${docId}\n\nYou can start asking questions.`,
          sources: [],
        },
      ]);
    } finally {
      setBusy(false);
    }
  }

  async function sendMessage() {
    if (!input.trim()) return;
    if (!documentId) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: "Upload a PDF first.",
          sources: [],
        },
      ]);
      return;
    }

    const userText = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: "user", content: userText }]);
    setBusy(true);

    try {
      const res = await fetch(`${API_BASE}/rag/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          document_id: documentId,
          query: userText,
          k: 8,
        }),
      });

      if (!res.ok) throw new Error(await res.text());
      const json = await res.json();

      setMessages((m) => [
        ...m,
        { role: "assistant", content: json.answer, sources: json.sources ?? [] },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col p-4">
      <div className="mb-4 rounded-2xl border border-slate-800 bg-slate-950 p-4">
        <div className="text-lg font-semibold text-slate-100">
          MultimodalDoc (Single PDF Chat)
        </div>
        <div className="mt-1 text-sm text-slate-300">
          Upload one PDF → ask questions → hover citations to see evidence (text/table).
        </div>

        <div className="mt-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div className="text-sm text-slate-300">
            {documentId ? (
              <>
                <span className="font-semibold text-slate-100">Active PDF:</span>{" "}
                {uploadName || "uploaded"} ·{" "}
                <span className="font-mono text-xs">{documentId}</span>
              </>
            ) : (
              "No PDF uploaded."
            )}
          </div>

          <label className="inline-flex cursor-pointer items-center justify-center rounded-xl bg-slate-800 px-3 py-2 text-sm text-slate-100 hover:bg-slate-700">
            <input
              type="file"
              accept="application/pdf"
              className="hidden"
              disabled={busy}
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) uploadAndProcess(f);
              }}
            />
            {busy ? "Working..." : "Upload PDF"}
          </label>
        </div>
      </div>

      <div className="flex-1 space-y-3 overflow-auto rounded-2xl border border-slate-800 bg-slate-950 p-4">
        {messages.length === 0 && (
          <div className="text-sm text-slate-400">
            Upload a PDF to begin.
          </div>
        )}

        {messages.map((m, idx) => {
          if (m.role === "user") {
            return (
              <div key={idx} className="flex justify-end">
                <div className="max-w-[85%] rounded-2xl bg-slate-800 p-3 text-slate-100">
                  {m.content}
                </div>
              </div>
            );
          }
          return (
            <div key={idx} className="flex justify-start">
              <div className="max-w-[85%]">
                <AssistantMessage content={m.content} sources={m.sources} />
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-3 flex gap-2 rounded-2xl border border-slate-800 bg-slate-950 p-3">
        <input
          className="flex-1 rounded-xl bg-slate-900 px-3 py-2 text-slate-100 outline-none placeholder:text-slate-500"
          placeholder={documentId ? "Ask a question..." : "Upload a PDF first..."}
          value={input}
          disabled={busy}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") sendMessage();
          }}
        />
        <button
          className="rounded-xl bg-slate-800 px-4 py-2 text-slate-100 hover:bg-slate-700 disabled:opacity-50"
          onClick={sendMessage}
          disabled={busy}
        >
          Send
        </button>
      </div>
    </main>
  );
}