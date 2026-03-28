## Round 2 - Topic Mapping and Search Blueprint

### 1) Thematic clusters (6-8)

### Cluster A - Reproducibility and benchmark-governance for RAG retrieval

**Why relevant:** Round-3 gap memo identified missing evidence on reproducible, auditable evaluation workflows and benchmark-governance practices.
**Search queries:**

* reproducible rag retrieval benchmarking workflow
* auditability versioning retrieval evaluation artifacts
* governance framework for llm rag evaluation pipelines
* reproducibility checklist dense retrieval benchmark
* benchmark drift control in retrieval systems
* experiment traceability for rag evaluation
  **Inclusion:** Retrieval or RAG studies that define reproducibility controls, artifact governance, or audit trails.
  **Exclusion:** Leaderboard-only papers without methodology controls.
  **Target count:** Batch-2: 1

---

### Cluster B - Local-corpus model selection under fixed protocol

**Why relevant:** Core paper claim requires stronger prior-work coverage for local corpus decisions under one controlled protocol.
**Search queries:**

* local corpus embedding model selection fixed protocol
* enterprise document collection retrieval benchmark comparison
* corpus-specific ranking instability embedding models
* practitioner-oriented retrieval model selection
* cross-corpus embedding ranking reproducible evaluation
* local deployment retrieval benchmark framework
  **Inclusion:** Studies comparing multiple embedding models across at least two local or enterprise corpora with controlled settings.
  **Exclusion:** Single-model case studies without cross-model comparison.
  **Target count:** Batch-2: 1

---

### Cluster C - Multilingual comparability and cross-lingual fairness in RAG evaluation

**Why relevant:** Round-3 gap memo showed weak claim coverage for multilingual comparability and judge fairness/calibration.
**Search queries:**

* multilingual rag evaluation calibration llm judge
* cross-lingual fairness retrieval benchmark embeddings
* language-conditioned ranking shifts dense retrieval
* multilingual qrels consistency rag
* non-english enterprise rag benchmark
* cross-language comparability retrieval pipelines
  **Inclusion:** Multilingual retrieval or RAG evaluation with explicit cross-language comparability or fairness analysis.
  **Exclusion:** General multilingual NLP papers without retrieval evaluation.
  **Target count:** Batch-2: 1

---

### Cluster D - Synthetic query and qrels construction quality controls

**Why relevant:** Round-3 gap memo identified missing methodology evidence on synthetic query quality control and qrels construction policy.
**Search queries:**

* synthetic query generation quality control retrieval evaluation
* automatic qrels construction llm judge reliability
* query distribution matching for rag benchmark design
* leakage contamination checks synthetic ir queries
* weak supervision relevance labeling dense retrieval
* abstention adjudication policy llm as judge
  **Inclusion:** Works that report protocols for generating/validating synthetic queries or automatic relevance labels.
  **Exclusion:** Papers using synthetic data without validation protocol details.
  **Target count:** Batch-2: 1

---

### Cluster E - Evaluation-design and human-alignment of LLM-as-judge

**Why relevant:** Round-3 gap memo flagged limited evidence on when judge outputs can replace or complement human judgments.
**Search queries:**

* llm as judge agreement with human evaluators rag
* calibrated llm judge uncertainty scoring retrieval
* judge reliability under domain shift rag evaluation
* evaluator bias and consistency in llm judging
* ranking metrics for judge-human agreement
* robust evaluation design for judge-based qrels
  **Inclusion:** Papers with explicit human-vs-LLM agreement analysis, calibration, uncertainty, or evaluator reliability design.
  **Exclusion:** Studies using LLM-as-judge without agreement evidence.
  **Target count:** Batch-2: 1

---

### Cluster F - Quality-speed-cost tradeoff evidence for deployment decisions

**Why relevant:** Paper claims emphasize deployment-oriented quality-speed tradeoff; Round-3 gap memo asks for stronger prior evidence.
**Search queries:**

* quality latency cost tradeoff embedding retrieval
* efficiency effectiveness tradeoff rag retrieval systems
* deployment constraints semantic search benchmarking
* throughput accuracy tradeoff vector retrieval
* model size latency retrieval performance comparison
* operational benchmarking for rag pipelines
  **Inclusion:** Studies reporting retrieval quality together with latency, throughput, runtime, or cost signals.
  **Exclusion:** Quality-only papers without operational metrics.
  **Target count:** Batch-2: 1

---

### Cluster G - Optional targeted closure if one gap remains weak

**Why relevant:** Keep one slot flexible to close the weakest unresolved gap after first five papers are screened.
**Search queries:**

* targeted retrieval benchmark gap closure
* domain shift failure analysis rag retrieval
* reproducible multilingual rag benchmarking
* enterprise rag evaluation protocol validation
* calibration drift llm judge multilingual
  **Inclusion:** Strong direct fit to the weakest open gap after initial Round-2 intake.
  **Exclusion:** Indirect relevance that does not close an identified claim gap.
  **Target count:** Batch-2: 0-1

---

## 2) Acquisition plan (5-7 papers total, peer-reviewed first)

* **Batch-2 target:** 6 papers (minimum 5, maximum 7).
* **Default distribution:** A:1, B:1, C:1, D:1, E:1, F:1, G:0-1 optional.
* **Decision rule:** If one cluster fails quality screening, reallocate that slot to Cluster G.

## 3) Claim coverage map

* **Claim C1:** local corpus-specific selection is necessary.
  * Clusters: B, F
* **Claim C2:** reusable and transparent benchmarking workflow is a contribution.
  * Clusters: A, B
* **Claim C3:** language and domain conditions change outcomes.
  * Clusters: C, B
* **Claim C4:** quality-speed tradeoff is deployment-critical.
  * Clusters: F, B
* **Claim C5:** automated synthetic query and judge-based labeling are methodologically justified but bounded.
  * Clusters: D, E, C

## 4) No-overlap guide (Related Work vs Method/Experiments/Results)

* **Keep in Related Work:**
  * Prior study categories, comparative findings, evaluation-design strengths and limits, unresolved gaps.
* **Keep out of Related Work (belongs elsewhere):**
  * Method internals of this paper, implementation pipeline details, fixed snapshot setup tables, this paper's metric results.
* **Transition requirement:**
  * End each thematic block with one sentence that states unresolved gap and links to this paper's positioning.

## 5) Round-2 paper intake template (required gap tag per paper)

Use one block per candidate paper:

```text
paper_id:
required_gap: [reproducibility gap | local-corpus gap | multilingual gap | evaluation-design gap | quality-speed gap | judge-reliability gap]
cluster:
title:
authors:
year:
venue:
publication_type: [journal | conference | workshop | preprint]
doi_or_url:
abstract:
why_relevant_to_this_paper:
evidence_for_gap_closure:
optional: dataset_context, retrieval_setting, embedding_family, evaluation_metrics, reported_limitations
confidence_note: [high | medium | low]
```

## 6) Batch-2 screening checklist (quick gate)

* Has explicit relevance to one `required_gap` tag.
* Contains usable metadata (authors, year, title).
* Provides claim-level evidence, not only broad narrative.
* Avoids duplication with already integrated Round-1 evidence.
