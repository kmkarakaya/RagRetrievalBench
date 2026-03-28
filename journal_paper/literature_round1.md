## Cluster A — RAG Retrieval Quality ve Grounding Bağımlılığı

Bu küme, RAG sistemlerinde retrieval bileşeninin doğruluk, bağlamsal güvenilirlik ve halüsinasyon kontrolündeki rolünü ele alan çalışmaları içerir.

| Makale                                                                                                                                                                                                        | Dergi/Yıl                           | Cilt–Sayı / DOI                                  | Anahtar Noktalar                                                                                                                                                                                                                                                                                                                                                                                                       |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Yutao Zhu, Huaying Yuan, Shuting Wang, Jiongnan Liu, Wenhan Liu, Chenlong Deng, Haonan Chen, Zheng Liu, Zhicheng Dou ve Ji‑Rong Wen, “Large Language Models for Information Retrieval: A Survey”** | ACM Trans. Information Systems, 2025 | 44(1); DOI 10.1145/3748304                         | LLM’ler ile bilgi erişim entegrasyonunu inceler; query‑rewriter, retriever, reranker ve reader bileşenlerini özetler ve IR‑LLM birleşiminde halüsinasyon riski gibi sorunları tartışır.                                                                                                                                                                                                                    |
| **Xingzheng Gao & Chang Xing, “A Retrieval‑Augmented Generation Framework Based on a Knowledge Graph of Cybersecurity Vulnerabilities in Power Networks”**                                           | IEEE Access, 2025                    | 13:186693‑186710; DOI 10.1109/ACCESS.2025.3627277 | Elektrik şebekelerindeki güvenlik açıklarını temsil eden bir bilgi grafiği ile RAG akışı kurar; benzerlik retrieval’i ve problem‑çözme modüllerinin kaldırılmasının cevap uygunluğu ve doğruluğunu ciddi oranda düşürdüğü gösterilir.                                                                                                                                                     |
| **Binita Saha, Utsha Saha ve Muhammad Zubair Malik, “QuIM‑RAG: Advancing Retrieval‑Augmented Generation with Inverted Question Matching for Enhanced QA Performance”**                              | IEEE Access, 2024                    | 12:185401‑185410; DOI 10.1109/ACCESS.2024.3513155 | Domain‑özgü veriden potansiyel sorular üretip bunları kullanıcı sorguları ile eşleştirerek retrieval kalitesini artıran “ters soru eşleştirme” mekanizmasını tanıtır; BERTScore ve RAGAS ile yapılan değerlendirmelerde geleneksel RAG’ı geride bırakır.                                                                                                                                      |
| **Rong Hu, Sen Liu, Panpan Qi, Jingyi Liu ve Fengyuan Li, “ICCA‑RAG: Intelligent Customs Clearance Assistant Using Retrieval‑Augmented Generation”**                                                | IEEE Access, 2025                    | 13:39711‑39726; DOI 10.1109/ACCESS.2025.3544408   | Gümrük mevzuat belgelerini bilgi grafiği olarak modeller ve RAG ile birleştirir. Değerlendirme sonuçlarına göre cevap doğruluğu %20, cevap uygunluğu %15 ve bağlamsal doğruluk %19 artmıştır![](https://chatgpt.com/backend-api/estuary/content?id=file_00000000521072438d69d91865054368&ts=492949&p=fs&cid=1&sig=12fef8786ace119aecd45373f7105ca7f337af2b55c37c163bc2e847504e3a3d&v=0)researchgate.net. |
| **Shima Ghasemi & Azadeh Shakery, “Harnessing the Power of Metadata for Enhanced Question Retrieval in Community Question Answering”**                                                                | IEEE Access, 2024                    | 12:65768‑65779; DOI 10.1109/ACCESS.2024.3395449   | Topluluk soru‑cevap forumlarında soru benzerliği bulmak için kategori ve yanıt bilgilerini kullanan iki transformer tekniği önerir; RAG tabanlı bir soru genişletme modeli ile MAP 51.47 elde ederek mevcut yöntemleri aşar.                                                                                                                                                                                |

**Özet:** Bu kümedeki çalışmalar, retrieval bileşeninin doğru ve anlamlı içerik üretimindeki kritik rolünü vurgular. Gao ve Chang  retrieval ve problem‑çözme modüllerinin kaldırılmasının performansı ciddi biçimde düşürdüğünü gösterirken, Saha ve arkadaşları ters soru eşleştirme sayesinde retrieval kalitesini artırır. ICCA‑RAG çalışması, gümrük belgelerinde bilgi grafiği tabanlı retrieval’in cevap doğruluğunu ve bağlamsal doğruluğu artırdığını rapor eder![](https://chatgpt.com/backend-api/estuary/content?id=file_00000000521072438d69d91865054368&ts=492949&p=fs&cid=1&sig=12fef8786ace119aecd45373f7105ca7f337af2b55c37c163bc2e847504e3a3d&v=0)researchgate.net. Survey makalesi ise LLM‑IR entegrasyonunda halüsinasyon riskini azaltmak için RAG bileşenlerinin dikkatle seçilmesi gerektiğini vurgular.

## Cluster B — Korpus/Alan/Dil Kaymasına Göre Embedding Modeli Seçimi

Bu küme, embedding modelinin seçimindeki alan ve dil bağımlılığını araştıran çalışmaları kapsar.

Paper:

```
 @article{Mikkelsen_2026, title={Context Matters More Than Model Choice: A Multi-Corpus Benchmark of Embedding Models for Clinical Retrieval-Augmented Generation (Preprint)}, url={http://dx.doi.org/10.2196/preprints.94241}, DOI={10.2196/preprints.94241}, publisher={JMIR Publications Inc.}, author={Mikkelsen, Yngve}, year={2026}, month=feb }
```

Background:

Retrieval-augmented generation (RAG) systems increasingly support clinical decision-making by grounding large language model outputs in verifiable evidence. The retrieval component is foundational: if the correct document is not retrieved, downstream generation cannot recover it. Despite this, embedding model selection for clinical RAG remains guided by general-domain benchmarks with limited clinical coverage. Given the heterogeneity of clinical documentation across institutions, specialties, and electronic health record systems, it is unclear whether general-domain model rankings generalize to clinical retrieval tasks.

Objective:

This study evaluated whether clinical context variables—corpus type (encompassing differences in document length, medical specialty, and structural characteristics) and query format—have effects on retrieval performance comparable to or exceeding those of embedding model choice.

Methods:

Ten embedding models were benchmarked against BM25 on three clinical corpora (MTSamples medical transcriptions, n=500; PMC-Patients case reports, n=500; Mistral-7B-generated synthetic clinical notes, n=500). Twelve embedding configurations were evaluated across 3 corpora × 2 query formats (keyword vs natural language) × 4 chunking strategies, yielding 294 experimental conditions. Primary metrics included MRR@10, P@1, Recall@10/20/50/100, and NDCG@10, with bootstrap confidence intervals. Relative factor contributions were quantified using factorial ANOVA with η² effect sizes, including all two-way interactions.

Results:

In a factorial ANOVA across 288 balanced embedding conditions, embedding model choice explained 40.8% of variance in MRR@10 (η²=0.408), corpus type 24.6%, and query format 19.2%. Chunking strategy explained minimal variance (η²=0.002). The model × query format interaction (η²=0.029, p<.001) indicated differential query sensitivity across models. A model × corpus interaction (η²=0.040, p<.001) indicated that model rankings shifted meaningfully across corpora. Combined context variables (corpus + query format + context interactions) explained 49.0% of total variance, compared with 47.6% for model-related effects. Model rankings were moderately unstable under keyword queries (Kendall τ=0.59, 95% CI [0.21, 0.89]) but highly stable under natural language queries (τ=0.82–0.87). BM25 achieved near-perfect retrieval on PMC-Patients in this known-item setting (MRR@10=0.999). Domain-specific models (BioBERT, ClinicalBERT) performed worse than general-purpose embeddings despite biomedical pretraining, with mean pairwise cosine similarity exceeding 0.90, indicating that all embeddings clustered in a narrow cone. A validation experiment using reduced-lexical-dependence queries—generated from GPT-4o-extracted metadata rather than document text—supported rank stability across query derivations (Kendall τ=0.59–0.90, mean 0.76, all p<.005) and showed that BM25 remained strong on structured case reports (MRR@10=0.980).

Conclusions:

Clinical context variables explained as much variance in retrieval performance as embedding model choice, and model × corpus interactions showed that rankings are not portable across documentation types. Validation with reduced-lexical-dependence queries supported rank stability across query derivations. These results argue against reliance on general-domain leaderboards for clinical RAG deployment and support mandatory local validation as a methodological requirement.

paper:

```
 @article{Margit_2025, title={Evaluation of Embedding Models for Hungarian Question-Answer Retrieval on Domain-Specific and Public Benchmarks}, volume={17}, ISSN={2061-2079}, url={http://dx.doi.org/10.36244/icj.2025.4.1}, DOI={10.36244/icj.2025.4.1}, number={4}, journal={Infocommunications journal}, publisher={Infocommunications Journal}, author={Margit, Antal}, year={2025}, pages={2–11} }
```

## Abstract

Embedding models have become a fundamental component of modern natural language processing, yet their performance in morphologically rich, low-resource languages such as Hungarian remains underexplored. In this paper, we present a systematic evaluation of state-of-the-art embedding models for Hungarian question-answer retrieval. We construct two complementary evaluation datasets: (i) a domain-specific corpus collected from company documentation, preprocessed into topical chunks with human-verified question-answer pairs, and (ii) the publicly available HuRTE benchmark. Using FAISS as the vector database, we compare eight multilingual and crosslingual embedding models. Performance is measured using Mean Reciprocal Rank (MRR) and Recall@k. Results show substantial variation across models and datasets, with notable differences between domain-specific and general-purpose retrieval tasks. We complement the evaluation with error analysis, highlighting challenges posed by Hungarian morphology and compounding, and discuss trade-offs in efficiency. Our findings provide the first comparative study of embedding-based retrieval in Hungarian, offering practical guidance for downstream applications and setting a foundation for future research in Hungarian representation learning. The dataset and the corresponding evaluation code are publicly accessible at https://github.com/margitantal68/ hu-embeddings-hurte.

paper:

```
@article{sajja2025domain,
  title={Domain-specific embedding models for hydrology and environmental sciences: enhancing semantic retrieval and question answering},
  author={Sajja, Ramteja and Sermet, Yusuf and Demir, Ibrahim},
  journal={Water Science \& Technology},
  volume={92},
  number={9},
  pages={1328--1342},
  year={2025},
  publisher={IWA Publishing}
}
```

## Abstract

Large Language Models (LLMs) have shown strong performance across natural language processing tasks, yet their general-purpose embeddings often fall short in domains with specialized terminology and complex syntax, such as hydrology and environmental science. This study introduces HydroEmbed, a suite of open-source sentence embedding models fine-tuned for four QA formats: multiple-choice (MCQ), true/false (TF), fill-in-the-blank (FITB), and open-ended questions. Models were trained on the HydroLLM Benchmark, a domain-aligned dataset combining textbook and scientific article content. Fine-tuning strategies included MultipleNegativesRankingLoss, CosineSimilarityLoss, and TripletLoss, selected to match each task's semantic structure. Evaluation was conducted on a held-out set of 400 textbook-derived QA pairs, using top-k similarity-based context retrieval and GPT-4o-mini for answer generation. Results show that the fine-tuned models match or exceed performance of strong proprietary and open-source baselines, particularly in FITB and open-ended tasks, where domain alignment significantly improves semantic precision. The MCQ/TF model also achieved competitive accuracy. These findings highlight the value of task- and domain-specific embedding models for building robust retrieval-augmented generation (RAG) pipelines and intelligent QA systems in scientific domains. This work represents a foundational step toward HydroLLM, a domain-specialized language model ecosystem for environmental sciences.

Paper:

```
 @article{Song_2024, title={Mlke: A Benchmark for Multilingual Knowledge Editing on Large Language Model}, url={http://dx.doi.org/10.2139/ssrn.4882305}, DOI={10.2139/ssrn.4882305}, publisher={Elsevier BV}, author={Song, Ran and Gao, Shengxiang and Mao, Cunli and Yu, Zhengtao}, year={2024} }
```

### Abstract

Multilingual Large Language Models (mLLMs) have demonstrated remarkable performance in various downstream tasks, yet they still contain factual errors.  Knowledge editing aims to rectify these errors by modifying the knowledge within pretrained model.  However, current knowledge editing methods predominantly focus on monolingual contexts and neglect the complexities and interrelations of multiple languages. In this paper, we introduce a multilingual knowledge editing benchmark designed to evaluate the performance of knowledge editing methods on mLLMs. This benchmark treats different knowledge items as editing subjects and includes multiple languages.  It assesses methods based on four key aspects: accuracy, reliability, generalizability, and consistency. We conducted a thorough analysis to ensure the  robustness and usability for the benchmark. Additionally, we propose a baseline approach that adapts existing monolingual knowledge editing methods for use in multilingual environments.  Comprehensive experimental results demonstrate the effectiveness of our benchmark in multilingual knowledge editing.

Paper:

```
@inproceedings{Baysan_2025, title={TR-MTEB: A Comprehensive Benchmark and Embedding Model Suite for Turkish Sentence Representations}, url={http://dx.doi.org/10.18653/v1/2025.findings-emnlp.471}, DOI={10.18653/v1/2025.findings-emnlp.471}, booktitle={Findings of the Association for Computational Linguistics: EMNLP 2025}, publisher={Association for Computational Linguistics}, author={Baysan, Mehmet Selman and Gungor, Tunga}, year={2025}, pages={8867–8887} }
```

##### Abstract

We introduce TR-MTEB, the first large-scale, task-diverse benchmark designed to evaluate sentence embedding models for Turkish. Covering six core tasks as classification, clustering, pair classification, retrieval, bitext mining, and semantic textual similarity, TR-MTEB incorporates 26 high-quality datasets, including native and translated resources. To complement this benchmark, we construct a corpus of 34.2 million weakly supervised Turkish sentence pairs and train two Turkish-specific embedding models using contrastive pretraining and supervised fine-tuning. Evaluation results show that our models, despite being trained on limited resources, achieve competitive performance across most tasks and significantly improve upon baseline monolingual models. All datasets, models, and evaluation pipelines are publicly released to facilitate further research in Turkish natural language processing and low-resource benchmarking.

Paper: @ARTICLE{11426790,
  author={Abimbola, Jeremiah O. and Kuaban, Godlove Suila and Ajayi, Samuel Abiola},
  journal={IEEE Access},
  title={Open-Source Embedding Models: A Comprehensive Survey of Techniques, Benchmarks, and Applications},
  year={2026},
  volume={14},
  number={},
  pages={41284-41302},
  doi={10.1109/ACCESS.2026.3670100}}


## Abstract:

Embedding models are fundamental to modern Natural Language Processing (NLP), transforming textual data into dense vector representations that capture semantic meaning and relationships. This systematic survey focuses exclusively on the landscape of open-source embedding models, tracing their evolution from early word embeddings (Word2Vec, GloVe) to advanced contextual and multimodal architectures (BERT, Sentence-BERT, BGE, Nomic Embed). Moving beyond descriptive narratives, our core contribution is a structured, comparative analysis of these models’ operational tradeoffs, including model size, embedding dimensionality, inference latency, and memory consumption. This systematic review spans the literature up to 2025 drawing upon 70 papers to provide a critical assessment of standardized benchmarks, such as MTEB, and their limitations regarding bias and robustness. Finally, the paper concludes by discussing the broad applicability of embedding models across diverse domains, including search engines, recommendation systems, fraud detection, and healthcare, and offer recommendations for effective model selection and utilization.

paper: @INPROCEEDINGS{10892801,
  author={Kalantari, Mahmood and Feghhi, Mehdi and Mozayani, Nasser},
  booktitle={2024 15th International Conference on Information and Knowledge Technology (IKT)},
  title={Benchmarking Embedding Models for Persian-Language Semantic Information Retrieval},
  year={2024},
  volume={},
  number={},
  pages={53-58},
  doi={10.1109/IKT65497.2024.10892801}}


## Abstract:

The increasing reliance on semantic-based retrieval, especially in the context of large language model-powered chat-bots, underscores the need for robust evaluation of embedding models. In this study, the performance of embedding models for Persian-language information retrieval was investigated, addressing an area with limited prior research. Four question-answering datasets were used-two publicly available datasets adapted for this study and two custom datasets derived from translations. A systematic evaluation of 17 embedding models was conducted, and the models were ranked based on their accuracy in retrieving relevant content using similarity measures such as dot product, cosine similarity, and L2 distance. The findings emphasize the adaptability of these models to diverse textual data and address the specific challenges posed by the Persian language. This research bridges a critical gap in Persian-language retrieval tasks, providing a comprehensive benchmark for evaluating embedding models in semantic information retrieval scenarios.

### Cluster C — Local/enterprise/document-collection benchmarking pipelines

**Why relevant:** Method ve Intro, yerel doküman koleksiyonu için tekrarlanabilir pipeline katkısını vurguluyor.

Paper: @inproceedings{10.1145/3721201.3721396,
author = {Cummings, Aaron and Zhang, Xinyue and Olaniran, Mercy and Akintomide, Modupe},
title = {RAG Pipeline for Domain Specific Applications: A Case Study in Disseminating Dementia Care Practices},
year = {2025},
isbn = {9798400715396},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3721201.3721396},
doi = {10.1145/3721201.3721396},
booktitle = {Proceedings of the ACM/IEEE International Conference on Connected Health: Applications, Systems and Engineering Technologies},
pages = {139–143},
numpages = {5},
location = {Yeshiva University Museum, New York, NY, USA},
series = {CHASE '25}
}

## Abstract:

 In closed-domain Question Answering (QA), Large Language Models (LLMs) often fail to deliver responses specialized enough for niche subdomains. Broadly trained models may not capture the nuanced terminology and contextual precision required in these fields, which frequently lack domain-specific conversational data and face computational constraints. To address this, we propose a methodology leveraging a Retrieval-Augmented Generation (RAG) framework that integrates data extraction with fine-tuning using domain-specific question-answer pairs. Our approach employs Question-Answer Generation (QAG) to create tailored training datasets, enabling fine-tuned models to incorporate specialized jargon and context while remaining computationally accessible to domain experts. To exemplify this methodology, we demonstrate its application within the medical domain through a case study centered on the creation of a dementia care chat assistant. A significant benefit of this approach lies in its ease of replication across various domains and scalability for integration into diverse user groups, making it a versatile solution for enhancing chat assistants.

Paper: @INPROCEEDINGS{11166412,
  author={Yozkan, Elif and Supriyanto, Ilham},
  booktitle={2025 International Conference on Artificial Intelligence, Computer, Data Sciences and Applications (ACDSA)},
  title={How Reliable Is Semantic Search in Industrial Computing Domain? A Statistical Evaluation Pipeline},
  year={2025},
  volume={},
  number={},
  pages={1-6},
  doi={10.1109/ACDSA65407.2025.11166412}}


## Abstract:

Statistical evaluation is crucial for improving semantic search, especially in highly technical domains such as industrial computing. Although qualitative human assessments are often used, they are time-consuming, expensive, and cover only a limited range of scenarios. A key challenge in conducting statistical evaluation is generating a realistic ground truth test set that accurately represents complex domain-specific terminology, including users’ persona and background knowledge. However, once this test set is established, it enables systematic experimentation to refine AI search configurations. Our study finds that increasing text volume improves search accuracy, leading to a precision increase from 77% to 82%. However, an excess of specialized terms, indicated by a relatively higher token-to-word conversion rate, can potentially weaken semantic understanding. To mitigate this, a hybrid approach that integrates semantic search with the traditional lexical method is utilized, with OpenAI embeddings to further enhance search performance.

Paper:

@misc{steve_2023, title={Domain-Specific Contextualized Embedding : A Systematic Literature Review}, url={osf.io/jqdca_v1}, DOI={10.31219/osf.io/jqdca}, publisher={OSF Preprints}, author={Steve, Michael}, year={2023}, month={May} }

## Abstract:

Word embedding has successfully resolved various Natural Language Processing (NLP) problems. Unfortunately, the method has a weakness in detecting polysemy and homonym. Those issues led to the emergence of a new approach, which is named contextualized embedding. Many researchers examined such embedding to resolve problems in various particular areas. However, the studies are published disparate and complex. To provide a more comprehensive overview of contextualized embedding research in specific domains, a Systematic Literature Review (SLR) was conducted. The SLR results show that research on domain-specific contextualized embedding pays more attention to solving NLP problems in the Healthcare domain, by the percentage of more than 65%, followed by the Academic & Research field and other areas. The popularity of the Healthcare domain is associated with the availability of abundant datasets, mostly in English. BERT is the most contextualized embedding models used for domain-specific tasks, followed by ELMo, and finally GPT-1, as well as XLNET. Almost all reviewed papers reported performance improvements by using domain-specific contextualized embedding in their proposed model. Contextualized embedding can resolve polysemy problems and reduces overfitting. Besides, many downstream tasks have proved the ease implementation of the embedding. The shortcomings of this embedding are the high requirements of computation resources, the long execution time, and the computation complexity. Domain-specific contextualized embedding has resolved many problems, mostly classification tasks (e.g., Question and Answering) and tagging tasks (e.g., Named Entity Recognition). The two evaluation methods for measuring the performance of domain-specific contextualized embedding are Intrinsic evaluation and Extrinsic evaluation.

Paper: 

@INPROCEEDINGS{11152931,
  author={Khan, Muhammad Zakir and Ge, Yao and Ullah, Ubaid and Ansari, Shuja and Imran, Muhamamd and Abbasi, Qammer H.},
  booktitle={IEEE INFOCOM 2025 - IEEE Conference on Computer Communications Workshops (INFOCOM WKSHPS)},
  title={TelcoGPT: A Hybrid Embedding Approach for Telecom-Specific Q&A and Code Retrieval},
  year={2025},
  volume={},
  number={},
  pages={1-6},
  doi={10.1109/INFOCOMWKSHPS65812.2025.11152931}}

## Abstract:

This paper presents TelcoGPT, a specialised question-answering (Q&A) and code retrieval system for telecommunications that combines retrieval-augmented generation (RAG) with domain-specific optimizations. TelcoGPT introduces three key enhancements: (1) a HybridEmbedding method-ology integrating text-embedding models with telecom-specific filtering mechanisms; (2) an advanced document processing pipeline with adaptive chunking and technical term density scoring; and (3) a dual-path query engine optimized for both question-answering and code retrieval tasks. Evaluation on the RedPajama-Data-1T arxiv subset demonstrates that hybrid embedding approach achieves mean reciprocal rank (MRR) of 0.89 and hit rate (HR) of 0.94 with optimal configuration (thresh-old=0.8, chunk size=12K, k=15), outperforming single-embedding approaches by 5-7%. The hybrid RAG implementation increases MRR by 8.5% (0.82 to 0.89) and HR by 10.6% (0.85 to 0.94). TelcoGPT achieves 95% accuracy in domain-specific Q&A tasks versus 87% for base models, while maintaining higher technical term density scores (0.90 vs 0.81). For code retrieval, our system demonstrates 93% execution success rate with comprehensive error handling, surpassing baseline approaches by 6-8%. Comparative analysis with GPT-3.5, GPT-4, and LLAMA-2/3 shows significant improvements in context relevance (0.92 vs 0.84), information accuracy (0.95 vs 0.89), faithfulness (0.84 to 0.92), and relevancy (0.83 to 0.93), demonstrating the effectiveness of our architecture for telecommunications applications.

Paper:

@inproceedings{10.1145/3759355.3759360,
author = {Szab\'{o}, Barbara No\'{e}mi and Gy\"{o}ngy\"{o}ssy, Natabara M\'{a}t\'{e} and Dalos, Attila},
title = {Applied Domain Adaptation of LLM-based Document Embeddings for Engineering Knowledge Retrieval},
year = {2025},
isbn = {9798400715891},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3759355.3759360},
doi = {10.1145/3759355.3759360},
booktitle = {Proceedings of the Intelligent Robotics FAIR 2025},
pages = {29–37},
numpages = {9},
keywords = {retrieval-augmented generation, embedding model, fine-tuning, contrastive learning, engineering knowledge management},
location = {
},
series = {IntRob '25}
}

## Abstract:

Technical documentation related to engineering and manufacturing is often stored in unstructured documents, rendering search and information retrieval processes time-consuming and inefficient. Recently, Retrieval-Augmented Generation (RAG) pipelines and AI agents leveraging dense retrieval capabilities of document embedding language models have emerged as promising solutions to address these challenges. However, these methods typically lack semantic understanding of industry-specific terminology, limiting their retrieval accuracy in specialized domains.

In this paper, we identify the fine-tuning of dense retrieval models within RAG systems as an effective and cost-efficient approach for enhancing their industry- and enterprise-specific knowledge. We further investigate whether pretraining based on Masked Language Modeling is necessary for these scenarios. Through empirical evaluation, we show that automatic data preprocessing and synthetic data generation derived from human-labeled retrieval examples provide a cost-effective strategy for preparing fine-tuning data.

By training and evaluating an embedding model on 21 281 engineering documents encompassing best practices and lessons learned, totaling 75 million whitespace delimited words, we achieve a significant increase of  in Recall@10 for domain-specific retrieval performance, while retaining generalization capabilities on general retrieval tasks as measured by the Massive Text Embedding Benchmark (MTEB). Additionally, we present ablation studies on the effects of loss function symmetry, masking ratio in MLM, and sequence packing strategies.

Our results demonstrate that domain-specific fine-tuned embeddings consistently outperform both open-source and state-of-the-art proprietary general retrieval models, establishing this fine-tuning strategy as a viable solution even in computationally constrained, single-GPU training environments.


### Cluster D — Synthetic query generation and LLM-as-judge/qrels construction

**Why relevant:** Method’te query üretimi ve binary relevance labeling LLM destekli; buna metodolojik dayanak lazım.

Paper: 

@INPROCEEDINGS{11402164,
  author={Bellard, Broderick and Liu, Xinyi Celine and Lohani, Raima and Raza, Shaina and Velmovitksy, Pedro Elkind and Pham, Quynh and Saha, Shumit},
  booktitle={2025 IEEE International Conference on Big Data (BigData)},
  title={Development and Evaluation of an Agentic RAG with Embedded LLM-as-a Judge for Heart Failure Management: A Pilot Study},
  year={2025},
  volume={},
  number={},
  pages={7770-7774},
  doi={10.1109/BigData66926.2025.11402164}}


## Abstract:

This pilot study develops and evaluates an agentic Retrieval-Augmented Generation (RAG) system for heart failure management, integrating an LLM-as-a-Judge (LLM-J) to autonomously critique and refine a primary chatbot's outputs. The LLM-J evaluates responses on five dimensions—accuracy, safety, robustness, empathy, and clarity—within a two-stage feedback loop. Testing on 25 synthetic HF question–answer (QA) pairs demonstrated significant improvement in the robustness of responses (+0.39 mean **Δ**) by adding critical safety thresholds and escalation guidance, while maintaining high accuracy, safety, and empathy. A small subset (4.3%) failed the second safety gate due to contextual drift, triggering a reliable fallback message. The system operated with a mean total cycle time of 15.74 seconds and a mean cost of $0.00312 per query, confirming its scalability for real-time clinical support. This work demonstrates the feasibility of a lightweight, selfcorrecting AI governance layer to enhance the safety and reliability of patient-facing digital health tools.


Paper

@inproceedings{10.1145/3721146.3721958,
author = {Wang, Yifan and Birman, Kenneth P.},
title = {Diagnosing and Resolving Cloud Platform Instability with Multi-modal RAG LLMs},
year = {2025},
isbn = {9798400715389},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3721146.3721958},
doi = {10.1145/3721146.3721958},
booktitle = {Proceedings of the 5th Workshop on Machine Learning and Systems},
pages = {139–147},
numpages = {9},
keywords = {root cause analysis, RAG LLM, AI-Ops},
location = {World Trade Center, Rotterdam, Netherlands},
series = {EuroMLSys '25}
}

Abstract 

Today's cloud-hosted applications and services are complex systems, and a performance or functional instability can have dozens or hundreds of potential root causes. Our hypothesis is that by combining the pattern matching capabilities of modern AI tools with a natural multi-modal RAG LLM interface, problem identification and resolution can be simplified. ARCA is a new multi-modal RAG LLM system that targets this domain. Step-wise evaluations show that ARCA outperforms state-of-the-art alternatives. Rather than battling this reality, our work focuses on approximate match (an idea familiar in text-based contexts), but generalizes the mechanism to to encompass data modalities other than text. The idea, though, is similar: **RAG  LLMs** for search document collections treat each **query a***s** a vector database search for documents "similar" to the **query**. The output of this step is the closest resolved bug. We then prompt the Generator **LLM** with the input shown in Fig. 8. An additional benefit brought by using **LLM**-**as**-a-**judge** is that we can ask the **evaluating *LLM** to explain how and why it reached certain conclusions, either in summary form or even **as** a sequence of step-bystep decisions, allowing the SREs to better understand the results and hence increasing confidence in its coverage.


Paper: 


```
 @inproceedings{Kunuku_2025, title={Multimodal Quiz Generation via RAG with LLM-as-Judge Evaluation}, url={http://dx.doi.org/10.1109/fie63693.2025.11328244}, DOI={10.1109/fie63693.2025.11328244}, booktitle={2025 IEEE Frontiers in Education Conference (FIE)}, publisher={IEEE}, author={Kunuku, Mourya Teja and Dehbozorgi, Nasrin}, year={2025}, month=nov, pages={1–7} }
```


## Abstract:

This paper presents a novel multimodal quiz generation framework that integrates audio, visual, and textual data using a Retrieval-Augmented Generation (RAG) architecture. The system leverages LLaVA for vision-language understanding and LLaMA 3.1 for text generation to produce contextually relevant and pedagogically meaningful multiple-choice questions (MCQs) from lecture videos. This approach addresses key limitations of traditional text-only quiz generation models by capturing richer, multimodal information. The system was tested on a real-world use case, generating 15 MCQs from the first lecture in an introductory computer science course. To evaluate the effectiveness of the generated quizzes, we designed a two-stage evaluation framework. In the first stage, we assessed retrieval and generation performance using standard metrics such as Hit Rate, Mean Reciprocal Rank (MRR), Correctness, Relevance, and Faithfulness. In the second stage, we examined how closely AI evaluations align with human expert judgments. We involved four human raters and three LLM-as-Judge models—Claude 3 Sonnet, GPT-4, and LLaMA 3.1—to evaluate each question. To analyze agreement, we used Percentage Agreement, Cohen's Kappa, Spearman's Rho, and Krippendorff's Alpha, capturing both exact matches and ordinal consistency. Our results show high retrieval accuracy and reasonable alignment between LLM based and human assessments, particularly in factual and procedural questions. However, discrepancies emerged in questions requiring deeper reasoning or visual interpretation, where human raters exhibited stronger consistency. These findings highlight the strengths of LLMs in scalable content generation, while reinforcing the need for human oversight in evaluating complex educational tasks. This work takes a significant step toward more human-aligned and effective AI-driven assessment systems.


Paper: 

@INPROCEEDINGS{11431871,
  author={Taemkaeo, Chinnatip and Saetia, Chanatip and Chalothorn, Tawunrat and Titijaroonroj, Taravichet},
  booktitle={2026 18th International Conference on Knowledge and Smart Technology (KST)},
  title={Enhancing HR Support in a Thai Organization with LLM-Based Question Answering},
  year={2026},
  volume={},
  number={},
  pages={1-6},
  doi={10.1109/KST67832.2026.11431871}}


## Abstract:

Large language models (LLMs) enhanced with retrieval-augmented generation (RAG) and multimodal inputs are increasingly used as interfaces to organizational knowledge. However, their effectiveness in specialized, non-English enterprise settings-such as Thai HR support-remains largely unclear. In many Thai organizations, employees frequently ask detailed HR-related questions, but the relevant information is scattered across internal webpages, PDF manuals, announcements, and images, making it difficult for generic LLMs to provide accurate, policy-consistent responses. To address this issue, we develop a multimodal RAG pipeline that combines hybrid dense-sparse retrieval over a vector database and evaluate six LLM models on a private Thai Visual Question Answering (VQA) HR dataset consisting of 226 questions and reference images across five HR topics. The results show that recent multimodal models, especially Qwen2.5-VL, achieve the best performance, with the highest averages in correctness (0.54), relevance (0.75), and helpfulness (0.64), clearly outperforming older vision-language systems and a text-only reasoning model. For large-scale answer evaluation, we apply an LLM-as-a-judge approach using GPT-4.1 and Gemini 2.5 Flash. We found that it serves as a generally reliable, though imperfect, substitute for human evaluation.

Paper: 


```
 @article{Wen_2026, title={CalibJudge: Calibrated LLM-as-a-Judge for Multilingual RAG with Uncertainty-Aware Scoring}, url={http://dx.doi.org/10.20944/preprints202603.1324.v1}, DOI={10.20944/preprints202603.1324.v1}, publisher={MDPI AG}, author={Wen, Chenfeiyu and Zhu, Ao and Long, Runkun and Huang, Hejun and Jiang, Junjie and Lee, Chi Shing}, year={2026}, month=mar }
```


###### Abstract

Large Language Models (LLMs) serving as automatic evaluators (LLM-as-a-Judge) have become essential for assessing Retrieval-Augmented Generation (RAG) systems. However, in multilingual settings, these judges exhibit significant calibration drift across languages, producing scores that are neither comparable nor aligned with human judgments. We present CalibJudge, a post-hoc calibration framework that addresses this challenge through: (1) language-specific temperature scaling, (2) uncertainty quantification, and (3) selective abstention. We evaluate CalibJudge on the MEMERAG benchmark covering five languages. Our experiments demonstrate that CalibJudge improves correlation with human annotations by up to 21.3% relative improvement in Kendall's while reducing cross-lingual fairness gaps by 42% and achieving 88% balanced accuracy at 70% coverage.
