import { useEffect, useState } from "react";
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

export default function Page() {
  const [documentId, setDocumentId] = useState<string>("");  // Track selected document ID
  const [busy, setBusy] = useState(false);
  const [uploadName, setUploadName] = useState<string>("");

  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);
  const [documents, setDocuments] = useState<any[]>([]);
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [input, setInput] = useState("");

  useEffect(() => {
    async function fetchDocuments() {
      const response = await fetch(`${API_BASE}/documents`);
      const data = await response.json();
      setDocuments(data);
      if (data.length > 0) {
        setSelectedDocumentId(data[0].id);  // Default to the first document
        setUploadName(data[0].filename);    // Set filename for the first document
      }
    }
    fetchDocuments();
  }, []);

  // Handle document select change
  async function handleDocumentSelect(event: React.ChangeEvent<HTMLSelectElement>) {
    const docId = event.target.value;
    setSelectedDocumentId(docId);
    if (docId) {
      const res = await fetch(`${API_BASE}/documents/${docId}`);
      const docData = await res.json();
      setUploadName(docData.filename);
      setMessages([
        ...messages,
        {
          role: "assistant",
          content: `Now interacting with document: ${docData.filename}`,
          sources: [],
        },
      ]);
    }
  };

  // Handle user message and call RAG API
  async function sendMessage() {
    if (!selectedDocumentId) return; // Ensure document is selected

    const userText = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: "user", content: userText }]);
    setBusy(true);

    try {
      const res = await fetch(`${API_BASE}/rag/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          document_id: selectedDocumentId,
          query: userText,
          k: 8,
        }),
      });

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
        <div>
          <div>
            <label htmlFor="documentSelect" className="text-slate-100">
              Select a Document:
            </label>
            <select
              id="documentSelect"
              onChange={handleDocumentSelect}
              value={selectedDocumentId || ""}
            >
              <option value="">Select a document...</option>
              {documents.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.filename}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mt-1 text-sm text-slate-300">
          {selectedDocumentId ? (
            <>
              <span className="font-semibold text-slate-100">Active PDF:</span>{" "}
              {uploadName || "uploaded"} ·{" "}
              <span className="font-mono text-xs">{selectedDocumentId}</span>
            </>
          ) : (
            "No PDF uploaded"
          )}
        </div>

        <div className="mt-1 text-sm text-slate-300">
          Upload one PDF → ask questions → hover citations to see evidence (text/table).
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
          placeholder={selectedDocumentId ? "Ask a question..." : "Upload a PDF first..."}
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