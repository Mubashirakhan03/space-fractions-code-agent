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

---

## Phase 2 — Tools, Sandbox, Agent Loop (agent ka dil)

### 1) Agent loop — do layers (Claude Code jaisa)
- **Bahar wali layer** (`Agent.run`): poora session sambhalti hai — messages, tokens, kharcha, `state.json`.
  Phases chalati hai: **plan → implement → verify ⇄ fix → report**.
- **Andar wali layer** (`_run_phase`): ek chakkar (loop): AI ko messages + tools bhejo → AI tool calls lautaye →
  hum tools chalayein → result `role:"tool"` message mein wapas → dobara... jab tak `submit_plan`/`finish` na aaye.
- Agar AI tool call na kare → 2 dafa yaad dilate hain (nudge); jawab beech mein kat jaye (`length`) → "continue" bolte hain.

### 2) Plan mode
- Plan phase mein AI sirf **parh** sakta hai (list_dir, read_file...) aur `update_todos` + `submit_plan`.
  Likhne ki koshish kare to "Permission denied: not available in plan mode" milta hai.
- `submit_plan` mein AI `DESIGN_DECISIONS.md` ka content + file tree + notes deta hai; **harness khud** file likhta hai
  (bilkul Claude Code ke ExitPlanMode jaisa).

### 3) Tools aur Sandbox (hifazat)
- Har path output folder ke andar hi hona chahiye — `../` ya `C:\...` block. `agent_run/` folder AI ke liye read-only.
- `.bat/.exe/.ps1` jaisi files likhna mana. Koi shell nahi.
- `edit_file`: exact text dhoond kar badalta hai; text **ek hi dafa** mile warna error ("Found 2 matches...").
  Pehle file **poori parhna** zaroori; parhne ke baad kisi aur ne file badli ho to dobara parhna padta hai.
- `write_files`: ek hi call mein kai files — **requests bachti hain** (paisa bachta hai).
- Read-only tools ek saath (parallel) chalte hain, likhne wale ek-ek kar ke.
- Tool ka error crash nahi karta — AI ko "Error: ..." result milta hai taake wo khud theek kare.

### 4) Self-verification
- AI `finish` bole to harness khud check karta hai: zaroori files hain? sab `.py` compile hoti hain? pytest pass?
- Fail ho to report AI ko "FIX phase" mein milti hai — max `fix_rounds` dafa.
- Tests **bundled interpreter** se chalte hain (`app.main --run-pytest`) — exe mein bhi Python ki zaroorat nahi.

### 5) Context management (3 levels)
1. Bara tool output (8000+ chars) → poora file mein save, AI ko sirf shuru + aakhir + file ka path.
2. Microcompact → purane tool results ki jagah chhota placeholder.
3. Auto-compact → beech ki baatcheet ka khulasa (summary) bana kar replace; system prompt + spec kabhi nahi chhede
   (taake **cache** hit hota rahe), aur current phase ki instructions dobara likh di jati hain.

### 6) Budget aur hifazati limits
- Max LLM requests (40), max cost ($1), max tokens, max steps, Stop button → run aaram se rukta hai, sab save.
- **Resume**: `state.json` se wahin se dobara shuru.
- **Replay**: recorded transcript ke AI jawab dobara chala kar poora project dobara banata hai — **zero kharcha**,
  report par saaf likha hota hai "REPLAY of a recorded run".

### 7) Testing (mock parity harness)
- 15 end-to-end scenarios MockProvider ke saath: happy path, fix round, plan mode write denied, budget stop, cost cap,
  resume, nudges, length continue, auto-compaction, replay, user stop, bara output, ghalat JSON. Sab bina paise ke.

### Interview line
"Mera agent Claude Code ki tarah two-layer loop chalata hai, plan mode mein sirf read-only tools deta hai, code ko
search-and-replace se edit karta hai, khud tests chala kar apni ghaltiyan theek karta hai, aur har request ka
kharcha track karta hai. Sab kuch MockProvider se deterministic tested hai."

---

## Phase 3 — GUI (desktop window)

### Kya bana
- **customtkinter** window (Windows desktop look). Chalane ka tareeqa (dev): `python -m app.main`.
- **Bayen taraf (settings):** DeepSeek API key (•••• chhupi hui, 👁 se dikh sakti hai), "Remember key", Test connection,
  Thinking mode, Mock mode; dono `.md` files ke pickers (samples/ se khud bhar jaate hain); output folder; limits
  (steps, requests, cost $, fix rounds); "Ask before every file write".
- **Neeche fixed buttons:** Generate, Stop, Resume, Replay, Open output folder, **▶ Run generated game**.
- **Dayen taraf:** phases ki patti (Plan → Implement → Verify → Fix → Report; chal raha = orange, ho gaya = green),
  tabs: Log (har tool call: `→ write_files main.py, ...`), Todos (○ ◐ ●), Spec preview, Report; neeche kharcha line.

### Window freeze kyun nahi hoti? (zaroori concept)
- Agent ek **alag thread** (worker) mein chalta hai. Wo har cheez ek **queue** mein daalta hai (log, phase, todos...).
- Window har 100ms baad queue check karti hai aur screen update karti hai. Is liye AI ka jawab aane tak bhi window chalti rehti hai.
- "Ask before write" mein worker ruk kar intezar karta hai; window Yes/No poochti hai aur jawab wapas worker ko deti hai.

### Hifazati baatein
- Asal DeepSeek run se pehle **confirmation**: price + is run ki hard limits ($ aur requests).
- Naya run sirf **khaali folder** mein (do runs mix na hon; hum kuch delete nahi karte).
- Mock mode aur Replay par upar saaf banner: "MOCK MODE — no API calls" / "REPLAY of recorded run".
- Mock demo project ke README aur window par likha hai: "NOT generated by an LLM" — imaandari.

### Interview line
"GUI non-blocking hai: agent worker thread mein chalta hai aur events queue ke zariye UI tak aate hain. User har waqt
Stop kar sakta hai, state save hoti hai, aur Resume se wahin se dobara chal sakta hai."
