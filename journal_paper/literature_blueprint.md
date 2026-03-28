## Round 1 — Topic Mapping and Search Blueprint

### 1) Thematic clusters (6–8)

### Cluster A — RAG retrieval quality and grounding dependence

**Why relevant:** Intro ve Method, RAG kalitesinin retrieval kalitesine bağımlı olduğunu temel varsayım olarak kuruyor; bunu literatürde konumlandırmak gerekiyor.
**Search queries:**

* **retrieval-augmented generation retrieval quality grounding reliability**
* **RAG retrieval component impact downstream generation quality**
* **knowledge-intensive NLP retrieval augmented generation evaluation**
* **RAG retrieval errors hallucination grounding**
* **dense retrieval for RAG effectiveness**
* **RAG retrieval evaluation metrics MAP NDCG MRR**
  **Inclusion:** RAG’de retrieval bileşeninin kalite etkisini açık ölçen çalışmalar (journal/conference öncelikli).
  **Exclusion:** Sadece generative model tuning odaklı, retrieval analizi olmayan çalışmalar.
  **Target count:** Batch-1: 2, Batch-2: 1

---

### Cluster B — Embedding model selection under corpus/domain/language shift

**Why relevant:** Paper’ın ana iddiası “model seçimi corpus/language/domain’e bağlıdır”; Results’te language/domain effect var.
**Search queries:**

* **embedding model selection corpus-specific retrieval**
* **domain shift dense retrieval embedding model performance**
* **multilingual embedding retrieval benchmark cross-language**
* **embedding robustness across domains retrieval tasks**
* **sentence transformer model comparison retrieval datasets**
* **language-specific retrieval performance embeddings**
  **Inclusion:** Corpus-dependent model ranking değişimini gösteren karşılaştırmalı retrieval çalışmaları.
  **Exclusion:** Sadece classification/STS benchmark, retrieval bağlamı olmayan çalışmalar.
  **Target count:** Batch-1: 2, Batch-2: 2

---

### Cluster C — Local/enterprise/document-collection benchmarking pipelines

**Why relevant:** Method ve Intro, yerel doküman koleksiyonu için tekrarlanabilir pipeline katkısını vurguluyor.
**Search queries:**

* **local corpus retrieval benchmarking pipeline**
* **enterprise RAG evaluation framework document collections**
* **domain-specific semantic search evaluation pipeline**
* **reproducible retrieval benchmark workflow**
* **practitioner-oriented retrieval benchmarking**
* **benchmark automation for document retrieval systems**
  **Inclusion:** Pipeline/workflow sunan, artifact/reproducibility vurgusu olan çalışmalar.
  **Exclusion:** Yalnızca tek model performans raporu, framework/pipeline olmayan çalışmalar.
  **Target count:** Batch-1: 1, Batch-2: 1

---

### Cluster D — Synthetic query generation and LLM-as-judge/qrels construction

**Why relevant:** Method’te query üretimi ve binary relevance labeling LLM destekli; buna metodolojik dayanak lazım.
**Search queries:**

* **synthetic query generation for retrieval evaluation**
* **LLM as judge relevance labeling retrieval**
* **automatic qrels generation information retrieval**
* **weak supervision relevance judgments dense retrieval**
* **LLM-generated evaluation sets retrieval benchmarks**
* **query generation from corpus passages IR**
  **Inclusion:** Otomatik query/qrels üretimi veya LLM-judge güvenilirliği/limitleri.
  **Exclusion:** İnsan qrels çalışmaları ama otomasyonla ilişkisiz olanlar (tamamen farklı kurgu).
  **Target count:** Batch-1: 1, Batch-2: 1

---

### Cluster E — Reproducibility, comparability, and evaluation protocol control

**Why relevant:** Paper’ın farkı “same protocol / controlled setup / reusable artifacts”; bunu literatürdeki evaluation-practice ile karşılaştırmak önemli.
**Search queries:**

