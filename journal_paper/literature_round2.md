
Cluster A - Reproducibility and benchmark-governance for RAG retrieval

**Why relevant:** Round-3 gap memo identified missing evidence on reproducible, auditable evaluation workflows and benchmark-governance practices.
**Search** Results:

Paper: 

```
@article{wang2025reproducibility,
  title={On The Reproducibility Limitations of RAG Systems},
  author={Wang, Baiqiang and Zhao, Dongfang and Tallent, Nathan R and Guo, Luanzheng},
  journal={arXiv preprint arXiv:2509.18869},
  year={2025}
}
```

Absract:

Retrieval-Augmented Generation (RAG) is increasingly employed in generative AI-driven scientific workflows to integrate rapidly evolving scientific knowledge bases, yet its reliability is frequently compromised by non-determinism in their retrieval components. This paper introduces ReproRAG, a comprehensive benchmarking framework designed to systematically measure and quantify the reproducibility of vector-based retrieval systems. ReproRAG investigates sources of uncertainty across the entire pipeline, including different embedding models, precision, retrieval algorithms, hardware configurations, and distributed execution environments. Utilizing a suite of metrics, such as Exact Match Rate, Jaccard Similarity, and Kendall's Tau, the proposed framework effectively characterizes the trade-offs between reproducibility and performance. Our large-scale empirical study reveals critical insights; for instance, we observe that different embedding models have remarkable impact on RAG reproducibility. The open-sourced ReproRAG framework provides researchers and engineers productive tools to validate deployments, benchmark reproducibility, and make informed design decisions, thereby fostering more trustworthy AI for science.

Paper


```
@phdthesis{xu2025end,
  title={An end-to-end benchmarking framework for retrieval-augmented generation systems},
  author={Xu, Yuan},
  year={2025},
  school={University of Illinois Urbana-Champaign}
}
```

Absract:

 Current evaluation methods often focus exclusively on generation quality or individual components in isolation, such as vector database latency or model inference speed. This fragmented approach leaves developers without a clear understanding of the complex interactions between storage and compute layers, leading to suboptimal resource utilization and unpredictable performance in production environments. To bridge this gap, this thesis introduces  **RAG-based AI system benchmarking (RASB)** , a modular and system-aware framework designed to evaluate end-to-end RAG performance. RASB addresses the heterogeneity of RAG pipelines by providing a configuration-driven architecture that supports various backends, a lightweight system profiler for hardware metrics, and a workload generator for realistic data streaming. By integrating diverse real-world datasets and supporting a wide range of embedding and generation models, RASB enables developers to analyze the sensitivity of throughput to parameters like batch size and indexing strategies. Ultimately, this work provides a reproducible testbed and extensive experimental baselines on high-performance hardware to guide future system-optimized AI research.

Paper:


```
@article{friel2024ragbench,
  title={Ragbench: Explainable benchmark for retrieval-augmented generation systems},
  author={Friel, Robert and Belyi, Masha and Sanyal, Atindriyo},
  journal={arXiv preprint arXiv:2407.11005},
  year={2024}
}
```

