# Learning Notes (Roman Urdu)

Har phase ke baad yahan simple alfaaz mein likha jayega: kya banaya, kyun, kaise kaam karta hai,
aur Claude Code ka kaun sa mechanism mirror karta hai.

---

## Phase 0 — Research aur Plan

### Kya kiya?
- Professor ki instructions, dono architecture files aur teen reference repos parhe.
- DeepSeek ki official docs se API ki asal details check ki.
- Project folder banaya, input files copy ki, aur `.gitignore` banaya taake API key kabhi GitHub par na jaye.

### Do programs ka farq (sab se zaroori baat)
- **Program A = Code Agent**: ye hum banayenge. Ek chhota sa "Claude Code" jaisa program jo DeepSeek AI se baat karta hai.
- **Program B = Space Fractions game**: ye hum **nahi** likhenge. Ye agent khud DeepSeek ki madad se likhega.
  Hum sirf agent ko instructions (system prompt) aur tools denge.

### Agent kaise kaam karta hai (simple misaal)
Socho ek naya intern hai (AI model). Hum usay:
1. **Kaam ki detail** dete hain (spec.json — architecture docs ko saaf JSON mein badal kar).
2. **Auzaar (tools)** dete hain: file parhna, file likhna, file mein chhoti tabdeeli karna, test chalana.
3. Ek **loop** chalate hain: intern bolta hai "ye file likho" → hum likh kar result batate hain → wo agla qadam batata hai...
   jab tak wo "finish" na bole.
Yahi Claude Code ka **agent loop** hai.

### Research mein kya naya mila?
- OpenRouter par DeepSeek V4 ka **free** model ab maujood nahi. Demo run ke liye baad mein faisla karna hoga.
- DeepSeek mein "thinking mode" default ON hota hai. Hum isay OFF rakhenge (sasta). ON karein to `reasoning_content`
  wapas bhejna zaroori hai warna error aata hai.
- Flash model ka naya naam `deepseek-flash` hai.

### Input docs ki ghaltiyan (agent ko pakarni hain)
- Docs **web/microservices** keh rahi hain, professor **desktop** app chahte hain → agent adapt karega
  (PostgreSQL → SQLite, REST → Python functions, Kubernetes → zaroorat nahi).
- Testing table khaali hai, file naam mismatch (`question_ddl.sql` vs `game_ddl.sql`), UML mein galat syntax (`->>`).

### Interview mein kaise samjhayein
"Main ne Claude Code ke andar ke mechanisms parhe — agent loop, tools, plan mode, context compaction,
permissions — aur unka chhota Python version banaya jo DeepSeek ke saath architecture docs se poora desktop game generate karta hai."

---

## Phase 1 — Config, LLM providers, aur Parsers

### 1) LLM Provider (AI se baat karne wala hissa)
- `LLMProvider` ek **interface** hai, yani ek "plug ka shape". Agent sirf is shape ko jaanta hai.
- Is shape mein do plug lagte hain:
  - **DeepSeekProvider** — asal API (`deepseek-v4-pro`), paise lagte hain. Thinking mode hum OFF bhejte hain (sasta).
    Error aaye (429 rate limit, 500/503 server) to thora ruk kar dobara try karta hai (**retry with backoff**).
    401 (ghalat key) ya 402 (balance khatam) par saaf message deta hai.
  - **MockProvider** — nakli AI. Hum pehle se likh dete hain ke "pehle ye tool call karo, phir ye". Koi paisa nahi,
    har dafa bilkul same result → tests reliable. Ye claw-code ke **mock parity harness** jaisa hai.
- `pricing.py` — tokens se kharcha nikalta hai (cache hit sasta, cache miss mehnga, output sab se mehnga; peak hours mein 2×).

### 2) Config
- API key GUI se `%APPDATA%\SpaceFractionsAgent\config.json` mein save hogi — repo mein kabhi nahi.
- Dev mode mein `.env` se bhi parh leta hai. `mask_key()` key ke sirf aakhri 4 harf dikhata hai.

### 3) Parsers (markdown → JSON) — bina AI ke
- `doc_parser.py`: architecture doc ke sections A–L, tables, code blocks (OpenAPI, SQL, proto, k8s, CSV), requirements,
  components, assumptions nikalta hai.
- `uml_parser.py`: 13 PlantUML diagrams parhta hai — actors, use cases, classes (attributes/methods), states, sequence messages.
  Ghalat syntax (`->>`, object diagram mein `participant`) par **crash nahi karta**, warning likh deta hai.
- `spec.py`: dono ko jor kar `spec.json` banata hai + `domain_model` (chhota khulasa jo AI ko diya jayega).
  Is mein koi timestamp nahi — har dafa bilkul same, taake DeepSeek ka **prompt cache** hit ho aur kharcha kam ho.
- **Issues khud pakre** (7 types): khaali testing table, file naam mismatch, kam requirements, copy-paste justifications,
  duplicate blocks, web vs desktop conflict, UML syntax ghaltiyan.

### 4) Security
- Pre-commit hook: har commit se pehle `sk-...` jaisi key dhoondta hai; mile to commit **rok** deta hai.

### Interview line
"Main ne input ko pehle deterministic parser se structured JSON mein badla — ye sasta, testable aur reproducible hai.
AI sirf wahan use hota hai jahan zaroori hai: design decisions aur code likhna."
