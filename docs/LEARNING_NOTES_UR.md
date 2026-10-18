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