Retrieval-Augmented Generation (RAG) has become a standard architectural pattern for incorporating domain-specific knowledge into user-facing chat applications powered by Large Language Models (LLMs). RAG systems are characterized by (1) a document retriever that queries a domain-specific corpus for context information relevant to an input query, and (2) an LLM that generates a response based on the provided query and context. However, comprehensive evaluation of RAG systems remains a challenge due to the lack of unified evaluation criteria and annotated datasets. In response, we introduce RAGBench: the first comprehensive, large-scale RAG benchmark dataset of 100k examples. It covers five unique industry-specific domains and various RAG task types. RAGBench examples are sourced from industry corpora such as user manuals, making it particularly relevant for industry applications. Further, we formalize the TRACe evaluation framework: a set of explainable and actionable RAG evaluation metrics applicable across all RAG domains. We release the labeled dataset at [this https URL](https://huggingface.co/datasets/rungalileo/ragbench). RAGBench explainable labels facilitate holistic evaluation of RAG systems, enabling actionable feedback for continuous improvement of production applications. Thorough extensive benchmarking, we find that LLM-based RAG evaluation methods struggle to compete with a finetuned RoBERTa model on the RAG evaluation task. We identify areas where existing approaches fall short and propose the adoption of RAGBench with TRACe towards advancing the state of RAG evaluation systems.

Paper:


```
@inproceedings{ali2024establishing,
  title={Establishing traceability between natural language requirements and software artifacts by combining rag and llms},
  author={Ali, Syed Juned and Naganathan, Varun and Bork, Dominik},
  booktitle={International Conference on Conceptual Modeling},
  pages={295--314},
  year={2024},
  organization={Springer}
}
```

Software Engineering aims to effectively translate stakeholders’ requirements into executable code to fulfill their needs. Traceability from natural language use case requirements to classes in a UML class diagram, subsequently translated into code implementation, is essential in systems development and maintenance. Tasks such as assessing the impact of changes and enhancing software reusability require a clear link between these requirements and their software implementation. However, establishing such links manually across extensive codebases is prohibitively challenging. Requirements, typically articulated in natural language, embody semantics that clarify the purpose of the codebase. Conventional traceability methods, relying on textual similarities between requirements and code, often suffer from low precision due to the semantic gap between high-level natural language requirements and the syntactic nature of code. The advent of Large Language Models (LLMs) provides new methods to address this challenge through their advanced capability to interpret both natural language and code syntax. Furthermore, representing code as a knowledge graph facilitates the use of graph structural information to enhance traceability links. This paper introduces an LLM-supported retrieval augmented generation approach for enhancing requirements traceability to the class diagram of the code, incorporating keyword, vector, and graph indexing techniques, and their integrated application. We present a comparative analysis against conventional methods and among different indexing strategies and parameterizations on the performance. Our results demonstrate how this methodology significantly improves the efficiency and accuracy of establishing traceability links in software development processes.

Paper:

```
@article{xu2025ragops,
  title={RAGOps: Operating and Managing Retrieval-Augmented Generation Pipelines},
  author={Xu, Xiwei and Weytjens, Hans and Zhang, Dawen and Lu, Qinghua and Weber, Ingo and Zhu, Liming},
  journal={arXiv preprint arXiv:2506.03401},
  year={2025}
}
```

Recent studies show that 60% of LLM-based compound systems in enterprise environments leverage some form of retrieval-augmented generation (RAG), which enhances the relevance and accuracy of LLM (or other genAI) outputs by retrieving relevant information from external data sources. LLMOps involves the practices and techniques for managing the lifecycle and operations of LLM compound systems in production environments. It supports enhancing LLM systems through continuous operations and feedback evaluation. RAGOps extends LLMOps by incorporating a strong focus on data management to address the continuous changes in external data sources. This necessitates automated methods for evaluating and testing data operations, enhancing retrieval relevance and generation quality. In this paper, we (1) characterize the generic architecture of RAG applications based on the 4+1 model view for describing software architectures, (2) outline the lifecycle of RAG systems, which integrates the management lifecycles of both the LLM and the data, (3) define the key design considerations of RAGOps across different stages of the RAG lifecycle and quality trade-off analyses, (4) highlight the overarching research challenges around RAGOps, and (5) present two use cases of RAG applications and the corresponding RAGOps considerations.


### Cluster B - Local-corpus model selection under fixed protocol

**Why relevant:** Core paper claim requires stronger prior-work coverage for local corpus decisions under one controlled protocol.
Search Results:

Paper: 

```
@inproceedings{yoon2025embedding,
  title={Embedding-Converter: A Unified Framework for Cross-Model Embedding Transformation},
  author={Yoon, Jinsung and Arik, Sercan O},
  booktitle={Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)},
  pages={25464--25482},
  year={2025}
}
```

Embedding models play a crucial role in machine learning. However, the continuous development of new models presents a major challenge: migrating to a potentially superior model often requires the computationally expensive process of re-embedding entire datasets—without any guarantee of performance improvement. This paper presents Embedding-Converter, a novel framework for efficiently transforming embeddings between different models, thus avoiding costly ‘re-embedding’. The proposed approach achieves 100 times faster and cheaper computations in real-world applications. Experiments show that Embedding-Converter not only streamlines transitions to new models, but can also improve upon the source model’s performance, approaching that of the target model. This facilitates efficient evaluation and broader adoption of new embedding models by significantly reducing the overhead of model switching. Furthermore, Embedding-Converter addresses latency limitations by enabling the use of smaller models for online tasks while still benefiting from the performance of larger models offline. By promoting the release of converters alongside new embedding models, Embedding-Converter fosters a more dynamic and accessible ecosystem for embedding model development and deployment.

Paper


```
@article{dvovravckova2025analyzing,
  title={Analyzing word embeddings and their impact on semantic similarity: Through extreme simulated conditions to real dataset characteristics},
  author={Dvo{\v{r}}{\'a}{\v{c}}kov{\'a}, Lucie},
  journal={Neural Computing and Applications},
  volume={37},
  number={19},
  pages={13765--13793},
  year={2025},
  publisher={Springer}
}
```


This study investigates the behavior and characteristics of word embeddings through a series of experiments, focusing on models such as Word2Vec, FastText, and BERT. First, we analyze word embeddings under extreme simulated conditions by creating a data corpus without any interrelation of words and compare the resulting embeddings with randomly initialized vectors. This experiment reveals the tendency of word embedding models to create apparent word relationships even in the absence of real contextual connections. Second, we examine the evolution of word similarity with respect to increasing frequency of co-occurrence, demonstrating how embedding similarity changes as word co-occurrence frequency increases and identifying potential saturation effects. Third, we employ machine learning models-including random forest and XGBoost—to predict word similarity based on various statistical and lexical characteristics derived from real-world data. We identify influential factors such as co-occurrence frequency, context correlation, word frequency, and human-judged similarity scores, which significantly contribute to the prediction of word similarity. The prediction of semantic similarity was formulated as both regression and classification tasks, achieving high accuracy, with the random forest regression model yielding a Pearson correlation of 0.84 (p !' 5e-145). Interpretability methods such as feature importance, partial dependence plots (PDP), and local interpretable model-agnostic explanations (LIME) were used to reveal important relationships and provide insights into the factors influencing embedding similarity. Our findings contribute to a deeper understanding of how word embeddings capture semantic similarity and the factors that influence this process, offering valuable implications for the development of more transparent natural language processing models.

Paper: 


```
@article{cohen2025wixqa,
  title={Wixqa: A multi-dataset benchmark for enterprise retrieval-augmented generation},
  author={Cohen, Dvir and Burg, Lin and Pykhnivskyi, Sviatoslav and Gur, Hagit and Kovynov, Stanislav and Atzmon, Olga and Barkan, Gilad},
  journal={arXiv preprint arXiv:2505.08643},
  year={2025}
}
```


Retrieval-Augmented Generation (RAG) is a cornerstone of modern question answering (QA) systems, enabling grounded answers based on external knowledge. Although recent progress has been driven by open-domain datasets, enterprise QA systems need datasets that mirror the concrete, domain-specific issues users raise in day-to-day support scenarios. Critically, evaluating end-to-end RAG systems requires benchmarks comprising not only question--answer pairs but also the specific knowledge base (KB) snapshot from which answers were derived. To address this need, we introduce WixQA, a benchmark suite featuring QA datasets precisely grounded in the released KB corpus, enabling holistic evaluation of retrieval and generation components. WixQA includes three distinct QA datasets derived from [this http URL](http://wix.com/) customer support interactions and grounded in a snapshot of the public Wix Help Center KB: (i) WixQA-ExpertWritten, 200 real user queries with expert-authored, multi-step answers; (ii) WixQA-Simulated, 200 expert-validated QA pairs distilled from user dialogues; and (iii) WixQA-Synthetic, 6,222 LLM-generated QA pairs, with one pair systematically derived from each article in the knowledge base. We release the KB snapshot alongside the datasets under MIT license and provide comprehensive baseline results, forming a unique benchmark for evaluating enterprise RAG systems in realistic enterprise environments.

Paper:


```
@article{luo2025domain,
  title={Domain-Specific Retrieval-Augmented Generation with Adaptive Embedding and Knowledge Distillation-Based Re-Ranking},
  author={Luo, Hao and Luo, Xiong and Zhao, Weibo and Peng, Qiaojuan and Chen, Ke and Liu, Yinghui and Du, Congcong},
  journal={Processes},
  volume={14},
  number={1},
  pages={99},
  year={2025},
  publisher={MDPI}
}
```


Retrieval-augmented generation (RAG) has emerged as an effective approach for analyzing massive and diverse data. It offers promising avenues for energy management and intelligent decision support amid the accelerating digital transformation of the power industry. However, when applied to this specialized domain, traditional RAG systems face two key challenges: (1) poor comprehension of domain-specific terminology, leading to irrelevant retrieval, and (2) limited precision in re-ranking the retrieved results. To address these limitations, this paper presents an innovative integrated optimization framework. The framework enhances RAG performance in the electric power domain through two key strategies. First, we adapt a base embedding model to the domain using contrastive learning and iteratively refine hard negative samples to improve retrieval quality. Second, we employ a large language model (LLM) as a teacher to distill re-ranking knowledge into a lightweight bidirectional encoder representations from transformers (BERT) model, using a hybrid loss function that combines mean squared error (MSE) loss and margin ranking loss. The framework aims to simultaneously improve the model’s understanding of domain-specific terminology and the re-ranking accuracy of critical information. Experimental results on both a private power-domain dataset and the public DuReader_robust benchmark demonstrate that the proposed framework achieves significant performance gains. Comprehensive ablation studies confirm the necessity of each component and reveal their synergistic effects within the framework. Furthermore, sensitivity analyses of key hyperparameters confirm the effectiveness of our hybrid loss and identify optimal configurations that enhance both retrieval and generation performance. This work not only introduces an effective optimization framework tailored for domain-specific RAG applications but also advances industrial intelligence by enhancing the accuracy and reliability of information services.



### Cluster C - Multilingual comparability and cross-lingual fairness in RAG evaluation

**Why relevant:** Round-3 gap memo showed weak claim coverage for multilingual comparability and judge fairness/calibration.
**Search** Results:

Paper:


```
 @inproceedings{Iscan_2024, title={Enhancing RAG Pipeline Performance with Translation-Based Embedding Strategies for Non-English Documents}, url={http://dx.doi.org/10.1109/asyu62119.2024.10756977}, DOI={10.1109/asyu62119.2024.10756977}, booktitle={2024 Innovations in Intelligent Systems and Applications Conference (ASYU)}, publisher={IEEE}, author={Iscan, Can and Ozara, Muhammet Furkan and Akbulut, Akhan}, year={2024}, month=oct, pages={1–6} }
```

Despite the advances in multilingual embedding models, they often underperform compared to embedding doc-uments in English, which limits the effectiveness of Retrieval-Augmented Generation (RAG) systems in non-English question-answering contexts. This disparity poses a significant barrier for non-English speakers to access high-quality AI-driven re-trieval systems. To address this challenge, this paper proposes a novel approach that leverages English embeddings enhanced by translation. Our approach involves translating texts into English and then embedding them while preserving the original information as metadata. By utilizing robust English and multi-lingual embedding models, we achieve superior results in RAG systems. We present a comprehensive approach for constructing a question-answering system using GPT-40 technology, which leverages translation models to enhance English embeddings. We conducted actual studies to compare the suggested methodology with conventional methods using various embedding models, employing the RAGAS framework. Initial findings indicate that our method greatly improves the retrieval effectiveness of RAG systems in non-English environments, attaining higher context precision and recall metrics. This adaptable solution incorporates English embeddings into multilingual applications, providing a versatile and effective method to improve non-English scenarios by using the capabilities of translation models.

Paper: 

```
@inproceedings{nezhad2025cross,
  title={CROSS: Analyzing the Trade-offs in Long-Context Cross-lingual Retrieval},
  author={Nezhad, Sina Bagheri and Agrawal, Ameeta},
  booktitle={ICLR 2025 Workshop on Foundation Models in the Wild},
  year={2025}
}
```

Cross-lingual information retrieval in long-context settings faces challenges such as the "lost-in-the-middle" phenomenon and computational inefficiencies. We introduce CROSS (Cross-lingual Retrieval Optimized for Scalable Solutions), a two-phase retrieval framework that integrates multilingual embeddings with efficient candidate selection to enhance retrieval-augmented generation (RAG). Evaluating CROSS on the newly developed mLongRR-V2 benchmark—covering seven languages and 49 language pairs—we demonstrate substantial improvements in retrieval accuracy, scalability to 512,000-token contexts, and robustness across linguistic structures. Compared to baseline large language models (LLMs), CROSS significantly mitigates mid-context retrieval failures while reducing computational overhead. Our results establish CROSS as an efficient and scalable solution for multilingual long-context retrieval.

Paper:


```
@inproceedings{mekonnen2025optimized,
  title={Optimized Text Embedding Models and Benchmarks for Amharic Passage Retrieval},
  author={Mekonnen, Kidist Amde and Alemneh, Yosef Worku and de Rijke, Maarten},
  booktitle={Findings of the Association for Computational Linguistics: ACL 2025},
  pages={10428--10445},
  year={2025}
}
```

Neural retrieval methods using transformer-based pre-trained language models have advanced multilingual and cross-lingual retrieval. However, their effectiveness for low-resource, morphologically rich languages such as Amharic remains underexplored due to data scarcity and suboptimal tokenization. We address this gap by introducing Amharic-specific dense retrieval models based on pre-trained Amharic BERT and RoBERTa backbones. Our proposed RoBERTa-Base-Amharic-Embed model (110M parameters) achieves a 17.6% relative improvement in MRR@10 and a 9.86% gain in Recall@10 over the strongest multilingual baseline, Arctic Embed 2.0 (568M parameters). More compact variants, such as RoBERTa-Medium-Amharic-Embed (42M), remain competitive while being over 13**×** smaller. Additionally, we train a ColBERT-based late interaction retrieval model that achieves the highest MRR@10 score (0.843) among all evaluated models. We benchmark our proposed models against both sparse and dense retrieval baselines to systematically assess retrieval effectiveness in Amharic. Our analysis highlights key challenges in low-resource settings and underscores the importance of language-specific adaptation. To foster future research in low-resource IR, we publicly release our dataset, codebase, and trained models at https://github.com/kidist-amde/amharic-ir-benchmarks.


Paper:

@article{10.1145/3777415,
author = {Iana, Andreea and Glava\v{s}, Goran and Paulheim, Heiko},
title = {Multilinguality in MIND: Advancing Cross-lingual News Recommendation with a Multilingual Dataset},
year = {2026},
issue_date = {September 2026},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
volume = {4},
number = {3},
url = {https://doi.org/10.1145/3777415},
doi = {10.1145/3777415},
journal = {ACM Trans. Recomm. Syst.},
month = mar,
articleno = {39},
numpages = {36},
keywords = {Multilingual news dataset, news recommendation, low-resource languages, cross-lingual recommendation, machine translation}
}

Digital news platforms rely on recommendation systems to meet the diverse information needs of readers. However, most research focuses on major, resource-rich languages, overlooking the linguistic diversity of online communities. Moreover, existing work typically assumes monolingual news consumption, neglecting polyglot users, and resulting in a lack of multilingual benchmarks for developing recommenders suited to multilingual and low-resource contexts. To address this gap, we introduce xMIND, an open, multilingual news recommendation dataset created by machine translating the English MIND dataset into 14 linguistically and geographically diverse languages with varying digital footprints. Using xMIND, we systematically evaluate several content-based neural news recommenders (NNRs) in zero-shot (ZS-XLT) and few-shot (FS-XLT) cross-lingual transfer, examining both monolingual and bilingual consumption patterns. In FS-XLT, we compare random and category-based replacement methods for incorporating target-language data during training. Our results show that (i) current NNRs, grounded in multilingual language models, experience significant performance drops in ZS-XLT, and (ii) injecting target-language data in FS-XLT provides limited improvements, especially for bilingual consumption. Notably, randomly injecting target-language news during training leads to greater performance gains compared to category-based replacements. Our in-depth analysis of representation alignment between source and target languages within the language model shows that FS-XLT improves cross-lingual alignment primarily for high-resource languages, while low-resource languages remain weakly aligned with English. These findings highlight the need for broader research efforts in multilingual and cross-lingual news recommendation. 

Paper:


```
 @article{Gu_u_2025, title={From Dataset to Model: A Romanian–English Corpus and Fine-Tuned Cross-Lingual Embeddings for Text and Tabular Retrieval}, volume={15}, ISSN={2076-3417}, url={http://dx.doi.org/10.3390/app152212219}, DOI={10.3390/app152212219}, number={22}, journal={Applied Sciences}, publisher={MDPI AG}, author={Guțu, Bogdan Mihai and Popescu, Nirvana}, year={2025}, month=nov, pages={12219} }
```

This study introduces a Romanian–English bilingual corpus and a fine-tuned cross-lingual embedding framework aimed at improving retrieval performance in Retrieval-Augmented Generation (RAG) systems. The dataset integrates over 130,000 unstructured question–answer pairs derived from SQuAD and 9750 Romanian-generated questions linked to governmental tabular data, subsequently translated bidirectionally to build parallel Romanian–English resources. Multiple state-of-the-art embedding models, including multilingual-e5, Jina-v3, and the Qwen3-Embeddings family, were systematically evaluated on both text and tabular inputs across four language directions (eng-eng, ro-ro, eng-ro, ro-eng). The results show that while multilingual-e5-large achieved the strongest monolingual retrieval performance, Qwen3-Embedding-4B provided the best overall balance across languages and modalities. Fine-tuning this model using Low-Rank Adaptation (LoRA) and InfoNCE loss improved its Mean Reciprocal Rank (MRR) from 0.4496 to 0.4872 (+8.36%), with the largest gains observed in cross-lingual retrieval tasks. The research highlights persistent challenges in structured (tabular) data retrieval due to dataset imbalance and outlines future directions including dataset expansion, translation refinement, and instruction-based fine-tuning. Overall, this work contributes new bilingual analyses and methodological insights for advancing embedding-based retrieval in low-resource and multimodal contexts.



### Cluster D - Synthetic query and qrels construction quality controls

**Why relevant:** Round-3 gap memo identified missing methodology evidence on synthetic query quality control and qrels construction policy.
**Search** Results:

Paper:


```
@article{caferouglu2025sing,
  title={Sing-sql: A synthetic data generation framework for in-domain text-to-sql translation},
  author={Cafero{\u{g}}lu, Hasan Alp and {\c{C}}elik, Mehmet Serhat and Ulusoy, {\"O}zg{\"u}r},
  journal={arXiv preprint arXiv:2509.25672},
  year={2025}
}
```

Translating natural language questions into SQL has become a core challenge in enabling non-technical users to query databases. While recent work has explored large-scale synthetic data generation to improve model performance through post-training, most efforts emphasize cross-domain generalization. This leaves a gap for real-world enterprise scenarios, where models need to specialize to a single database schema and organizations require to be able to evaluate their Text-to-SQL systems on their own databases. To address this, we introduce SING-SQL, a fully automated two-stage framework for generating high-quality, high-coverage synthetic Text-to-SQL data for any target database, without relying on SQL logs or manual annotations. Our approach hierarchically partitions a database schema into sub-schemas, synthesizes SQL queries across multiple complexity levels, and applies a quality-aware pipeline that includes LLM-as-a-judge validation, executability checks, automatic repair, and column balancing. We further release SingSQL-LM, a family of compact language models fine-tuned on the synthetic data, achieving strong in-domain generalization. On the subset of the BIRD benchmark, SingSQL-LM-3B-R64 reaches 82.87% Soft F1 and 73.03% EX upper bound with 32 candidates, outperforming the best 3B-scale baseline by +16.21 in Soft F1 and +12.36 in EX. At the 1.5B scale, SingSQL-LM-1.5B-R64 improves over prior systems by +9.30 in Soft F1 and +4.49 in EX. On synthetic evaluation sets, SingSQL-LMs exceed prior systems by wide margins, establishing state-of-the-art performance among open models at comparable scales. Our study of context management strategies reveals that schema-free fine-tuning combined with schema-only inference provides the most robust results. These findings establish SING-SQL as a scalable, database-agnostic paradigm for producing and evaluating enterprise-grade Text-to-SQL systems.

Paper:


```
@inproceedings{huang-etal-2025-targa,
    title = "{TARGA}: Targeted Synthetic Data Generation for Practical Reasoning over Structured Data",
    author = "Huang, Xiang  and
      Shen, Jiayu  and
      Huang, Shanshan  and
      Cheng, Sitao  and
      Wang, Xiaxia  and
      Qu, Yuzhong",
    editor = "Che, Wanxiang  and
      Nabende, Joyce  and
      Shutova, Ekaterina  and
      Pilehvar, Mohammad Taher",
    booktitle = "Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)",
    month = jul,
    year = "2025",
    address = "Vienna, Austria",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2025.acl-long.137/",
    doi = "10.18653/v1/2025.acl-long.137",
    pages = "2704--2726",
    ISBN = "979-8-89176-251-0",
  
}
```

Semantic parsing, which converts natural language queries into logic forms, plays a crucial role in reasoning within structured environments. However, existing methods encounter two significant challenges: reliance on extensive manually annotated datasets and limited generalization capability to unseen examples. To tackle these issues, we propose Targeted Synthetic Data Generation (Targa), a practical framework that dynamically generates high-relevance synthetic data without manual annotation. Starting from the pertinent entity and relation of a given question, we probe for the potential relevant queries through layer-wise expansion and cross-layer combination. Then, we generate corresponding natural language questions for these constructed queries to jointly serve as the synthetic demonstration for in-context learning. Experiments on multiple knowledge-based question answering (KBQA) datasets demonstrate that Targa, using only a 7B-parameter model, substantially outperforms existing non-fine-tuned methods that utilize close-sourced model, achieving notable improvements in F1 scores on GrailQA(+7.7) and KBQA-Agent(+12.2). Furthermore, Targa also exhibits superior sample efficiency, robustness, and generalization capabilities under non-I.I.D. settings.

Paper:


```
 @inproceedings{Bassani_2021, series={SIGIR ’21}, title={Semantic Query Labeling Through Synthetic Query Generation}, url={http://dx.doi.org/10.1145/3404835.3463071}, DOI={10.1145/3404835.3463071}, booktitle={Proceedings of the 44th International ACM SIGIR Conference on Research and Development in Information Retrieval}, publisher={ACM}, author={Bassani, Elias and Pasi, Gabriella}, year={2021}, month=jul, pages={2278–2282}, collection={SIGIR ’21} }
```


Searching in a domain-specific corpus of structured documents (e.g., e-commerce, media streaming services, job-seeking platforms) is often managed as a traditional retrieval task or through faceted search. Semantic Query Labeling --- the task of locating the constituent parts of a query and assigning domain-specific predefined semantic labels to each of them --- allows leveraging the structure of documents during retrieval while leaving unaltered the keyword-based query formulation. Due to both the lack of a publicly available dataset and the high cost of producing one, there have been few published works in this regard. In this paper, basing on the assumption that a corpus already contains the information the users search, we propose a method for the automatic generation of semantically labeled queries and show that a semantic tagger --- based on BERT, gazetteers-based features, and Conditional Random Fields --- trained on our synthetic queries achieves results comparable to those obtained by the same model trained on real-world data. We also provide a large dataset of manually annotated queries in the movie domain suitable for studying Semantic Query Labeling. We hope that the public availability of this dataset will stimulate future research in this area.



### Cluster E - Evaluation-design and human-alignment of LLM-as-judge

**Why relevant:** Round-3 gap memo flagged limited evidence on when judge outputs can replace or complement human judgments.

Paper:

```
@article{thakur2025support,
  title={Support evaluation for the trec 2024 RAG track: Comparing human versus llm judges},
  author={Thakur, Nandan and Pradeep, Ronak and Upadhyay, Shivani and Campos, Daniel and Craswell, Nick and Lin, Jimmy},
  journal={arXiv preprint arXiv:2504.15205},
  year={2025}
}
```

Retrieval-augmented generation (RAG) enables large language models (LLMs) to generate answers with citations from source documents containing "ground truth", thereby reducing system hallucinations. A crucial factor in RAG evaluation is "support", whether the information in the cited documents supports the answer. To this end, we conducted a large-scale comparative study of 45 participant submissions on 36 topics to the TREC 2024 RAG Track, comparing an automatic LLM judge (GPT-4o) against human judges for support assessment. We considered two conditions: (1) fully manual assessments from scratch and (2) manual assessments with post-editing of LLM predictions. Our results indicate that for 56% of the manual from-scratch assessments, human and GPT-4o predictions match perfectly (on a three-level scale), increasing to 72% in the manual with post-editing condition. Furthermore, by carefully analyzing the disagreements in an unbiased study, we found that an independent human judge correlates better with GPT-4o than a human judge, suggesting that LLM judges can be a reliable alternative for support assessment. To conclude, we provide a qualitative analysis of human and GPT-4o errors to help guide future iterations of support assessment.


Paper:


```
@inproceedings{abdallah2025rerankarena,
  title={Rerankarena: A unified platform for evaluating retrieval, reranking and rag with human and llm feedback},
  author={Abdallah, Abdelrahman and Abdalla, Mahmoud and Piryani, Bhawna and Mozafari, Jamshid and Ali, Mohammed and Jatowt, Adam},
  booktitle={Proceedings of the 34th ACM International Conference on Information and Knowledge Management},
  pages={6593--6597},
  year={2025}
}
```

Evaluating the quality of retrieval-augmented generation (RAG) and document reranking systems remains challenging due to the lack of scalable, user-centric, and multi-perspective evaluation tools. We introduce RankArena, a unified platform for comparing and analysing the performance of retrieval pipelines, rerankers, and RAG systems using structured human and LLM-based feedback as well as for collecting such feedback. RankArena supports multiple evaluation modes: direct reranking visualisation, blind pairwise comparisons with human or LLM voting, supervised manual document annotation, and end-to-end RAG answer quality assessment. It captures fine-grained relevance feedback through both pairwise preferences and full-list annotations, along with auxiliary metadata such as movement metrics, annotation time, and quality ratings. The platform also integrates LLM-as-a-judge evaluation, enabling comparison between model-generated rankings and human ground truth annotations. All interactions are stored as structured evaluation datasets that can be used to train rerankers, reward models, judgment agents, or retrieval strategy selectors. 

Paper:


```
@inproceedings{miyaji2025evaluating,
  title={Evaluating RAG-based QA Systems: A Comparative Analysis of LLM as a Judge, Traditional Metrics, and Human Alignment},
  author={Miyaji, Renato and Moulin, Renato and Mon{\c{c}}{\~a}o, Samuel and Machado, Leonardo},
  booktitle={Simp{\'o}sio Brasileiro de Tecnologia da Informa{\c{c}}{\~a}o e da Linguagem Humana (STIL)},
  pages={247--258},
  year={2025},
  organization={SBC}
}
```

Evaluating RAG based Question Answering systems presents ongoing challenges, as traditional NLP metrics often inadequately capture nuanced answer quality and the reliability of LLM as a Judge paradigms requires further validation. This study comprehensively compares two distinct RAG QA systems on a domain-specific dataset from a consulting company. We investigate the efficacy and human alignment of LLM as a Judge configurations (Fine-Tuning and In-Context Learning) benchmarking them against NLP metrics and human evaluations. Results indicate that BERTScore is more indicative of semantic similarity than lexical-based metrics. For LLM as a Judge evaluations, Prometheus 2 using Pairwise Comparison demonstrated the strongest human alignment.
