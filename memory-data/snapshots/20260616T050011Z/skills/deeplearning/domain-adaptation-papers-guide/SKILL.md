---
name: domain-adaptation-papers-guide
description: "Comprehensive collection of domain adaptation research papers"
metadata:
  openclaw:
    emoji: "馃攧"
    category: "domains"
    subcategory: "ai-ml"
    keywords: ["domain adaptation", "transfer learning", "distribution shift", "domain gap", "UDA", "domain generalization"]
    source: "https://github.com/zhaoxin94/awesome-domain-adaptation"
---

# Domain Adaptation Papers Guide

## Overview

Domain adaptation addresses the problem of training models on one data distribution (source domain) and deploying them on a different distribution (target domain). This curated collection covers the full spectrum 鈥?from unsupervised domain adaptation (UDA) and domain generalization to partial, open-set, and source-free adaptation. Organized by methodology and application area with regularly updated paper lists.

## Taxonomy of Methods

```
Domain Adaptation
鈹溾攢鈹€ Unsupervised DA (UDA)
鈹?  鈹溾攢鈹€ Discrepancy-based (MMD, CORAL, CDD)
鈹?  鈹溾攢鈹€ Adversarial-based (DANN, ADDA, CDAN)
鈹?  鈹溾攢鈹€ Reconstruction-based (DRCN, DSN)
鈹?  鈹斺攢鈹€ Self-training (SHOT, CBST)
鈹溾攢鈹€ Semi-supervised DA
鈹溾攢鈹€ Source-free DA (no source data at adaptation time)
鈹溾攢鈹€ Partial DA (target has subset of source classes)
鈹溾攢鈹€ Open-set DA (target has unknown classes)
鈹溾攢鈹€ Universal DA (no prior on label set relationship)
鈹溾攢鈹€ Multi-source DA
鈹溾攢鈹€ Domain Generalization (no target data at all)
鈹斺攢鈹€ Test-time Adaptation (adapt at inference)
```

## Key Methods by Era

### Classical Methods

| Method | Year | Approach | Key Idea |
|--------|------|----------|----------|
| **TCA** | 2011 | Kernel | Transfer Component Analysis |
| **GFK** | 2012 | Subspace | Geodesic Flow Kernel |
| **SA** | 2013 | Subspace | Subspace Alignment |
| **DAN** | 2015 | MMD | Deep Adaptation Networks |
| **DANN** | 2016 | Adversarial | Domain-Adversarial Neural Networks |
| **ADDA** | 2017 | Adversarial | Adversarial Discriminative DA |
| **CORAL** | 2016 | Statistics | Correlation Alignment |

### Modern Methods

| Method | Year | Approach | Key Idea |
|--------|------|----------|----------|
| **CDAN** | 2018 | Adversarial | Conditional adversarial + entropy |
| **MCD** | 2018 | Discrepancy | Maximum Classifier Discrepancy |
| **SHOT** | 2020 | Source-free | Self-supervised pseudo-labeling |
| **TENT** | 2021 | Test-time | Entropy minimization at test time |
| **DAFormer** | 2022 | Transformer | DA for semantic segmentation |
| **PADCLIP** | 2023 | Vision-language | CLIP-based domain adaptation |

## Paper Tracking

```python
import arxiv

def find_da_papers(subtopic="unsupervised", days=30):
    """Find recent domain adaptation papers on arXiv."""
    queries = {
        "unsupervised": "abs:unsupervised domain adaptation",
        "source_free": "abs:source-free domain adaptation",
        "generalization": "abs:domain generalization",
        "test_time": "abs:test-time adaptation OR test-time training",
    }

    search = arxiv.Search(
        query=queries.get(subtopic, queries["unsupervised"]),
        max_results=30,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    for result in search.results():
        print(f"[{result.published.strftime('%Y-%m-%d')}] "
              f"{result.title}")
        print(f"  {result.entry_id}")

find_da_papers("source_free")
```

## Benchmark Datasets

```python
# Standard DA benchmarks
benchmarks = {
    "Office-31": {
        "domains": ["Amazon", "DSLR", "Webcam"],
        "classes": 31,
        "task": "Object recognition",
    },
    "Office-Home": {
        "domains": ["Art", "Clipart", "Product", "Real World"],
        "classes": 65,
        "task": "Object recognition",
    },
    "VisDA-2017": {
        "domains": ["Synthetic", "Real"],
        "classes": 12,
        "task": "Large-scale sim-to-real",
    },
    "DomainNet": {
        "domains": ["Clipart", "Infograph", "Painting",
                     "Quickdraw", "Real", "Sketch"],
        "classes": 345,
        "task": "Large-scale multi-domain",
    },
    "PACS": {
        "domains": ["Photo", "Art", "Cartoon", "Sketch"],
        "classes": 7,
        "task": "Domain generalization",
    },
}

for name, info in benchmarks.items():
    print(f"\n{name}: {info['classes']} classes, "
          f"{len(info['domains'])} domains")
    print(f"  Domains: {', '.join(info['domains'])}")
```

## Application Areas

| Application | Source 鈫?Target Example |
|-------------|----------------------|
| **Medical imaging** | Hospital A 鈫?Hospital B scanners |
| **Autonomous driving** | Simulation 鈫?Real world |
| **Remote sensing** | Region A 鈫?Region B satellite |
| **NLP** | News text 鈫?Social media |
| **Speech** | Studio 鈫?Noisy environments |
| **Robotics** | Sim 鈫?Real manipulation |

## Reading Roadmap

```markdown
### Beginner Path
1. "A Survey on Transfer Learning" (Pan & Yang, 2010)
2. "Domain Adaptation for Object Recognition" (Saenko et al., 2010)
3. "Deep Domain Confusion" (Tzeng et al., 2014)
4. DANN paper (Ganin et al., 2016)

### Intermediate Path
5. CDAN (Long et al., 2018)
6. MCD (Saito et al., 2018)
7. "Moment Matching for Multi-Source DA" (Peng et al., 2019)

### Advanced Path
8. SHOT (Liang et al., 2020) 鈥?source-free
9. TENT (Wang et al., 2021) 鈥?test-time
10. "Benchmarking DA on Language" (Ramponi & Plank, 2020)
```

## Use Cases

1. **Literature survey**: Map the DA research landscape
2. **Method selection**: Choose appropriate DA technique for your task
3. **Benchmark comparison**: Compare methods on standard datasets
4. **Research gaps**: Identify under-explored DA settings
5. **Course material**: Teach transfer learning and DA

## References

- [awesome-domain-adaptation](https://github.com/zhaoxin94/awesome-domain-adaptation)
- [Transfer Learning Library](https://github.com/thuml/Transfer-Learning-Library)
- [DomainBed](https://github.com/facebookresearch/DomainBed)
