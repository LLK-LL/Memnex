---
name: nlp-toolkit-guide
description: "NLP analysis with perplexity scoring, burstiness, and entropy metrics"
metadata:
  openclaw:
    emoji: "馃挰"
    category: "domains"
    subcategory: "ai-ml"
# REDACTED: sensitive-looking memory line
    source: "https://github.com/huggingface/transformers"
---

# NLP Toolkit Guide

## Overview

Natural Language Processing research requires a diverse set of analytical tools beyond standard model training. Text quality assessment, AI-generated text detection, linguistic feature extraction, and corpus analysis all depend on well-understood metrics: perplexity, burstiness, entropy, and their variants.

# REDACTED: sensitive-looking memory line

These tools are framework-agnostic where possible, but leverage Hugging Face Transformers for language model operations and standard Python scientific computing libraries for statistical analysis.

## Perplexity Scoring

Perplexity measures how well a language model predicts a text. Lower perplexity means the text is more predictable to the model -- a key signal in AI text detection, model evaluation, and domain adaptation.

```python
import torch
import numpy as np
# REDACTED: sensitive-looking memory line

def compute_perplexity(text: str, model_name: str = "gpt2") -> dict:
    """
# REDACTED: sensitive-looking memory line

    Returns:
# REDACTED: sensitive-looking memory line
    """
# REDACTED: sensitive-looking memory line
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.eval()

# REDACTED: sensitive-looking memory line
    input_ids = encodings.input_ids

    with torch.no_grad():
        outputs = model(input_ids, labels=input_ids)
        neg_log_likelihood = outputs.loss.item()

# REDACTED: sensitive-looking memory line
    with torch.no_grad():
# REDACTED: sensitive-looking memory line
        targets = input_ids[:, 1:]
        log_probs = torch.log_softmax(logits, dim=-1)
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

    perplexity = np.exp(neg_log_likelihood)

    return {
        "perplexity": perplexity,
        "log_likelihood": -neg_log_likelihood,
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
    }
```

## Burstiness Analysis

Burstiness measures the tendency of words to appear in clusters rather than uniformly across a text. Human writing tends to be "burstier" -- once a topic is introduced, related terms cluster together, then disappear.

```python
from collections import Counter
import numpy as np

def compute_burstiness(text: str, min_freq: int = 2) -> dict:
    """
    Compute burstiness score for a text.

    Burstiness B = (sigma - mu) / (sigma + mu)
    where sigma and mu are the std dev and mean of inter-arrival times.
    B ranges from -1 (periodic) to 1 (bursty). Human text typically B > 0.
    """
    words = text.lower().split()
    word_positions = {}
    for i, word in enumerate(words):
        word_positions.setdefault(word, []).append(i)

    burstiness_scores = {}
    for word, positions in word_positions.items():
        if len(positions) < min_freq:
            continue
        inter_arrivals = np.diff(positions)
        mu = np.mean(inter_arrivals)
        sigma = np.std(inter_arrivals)
        if mu + sigma == 0:
            burstiness_scores[word] = 0.0
        else:
            burstiness_scores[word] = (sigma - mu) / (sigma + mu)

    # Aggregate burstiness
    if burstiness_scores:
        avg_burstiness = np.mean(list(burstiness_scores.values()))
    else:
        avg_burstiness = 0.0

    return {
        "average_burstiness": avg_burstiness,
        "word_burstiness": burstiness_scores,
        "num_words_analyzed": len(burstiness_scores),
    }
```

## Entropy and Information-Theoretic Metrics

```python
from collections import Counter
import numpy as np

def compute_entropy(text: str, level: str = "word") -> dict:
    """
    Compute Shannon entropy at word or character level.

    Higher entropy indicates more diverse, less predictable text.
    AI-generated text often has lower entropy than human text.
    """
    if level == "word":
# REDACTED: sensitive-looking memory line
    elif level == "character":
# REDACTED: sensitive-looking memory line
    else:
        raise ValueError("level must be 'word' or 'character'")

# REDACTED: sensitive-looking memory line
    total = sum(counts.values())
    probabilities = np.array([c / total for c in counts.values()])

    entropy = -np.sum(probabilities * np.log2(probabilities + 1e-12))
    max_entropy = np.log2(len(counts)) if len(counts) > 1 else 1.0
    normalized_entropy = entropy / max_entropy

    return {
        "entropy": entropy,
        "normalized_entropy": normalized_entropy,
        "vocabulary_size": len(counts),
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
    }

def compute_conditional_entropy(text: str, n: int = 2) -> float:
    """Compute conditional entropy H(X_n | X_{n-1}) for n-gram analysis."""
    words = text.lower().split()
    if len(words) < n:
        return 0.0

    ngrams = [tuple(words[i:i+n]) for i in range(len(words) - n + 1)]
    contexts = [ng[:-1] for ng in ngrams]

    context_counts = Counter(contexts)
    ngram_counts = Counter(ngrams)

    h = 0.0
    total = len(ngrams)
    for ngram, count in ngram_counts.items():
        context = ngram[:-1]
        p_ngram = count / total
        p_context = context_counts[context] / total
        h -= p_ngram * np.log2(count / context_counts[context] + 1e-12)

    return h
```

## AI Text Detection Pipeline

Combining perplexity, burstiness, and entropy into a detection pipeline:

```python
# REDACTED: sensitive-looking memory line
    """
    Multi-signal analysis for AI vs. human text classification.
    Uses perplexity, burstiness, and entropy as features.
    """
    perplexity_result = compute_perplexity(text)
    burstiness_result = compute_burstiness(text)
    entropy_result = compute_entropy(text, level="word")
    char_entropy = compute_entropy(text, level="character")

    # Heuristic thresholds from literature
    signals = {
        "low_perplexity": perplexity_result["perplexity"] < 30,
        "low_burstiness": burstiness_result["average_burstiness"] < 0.1,
        "low_entropy": entropy_result["normalized_entropy"] < 0.7,
# REDACTED: sensitive-looking memory line
    }

    ai_score = sum(signals.values()) / len(signals)

    return {
        "perplexity": perplexity_result["perplexity"],
        "burstiness": burstiness_result["average_burstiness"],
        "word_entropy": entropy_result["entropy"],
        "char_entropy": char_entropy["entropy"],
# REDACTED: sensitive-looking memory line
        "ai_likelihood_score": ai_score,
        "signals": signals,
    }
```

# REDACTED: sensitive-looking memory line

```python
# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
    if models is None:
        models = ["gpt2", "bert-base-uncased", "facebook/opt-1.3b"]

    results = {}
    for model_name in models:
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
        results[model_name] = {
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
        }
    return results
```

## Best Practices

- **Always specify the model** when computing perplexity. Perplexity is model-relative, not absolute.
- **Normalize by text length** when comparing entropy across texts of different sizes.
- **Use sliding windows** for long documents to capture local variation in metrics.
- **Combine multiple signals** for AI text detection -- no single metric is reliable alone.
- **Report confidence intervals** by computing metrics on paragraph-level chunks, then aggregating.
- **Be aware of domain shift.** Perplexity thresholds trained on news text will not transfer to scientific papers.

## References

# REDACTED: sensitive-looking memory line
- [DetectGPT](https://arxiv.org/abs/2301.11305) -- Perplexity-based AI text detection (Mitchell et al., 2023)
- [Burstiness and Memory in Text](https://doi.org/10.1103/PhysRevLett.114.078101) -- Altmann et al., 2015
- [NLTK documentation](https://www.nltk.org/) -- Classic NLP toolkit for feature engineering
- [spaCy documentation](https://spacy.io/) -- Industrial-strength NLP for production pipelines
