# CULTUREMAP-IR
*A Persian-centric corpus and retrieval benchmark for province-level cultural, geographic, and touristic knowledge in Iran.*

<div align="center">
  
[![Status](https://img.shields.io/badge/status-active-success)](#)
[![Language](https://img.shields.io/badge/lang-Persian%20(Fa)-blue)](#)
[![Retrieval](https://img.shields.io/badge/retriever-GLOT500%20%2B%20LoRA-7f52ff)](#)

</div>

---

## Table of Contents
- [Overview](#overview)
- [What’s in the Repo](#whats-in-the-repo)
- [Data Schema](#data-schema)
- [Corpus Quality & Stats](#corpus-quality--stats)
- [Retrieval Dataset](#retrieval-dataset)
- [Methods](#methods)
- [Results (TL;DR)](#results-tldr)
- [Quickstart](#quickstart)
- [Reproducing Experiments](#reproducing-experiments)
- [Duplicate Detection](#duplicate-detection)
- [Limitations](#limitations)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Citing](#citing)
- [Authors](#authors)

---

## Overview
**CULTUREMAP-IR** is a province-scoped, **Persian-first** corpus and accompanying **retrieval benchmark** focused on cultural, geographic, and touristic knowledge across Iran. The project emphasizes **evidence-anchored**, **schema-controlled** entries suitable for both downstream applications and rigorous evaluation of retrieval and generation systems in Persian.

- **Core provinces (6):** اصفهان (Isfahan), فارس (Fars), بوشهر (Bushehr), هرمزگان (Hormozgan), چهارمحال و بختیاری (Chahar Mahal & Bakhtiari), کهگیلویه و بویراحمد (Kohgiluyeh & Boyerahmad).  
- **Extended provinces (6):** آذربایجان شرقی (East Azerbaijan), کردستان (Kurdistan), آذربایجان غربی (West Azerbaijan), زنجان (Zanjan), گیلان (Gilan), اردبیل (Ardabil).

### Why this matters
- Persian web content is **heterogeneous** and **orthographically variable**.  
- Many sources are **sparse** or **outdated** at the provincial level.  
- This corpus provides **clean, localized** data and a **reproducible benchmark** to test whether models retrieve and articulate **provincial** facts without drifting to generic national summaries.

---

## What’s in the Repo
> Directory names below mirror the report; yours may differ slightly. Adjust paths as needed.

- `data/`  
  - Normalized, schema-controlled JSON per province (entries with names, optional images, and short evidence-tied descriptions).
- `retrieval/`  
  - Synthesized passages (≤100 words each) and **exact** span **question–answer pairs** (5 per passage).
- `stats/` or `Stats/`  
  - Summary tables/figures used in the report (e.g., `corpus_ratios.png`, `avg_passage_lenght.png`, combined metrics).
- `scripts/` & `notebooks/`  
  - Utilities to build the corpus, generate retrieval data, fine-tune retrievers, evaluate, and check duplicates.
- `models/` (optional)  
  - LoRA adapter weights and projection head for the fine-tuned retriever.
- `report/`  
  - The LaTeX report (this README summarizes it).

---

## Data Schema

### (A) Geographical Features, Topography, Natural Resources
Structured as an **array of blocks** with subcategories (if available):

```jsonc
[
  {
    "name": "<subcategory>",          // e.g., "رودخانه‌ها" (rivers)
    "description": [
      {
        "name": "<item name>",
        "images": ["<image-url-1>", "<image-url-2>"],
        "description": "<short, evidence-anchored Persian description>"
      }
      // ...
    ]
  }
  // ...
]
```

### (B) Tourist Attractions
Each item is a flat object with optional metadata:

```jsonc
[
  {
    "name": "<name>",
    "images": ["<image-url-1>", "<image-url-2>"],
    "year_built": "<if known or null>",
    "architect": "<if known or null>",
    "constructor": "<if known or null>",
    "description": "<short, evidence-anchored Persian description>"
  }
  // ...
]
```

> **Strict image policy:** Only include an image when there is **indisputable, verifiable evidence** that it depicts the exact item. When in doubt: **omit**.

---

## Corpus Quality & Stats
- **Structured records:** **893**
- **Total content words:** **30,312**
- **Inter-annotator agreement (Cohen’s κ):** **0.9494 overall**  
  - Province breakdown (κ):  
    - چهارمحال و بختیاری: 1.0000  
    - کهگیلویه و بویراحمد: 0.8952  
    - بوشهر: 0.8998  
    - فارس: 1.0000  
    - اصفهان: 0.7592  
    - هرمزگان: 1.0000

> See figures/tables in `Stats/` such as `corpus_ratios.png` and field-level word count plots per province.

---

## Retrieval Dataset
Built in two stages from the normalized corpus:

1. **Passage synthesis**: For each structured record, generate a **≤100-word** Persian paragraph integrating names, locations/classifications, salient attributes, and dates/numbers—**tied to evidence**.
2. **Question generation**: From each paragraph, derive **exactly five** **extractive** QA pairs (answers are exact spans from the same paragraph).

**Totals (core + extended):**
- **Passages:** **1,510**
- **QA pairs:** **7,550** (5 per passage)  
- Average passage length ≈ **80 words**

A **50-question human-authored evaluation set** complements the automatic QA for a gold-standard benchmark.

---

## Methods

### TF–IDF
Classical sparse retrieval (character n-grams optional), cosine similarity on L2-normalized vectors.

### Dense Retriever: GLOT500
- **Backbone:** `cis-lmu/glot500-base` multilingual sentence encoder.  
- **Zero-shot:** Encode query & passages; cosine similarity for ranking.  
- **Fine-tuned (recommended):** Two-stage, parameter-efficient adaptation:
  1. **MLM warm-up** (LoRA adapters) on domain text.
  2. **Contrastive learning** on our QA pairs (symmetric InfoNCE; in-batch negatives).

> LoRA targets `query`, `key`, `value`, and `dense`; projection head to 128-D; temperature ~0.05.

---

## Results (TL;DR)
Human **blind ranking** over **50** eval questions, comparing **TF–IDF**, **GLOT500 (zero-shot)**, and **GLOT500 + LoRA (fine-tuned)**:

- **Median rank** (lower is better):  
  - TF–IDF: **6.0**  
  - Zero-shot GLOT500: **6.0**  
  - **Fine-tuned GLOT500–LoRA: 2.0** ✅
- **Mean Reciprocal Rank (MRR):**  
  - TF–IDF: **≈ 0.318**  
  - Zero-shot GLOT500: **≈ 0.292**  
  - **Fine-tuned GLOT500–LoRA: ≈ 0.924–0.929** ✅
- Fine-tuning **greatly reduces worst-case failures** and boosts **Top‑K presence** (≈ **77%** of all top-3 placements across two annotators).

**Takeaway:** For Persian, province-scoped cultural QA, **fine-tuned dense retrieval** substantially outperforms both TF–IDF and zero-shot embeddings. A practical hybrid is TF–IDF for fast prefiltering + fine-tuned dense reranking.

---

## Quickstart

### 1) Environment
```bash
# Python 3.10+ recommended
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate

pip install -U pip
pip install torch transformers peft accelerate datasets scikit-learn numpy pandas tqdm matplotlib
# Optional: faiss-cpu for ANN search
# pip install faiss-cpu
```

### 2) Get the model
```python
from transformers import AutoModel, AutoTokenizer
tok = AutoTokenizer.from_pretrained("cis-lmu/glot500-base")
model = AutoModel.from_pretrained("cis-lmu/glot500-base")
```

### 3) Encode passages (zero-shot example)
```python
import torch, numpy as np
def mean_pool(last_hidden_state, attention_mask):
    masked = last_hidden_state * attention_mask.unsqueeze(-1)
    return masked.sum(1) / attention_mask.sum(1, keepdim=True)

# texts = [...]  # your corpus passages
# queries = [...]

# Encode (batch your passages in practice)
# Use cosine similarity between L2-normalized embeddings
```

> For **fine-tuned** usage, load the **LoRA adapters** and **projection head** saved in this repo (see `models/` or training outputs).

---

## Reproducing Experiments

### A) MLM Warm-Up (LoRA)
- Mask probability: **0.15**
- Rank **r=16**, α=32, dropout=0.05
- LR **2e-4**, weight decay **0.01**, warmup ratio **0.06**, small batch with gradient accumulation

### B) Contrastive Training
- Sequence length **≤192**, projection **128-D**
- Symmetric InfoNCE with temperature **0.05**
- In-batch negatives, cosine similarity on L2-normalized embeddings

> See `scripts/` or notebooks for end-to-end examples: embedding passages, building ANN indices, and evaluating on the 50-question set.

---

## Duplicate Detection
Use the **fine-tuned embeddings** + nearest neighbors (cosine) and flag pairs above a chosen threshold (e.g., **0.90**).

- Example finding: a **0.915** similarity pair denoting near-duplicate river descriptions from neighboring localities.

```python
from sklearn.neighbors import NearestNeighbors
# X = normalized embeddings (n_samples x dim)
nbrs = NearestNeighbors(metric="cosine", n_neighbors=5, n_jobs=-1).fit(X)
# query radius / threshold or use kneighbors to scan top matches
```

---

## Limitations
- Current schema emphasizes **geography/resources/attractions**; cultural facets like **dialects, cuisine, rituals** are planned.
- Some provinces are **under-documented** online; the pipeline errs on the side of **no speculation**.
- Very rare technical terms may require **more targeted data** for best retrieval performance.

---

## Roadmap
- Extend coverage to additional provinces and cultural dimensions.
- Add coordinates and temporal validity to schema.
- Release ablations: prompt variants, adapter targets, negatives design.
- Provide Docker image and fully scripted end-to-end runners.

---

## Contributing
Contributions are welcome!  
Please open an issue for bugs/requests or a PR for fixes and new features.  
For major changes, start a discussion describing your proposal and how it impacts the schema, data quality, or evaluation.

---

## Citing

If you use **CULTUREMAP-IR**, please cite the repo/report:

```bibtex
@misc{culturemap-ir,
  title  = {CULTUREMAP-IR: Cultural Unification and Linguistic Textual Utilization for Regional Extraction and Mapping of All Iranian Provinces},
  author = {Meskin, Asal and Mirrokni, Alireza},
  year   = {2025},
  note   = {Sharif University of Technology. Persian-centric cultural, geographic, and touristic corpus with retrieval benchmark.}
}
```

---

## Authors
**[Asal Meskin](https://github.com/asalmskin)** • **[Alireza Mirrokni](https://github.com/alirezamirrokni)**
Computer Engineering Department, **Sharif University of Technology**  
*Equal contribution.*