* **reproducibility in information retrieval benchmarks**
* **controlled evaluation protocol dense retrieval**
* **cross-dataset comparability retrieval evaluation**
* **benchmark artifacts reproducible IR pipelines**
* **evaluation leakage retrieval benchmark design**
* **experimental control in semantic retrieval studies**
  **Inclusion:** Protokol kontrolü, comparability, reproducibility tartışan retrieval benchmark çalışmaları.
  **Exclusion:** Benchmark sunup metodolojik kontrol tartışmayan “leaderboard only” raporlar.
  **Target count:** Batch-1: 1, Batch-2: 1

---

### Cluster F — Quality–speed tradeoff in embedding-based retrieval

**Why relevant:** Results’te merkezi bulgu kalite-hız tradeoff; related work bunu dayandırmalı.
**Search queries:**

* **embedding retrieval quality latency tradeoff**
* **dense retrieval efficiency effectiveness trade-off**
* **semantic search throughput latency benchmarking**
* **model size vs retrieval performance sentence embeddings**
* **practical deployment constraints vector retrieval**
* **cost-performance tradeoff embedding models**
  **Inclusion:** Hem effectiveness hem operational metric (latency/throughput/cost) raporlayan çalışmalar.
  **Exclusion:** Sadece kalite metriği verip operasyonel tarafı olmayan çalışmalar.
  **Target count:** Batch-1: 1, Batch-2: 1

---

### Cluster G — Multilingual and legal/regulatory retrieval contexts (optional but strong)

**Why relevant:** Experiments sonuçları TR/EN ve education/law ayrımı içeriyor; domain-language bağlamı güçlendirir.
**Search queries:**

* **multilingual legal document retrieval embeddings**
* **cross-lingual dense retrieval domain-specific corpora**
* **regulatory document semantic retrieval benchmark**
* **Turkish document retrieval embedding models**
* **domain-specific multilingual semantic search evaluation**
  **Inclusion:** Multilingual + domain-specific retrieval benchmark/analysis.
  **Exclusion:** Genel multilingual NLP ama retrieval odaklı olmayan çalışmalar.
  **Target count:** Batch-1: 0–1, Batch-2: 1–2

---

## 2) Acquisition plan (12–16 papers total, peer-reviewed first)

* **Batch-1 (7–10 papers):**
  * A:2, B:2, C:1, D:1, E:1, F:1 (+ opsiyonel G:0–1)
  * Amaç: iskelet argümanı ve temel literatür omurgasını kurmak.
* **Batch-2 (5–7 papers):**
  * B:+2, D:+1, E:+1, F:+1, G:+1–2
  * Amaç: gap memo’daki zayıf noktaları hedefli kapatmak (özellikle multilingual/domain + qrels otomasyonu + tradeoff).

## 3) Claim coverage map

* **Claim C1:** “Local corpus-specific selection is necessary; leaderboard is insufficient.”
  * Clusters: A, B, C
* **Claim C2:** “Controlled, reusable pipeline provides actionable evidence.”
  * Clusters: C, E
* **Claim C3:** “Language and domain materially change embedding outcomes.”
  * Clusters: B, G
* **Claim C4:** “Quality-speed tradeoff is decision-critical in practice.”
  * Clusters: F, C
* **Claim C5:** “Automated query/qrels/reporting workflow is methodologically justified but bounded.”
  * Clusters: D, E

## 4) No-overlap guide (Related Work vs other sections)

* **Related Work’te olmalı:**
  * Önceki çalışmaların problem yaklaşımı, yöntem sınıfları, bulgu yönleri, sınırlılıkları.
  * Bu paper’ın literatüre göre konumlanması (fark, katkı, sınırlar).
* **Method’e kaymamalı:**
  * Bu paper’daki adım adım pipeline detayları, artifact akışı, implementation mekanikleri.
* **Experiments’e kaymamalı:**
  * Bu snapshot’a özgü dataset provenance, parameter tabloları, model roster ayrıntıları.
* **Results’e kaymamalı:**
  * Bu paper’ın metrik sonuçları, karşılaştırmalı bulgular, sayısal yorumlar.
* **Related Work kapanışı:**
  * “Literatürde hangi boşluklar kalıyor ve bu paper hangi boşluğu hedefliyor?” cümlesiyle Method’e temiz geçiş.
