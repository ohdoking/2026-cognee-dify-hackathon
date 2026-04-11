import { useEffect, useMemo, useRef, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const THEMES = {
  light: {
    label: "Light",
    className: "theme-light",
  },
  dark: {
    label: "Dark",
    className: "theme-dark",
  },
};

function getStats(text) {
  const cleaned = text.trim();
  if (!cleaned) {
    return { words: 0, chars: 0, lines: 0 };
  }
  return {
    words: cleaned.split(/\s+/).filter(Boolean).length,
    chars: cleaned.length,
    lines: cleaned.split("\n").length,
  };
}

function App() {
  const [theme, setTheme] = useState("light");
  const [inputSource, setInputSource] = useState("Awaiting input");
  const [textInput, setTextInput] = useState("");
  const [transcript, setTranscript] = useState("");
  const [result, setResult] = useState(null);
  const [selectedAnswer, setSelectedAnswer] = useState("");
  const [revealed, setRevealed] = useState(false);
  const [quizIndex, setQuizIndex] = useState(0);
  const [busyState, setBusyState] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [health, setHealth] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const streamRef = useRef(null);

  const stats = useMemo(() => getStats(transcript), [transcript]);
  const quizzes = useMemo(() => {
    if (result && typeof result === "object" && Array.isArray(result.quizzes)) {
      return result.quizzes;
    }
    return [];
  }, [result]);
  const activeQuiz = quizzes[quizIndex] || null;

  useEffect(() => {
    document.body.className = THEMES[theme].className;
  }, [theme]);

  useEffect(() => {
    let cancelled = false;
    fetch(`${API_BASE}/api/health`)
      .then(async (response) => {
        if (!response.ok) {
          throw new Error("Failed to load API health.");
        }
        return response.json();
      })
      .then((data) => {
        if (!cancelled) {
          setHealth(data);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setHealth({ status: "offline", openaiConfigured: false, difyConfigured: false });
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function uploadAudio(file, sourceLabel) {
    const formData = new FormData();
    formData.append("file", file);

    setBusyState("transcribe");
    setError("");
    setStatus("Transcribing audio...");

    try {
      const response = await fetch(`${API_BASE}/api/transcribe`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Transcription failed.");
      }
      setTranscript(data.transcript);
      setInputSource(sourceLabel);
      setResult(null);
      setQuizIndex(0);
      setSelectedAnswer("");
      setRevealed(false);
      setStatus("Transcript loaded.");
    } catch (err) {
      setError(err.message);
      setStatus("");
    } finally {
      setBusyState("");
    }
  }

  async function handleFileChange(event) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    if (file.type === "text/plain" || file.name.endsWith(".txt")) {
      const text = await file.text();
      setTranscript(text);
      setInputSource(`Text file: ${file.name}`);
      setResult(null);
      setQuizIndex(0);
      setSelectedAnswer("");
      setRevealed(false);
      setStatus("Transcript loaded from text file.");
      setError("");
      return;
    }

    await uploadAudio(file, `Audio file: ${file.name}`);
  }

  async function handleRecordToggle() {
    if (isRecording && mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      return;
    }

    setError("");
    setStatus("");

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      streamRef.current = stream;
      mediaRecorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType || "audio/webm" });
        const extension = blob.type.includes("mp4") ? "m4a" : "webm";
        const file = new File([blob], `recording.${extension}`, { type: blob.type });
        stream.getTracks().forEach((track) => track.stop());
        await uploadAudio(file, "Live recording");
      };

      recorder.start();
      setIsRecording(true);
      setStatus("Recording in progress...");
    } catch (err) {
      setError("Microphone access failed.");
    }
  }

  async function handleAudit() {
    if (!transcript.trim()) {
      setError("Provide a transcript before running the audit.");
      return;
    }

    setBusyState("audit");
    setError("");
    setStatus("Analyzing transcript...");

    try {
      const response = await fetch(`${API_BASE}/api/audit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ transcript }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Audit failed.");
      }
      setResult(data.result);
      setQuizIndex(0);
      setSelectedAnswer("");
      setRevealed(false);
      setStatus("Audit complete.");
    } catch (err) {
      setError(err.message);
      setStatus("");
    } finally {
      setBusyState("");
    }
  }

  function renderQuizStage() {
    if (!result) {
      return (
        <div className="empty-state">
          Step 3 appears here after the workflow returns quiz items.
        </div>
      );
    }

    if (activeQuiz) {
      const correct = String(activeQuiz.correct_answer || "").trim().toUpperCase();
      const options = [
        { key: "A", value: activeQuiz.options?.A || "" },
        { key: "B", value: activeQuiz.options?.B || "" },
      ];

      return (
        <div className="quiz-stage">
          <div className="quiz-progress">
            <span>Quiz {String(quizIndex + 1).padStart(2, "0")}</span>
            <strong>{activeQuiz.category || "Analysis"}</strong>
            <p>
              {quizIndex + 1} / {quizzes.length}
            </p>
          </div>

          <article className="quiz-card interactive">
            <h3>{activeQuiz.question || "No question provided."}</h3>
            <div className="options-grid">
              {options.map((option) => {
                const isSelected = selectedAnswer === option.key;
                const isCorrect = revealed && correct === option.key;
                const isWrong = revealed && isSelected && correct !== option.key;
                return (
                  <button
                    key={option.key}
                    type="button"
                    className={[
                      "option-card",
                      "option-button",
                      isSelected ? "selected" : "",
                      isCorrect ? "correct" : "",
                      isWrong ? "wrong" : "",
                    ]
                      .filter(Boolean)
                      .join(" ")}
                    onClick={() => !revealed && setSelectedAnswer(option.key)}
                  >
                    <span>Option {option.key}</span>
                    <p>{option.value}</p>
                  </button>
                );
              })}
            </div>

            <div className="quiz-actions">
              <button
                type="button"
                onClick={() => setRevealed(true)}
                disabled={!selectedAnswer || revealed}
              >
                Reveal answer
              </button>
              <div className="quiz-nav">
                <button
                  type="button"
                  onClick={() => {
                    setQuizIndex((current) => Math.max(0, current - 1));
                    setSelectedAnswer("");
                    setRevealed(false);
                  }}
                  disabled={quizIndex === 0}
                >
                  Previous
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setQuizIndex((current) => Math.min(quizzes.length - 1, current + 1));
                    setSelectedAnswer("");
                    setRevealed(false);
                  }}
                  disabled={quizIndex === quizzes.length - 1}
                >
                  Next
                </button>
              </div>
            </div>

            {revealed && (
              <div className="answer-card">
                <span>Correct answer</span>
                <strong>{correct}</strong>
                <p>{activeQuiz.insight || ""}</p>
              </div>
            )}
          </article>
        </div>
      );
    }

    return <pre className="raw-result">{String(result)}</pre>;
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <div className="eyebrow">Meeting Reliability Console</div>
          <h1>BrainSync Auditor</h1>
          <p>
            Review transcripts, transcribe live discussion, and turn weak agreement into
            concrete recall checks through your Dify workflow.
          </p>
        </div>
        <div className="hero-controls">
          <div className="mode-toggle">
            {Object.entries(THEMES).map(([key, item]) => (
              <button
                key={key}
                type="button"
                className={theme === key ? "active" : ""}
                onClick={() => setTheme(key)}
              >
                {item.label}
              </button>
            ))}
          </div>
          <div className="hero-pills">
            <div className="pill">
              <span>Current source</span>
              <strong>{inputSource}</strong>
            </div>
            <div className="pill">
              <span>Transcript size</span>
              <strong>{stats.words} words</strong>
            </div>
            <div className="pill">
              <span>API status</span>
              <strong>
                {health?.status === "ok"
                  ? `OpenAI ${health.openaiConfigured ? "on" : "off"} / Dify ${health.difyConfigured ? "on" : "off"}`
                  : "Backend offline"}
              </strong>
            </div>
          </div>
        </div>
      </header>

      {(status || error) && (
        <div className={`banner ${error ? "error" : "success"}`}>{error || status}</div>
      )}

      <main className="workspace">
        <section className="panel">
          <div className="step-card">
            <div className="section-head">
              <span>Step 1</span>
              <h2>Input</h2>
              <p>Provide meeting content as text, live recording, or uploaded file.</p>
            </div>

            <div className="input-grid">
              <div className="input-card">
                <h3>Direct text</h3>
                <textarea
                  value={textInput}
                  onChange={(event) => setTextInput(event.target.value)}
                  placeholder="Paste notes, transcript fragments, or a full conversation."
                />
                <button
                  type="button"
                  onClick={() => {
                    setTranscript(textInput);
                    setInputSource("Direct text");
                    setResult(null);
                    setQuizIndex(0);
                    setSelectedAnswer("");
                    setRevealed(false);
                    setStatus("Transcript loaded from direct text.");
                    setError("");
                  }}
                >
                  Load text into workspace
                </button>
              </div>

              <div className="input-card">
                <h3>Live recording</h3>
                <p>Capture a meeting snippet in the browser and send it to Whisper through the API.</p>
                <button
                  type="button"
                  className={isRecording ? "danger" : ""}
                  onClick={handleRecordToggle}
                  disabled={busyState === "transcribe"}
                >
                  {isRecording ? "Stop and transcribe" : "Start recording"}
                </button>
              </div>

              <div className="input-card">
                <h3>File upload</h3>
                <p>Upload `.txt`, `.mp3`, `.wav`, or browser-recorded audio.</p>
                <label className="file-picker">
                  <input type="file" accept=".txt,.mp3,.wav,audio/*" onChange={handleFileChange} />
                  Choose file
                </label>
              </div>
            </div>
          </div>

          <div className="step-card">
            <div className="section-head">
              <span>Step 2</span>
              <h2>Execute workflow</h2>
              <p>Review the transcript, then run the workflow and wait for quiz output.</p>
            </div>

            <div className="stats-grid">
              <div className="stat-card">
                <span>Words</span>
                <strong>{stats.words}</strong>
              </div>
              <div className="stat-card">
                <span>Characters</span>
                <strong>{stats.chars}</strong>
              </div>
              <div className="stat-card">
                <span>Lines</span>
                <strong>{stats.lines}</strong>
              </div>
            </div>

            <textarea
              className="review-area"
              value={transcript}
              onChange={(event) => setTranscript(event.target.value)}
              placeholder="Your working transcript appears here."
            />

            <div className="workflow-bar">
              <div className="workflow-meta">
                <span>Ready source</span>
                <strong>{inputSource}</strong>
              </div>
              <button
                type="button"
                className="primary"
                onClick={handleAudit}
                disabled={busyState === "audit" || busyState === "transcribe"}
              >
                {busyState === "audit" ? "Executing..." : "Execute workflow"}
              </button>
            </div>
          </div>
        </section>

        <aside className="panel result-panel">
          <div className="section-head">
            <span>Step 3</span>
            <h2>Interactive quiz cards</h2>
            <p>Move through returned quizzes one by one, choose an answer, and reveal the insight.</p>
          </div>
          <div className="result-body">{renderQuizStage()}</div>
        </aside>
      </main>
    </div>
  );
}

export default App;
