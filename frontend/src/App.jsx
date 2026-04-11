import { useEffect, useMemo, useRef, useState } from "react";
import FeedbackGraph from "./components/FeedbackGraph";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const THEMES = {
  light: {
    label: "Light",
    icon: "☀",
    className: "theme-light",
  },
  dark: {
    label: "Dark",
    icon: "☾",
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

function getCorrectAnswer(quiz) {
  return String(quiz?.correct_answer || "").trim().toUpperCase();
}

function getFeedbackMessage(quiz, userAnswer) {
  const correct = getCorrectAnswer(quiz);
  if (!userAnswer) {
    return "No answer was selected. Focus on the core rule before moving on.";
  }
  if (userAnswer === correct) {
    return "You matched the expected answer. Keep anchoring on the exact rule, not the general theme.";
  }
  return `You chose ${userAnswer}, but the governing answer is ${correct}. Anchor your memory to the exact constraint instead of the closest-sounding option.`;
}

function getContextMessage(quiz) {
  return quiz?.context || quiz?.insight || quiz?.question || "No supporting context returned by the workflow.";
}

function getRememberTip(quiz, userAnswer) {
  const correct = getCorrectAnswer(quiz);
  if (!userAnswer) {
    return "Pause before agreeing. Repeat the governing rule back in one sentence before you confirm.";
  }
  if (userAnswer === correct) {
    return "Keep using exact rule language when you answer so your agreement stays precise under pressure.";
  }
  return "Before saying yes, restate the constraint, the owner, and the exception path out loud. That prevents confident but incorrect approval.";
}

function getCommunicationRisk(quiz, userAnswer) {
  const correct = getCorrectAnswer(quiz);
  if (!userAnswer) {
    return "Silence or uncommitted responses can still create ambiguity for the team.";
  }
  if (userAnswer === correct) {
    return "Low risk. Your answer reinforced the correct shared memory.";
  }
  return "High risk. A wrong confirmation can cause the team to believe a non-compliant decision was approved.";
}

function getOverallFeedback(summary) {
  if (summary.total === 0) {
    return "No quiz results yet.";
  }
  if (summary.wrong === 0) {
    return "You stayed aligned with the policy rules. Keep confirming decisions with exact wording, not broad agreement.";
  }
  if (summary.correct === 0) {
    return "Your approvals were consistently misaligned with the policy source of truth. Slow the conversation down and verify the rule before agreeing.";
  }
  return "You remembered part of the policy set correctly, but some approvals were based on incomplete recall. The next improvement is precision under pressure.";
}

function getRememberChecklist(summary) {
  const checklist = [];
  if (summary.wrong > 0) {
    checklist.push("Restate the rule before approval.");
    checklist.push("Call out the owner or required approver by name.");
    checklist.push("Separate the default rule from the exception path.");
  }
  if (summary.unanswered > 0) {
    checklist.push("If you are unsure, ask for clarification instead of giving a soft yes.");
  }
  if (summary.correct > 0) {
    checklist.push("Keep using exact policy language when you agree so the team hears the real constraint.");
  }
  return [...new Set(checklist)].slice(0, 4);
}

function App() {
  const [theme, setTheme] = useState("light");
  const [inputTab, setInputTab] = useState("text");
  const [leftPanelCollapsed, setLeftPanelCollapsed] = useState(false);
  const [stepVisibility, setStepVisibility] = useState({ input: true, workflow: true });
  const [inputSource, setInputSource] = useState("Awaiting input");
  const [textInput, setTextInput] = useState("");
  const [transcript, setTranscript] = useState("");
  const [contextUploadMeta, setContextUploadMeta] = useState(null);
  const [result, setResult] = useState(null);
  const [auditMeta, setAuditMeta] = useState(null);
  const [quizSelections, setQuizSelections] = useState({});
  const [revealedQuestions, setRevealedQuestions] = useState({});
  const [expandedSummaryCards, setExpandedSummaryCards] = useState({});
  const [cogneeFeedbackByQuiz, setCogneeFeedbackByQuiz] = useState({});
  const [cogneeFeedbackLoading, setCogneeFeedbackLoading] = useState({});
  const [quizIndex, setQuizIndex] = useState(0);
  const [showSummary, setShowSummary] = useState(false);
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
  const selectedAnswer = quizSelections[quizIndex] || "";
  const revealed = Boolean(revealedQuestions[quizIndex]);
  const summary = useMemo(() => {
    const answered = quizzes.filter((_, index) => Boolean(quizSelections[index])).length;
    const correct = quizzes.filter(
      (quiz, index) => quizSelections[index] && quizSelections[index] === getCorrectAnswer(quiz),
    ).length;
    const unanswered = quizzes.length - answered;
    const wrongItems = quizzes
      .map((quiz, index) => ({
        index,
        quiz,
        userAnswer: quizSelections[index] || "",
        correctAnswer: getCorrectAnswer(quiz),
      }))
      .filter((item) => item.userAnswer !== item.correctAnswer);
    return {
      total: quizzes.length,
      answered,
      correct,
      unanswered,
      wrong: wrongItems.length,
      wrongItems,
    };
  }, [quizzes, quizSelections]);

  useEffect(() => {
    document.body.className = THEMES[theme].className;
  }, [theme]);

  function resetAuditWorkspace() {
    setResult(null);
    setAuditMeta(null);
    setQuizIndex(0);
    setQuizSelections({});
    setRevealedQuestions({});
    setExpandedSummaryCards({});
    setCogneeFeedbackByQuiz({});
    setCogneeFeedbackLoading({});
    setShowSummary(false);
  }

  function toggleStep(stepKey) {
    setStepVisibility((current) => ({
      ...current,
      [stepKey]: !current[stepKey],
    }));
  }

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

  useEffect(() => {
    if (!showSummary || !quizzes.length) {
      return;
    }

    const missingIndexes = quizzes
      .map((_, index) => index)
      .filter((index) => !cogneeFeedbackByQuiz[index] && !cogneeFeedbackLoading[index]);

    if (!missingIndexes.length) {
      return;
    }

    missingIndexes.forEach((index) => {
      setCogneeFeedbackLoading((current) => ({ ...current, [index]: true }));
    });

    fetch(`${API_BASE}/api/cognee/summary-feedback`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        items: missingIndexes.map((index) => ({
          index,
          question: quizzes[index]?.question || "",
          user_answer: quizSelections[index] || "",
          correct_answer: getCorrectAnswer(quizzes[index]),
          category: quizzes[index]?.category || "",
          insight: quizzes[index]?.insight || "",
        })),
      }),
    })
      .then(async (response) => {
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.detail || "Cognee summary feedback lookup failed.");
        }
        const mapped = {};
        (data.items || []).forEach((item) => {
          mapped[item.index] = item;
        });
        setCogneeFeedbackByQuiz((current) => ({ ...current, ...mapped }));
      })
      .catch((err) => {
        const fallback = {};
        missingIndexes.forEach((index) => {
          fallback[index] = {
            index,
            error: err.message,
            contexts: [],
            graph: { nodes: [], edges: [] },
          };
        });
        setCogneeFeedbackByQuiz((current) => ({ ...current, ...fallback }));
      })
      .finally(() => {
        missingIndexes.forEach((index) => {
          setCogneeFeedbackLoading((current) => ({ ...current, [index]: false }));
        });
      });
  }, [showSummary, quizzes, cogneeFeedbackByQuiz, cogneeFeedbackLoading, quizSelections]);

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
      resetAuditWorkspace();
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

    setStepVisibility((current) => ({ ...current, input: false }));

    if (file.type === "text/plain" || file.name.endsWith(".txt")) {
      const text = await file.text();
      setTranscript(text);
      setInputSource(`Text file: ${file.name}`);
      resetAuditWorkspace();
      setStatus("Transcript loaded from text file.");
      setError("");
      return;
    }

    await uploadAudio(file, `Audio file: ${file.name}`);
  }

  async function handleContextFileChange(event) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setBusyState("context-upload");
    setError("");
    setStatus("Uploading context file into Cognee...");

    try {
      const response = await fetch(`${API_BASE}/api/cognee/upload-context`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Context upload failed.");
      }
      setContextUploadMeta(data);
      setStatus(`Context file uploaded to ${data.datasetName}.`);
    } catch (err) {
      setError(err.message);
      setStatus("");
    } finally {
      setBusyState("");
      event.target.value = "";
    }
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
      setAuditMeta(data.cognee || null);
      setQuizIndex(0);
      setQuizSelections({});
      setRevealedQuestions({});
      setExpandedSummaryCards({});
      setCogneeFeedbackByQuiz({});
      setCogneeFeedbackLoading({});
      setShowSummary(false);
      setLeftPanelCollapsed(true);
      setStatus("Audit complete.");
    } catch (err) {
      setError(err.message);
      setStatus("");
    } finally {
      setBusyState("");
    }
  }

  function selectAnswer(answerKey) {
    if (revealed) {
      return;
    }
    setQuizSelections((current) => ({ ...current, [quizIndex]: answerKey }));
  }

  function revealCurrentAnswer() {
    setRevealedQuestions((current) => ({ ...current, [quizIndex]: true }));
  }

  function goToQuiz(nextIndex) {
    setQuizIndex(nextIndex);
    setShowSummary(false);
  }

  async function loadCogneeFeedback(index, quiz) {
    if (cogneeFeedbackByQuiz[index] || cogneeFeedbackLoading[index]) {
      return;
    }

    setCogneeFeedbackLoading((current) => ({ ...current, [index]: true }));
    try {
      const response = await fetch(`${API_BASE}/api/cognee/search-feedback`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          index,
          question: quiz.question || "",
          user_answer: quizSelections[index] || "",
          correct_answer: getCorrectAnswer(quiz),
          category: quiz.category || "",
          insight: quiz.insight || "",
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Cognee feedback lookup failed.");
      }
      setCogneeFeedbackByQuiz((current) => ({ ...current, [index]: data }));
    } catch (err) {
      setCogneeFeedbackByQuiz((current) => ({
        ...current,
        [index]: {
          index,
          error: err.message,
          contexts: [],
          graph: { nodes: [], edges: [] },
        },
      }));
    } finally {
      setCogneeFeedbackLoading((current) => ({ ...current, [index]: false }));
    }
  }

  function toggleSummaryCard(index, quiz) {
    setExpandedSummaryCards((current) => ({
      ...current,
      [index]: !current[index],
    }));
    if (!expandedSummaryCards[index]) {
      loadCogneeFeedback(index, quiz);
    }
  }

  function renderQuizStage() {
    if (busyState === "transcribe") {
      return (
        <div className="loading-state">
          <div className="loading-state__pulse" aria-hidden="true" />
          <span>Transcribing upload</span>
          <h3>Converting uploaded audio into a transcript</h3>
          <p>
            The file has been received by the backend and Whisper is still processing the audio.
            The transcript will appear in Step 2 as soon as transcription completes.
          </p>
          <div className="loading-state__steps">
            <div className="loading-step is-active">1. File uploaded</div>
            <div className="loading-step is-active">2. Audio transcription running</div>
            <div className="loading-step">3. Transcript ready for workflow</div>
          </div>
        </div>
      );
    }

    if (busyState === "audit") {
      return (
        <div className="loading-state">
          <div className="loading-state__pulse" aria-hidden="true" />
          <span>Waiting for workflow response</span>
          <h3>Generating quiz cards from the meeting transcript</h3>
          <p>
            The transcript has been sent to the backend and the Dify workflow is still processing.
            This can take a few moments depending on transcript length and workflow latency.
          </p>
          <div className="loading-state__steps">
            <div className="loading-step is-active">1. Transcript submitted</div>
            <div className="loading-step is-active">2. Workflow running</div>
            <div className="loading-step">3. Quiz list returned</div>
          </div>
        </div>
      );
    }

    if (!result) {
      return (
        <div className="empty-state">
          Step 3 appears here after the workflow returns quiz items.
        </div>
      );
    }

    if (activeQuiz) {
      const correct = String(activeQuiz.correct_answer || "").trim().toUpperCase();
      const isLastQuiz = quizIndex === quizzes.length - 1;
      const options = [
        { key: "A", value: activeQuiz.options?.A || "" },
        { key: "B", value: activeQuiz.options?.B || "" },
      ];

      if (showSummary) {
        return (
          <div className="summary-stage">
            <div className="summary-header">
              <span>Review complete</span>
              <h3>Memory overview</h3>
              <p>
                {summary.correct} of {summary.total} answers matched the workflow output.
              </p>
            </div>

            <div className="summary-metrics">
              <div className="stat-card">
                <span>Correct</span>
                <strong>{summary.correct}</strong>
              </div>
              <div className="stat-card">
                <span>Wrong</span>
                <strong>{summary.wrong}</strong>
              </div>
              <div className="stat-card">
                <span>Answered</span>
                <strong>{summary.answered}</strong>
              </div>
              <div className="stat-card">
                <span>Unanswered</span>
                <strong>{summary.unanswered}</strong>
              </div>
            </div>

            <div className="summary-overview-grid">
              <section className="summary-panel summary-panel--highlight">
                <span>Overall feedback</span>
                <h4>How your answers affected team alignment</h4>
                <p>{getOverallFeedback(summary)}</p>
              </section>

              <section className="summary-panel">
                <span>What to remember</span>
                <h4>Use this before the next meeting</h4>
                <ul className="summary-checklist">
                  {getRememberChecklist(summary).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </section>
            </div>

            {auditMeta && (
              <div className="summary-panel">
                <span>Workflow memory sync</span>
                <h4>Transcript update into Cognee</h4>
                <p>
                  {auditMeta.ingested
                    ? `Transcript was ingested into ${auditMeta.datasetName}.`
                    : `Cognee transcript ingestion did not complete for this audit run.${auditMeta.error ? ` ${auditMeta.error}` : ""}`}
                </p>
              </div>
            )}

            <div className="summary-list">
              {quizzes.map((quiz, index) => {
                const userAnswer = quizSelections[index] || "";
                const correctAnswer = getCorrectAnswer(quiz);
                const isCorrect = userAnswer === correctAnswer;
                const isExpanded = Boolean(expandedSummaryCards[index]);
                const cogneeFeedback = cogneeFeedbackByQuiz[index];
                const isLoadingFeedback = Boolean(cogneeFeedbackLoading[index]);
                const evidenceItems = cogneeFeedback?.contexts || [];
                return (
                  <article
                    key={`${quiz.category || "quiz"}-${index}`}
                    className={`summary-card ${isCorrect ? "is-correct" : "is-wrong"}`}
                  >
                    <div className="summary-card__summary">
                      <div className="summary-card__top">
                        <span>Quiz {String(index + 1).padStart(2, "0")}</span>
                        <strong>{quiz.category || "Analysis"}</strong>
                      </div>
                      <h4>{quiz.question || "No question provided."}</h4>
                      <div className="summary-card__summary-meta">
                        <div>
                          <span>Your answer</span>
                          <strong>{userAnswer || "No answer"}</strong>
                        </div>
                        <div>
                          <span>Correct answer</span>
                          <strong>{correctAnswer || "-"}</strong>
                        </div>
                        <div className={`summary-status ${isCorrect ? "summary-status--correct" : "summary-status--wrong"}`}>
                          {isCorrect ? "Right" : "Needs review"}
                        </div>
                        <button
                          type="button"
                          className="summary-toggle"
                          onClick={() => toggleSummaryCard(index, quiz)}
                        >
                          {isExpanded ? "Hide details" : "Show details"}
                        </button>
                      </div>
                    </div>

                    {isExpanded && (
                    <div className="summary-card__content">
                      <div className="summary-card__content-grid">
                        <div className="summary-card__content-main">
                          <div className="summary-card__block">
                            <span>Why this matters</span>
                            <p>{getContextMessage(quiz)}</p>
                          </div>
                          <div className="summary-card__block">
                            <span>Feedback</span>
                            <p>{getFeedbackMessage(quiz, userAnswer)}</p>
                          </div>
                          <div className="summary-card__block summary-card__block--memory">
                            <span>What to remember next time</span>
                            <p>{getRememberTip(quiz, userAnswer)}</p>
                          </div>
                          <div className="summary-card__block">
                            <span>Communication risk</span>
                            <p>{getCommunicationRisk(quiz, userAnswer)}</p>
                          </div>
                        </div>

                        <div className="summary-card__content-side">
                          <div className="summary-card__block">
                            <div className="summary-card__block-head">
                              <span>Cognee search query</span>
                              <strong>
                                {cogneeFeedback?.graphMeta?.datasetIdSource === "search_result"
                                  ? "Search dataset"
                                  : cogneeFeedback?.graphMeta?.datasetIdSource === "dataset_lookup"
                                    ? "Lookup dataset"
                                    : "Live lookup"}
                              </strong>
                            </div>
                            <p className="summary-query">
                              {cogneeFeedback?.query || "Query will appear after feedback lookup completes."}
                            </p>
                          </div>
                          <div className="summary-card__block">
                            <div className="summary-card__block-head">
                              <span>Cognee evidence</span>
                              {!isLoadingFeedback && !cogneeFeedback?.error ? <strong>{evidenceItems.length} items</strong> : null}
                            </div>
                            {isLoadingFeedback ? (
                              <p>Loading relevant context and graph from Cognee...</p>
                            ) : cogneeFeedback?.error ? (
                              <p>{cogneeFeedback.error}</p>
                            ) : (
                              <div className="cognee-feedback">
                                <div className="cognee-feedback__contexts">
                                  {evidenceItems.length ? (
                                    <ul className="cognee-context-list">
                                      {evidenceItems.map((context, contextIndex) => (
                                        <li key={`${index}-${contextIndex}`}>{context}</li>
                                      ))}
                                    </ul>
                                  ) : (
                                    <p>No relevant text context returned from Cognee.</p>
                                  )}
                                </div>
                                <FeedbackGraph graph={cogneeFeedback?.graph} meta={cogneeFeedback?.graphMeta} />
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="summary-card__actions">
                        <button
                          type="button"
                          className="quiz-action-button quiz-action-button--secondary"
                          onClick={() => goToQuiz(index)}
                        >
                          Revisit card
                        </button>
                      </div>
                    </div>
                    )}
                  </article>
                );
              })}
            </div>
          </div>
        );
      }

      return (
        <div className="quiz-stage">
          <div className="quiz-progress">
            <div className="quiz-progress__block">
              <span>Quiz {String(quizIndex + 1).padStart(2, "0")}</span>
              <strong>{activeQuiz.category || "Analysis"}</strong>
            </div>
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
                    onClick={() => selectAnswer(option.key)}
                  >
                    <span>Option {option.key}</span>
                    <p>{option.value}</p>
                  </button>
                );
              })}
            </div>

            <div className="quiz-actions">
              <div className="quiz-actions__hint">
                {revealed
                  ? "Review the explanation, then move to the next card."
                  : "Choose one option before revealing the answer."}
              </div>
              <button
                type="button"
                className="quiz-action-button quiz-action-button--primary"
                onClick={revealCurrentAnswer}
                disabled={!selectedAnswer || revealed}
              >
                Reveal answer
              </button>
              <div className="quiz-nav">
                <button
                  type="button"
                  className="quiz-action-button quiz-action-button--secondary"
                  onClick={() => goToQuiz(Math.max(0, quizIndex - 1))}
                  disabled={quizIndex === 0}
                >
                  <span aria-hidden="true">←</span>
                  Previous
                </button>
                {isLastQuiz ? (
                  <button
                    type="button"
                    className="quiz-action-button quiz-action-button--secondary"
                    onClick={() => setShowSummary(true)}
                    disabled={!selectedAnswer}
                  >
                    Finish review
                    <span aria-hidden="true">→</span>
                  </button>
                ) : (
                  <button
                    type="button"
                    className="quiz-action-button quiz-action-button--secondary"
                    onClick={() => goToQuiz(Math.min(quizzes.length - 1, quizIndex + 1))}
                  >
                    Next
                    <span aria-hidden="true">→</span>
                  </button>
                )}
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
      <header className="topbar">
        <div className="topbar__brand">
          <div className="eyebrow">Missed Context Verification</div>
          <div className="topbar__title-row">
            <h1>Misstery</h1>
            <p>Catch what was missed before it turns into action.</p>
          </div>
        </div>
        <div className="topbar__right">
          <div className="topbar__meta">
            <div className="pill pill--compact">
              <span>Source</span>
              <strong>{inputSource}</strong>
            </div>
            <div className="pill pill--compact">
              <span>Transcript</span>
              <strong>{stats.words} words</strong>
            </div>
            <div className="pill pill--compact">
              <span>API</span>
              <strong>
                {health?.status === "ok"
                  ? `Cognee ${health.cogneeConfigured ? "on" : "off"} / Dify ${health.difyConfigured ? "on" : "off"}`
                  : "Backend offline"}
              </strong>
            </div>
          </div>
          <div className="mode-toggle">
            {Object.entries(THEMES).map(([key, item]) => (
              <button
                key={key}
                type="button"
                className={theme === key ? "active" : ""}
                onClick={() => setTheme(key)}
                aria-label={`Switch to ${item.label} mode`}
                title={item.label}
              >
                <span aria-hidden="true">{item.icon}</span>
              </button>
            ))}
          </div>
        </div>
      </header>

      {(status || error) && (
        <div className={error ? "banner error" : "status-row"}>
          <div className={error ? "" : "status-pill"}>{error || status}</div>
        </div>
      )}

      <main className={`workspace workspace--stacked ${leftPanelCollapsed ? "workspace--focus-result" : ""}`}>
        <section className={`panel control-panel ${leftPanelCollapsed ? "control-panel--collapsed" : ""}`}>
          <div className={`control-panel__toolbar ${leftPanelCollapsed ? "control-panel__toolbar--collapsed" : ""}`}>
            {!leftPanelCollapsed && <div className="control-panel__eyebrow">Steps 1-2</div>}
            <button
              type="button"
              className={`panel-collapse-toggle ${leftPanelCollapsed ? "panel-collapse-toggle--collapsed" : ""}`}
              onClick={() => setLeftPanelCollapsed((current) => !current)}
              aria-expanded={!leftPanelCollapsed}
              aria-label={leftPanelCollapsed ? "Show Step 1 and Step 2 preparation panel" : "Hide Step 1 and Step 2 preparation panel"}
            >
              <span aria-hidden="true">{leftPanelCollapsed ? "▾" : "▴"}</span>
              {leftPanelCollapsed ? "Show prep" : "Hide prep"}
            </button>
          </div>

          {leftPanelCollapsed ? (
            <div className="control-panel__rail">
              <button
                type="button"
                className="rail-chip"
                onClick={() => {
                  setLeftPanelCollapsed(false);
                  setStepVisibility((current) => ({ ...current, input: true }));
                }}
              >
                Step 1
              </button>
              <button
                type="button"
                className="rail-chip"
                onClick={() => {
                  setLeftPanelCollapsed(false);
                  setStepVisibility((current) => ({ ...current, workflow: true }));
                }}
              >
                Step 2
              </button>
            </div>
          ) : (
            <>
          <div className={`step-card ${stepVisibility.input ? "" : "step-card--collapsed"}`}>
            <div className="section-head section-head--foldable">
              <div>
                <span>Step 1</span>
                <h2>Input</h2>
                <p>Choose one input method, complete it, then move the transcript into the workflow.</p>
              </div>
              <button
                type="button"
                className="section-toggle"
                onClick={() => toggleStep("input")}
              >
                {stepVisibility.input ? "Hide" : "Show"}
              </button>
            </div>

            {stepVisibility.input && <div className="step-body input-shell">
              <div className="input-tabs" role="tablist" aria-label="Input method">
                <button
                  type="button"
                  role="tab"
                  aria-selected={inputTab === "text"}
                  className={inputTab === "text" ? "active" : ""}
                  onClick={() => setInputTab("text")}
                >
                  <span className="input-tab__eyebrow">Quickest</span>
                  <strong>Direct text</strong>
                  <span className="input-tab__meta">Paste notes or a full transcript</span>
                </button>
                <button
                  type="button"
                  role="tab"
                  aria-selected={inputTab === "record"}
                  className={inputTab === "record" ? "active" : ""}
                  onClick={() => setInputTab("record")}
                >
                  <span className="input-tab__eyebrow">Browser mic</span>
                  <strong>Live recording</strong>
                  <span className="input-tab__meta">Capture and transcribe a snippet</span>
                </button>
                <button
                  type="button"
                  role="tab"
                  aria-selected={inputTab === "upload"}
                  className={inputTab === "upload" ? "active" : ""}
                  onClick={() => setInputTab("upload")}
                >
                  <span className="input-tab__eyebrow">Files</span>
                  <strong>File upload</strong>
                  <span className="input-tab__meta">Bring in text or audio from disk</span>
                </button>
              </div>

              <div className="input-card input-card--tabbed">
                {inputTab === "text" && (
                  <>
                    <div className="input-card__head">
                      <h3>Paste transcript or notes</h3>
                      <p>Use this when you already have the conversation as text.</p>
                    </div>
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
                        resetAuditWorkspace();
                        setStatus("Transcript loaded from direct text.");
                        setError("");
                      }}
                    >
                      Load text into workspace
                    </button>
                  </>
                )}

                {inputTab === "record" && (
                  <>
                    <div className="input-card__head">
                      <h3>Capture a live snippet</h3>
                      <p>Record in the browser, then send the audio to transcription.</p>
                    </div>
                    <button
                      type="button"
                      className={isRecording ? "danger" : ""}
                      onClick={handleRecordToggle}
                      disabled={busyState === "transcribe"}
                    >
                      {isRecording ? "Stop and transcribe" : "Start recording"}
                    </button>
                  </>
                )}

                {inputTab === "upload" && (
                  <>
                    <div className="input-card__head">
                      <h3>Upload from files</h3>
                      <p>Use one path for the working transcript, and another for extra Cognee context.</p>
                    </div>
                    <div className="upload-stack">
                      <div className="upload-block">
                        <div className="upload-block__head">
                          <strong>Transcript or audio</strong>
                          <p>Load `.txt`, `.mp3`, `.wav`, or browser-recorded audio into the workspace.</p>
                        </div>
                        <label className="file-picker">
                          <input type="file" accept=".txt,.mp3,.wav,audio/*" onChange={handleFileChange} />
                          Choose transcript file
                        </label>
                      </div>

                      <div className="upload-block">
                        <div className="upload-block__head">
                          <strong>Context file to Cognee</strong>
                          <p>Send `.txt`, `.md`, `.json`, `.csv`, `.yaml`, or `.yml` directly into Cognee memory.</p>
                        </div>
                        <label className="file-picker">
                          <input
                            type="file"
                            accept=".txt,.md,.markdown,.json,.csv,.yaml,.yml,text/plain,application/json,text/csv"
                            onChange={handleContextFileChange}
                          />
                          {busyState === "context-upload" ? "Uploading..." : "Upload context file"}
                        </label>
                        {contextUploadMeta && (
                          <div className="upload-meta">
                            <span>Latest context</span>
                            <strong>{contextUploadMeta.fileName}</strong>
                            <p>
                              Added to {contextUploadMeta.datasetName} with {contextUploadMeta.chars} characters.
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>}
          </div>

          <div className={`step-card ${stepVisibility.workflow ? "" : "step-card--collapsed"}`}>
            <div className="section-head section-head--foldable">
              <div>
                <span>Step 2</span>
                <h2>Execute workflow</h2>
                <p>Review the transcript, then run the workflow and wait for quiz output.</p>
              </div>
              <button
                type="button"
                className="section-toggle"
                onClick={() => toggleStep("workflow")}
              >
                {stepVisibility.workflow ? "Hide" : "Show"}
              </button>
            </div>

            {stepVisibility.workflow && <>
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
            </>}
          </div>
            </>
          )}
        </section>

        <aside className="panel result-panel result-panel--priority">
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
