# LLM instructions used for the reported experimental snapshot

These files are the exact query-generation and relevance-judgment instructions that produced
the frozen queries and qrels in `datasets/*/queries.jsonl` and `datasets/*/qrels.tsv`, the
snapshot reported in the PeerJ Computer Science paper. They are copied from the pipeline as
it stood at commit `8e2e303` (`config.py` and `rag_benchmark.py`); the two system
instructions were extracted programmatically, byte for byte.

| Setting | Value |
|---|---|
| Model | `models/gemini-2.5-flash-lite` |
| Temperature | `0.1` |
| Candidate pool | top-20 chunks from each of the five evaluated models, deduplicated |
| Seed chunk | judged like any other candidate (`force_source_chunk_relevant = False`) |

## Files

| File | Role | Sent as |
|---|---|---|
| `query_generation_system.txt` | Query generator | system instruction |
| `query_generation_user.txt` | Query generator | user message, synchronous mode |
| `relevance_judge_system.txt` | Relevance judge | system instruction |
| `relevance_judge_user.txt` | Relevance judge | user message, both modes |

Placeholders in the user templates:

- `{chunk_text}`: the seed chunk (query generation) or the candidate chunk (judging).
- `{query_text}`: the generated query being judged.
- `{chunk_id}`: the candidate's chunk identifier, e.g. `English_chunk12`.
- `{position}`: the candidate's 1-based position in that query's pool. Each candidate is
  judged in its own request, so this index carries no information to the judge.

In batch mode the query generator received the seed chunk text alone as the user message,
without the wrapper in `query_generation_user.txt`; the system instruction was the same.

## Differences from the current code

The current pipeline no longer sends exactly these messages, so re-running it will not
reproduce the frozen qrels byte for byte:

- `relevance_judge_system.txt` asks whether the excerpt "fully answers the question" but
  defines label 1 as "complete or partial information". The current `config.py` states only
  the complete-or-partial criterion.
- The judge user message no longer carries the `{position}.` index.

The query-generation system instruction is unchanged.
