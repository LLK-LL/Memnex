#!/usr/bin/env python3
"""
Reflection Scheduler -- runs reflection agent on a schedule.

Schedules:
- After session: quick reflection (dedup + decay)
- Every 6 hours: full reflection (digest + synthesize)
- Sunday midnight: weekly deep reflection
- Every 2 hours: RSS feed polling
- Daily 9:00 AM: inactive project reminders
- Every 6 hours: GitHub repo release monitor
- Weekly Wednesday 4:00 AM: auto-retrain Ollama model
- Every 12 hours: Tech Radar (tech stack release monitor)
- Daily 7:00 AM: Dependency Monitor (project dependency updates)

Usage:
    python src/reflection/scheduler.py [--db PATH]

Dependencies:
    pip install apscheduler  (optional -- falls back to simple loop)
"""

import asyncio
import json
import os
import re
import sqlite3
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

MEMORY_DIR = Path(os.environ.get("CLAUDE_MEMORY_DIR", os.path.expanduser("~/.claude-memory")))
LOG = lambda msg: sys.stderr.write(f"[reflection-scheduler] {datetime.now().strftime('%H:%M:%S')} {msg}\n")

# Try APScheduler
_HAS_APSCHEDULER = False
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.triggers.cron import CronTrigger
    _HAS_APSCHEDULER = True
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Level 1-5 Autonomous Brain imports (lazy, fail-safe)
# ---------------------------------------------------------------------------


def _import_brain_module(module_path: str, func_name: str):
    """Lazy import a function from brain modules."""
    try:
        import importlib
        mod = importlib.import_module(module_path)
        return getattr(mod, func_name)
    except (ImportError, AttributeError) as e:
        LOG(f"Brain module import error ({module_path}.{func_name}): {e}")
        return None


def _run_brain_task(module_path: str, func_name: str, db_path: str) -> None:
    """Run a brain module function with error handling and Telegram logging."""
    fn = _import_brain_module(module_path, func_name)
    if fn:
        start = time.time()
        try:
            _brain_log(f"\U0001f9e0 Starting: <b>{func_name}</b>")
            fn(db_path)
            elapsed = time.time() - start
            _brain_log(f"\u2705 <b>{func_name}</b> done ({elapsed:.1f}s)")
        except Exception as e:
            elapsed = time.time() - start
            LOG(f"Brain task error ({func_name}): {e}")
            _brain_log(f"\u274c <b>{func_name}</b> failed ({elapsed:.1f}s): {str(e)[:200]}")
    else:
        LOG(f"Brain task skipped ({func_name}): module not available")


def _brain_log(message: str) -> None:
    """Send brain activity log to Telegram (non-blocking, fire-and-forget)."""
    try:
        env = _load_dotenv(TELEGRAM_ENV_PATH)
        token = env.get("TELEGRAM_BOT_TOKEN", "")
        allowed = env.get("TELEGRAM_ALLOWED_USERS", "")
        if not token or not allowed:
            return
        ts = datetime.now().strftime("%H:%M")
        msg = f"<i>[{ts}]</i> {message}"
        for uid in allowed.split(","):
            uid = uid.strip()
            if uid:
                try:
                    _telegram_send(token, int(uid), msg)
                except ValueError:
                    pass
    except Exception:
        pass  # Never let logging break the brain


def run_reflection(scope: str, db_path: str) -> None:
    """Run reflection with a fresh DB connection."""
    LOG(f"Starting {scope} reflection...")
    try:
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row

        from reflection.agent import ReflectionAgent
        agent = ReflectionAgent(db)

        if scope == "quick":
            result = asyncio.run(agent.run_quick())
        elif scope == "weekly":
            result = asyncio.run(agent.run_weekly())
        else:
            result = asyncio.run(agent.run_full())

        LOG(f"{scope} reflection complete: {result.get('type', '?')}")
        db.close()
    except Exception as e:
        LOG(f"{scope} reflection error: {e}")


def run_graph_enrichment(db_path: str) -> None:
    """Run graph enrichment (PageRank, co-occurrences)."""
    LOG("Starting graph enrichment...")
    try:
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row

        from graph.enricher import GraphEnricher
        enricher = GraphEnricher(db)

        enricher.compute_pagerank()
        cooc = enricher.strengthen_cooccurrences()

        LOG(f"Graph enrichment complete: {cooc} co-occurrence edges")
        db.close()
    except Exception as e:
        LOG(f"Graph enrichment error: {e}")


OLLAMA_BIN = "/usr/local/bin/ollama"
TELEGRAM_ENV_PATH = Path(__file__).parent.parent.parent / "telegram" / ".env"


def _load_dotenv(path: Path) -> dict[str, str]:
    """Load .env file and return key-value pairs (no side effects)."""
    result: dict[str, str] = {}
    if not path.is_file():
        return result
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            if key:
                result[key] = value
    return result


def _make_ssl_context() -> ssl.SSLContext:
    """Create SSL context using certifi certs if available."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _telegram_send(token: str, chat_id: int, text: str, parse_mode: str = "HTML") -> bool:
    """Send a Telegram message via Bot API. Returns True on success."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    # Telegram limit is 4096 chars
    payload = json.dumps({
        "chat_id": chat_id,
        "text": text[:4096],
        "parse_mode": parse_mode,
    }).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        ctx = _make_ssl_context()
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            result = json.loads(resp.read())
            return result.get("ok", False)
    except Exception as e:
        LOG(f"Telegram send error: {e}")
        return False


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text (terminal colors, cursor moves, etc.)."""
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]|\x1b\].*?\x07", "", text)


def _ollama_generate(prompt: str, model: str = "vitalii-brain", timeout: int = 120) -> str:
    """Generate text with Ollama CLI. Returns generated text or empty string."""
    try:
        env = os.environ.copy()
        env["NO_COLOR"] = "1"
        result = subprocess.run(
            [OLLAMA_BIN, "run", model, prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return _strip_ansi(result.stdout).strip()
    except subprocess.TimeoutExpired:
        LOG(f"Ollama timeout after {timeout}s")
        return ""
    except FileNotFoundError:
        LOG(f"Ollama binary not found at {OLLAMA_BIN}")
        return ""
    except Exception as e:
        LOG(f"Ollama error: {e}")
        return ""


def _save_insight_to_db(db_path: str, content: str, tags: list[str]) -> None:
    """Save an auto-generated insight as a knowledge record."""
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    try:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        db.execute(
            """INSERT INTO knowledge
               (session_id, type, content, project, tags, source,
                confidence, created_at, status)
               VALUES (?, 'lesson', ?, 'general', ?, 'dream-mode', 0.6, ?, 'active')""",
            (
                f"dream_{now}",
                content,
                json.dumps(tags),
                now,
            ),
        )
        db.commit()
    except Exception as e:
        LOG(f"Error saving dream insight: {e}")
    finally:
        db.close()


def _save_knowledge_record(
    db_path: str,
    content: str,
    record_type: str = "fact",
    tags: list[str] | None = None,
    source: str = "auto",
    confidence: float = 0.5,
    project: str = "general",
) -> None:
    """Save a knowledge record to DB. Reusable helper for new autonomous features."""
    db = sqlite3.connect(db_path)
    try:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        db.execute(
            """INSERT INTO knowledge
               (session_id, type, content, project, tags, source,
                confidence, created_at, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')""",
            (
                f"{source}_{now}_{uuid.uuid4().hex[:6]}",
                record_type,
                content,
                project,
                json.dumps(tags or []),
                source,
                confidence,
                now,
            ),
        )
        db.commit()
    except Exception as e:
        LOG(f"Error saving knowledge ({source}): {e}")
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Web Search Helper
# ---------------------------------------------------------------------------


def web_search(query: str, max_results: int = 5) -> list[dict[str, str]]:
    """Search DuckDuckGo HTML and return list of {title, url, snippet}."""
    import html as _html
    import re as _re
    ctx = _make_ssl_context()
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 ClaudeMemory/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        LOG(f"web_search fetch error: {e}")
        return []

    results: list[dict[str, str]] = []

    # DuckDuckGo HTML results are in <a class="result__a" ...> blocks
    # Title+URL from <a class="result__a" href="...">title</a>
    # Snippet from <a class="result__snippet" ...>snippet text</a>
    title_pattern = _re.compile(
        r'<a[^>]+class="result__a"[^>]+href="([^"]*)"[^>]*>(.*?)</a>',
        _re.DOTALL | _re.IGNORECASE,
    )
    snippet_pattern = _re.compile(
        r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
        _re.DOTALL | _re.IGNORECASE,
    )

    titles_urls = title_pattern.findall(html)
    snippets = snippet_pattern.findall(html)

    for i, (raw_url, raw_title) in enumerate(titles_urls):
        if i >= max_results:
            break
        # Clean HTML tags from title/snippet and decode entities
        clean_title = _html.unescape(_re.sub(r"<[^>]+>", "", raw_title).strip())
        clean_snippet = ""
        if i < len(snippets):
            clean_snippet = _html.unescape(_re.sub(r"<[^>]+>", "", snippets[i]).strip())

        # DuckDuckGo wraps URLs through redirect; extract actual URL
        if "uddg=" in raw_url:
            match = _re.search(r"uddg=([^&]+)", raw_url)
            if match:
                raw_url = urllib.parse.unquote(match.group(1))

        if clean_title and raw_url:
            results.append({
                "title": clean_title,
                "url": raw_url,
                "snippet": clean_snippet,
            })

    return results


def fetch_and_summarize(url: str, max_chars: int = 5000) -> str:
    """Fetch URL content, strip HTML, truncate to max_chars. Returns plain text."""
    import html as _html
    import re as _re
    ctx = _make_ssl_context()
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 ClaudeMemory/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "text" not in content_type and "html" not in content_type:
                return ""
            raw = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        LOG(f"fetch_and_summarize error for {url}: {e}")
        return ""

    # Strip HTML tags (simple approach)
    text = _re.sub(r"<script[^>]*>.*?</script>", " ", raw, flags=_re.DOTALL | _re.IGNORECASE)
    text = _re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=_re.DOTALL | _re.IGNORECASE)
    text = _re.sub(r"<[^>]+>", " ", text)
    # Collapse whitespace and decode HTML entities
    text = _re.sub(r"\s+", " ", text).strip()
    text = _html.unescape(text)
    return text[:max_chars]


# ---------------------------------------------------------------------------
# Curiosity Engine -- daily at 2:00 AM
# ---------------------------------------------------------------------------


def run_curiosity(db_path: str) -> None:
    """Research blind spots and uncertain knowledge via web search + Ollama.

    Runs daily at 2:00 AM (before dream mode at 3:00 AM).
    """
    LOG("=== CURIOSITY ENGINE STARTING ===")

    gaps: list[dict[str, str]] = []  # {description, source_type}

    try:
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row

        # 1. Active blind spots
        try:
            blind_spots = db.execute(
                "SELECT id, description FROM blind_spots WHERE status = 'active' ORDER BY severity DESC LIMIT 5"
            ).fetchall()
            for bs in blind_spots:
                gaps.append({"description": bs["description"], "source_type": "blind_spot"})
        except Exception as e:
            LOG(f"[curiosity] blind_spots query error: {e}")

        # 2. High recall but low confidence -- uncertain knowledge
        try:
            uncertain = db.execute(
                """SELECT content FROM knowledge
                   WHERE status = 'active' AND recall_count >= 3 AND confidence < 0.6
                   ORDER BY recall_count DESC LIMIT 5"""
            ).fetchall()
            for row in uncertain:
                # Extract first 200 chars as topic description
                topic = row["content"][:200].strip()
                gaps.append({"description": topic, "source_type": "uncertain_knowledge"})
        except Exception as e:
            LOG(f"[curiosity] uncertain knowledge query error: {e}")

        # 3. Recurring error categories
        try:
            cutoff_30d = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
            errors = db.execute(
                """SELECT category, COUNT(*) as cnt FROM errors
                   WHERE created_at > ? AND status = 'open'
                   GROUP BY category HAVING cnt >= 3
                   ORDER BY cnt DESC LIMIT 3""",
                (cutoff_30d,),
            ).fetchall()
            for row in errors:
                gaps.append({
                    "description": f"Recurring error: {row['category']} ({row['cnt']} times in 30 days)",
                    "source_type": "error_pattern",
                })
        except Exception as e:
            LOG(f"[curiosity] errors query error: {e}")

        db.close()
    except Exception as e:
        LOG(f"[curiosity] DB connection error: {e}")
        return

    if not gaps:
        LOG("[curiosity] No knowledge gaps found, skipping")
        return

    # Process max 3 gaps per run
    topics_researched = 0
    for gap in gaps[:3]:
        desc = gap["description"]
        LOG(f"[curiosity] Researching: {desc[:80]}...")

        # Build search query
        search_query = desc[:100]
        if gap["source_type"] == "error_pattern":
            search_query += " solution best practice"
        elif gap["source_type"] == "uncertain_knowledge":
            search_query += " explained tutorial"

        try:
            results = web_search(search_query, max_results=5)
            if not results:
                LOG(f"[curiosity] No search results for: {search_query[:60]}")
                time.sleep(2)  # Rate limit
                continue

            # Fetch top 2 results
            combined_text = ""
            for r in results[:2]:
                fetched = fetch_and_summarize(r["url"], max_chars=3000)
                if fetched:
                    combined_text += f"\n\n--- Source: {r['title']} ({r['url']}) ---\n{fetched}"
                time.sleep(2)  # Rate limit between requests

            if not combined_text.strip():
                LOG(f"[curiosity] No content fetched for: {desc[:60]}")
                continue

            # Ask Ollama to summarize
            prompt = (
                f"Summarize this for a developer. Extract key facts and actionable advice.\n\n"
                f"Topic: {desc}\n\n"
                f"Sources:\n{combined_text[:6000]}"
            )
            summary = _ollama_generate(prompt, timeout=180)
            if not summary:
                LOG(f"[curiosity] Ollama returned empty for: {desc[:60]}")
                continue

            # Save to knowledge
            _save_knowledge_record(
                db_path,
                content=f"[Curiosity Research] {desc}\n\n{summary}",
                record_type="fact",
                tags=["curiosity", "auto-research", gap["source_type"]],
                source="curiosity-engine",
                confidence=0.5,
            )
            topics_researched += 1
            LOG(f"[curiosity] Saved research on: {desc[:60]}")

        except Exception as e:
            LOG(f"[curiosity] Error researching '{desc[:60]}': {e}")

        time.sleep(2)  # Rate limit between gap research

    # Telegram notification
    if topics_researched > 0:
        env = _load_dotenv(TELEGRAM_ENV_PATH)
        token = env.get("TELEGRAM_BOT_TOKEN", "")
        allowed = env.get("TELEGRAM_ALLOWED_USERS", "")
        if token and allowed:
            msg = (
                f"\U0001f9e0 Curiosity: I researched {topics_researched} topic(s) overnight. "
                f"Check /search curiosity for details."
            )
            for uid in allowed.split(","):
                uid = uid.strip()
                if uid:
                    try:
                        _telegram_send(token, int(uid), msg)
                    except ValueError:
                        pass

    LOG(f"=== CURIOSITY ENGINE COMPLETE === ({topics_researched} topics researched)")


# ---------------------------------------------------------------------------
# Proactive Advisor -- daily at 8:30 AM
# ---------------------------------------------------------------------------


def run_advisor(db_path: str) -> None:
    """Analyze recent activity and send practical daily tips via Telegram.

    Runs daily at 8:30 AM.
    """
    LOG("=== PROACTIVE ADVISOR STARTING ===")

    env = _load_dotenv(TELEGRAM_ENV_PATH)
    token = env.get("TELEGRAM_BOT_TOKEN", "")
    allowed = env.get("TELEGRAM_ALLOWED_USERS", "")

    if not token or not allowed:
        LOG("[advisor] Telegram credentials not configured, skipping")
        return

    analysis_parts: list[str] = []

    try:
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row

        cutoff_7d = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
        cutoff_14d = (datetime.now(timezone.utc) - timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%SZ")

        # 1. Solutions per project (most active)
        try:
            active_projects = db.execute(
                """SELECT project, COUNT(*) as cnt FROM knowledge
                   WHERE status = 'active' AND type = 'solution' AND created_at > ?
                   GROUP BY project ORDER BY cnt DESC LIMIT 5""",
                (cutoff_7d,),
            ).fetchall()
            if active_projects:
                parts = [f"{r['project']}({r['cnt']})" for r in active_projects]
                analysis_parts.append(f"Active projects (7d solutions): {', '.join(parts)}")
        except Exception as e:
            LOG(f"[advisor] active projects query error: {e}")

        # 2. Repeated concepts (3+ times in 7 days)
        try:
            # Look at tags for recurring themes
            rows = db.execute(
                """SELECT tags FROM knowledge
                   WHERE status = 'active' AND created_at > ?""",
                (cutoff_7d,),
            ).fetchall()
            tag_counts: dict[str, int] = {}
            for row in rows:
                try:
                    tags_list = json.loads(row["tags"]) if row["tags"] else []
                    for tag in tags_list:
                        if tag and tag not in ("auto", "session-autosave", "context-recovery"):
                            tag_counts[tag] = tag_counts.get(tag, 0) + 1
                except (json.JSONDecodeError, TypeError):
                    pass
            frequent = [(t, c) for t, c in tag_counts.items() if c >= 3]
            frequent.sort(key=lambda x: x[1], reverse=True)
            if frequent:
                parts = [f"{t}({c})" for t, c in frequent[:8]]
                analysis_parts.append(f"Recurring topics (7d, 3+): {', '.join(parts)}")
        except Exception as e:
            LOG(f"[advisor] recurring topics query error: {e}")

        # 3. Stale projects (10+ records, no activity 14+ days)
        try:
            stale = db.execute(
                """SELECT project, COUNT(*) as cnt, MAX(created_at) as last_active
                   FROM knowledge
                   WHERE project IS NOT NULL AND project != 'general' AND status = 'active'
                   GROUP BY project
                   HAVING cnt >= 10 AND last_active < ?
                   ORDER BY last_active ASC LIMIT 5""",
                (cutoff_14d,),
            ).fetchall()
            if stale:
                parts = [f"{r['project']}(last: {r['last_active'][:10]})" for r in stale]
                analysis_parts.append(f"Stale projects (14+ days idle): {', '.join(parts)}")
        except Exception as e:
            LOG(f"[advisor] stale projects query error: {e}")

        # 4. Recent error count
        try:
            error_row = db.execute(
                "SELECT COUNT(*) as cnt FROM errors WHERE created_at > ? AND status = 'open'",
                (cutoff_7d,),
            ).fetchone()
            if error_row and error_row["cnt"] > 0:
                analysis_parts.append(f"Open errors (7d): {error_row['cnt']}")
        except Exception as e:
            LOG(f"[advisor] errors query error: {e}")

        # 5. Knowledge growth
        try:
            growth_row = db.execute(
                "SELECT COUNT(*) as cnt FROM knowledge WHERE created_at > ? AND status = 'active'",
                (cutoff_7d,),
            ).fetchone()
            total_row = db.execute(
                "SELECT COUNT(*) as cnt FROM knowledge WHERE status = 'active'"
            ).fetchone()
            if growth_row and total_row:
                analysis_parts.append(
                    f"Knowledge: +{growth_row['cnt']} this week, {total_row['cnt']} total"
                )
        except Exception as e:
            LOG(f"[advisor] knowledge growth query error: {e}")

        db.close()
    except Exception as e:
        LOG(f"[advisor] DB connection error: {e}")
        return

    if not analysis_parts:
        LOG("[advisor] No activity data to analyze")
        return

    # Ask Ollama for tips
    prompt = (
        "You are a productivity advisor for a software developer. "
        "Based on this week's activity data, generate 2-3 practical, specific tips. "
        "Be concise (1-2 sentences each). Focus on actionable advice.\n\n"
        "Activity data:\n"
        + "\n".join(f"- {p}" for p in analysis_parts)
        + "\n\nTips:"
    )

    tips = _ollama_generate(prompt, timeout=120)
    if not tips:
        LOG("[advisor] Ollama returned empty, sending raw data instead")
        tips = "Ollama unavailable. Raw activity:\n" + "\n".join(f"- {p}" for p in analysis_parts)

    # Build Telegram message
    today = datetime.now().strftime("%A, %B %d")
    message_lines = [
        f"<b>\u2615 Morning Briefing -- {today}</b>",
        "",
        tips,
        "",
        "<i>Data: " + " | ".join(analysis_parts[:3]) + "</i>",
    ]
    message = "\n".join(message_lines)

    # Send to all allowed users
    for uid in allowed.split(","):
        uid = uid.strip()
        if uid:
            try:
                _telegram_send(token, int(uid), message)
            except ValueError:
                pass

    # Save tips to knowledge
    _save_knowledge_record(
        db_path,
        content=f"[Daily Advisor Tips] {today}\n\n{tips}",
        record_type="lesson",
        tags=["advisor", "daily-tip"],
        source="advisor",
        confidence=0.6,
    )

    LOG("=== PROACTIVE ADVISOR COMPLETE ===")


def run_dream_mode(db_path: str) -> None:
    """Dream mode: deep night processing with extended reflection and Ollama insights.

    Runs daily at 3:00 AM:
    1. Full reflection with 30-day lookback
    2. SelfModel.update_trends()
    3. Graph enrichment (PageRank)
    4. Ollama insight generation from cross-project patterns
    5. Save insights as knowledge records
    """
    LOG("=== DREAM MODE STARTING ===")
    dream_start = time.time()

    # Phase 1: Full reflection (digest + synthesize) with 30-day lookback
    LOG("[dream] Phase 1: Extended reflection (30-day lookback)...")
    synthesis_stats: dict = {}
    cross_project_patterns: list[dict] = []
    try:
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row

        from reflection.agent import ReflectionAgent
        agent = ReflectionAgent(db)

        # Run digest
        digest_stats = agent.digest.run()
        LOG(f"[dream] Digest complete: {digest_stats}")

        # Run synthesize with extended 30-day lookback
        synthesis_stats = agent.synthesize.run(days=30)
        LOG(f"[dream] Synthesis complete: {synthesis_stats}")

        # Capture cross-project patterns for Ollama
        cross_project_patterns = agent.synthesize.find_cross_project_patterns()
        LOG(f"[dream] Found {len(cross_project_patterns)} cross-project patterns")

        db.close()
    except Exception as e:
        LOG(f"[dream] Phase 1 error: {e}")

    # Phase 2: Update competency trends
    LOG("[dream] Phase 2: Updating competency trends...")
    try:
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row

        from memory_systems.self_model import SelfModel
        model = SelfModel(db)
        model.update_trends()
        LOG("[dream] Competency trends updated")

        db.close()
    except Exception as e:
        LOG(f"[dream] Phase 2 error: {e}")

    # Phase 3: Graph enrichment (PageRank recalculation)
    LOG("[dream] Phase 3: Graph enrichment...")
    run_graph_enrichment(db_path)

    # Phase 4: Ollama insight generation
    LOG("[dream] Phase 4: Generating insights with Ollama...")
    insights_saved = 0
    try:
        if cross_project_patterns:
            # Build a prompt from cross-project patterns
            pattern_summary = "\n".join(
                f"- {p['pattern']}: used in {', '.join(p['projects'])} ({p['count']} times)"
                for p in cross_project_patterns[:20]
            )
            prompt = (
                "You are analyzing a developer's knowledge base. "
                "Here are cross-project patterns found:\n\n"
                f"{pattern_summary}\n\n"
                "Generate 3-5 actionable insights about:\n"
                "1. What skills are transferable across projects\n"
                "2. What architectural patterns keep recurring\n"
                "3. What blind spots might exist\n"
                "4. What should be learned next based on these patterns\n\n"
                "Format: one insight per line, prefixed with number. "
                "Be specific and practical. Max 2 sentences each."
            )

            raw_output = _ollama_generate(prompt, timeout=180)
            if raw_output:
                # Parse individual insights (lines starting with number)
                for line in raw_output.split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    # Lines that start with a digit or bullet
                    if line[0].isdigit() or line[0] in "-*":
                        # Clean the prefix
                        clean = line.lstrip("0123456789.-)*: ")
                        if len(clean) > 20:  # Skip trivially short lines
                            _save_insight_to_db(
                                db_path,
                                clean,
                                ["dream", "auto-insight", "cross-project"],
                            )
                            insights_saved += 1
                            LOG(f"[dream] Saved insight: {clean[:80]}...")

                LOG(f"[dream] Ollama generated {insights_saved} insights")
            else:
                LOG("[dream] Ollama returned empty response")
        else:
            LOG("[dream] No cross-project patterns to analyze")
    except Exception as e:
        LOG(f"[dream] Phase 4 error: {e}")

    elapsed = time.time() - dream_start
    LOG(
        f"=== DREAM MODE COMPLETE === "
        f"({elapsed:.1f}s, {insights_saved} insights saved, "
        f"{synthesis_stats.get('clusters_found', 0)} clusters, "
        f"{len(cross_project_patterns)} patterns)"
    )


def run_weekly_telegram_digest(db_path: str) -> None:
    """Send weekly digest via Telegram. Runs every Sunday at 10:00 AM."""
    LOG("Starting weekly Telegram digest...")

    # Load Telegram credentials
    env = _load_dotenv(TELEGRAM_ENV_PATH)
    token = env.get("TELEGRAM_BOT_TOKEN", "")
    allowed_users_raw = env.get("TELEGRAM_ALLOWED_USERS", "")

    if not token:
        LOG("TELEGRAM_BOT_TOKEN not found in .env, skipping digest")
        return

    chat_ids: list[int] = []
    for uid in allowed_users_raw.split(","):
        uid = uid.strip()
        if uid:
            try:
                chat_ids.append(int(uid))
            except ValueError:
                pass

    if not chat_ids:
        LOG("No TELEGRAM_ALLOWED_USERS configured, skipping digest")
        return

    # Phase 1: Run weekly reflection and get digest data
    weekly_digest: dict = {}
    competency_report: dict = {}
    try:
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row

        from reflection.agent import ReflectionAgent
        agent = ReflectionAgent(db)
        report = asyncio.run(agent.run_weekly())
        weekly_digest = report.get("weekly_digest") or {}

        LOG(f"Weekly digest data: {weekly_digest.get('sessions_count', 0)} sessions")

        # Get competency data for trends
        from memory_systems.self_model import SelfModel
        model = SelfModel(db)
        competency_report = model.full_report()

        db.close()
    except Exception as e:
        LOG(f"Weekly digest data collection error: {e}")

    if not weekly_digest:
        LOG("No weekly digest data available, skipping Telegram send")
        return

    # Phase 2: Format the message as HTML
    period = weekly_digest.get("period", "last week")
    sessions = weekly_digest.get("sessions_count", 0)
    memories = weekly_digest.get("memories_created", 0)
    focus_areas = weekly_digest.get("focus_areas", [])
    top_concepts = weekly_digest.get("top_concepts", [])
    blind_spots = weekly_digest.get("blind_spots_active", 0)
    skills_refined = weekly_digest.get("skills_refined", 0)
    episodes = weekly_digest.get("episodes", {})

    # Competency changes
    comp_count = competency_report.get("competency_count", 0)
    avg_level = competency_report.get("avg_level", 0)
    trend_summary = competency_report.get("trend_summary", {})
    improving = trend_summary.get("improving", 0)
    declining = trend_summary.get("declining", 0)

    # Build HTML message
    lines: list[str] = []
    lines.append(f"<b>Weekly Memory Digest</b>")
    lines.append(f"<i>{period}</i>")
    lines.append("")

    lines.append(f"<b>Activity</b>")
    lines.append(f"  Sessions: {sessions}")
    lines.append(f"  Memories created: {memories}")
    lines.append(f"  Skills refined: {skills_refined}")
    if episodes:
        ep_parts = [f"{k}: {v}" for k, v in episodes.items()]
        lines.append(f"  Episodes: {', '.join(ep_parts)}")
    lines.append("")

    if focus_areas:
        lines.append(f"<b>Focus Areas</b>")
        for area in focus_areas[:5]:
            lines.append(f"  {area}")
        lines.append("")

    if top_concepts:
        lines.append(f"<b>Top Concepts</b>")
        for c in top_concepts[:7]:
            name = c.get("name", "?")
            mentions = c.get("mentions", 0)
            lines.append(f"  {name} ({mentions} mentions)")
        lines.append("")

    lines.append(f"<b>Competencies</b>")
    lines.append(f"  Total: {comp_count} domains")
    lines.append(f"  Average level: {avg_level:.2f}")
    if improving:
        lines.append(f"  Improving: {improving}")
    if declining:
        lines.append(f"  Declining: {declining}")
    lines.append("")

    if blind_spots:
        lines.append(f"<b>Blind Spots</b>: {blind_spots} active")
        lines.append("")

    # Propose new skills from competency data
    new_skills: list[str] = []
    for comp in competency_report.get("competencies", []):
        if comp.get("trend") == "improving" and comp.get("level", 0) > 0.7:
            new_skills.append(comp["domain"])
    if new_skills:
        lines.append(f"<b>Skill Growth</b>")
        for s in new_skills[:5]:
            lines.append(f"  {s}")
        lines.append("")

    lines.append("Generated by Dream Mode")

    message = "\n".join(lines)

    # Phase 3: Send to all allowed users
    for chat_id in chat_ids:
        success = _telegram_send(token, chat_id, message)
        if success:
            LOG(f"Weekly digest sent to {chat_id}")
        else:
            LOG(f"Failed to send weekly digest to {chat_id}")

    LOG("Weekly Telegram digest complete")


def run_rss_poll(db_path: str) -> None:
    """Poll RSS feeds and save new items to knowledge. Runs every 2 hours."""
    LOG("Starting RSS feed poll...")

    feeds_path = MEMORY_DIR / "rss_feeds.json"
    state_path = MEMORY_DIR / "rss_state.json"

    if not feeds_path.is_file():
        LOG("No rss_feeds.json found, skipping RSS poll")
        return

    try:
        with open(feeds_path) as f:
            feeds: list[dict[str, Any]] = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        LOG(f"Error reading rss_feeds.json: {e}")
        return

    if not feeds:
        LOG("RSS feeds list is empty")
        return

    # Load state (last seen item id/link per feed URL)
    state: dict[str, str] = {}
    if state_path.is_file():
        try:
            with open(state_path) as f:
                state = json.load(f)
        except (json.JSONDecodeError, IOError):
            state = {}

    total_new = 0
    feeds_with_new = 0
    ctx = _make_ssl_context()

    for feed_info in feeds:
        feed_url = feed_info.get("url", "")
        if not feed_url:
            continue

        try:
            req = urllib.request.Request(
                feed_url,
                headers={"User-Agent": "ClaudeMemory-RSS/1.0"},
            )
            with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
                xml_data = resp.read()

            root = ET.fromstring(xml_data)

            # Support both RSS 2.0 and Atom
            items: list[tuple[str, str, str]] = []  # (id, title, link)
            # RSS 2.0
            for item in root.iter("item"):
                guid_el = item.find("guid")
                link_el = item.find("link")
                title_el = item.find("title")
                item_id = (guid_el.text if guid_el is not None and guid_el.text else
                           link_el.text if link_el is not None and link_el.text else "")
                title = title_el.text if title_el is not None and title_el.text else "Untitled"
                link = link_el.text if link_el is not None and link_el.text else ""
                if item_id:
                    items.append((item_id, title, link))

            # Atom
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
                id_el = entry.find("atom:id", ns)
                title_el = entry.find("atom:title", ns)
                link_el = entry.find("atom:link", ns)
                item_id = id_el.text if id_el is not None and id_el.text else ""
                title = title_el.text if title_el is not None and title_el.text else "Untitled"
                link = link_el.get("href", "") if link_el is not None else ""
                if not item_id and link:
                    item_id = link
                if item_id:
                    items.append((item_id, title, link))

            last_seen = state.get(feed_url, "")
            new_items: list[tuple[str, str, str]] = []
            for item_id, title, link in items:
                if item_id == last_seen:
                    break
                new_items.append((item_id, title, link))

            if new_items and items:
                state[feed_url] = items[0][0]  # Update to newest

            if new_items:
                feeds_with_new += 1
                total_new += len(new_items)

                # Save to DB
                db = sqlite3.connect(db_path)
                now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                for item_id, title, link in new_items:
                    content = f"{title}\n{link}" if link else title
                    try:
                        db.execute(
                            """INSERT INTO knowledge
                               (session_id, type, content, project, tags, source,
                                confidence, created_at, status)
                               VALUES (?, 'fact', ?, 'general', ?, 'rss', 0.5, ?, 'active')""",
                            (
                                f"rss_{now}_{uuid.uuid4().hex[:8]}",
                                content,
                                json.dumps(["rss", "news"]),
                                now,
                            ),
                        )
                    except Exception as e:
                        LOG(f"Error saving RSS item: {e}")
                db.commit()
                db.close()

                LOG(f"RSS: {len(new_items)} new items from {feed_url}")

        except Exception as e:
            LOG(f"RSS fetch error for {feed_url}: {e}")

    # Save state
    try:
        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)
    except IOError as e:
        LOG(f"Error saving rss_state.json: {e}")

    # Telegram notification if significant
    if total_new > 3:
        env = _load_dotenv(TELEGRAM_ENV_PATH)
        token = env.get("TELEGRAM_BOT_TOKEN", "")
        allowed = env.get("TELEGRAM_ALLOWED_USERS", "")
        if token and allowed:
            for uid in allowed.split(","):
                uid = uid.strip()
                if uid:
                    try:
                        _telegram_send(
                            token, int(uid),
                            f"\U0001f4f0 {total_new} new articles from {feeds_with_new} feeds",
                        )
                    except ValueError:
                        pass

    LOG(f"RSS poll complete: {total_new} new items from {feeds_with_new} feeds")


def run_reminders(db_path: str) -> None:
    """Send reminders about inactive projects and upcoming deadlines. Daily at 9:00 AM."""
    LOG("Starting inactive project reminders...")

    env = _load_dotenv(TELEGRAM_ENV_PATH)
    token = env.get("TELEGRAM_BOT_TOKEN", "")
    allowed = env.get("TELEGRAM_ALLOWED_USERS", "")

    if not token or not allowed:
        LOG("Telegram credentials not configured, skipping reminders")
        return

    lines: list[str] = []

    try:
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row

        # Find projects with 10+ records but no activity in 14+ days
        cutoff = (datetime.now(timezone.utc) - timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%SZ")
        rows = db.execute(
            """SELECT project, COUNT(*) as cnt, MAX(created_at) as last_active
               FROM knowledge
               WHERE project IS NOT NULL AND project != 'general' AND status = 'active'
               GROUP BY project
               HAVING cnt >= 10 AND last_active < ?
               ORDER BY last_active ASC""",
            (cutoff,),
        ).fetchall()

        if rows:
            lines.append("<b>Inactive Projects (14+ days)</b>")
            for row in rows:
                last = row["last_active"][:10] if row["last_active"] else "?"
                lines.append(f"  {row['project']} — {row['cnt']} records, last: {last}")
            lines.append("")

        # Find upcoming deadlines
        deadline_rows = db.execute(
            """SELECT project, content, created_at
               FROM knowledge
               WHERE status = 'active'
                 AND (LOWER(content) LIKE '%deadline%' OR LOWER(content) LIKE '%дедлайн%')
               ORDER BY created_at DESC
               LIMIT 10""",
        ).fetchall()

        if deadline_rows:
            lines.append("<b>Deadline Mentions</b>")
            for row in deadline_rows:
                proj = row["project"] or "general"
                snippet = row["content"][:100].replace("<", "&lt;").replace(">", "&gt;")
                lines.append(f"  [{proj}] {snippet}")
            lines.append("")

        db.close()
    except Exception as e:
        LOG(f"Reminders query error: {e}")

    if not lines:
        LOG("No inactive projects or deadlines found")
        return

    message = "\n".join(lines)
    for uid in allowed.split(","):
        uid = uid.strip()
        if uid:
            try:
                _telegram_send(token, int(uid), message)
            except ValueError:
                pass

    LOG("Reminders sent")


def run_github_monitor(db_path: str) -> None:
    """Monitor GitHub repos for new releases. Runs every 6 hours."""
    LOG("Starting GitHub repo monitor...")

    repos_path = MEMORY_DIR / "github_repos.json"
    state_path = MEMORY_DIR / "github_state.json"

    if not repos_path.is_file():
        LOG("No github_repos.json found, skipping GitHub monitor")
        return

    try:
        with open(repos_path) as f:
            repos: list[dict[str, Any]] = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        LOG(f"Error reading github_repos.json: {e}")
        return

    if not repos:
        LOG("GitHub repos list is empty")
        return

    # Load state
    state: dict[str, str] = {}
    if state_path.is_file():
        try:
            with open(state_path) as f:
                state = json.load(f)
        except (json.JSONDecodeError, IOError):
            state = {}

    new_releases: list[str] = []
    ctx = _make_ssl_context()

    for repo_info in repos:
        owner = repo_info.get("owner", "")
        repo = repo_info.get("repo", "")
        if not owner or not repo:
            continue

        repo_key = f"{owner}/{repo}"
        api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"

        try:
            req = urllib.request.Request(
                api_url,
                headers={
                    "User-Agent": "ClaudeMemory-GitHub/1.0",
                    "Accept": "application/vnd.github+json",
                },
            )
            with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
                data = json.loads(resp.read())

            tag = data.get("tag_name", "")
            name = data.get("name", tag)
            html_url = data.get("html_url", "")
            body = data.get("body", "")[:300]

            if not tag:
                continue

            last_seen_tag = state.get(repo_key, "")
            if tag != last_seen_tag:
                state[repo_key] = tag

                # Only notify if we had a previous state (skip first run)
                if last_seen_tag:
                    new_releases.append(f"{repo_key} {tag}")

                    # Save to DB
                    db = sqlite3.connect(db_path)
                    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                    content = f"New release: {repo_key} {tag}\n{name}\n{html_url}\n{body}".strip()
                    try:
                        db.execute(
                            """INSERT INTO knowledge
                               (session_id, type, content, project, tags, source,
                                confidence, created_at, status)
                               VALUES (?, 'fact', ?, 'general', ?, 'github', 0.7, ?, 'active')""",
                            (
                                f"github_{now}_{uuid.uuid4().hex[:8]}",
                                content,
                                json.dumps(["github", "release", repo]),
                                now,
                            ),
                        )
                        db.commit()
                    except Exception as e:
                        LOG(f"Error saving GitHub release: {e}")
                    finally:
                        db.close()

                    LOG(f"GitHub: new release {repo_key} {tag}")

        except urllib.error.HTTPError as e:
            if e.code == 404:
                LOG(f"GitHub: no releases for {repo_key}")
            else:
                LOG(f"GitHub API error for {repo_key}: {e.code} {e.reason}")
        except Exception as e:
            LOG(f"GitHub fetch error for {repo_key}: {e}")

    # Save state
    try:
        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)
    except IOError as e:
        LOG(f"Error saving github_state.json: {e}")

    # Telegram notification
    if new_releases:
        env = _load_dotenv(TELEGRAM_ENV_PATH)
        token = env.get("TELEGRAM_BOT_TOKEN", "")
        allowed = env.get("TELEGRAM_ALLOWED_USERS", "")
        if token and allowed:
            msg_lines = ["\U0001f4e6 <b>New GitHub Releases</b>"]
            for rel in new_releases:
                msg_lines.append(f"  {rel}")
            msg = "\n".join(msg_lines)
            for uid in allowed.split(","):
                uid = uid.strip()
                if uid:
                    try:
                        _telegram_send(token, int(uid), msg)
                    except ValueError:
                        pass

    LOG(f"GitHub monitor complete: {len(new_releases)} new releases")


def run_auto_retrain(db_path: str) -> None:
    """Auto-retrain Ollama vitalii-brain if 100+ new knowledge records. Weekly Wednesday 4:00 AM."""
    LOG("Starting auto-retrain check...")

    state_path = MEMORY_DIR / "retrain_state.json"
    project_root = Path(__file__).parent.parent.parent  # claude-memory-server root
    export_script = project_root / "ollama" / "export_knowledge.py"
    venv_python = project_root / ".venv" / "bin" / "python"

    # Load state
    state: dict[str, Any] = {}
    if state_path.is_file():
        try:
            with open(state_path) as f:
                state = json.load(f)
        except (json.JSONDecodeError, IOError):
            state = {}

    last_retrain = state.get("last_retrain", "1970-01-01T00:00:00Z")

    try:
        db = sqlite3.connect(db_path)
        row = db.execute(
            "SELECT COUNT(*) as cnt FROM knowledge WHERE created_at > ? AND status = 'active'",
            (last_retrain,),
        ).fetchone()
        new_count = row[0] if row else 0
        db.close()
    except Exception as e:
        LOG(f"Auto-retrain DB query error: {e}")
        return

    LOG(f"Auto-retrain: {new_count} new records since last retrain ({last_retrain[:10]})")

    if new_count < 10:
        LOG("Not enough new records for retrain (need 10+), skipping")
        return

    # Phase 1: Export knowledge to Modelfile
    LOG("Auto-retrain: exporting knowledge...")
    python_bin = str(venv_python) if venv_python.is_file() else sys.executable
    try:
        result = subprocess.run(
            [python_bin, str(export_script), "--mode", "modelfile"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(project_root),
        )
        if result.returncode != 0:
            LOG(f"Auto-retrain export failed: {result.stderr[:500]}")
            return
        LOG("Auto-retrain: export complete")
    except Exception as e:
        LOG(f"Auto-retrain export error: {e}")
        return

    # Phase 2: Rebuild Ollama model
    LOG("Auto-retrain: creating Ollama model...")
    modelfile_path = project_root / "ollama" / "output" / "Modelfile"
    if not modelfile_path.is_file():
        # Fallback to ollama/Modelfile
        modelfile_path = project_root / "ollama" / "Modelfile"
    if not modelfile_path.is_file():
        LOG(f"Modelfile not found at {modelfile_path}")
        return

    try:
        result = subprocess.run(
            [OLLAMA_BIN, "create", "vitalii-brain", "-f", str(modelfile_path)],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=str(project_root / "ollama"),
        )
        if result.returncode != 0:
            LOG(f"Auto-retrain ollama create failed: {result.stderr[:500]}")
            return
        LOG("Auto-retrain: Ollama model rebuilt successfully")
    except Exception as e:
        LOG(f"Auto-retrain ollama error: {e}")
        return

    # Update state
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    state["last_retrain"] = now
    state["records_at_retrain"] = new_count
    try:
        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)
    except IOError as e:
        LOG(f"Error saving retrain_state.json: {e}")

    # Telegram notification
    env = _load_dotenv(TELEGRAM_ENV_PATH)
    token = env.get("TELEGRAM_BOT_TOKEN", "")
    allowed = env.get("TELEGRAM_ALLOWED_USERS", "")
    if token and allowed:
        msg = f"\U0001f9e0 Ollama vitalii-brain retrained ({new_count} new records)"
        for uid in allowed.split(","):
            uid = uid.strip()
            if uid:
                try:
                    _telegram_send(token, int(uid), msg)
                except ValueError:
                    pass

    LOG(f"Auto-retrain complete: model rebuilt with {new_count} new records")


def run_task_processor(db_path: str) -> None:
    """Process tasks: research, generate briefings, send notifications.

    Runs every 3 hours:
    1. Pending tasks with deadline 2+ days away -> start research
    2. Researching tasks -> generate briefings with Ollama
    3. Tasks due tomorrow -> send urgent reminders
    4. Overdue tasks -> update status, notify
    """
    LOG("Starting task processor...")

    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from tools.task_manager import TaskManager
    except ImportError as e:
        LOG(f"TaskManager import error: {e}")
        return

    tm = TaskManager(db_path)
    tm.ensure_table()

    # Ensure learning_saved_at column exists for Phase 6
    try:
        _db = sqlite3.connect(db_path)
        _db.execute("ALTER TABLE tasks ADD COLUMN learning_saved_at TEXT")
        _db.commit()
        _db.close()
    except Exception:
        pass  # Column already exists

    # Load Telegram credentials for notifications
    env = _load_dotenv(TELEGRAM_ENV_PATH)
    token = env.get("TELEGRAM_BOT_TOKEN", "")
    allowed_users_raw = env.get("TELEGRAM_ALLOWED_USERS", "")
    chat_ids: list[int] = []
    for uid in allowed_users_raw.split(","):
        uid = uid.strip()
        if uid:
            try:
                chat_ids.append(int(uid))
            except ValueError:
                pass

    now = datetime.now(timezone.utc)
    tasks_processed = 0
    briefings_created = 0
    notifications_sent = 0

    # Phase 1: Start research for pending tasks with deadline 2+ days away
    LOG("[task-proc] Phase 1: Research pending tasks...")
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    try:
        pending = db.execute(
            "SELECT * FROM tasks WHERE status = 'pending' AND deadline IS NOT NULL "
            "ORDER BY deadline ASC"
        ).fetchall()

        researched_count = 0
        for task in pending:
            if researched_count >= 2:
                break  # Max 2 per run to avoid rate limits

            deadline_str = task["deadline"]
            try:
                deadline_dt = datetime.fromisoformat(deadline_str.replace("Z", "+00:00"))
                if deadline_dt.tzinfo is None:
                    deadline_dt = deadline_dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue

            days_until = (deadline_dt - now).total_seconds() / 86400

            # Only auto-research tasks with 2+ days remaining
            if days_until >= 2:
                LOG(f"[task-proc] Researching task #{task['id']}: {task['title'][:50]}")
                try:
                    results = tm.research_task(task["id"])
                    if results:
                        researched_count += 1
                        tasks_processed += 1
                        LOG(f"[task-proc] Research complete: {len(results)} sources for #{task['id']}")
                except Exception as e:
                    LOG(f"[task-proc] Research error for #{task['id']}: {e}")
    except Exception as e:
        LOG(f"[task-proc] Phase 1 error: {e}")
    finally:
        db.close()

    # Phase 2: Generate briefings for researched tasks
    LOG("[task-proc] Phase 2: Generate briefings...")
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    try:
        researching = db.execute(
            "SELECT * FROM tasks WHERE status = 'researching' AND research_results IS NOT NULL "
            "ORDER BY deadline ASC NULLS LAST"
        ).fetchall()

        for task in researching[:2]:  # Max 2 briefings per run (Ollama is slow)
            LOG(f"[task-proc] Generating briefing for #{task['id']}: {task['title'][:50]}")
            try:
                briefing = tm.generate_briefing(task["id"])
                if briefing:
                    briefings_created += 1
                    LOG(f"[task-proc] Briefing ready for #{task['id']}")

                    # Notify via Telegram
                    if token and chat_ids:
                        title = task["title"][:60]
                        for cid in chat_ids:
                            _telegram_send(
                                token, cid,
                                f"\U0001f4cb Briefing ready for: <b>{title}</b>\n"
                                f"Send /task {task['id']} to read.",
                            )
                            notifications_sent += 1
                else:
                    LOG(f"[task-proc] Empty briefing for #{task['id']} (Ollama offline?)")
            except Exception as e:
                LOG(f"[task-proc] Briefing error for #{task['id']}: {e}")
    except Exception as e:
        LOG(f"[task-proc] Phase 2 error: {e}")
    finally:
        db.close()

    # Phase 3: Urgent reminders for tasks due within 1 day
    LOG("[task-proc] Phase 3: Deadline reminders...")
    if token and chat_ids:
        upcoming = tm.get_upcoming(days=1)
        for task in upcoming:
            if task["status"] not in ("done", "ready"):
                # Only notify if not already notified in last 6 hours
                last_notified = task.get("notified_at")
                if last_notified:
                    try:
                        last_dt = datetime.fromisoformat(last_notified.replace("Z", "+00:00"))
                        if last_dt.tzinfo is None:
                            last_dt = last_dt.replace(tzinfo=timezone.utc)
                        if (now - last_dt).total_seconds() < 6 * 3600:
                            continue
                    except ValueError:
                        pass

                title = task["title"][:60]
                status = task["status"]
                for cid in chat_ids:
                    _telegram_send(
                        token, cid,
                        f"\u26a0\ufe0f Task <b>#{task['id']}</b> due tomorrow!\n"
                        f"{title}\nStatus: {status}",
                    )
                    notifications_sent += 1
                tm.update_notified(task["id"])

    # Phase 4: Mark overdue tasks
    LOG("[task-proc] Phase 4: Overdue check...")
    overdue = tm.get_overdue()
    for task in overdue:
        tm.update_status(task["id"], "overdue")
        if token and chat_ids:
            title = task["title"][:60]
            for cid in chat_ids:
                _telegram_send(
                    token, cid,
                    f"\u2757 Overdue: <b>#{task['id']}</b> {title}",
                )
                notifications_sent += 1

    # Phase 5: Process recurring tasks (daily re-research)
    LOG("[task-proc] Phase 5: Recurring tasks...")
    recurring_processed = 0
    try:
        from tools.task_manager import get_recurring_tasks, mark_recurring_done
        recurring = get_recurring_tasks(db_path)
        for task in recurring[:13]:  # Process all self-learning tasks per run
            LOG(f"[task-proc] Re-researching recurring #{task['id']}: {task['title'][:50]}")
            try:
                # Reset and re-research
                mark_recurring_done(db_path, task["id"])
                results = tm.research_task(task["id"])
                if results:
                    briefing = tm.generate_briefing(task["id"])
                    if briefing and token and chat_ids:
                        title = task["title"][:60]
                        for cid in chat_ids:
                            _telegram_send(
                                token, cid,
                                f"\U0001f504 <b>Daily Update: {title}</b>\n\n"
                                f"{briefing[:3500]}",
                            )
                        recurring_processed += 1
                        LOG(f"[task-proc] Recurring #{task['id']} updated and sent")
            except Exception as e:
                LOG(f"[task-proc] Recurring #{task['id']} error: {e}")
    except ImportError:
        LOG("[task-proc] Recurring tasks: import error")

    # Phase 6: Persist self-learning results to memory and update competencies
    LOG("[task-proc] Phase 6: Save self-learning to memory...")
    learning_saved = 0
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    try:
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        learnable = db.execute(
            """SELECT * FROM tasks
               WHERE title LIKE '[Self-Learn]%'
                 AND briefing IS NOT NULL
                 AND status = 'ready'
                 AND (learning_saved_at IS NULL OR learning_saved_at < ?)""",
            (today_str,),
        ).fetchall()

        for task in learnable:
            title = task["title"]
            briefing = task["briefing"]
            if not briefing or len(briefing) < 50:
                continue

            # Extract domain from title and map to canonical competency name
            raw_domain = title.replace("[Self-Learn] ", "").replace("[Self-Learn]", "").strip()
            _DOMAIN_MAP = {
                "React 19 + TypeScript basics": "React/TypeScript",
                "Kubernetes fundamentals": "Kubernetes",
                "GitHub Actions CI/CD pipelines": "CI/CD",
                "Flutter cross-platform mobile development": "Flutter/Mobile",
                "Vue 3.6 + Nuxt 4 advanced patterns": "Vue/Nuxt",
                "Redis 7 caching strategies and patterns": "Redis/Caching",
                "RabbitMQ advanced patterns": "Message Queues",
                "Testing best practices (PHPUnit 11, Go, E2E)": "Testing",
                "Web Security (OWASP Top 10, JWT, CORS, CSP)": "Security",
                "Payment integration (Stripe, RevenueCat, PCI)": "Payment Systems",
                "Git advanced workflows (rebase, bisect, hooks)": "Git/VCS",
            }
            domain = _DOMAIN_MAP.get(raw_domain, raw_domain)

            condensed = briefing[:2000]
            now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            session_id = f"vito_learn_{today_str}"

            # Save condensed learning to knowledge base
            try:
                db.execute(
                    """INSERT INTO knowledge
                       (session_id, type, content, context, project, tags,
                        status, confidence, source, created_at, last_confirmed, recall_count)
                       VALUES (?, 'fact', ?, ?, 'self-learning', ?, 'active', 0.7, 'vito-autolearn', ?, ?, 0)""",
                    (
                        session_id,
                        f"[Daily Learning] {domain} ({today_str}):\n{condensed}",
                        f"Auto-learned by Vito task processor from web research on {today_str}",
                        json.dumps([domain.lower().replace(" ", "-"), "self-learn", "vito", "daily"]),
                        now_str,
                        now_str,
                    ),
                )
            except Exception as e:
                LOG(f"[task-proc] Knowledge save error for {domain}: {e}")

            # Update competency (same schema as SelfModel: domain, level, confidence, based_on, trend, last_updated)
            try:
                existing = db.execute(
                    "SELECT level, confidence, based_on FROM competencies WHERE domain = ?",
                    (domain,),
                ).fetchone()

                if existing:
                    new_level = min(1.0, round(float(existing["level"]) + 0.01, 4))
                    new_conf = min(1.0, round(float(existing["confidence"]) + 0.005, 4))
                    new_based_on = int(existing["based_on"]) + 1
                    db.execute(
                        """UPDATE competencies
                           SET level = ?, confidence = ?, based_on = ?, last_updated = ?
                           WHERE domain = ?""",
                        (new_level, new_conf, new_based_on, now_str, domain),
                    )
                else:
                    db.execute(
                        """INSERT INTO competencies (domain, level, confidence, based_on, trend, last_updated)
                           VALUES (?, 0.3, 0.3, 1, 'improving', ?)""",
                        (domain, now_str),
                    )
            except Exception as e:
                LOG(f"[task-proc] Competency update error for {domain}: {e}")

            # Mark as saved to avoid re-processing
            db.execute(
                "UPDATE tasks SET learning_saved_at = ? WHERE id = ?",
                (today_str, task["id"]),
            )
            learning_saved += 1
            LOG(f"[task-proc] Saved learning for: {domain}")

        db.commit()
    except Exception as e:
        LOG(f"[task-proc] Phase 6 error: {e}")
    finally:
        db.close()

    LOG(
        f"Task processor complete: {tasks_processed} researched, "
        f"{briefings_created} briefings, {notifications_sent} notifications, "
        f"{len(overdue)} overdue, {recurring_processed} recurring, "
        f"{learning_saved} learning saved"
    )


class ReflectionScheduler:
    """Schedule periodic reflection runs."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def run(self) -> None:
        """Start the scheduler. Uses APScheduler if available, else simple loop."""
        if _HAS_APSCHEDULER:
            self._run_apscheduler()
        else:
            LOG("APScheduler not installed -- using simple loop")
            self._run_simple_loop()

    def _run_apscheduler(self) -> None:
        """Run with APScheduler. Always-on like a thinking brain."""
        scheduler = BackgroundScheduler()

        # Quick reflection every 30 minutes (dedup + decay)
        scheduler.add_job(
            run_reflection,
            IntervalTrigger(minutes=30),
            args=["quick", self.db_path],
            id="quick_reflection",
            name="Quick Reflection (every 30m)",
        )

        # Full reflection every 2 hours (digest + synthesize)
        scheduler.add_job(
            run_reflection,
            IntervalTrigger(hours=2),
            args=["full", self.db_path],
            id="full_reflection",
            name="Full Reflection (every 2h)",
        )

        # Weekly reflection on Sunday at midnight
        scheduler.add_job(
            run_reflection,
            CronTrigger(day_of_week="sun", hour=0, minute=0),
            args=["weekly", self.db_path],
            id="weekly_reflection",
            name="Weekly Reflection (Sunday midnight)",
        )

        # Graph enrichment every 4 hours
        scheduler.add_job(
            run_graph_enrichment,
            IntervalTrigger(hours=4),
            args=[self.db_path],
            id="graph_enrichment",
            name="Graph Enrichment (every 4h)",
        )

        # Dream mode: deep night processing at 3:00 AM daily
        scheduler.add_job(
            run_dream_mode,
            CronTrigger(hour=3, minute=0),
            args=[self.db_path],
            id="dream_mode",
            name="Dream Mode (daily 3:00 AM)",
        )

        # Weekly Telegram digest: Sunday at 10:00 AM
        scheduler.add_job(
            run_weekly_telegram_digest,
            CronTrigger(day_of_week="sun", hour=10, minute=0),
            args=[self.db_path],
            id="weekly_telegram_digest",
            name="Weekly Telegram Digest (Sunday 10:00 AM)",
        )

        # RSS feed polling every 2 hours
        scheduler.add_job(
            run_rss_poll,
            IntervalTrigger(hours=2),
            args=[self.db_path],
            id="rss_poll",
            name="RSS Feed Poll (every 2h)",
        )

        # Inactive project reminders daily at 9:00 AM
        scheduler.add_job(
            run_reminders,
            CronTrigger(hour=9, minute=0),
            args=[self.db_path],
            id="reminders",
            name="Inactive Project Reminders (daily 9:00 AM)",
        )

        # GitHub repo monitor every 6 hours
        scheduler.add_job(
            run_github_monitor,
            IntervalTrigger(hours=6),
            args=[self.db_path],
            id="github_monitor",
            name="GitHub Repo Monitor (every 6h)",
        )

        # Auto-retrain Ollama 3x daily (6:00, 14:00, 22:00)
        scheduler.add_job(
            run_auto_retrain,
            CronTrigger(hour="6,14,22", minute=0),
            args=[self.db_path],
            id="auto_retrain",
            name="Auto-Retrain Ollama (3x daily: 6:00, 14:00, 22:00)",
        )

        # Curiosity Engine: daily at 2:00 AM (before dream mode)
        scheduler.add_job(
            run_curiosity,
            CronTrigger(hour=2, minute=0),
            args=[self.db_path],
            id="curiosity_engine",
            name="Curiosity Engine (daily 2:00 AM)",
        )

        # Proactive Advisor: daily at 8:30 AM
        scheduler.add_job(
            run_advisor,
            CronTrigger(hour=8, minute=30),
            args=[self.db_path],
            id="proactive_advisor",
            name="Proactive Advisor (daily 8:30 AM)",
        )

        # Task Processor: every 10 minutes (research + briefings + reminders)
        scheduler.add_job(
            run_task_processor,
            IntervalTrigger(minutes=10),
            args=[self.db_path],
            id="task_processor",
            name="Task Processor (every 10m)",
        )

        # ── Level 1: Tech Radar (every 12h) + Dependency Monitor (daily 7:00 AM) ──
        scheduler.add_job(
            lambda: _run_brain_task("tools.tech_radar", "run_tech_radar", self.db_path),
            IntervalTrigger(hours=12),
            id="tech_radar",
            name="Tech Radar (every 12h)",
        )
        scheduler.add_job(
            lambda: _run_brain_task("tools.dependency_monitor", "run_dependency_monitor", self.db_path),
            CronTrigger(hour=7, minute=0),
            id="dep_monitor",
            name="Dependency Monitor (daily 7:00 AM)",
        )

        # ── Level 2: Git Observer (daily 11:00 PM) + Error Miner (daily 11:30 PM) ──
        scheduler.add_job(
            lambda: _run_brain_task("tools.git_observer", "run_git_observer", self.db_path),
            CronTrigger(hour=23, minute=0),
            id="git_observer",
            name="Git Observer (daily 11:00 PM)",
        )
        scheduler.add_job(
            lambda: _run_brain_task("tools.git_observer", "run_error_pattern_miner", self.db_path),
            CronTrigger(hour=23, minute=30),
            id="error_miner",
            name="Error Pattern Miner (daily 11:30 PM)",
        )

        # ── Level 3: Cross-Project Intelligence (Sunday 2:00 AM) ──
        scheduler.add_job(
            lambda: _run_brain_task("tools.cross_project", "run_cross_project_intelligence", self.db_path),
            CronTrigger(day_of_week="sun", hour=2, minute=0),
            id="cross_project",
            name="Cross-Project Intelligence (Sunday 2:00 AM)",
        )

        # ── Level 4: Smart Briefing (daily 8:00 AM) + Pre-Research (every 4h) ──
        scheduler.add_job(
            lambda: _run_brain_task("tools.predictive", "run_smart_briefing", self.db_path),
            CronTrigger(hour=8, minute=0),
            id="smart_briefing",
            name="Smart Morning Briefing (daily 8:00 AM)",
        )
        scheduler.add_job(
            lambda: _run_brain_task("tools.predictive", "run_pre_research", self.db_path),
            IntervalTrigger(hours=4),
            id="pre_research",
            name="Pre-Research Engine (every 4h)",
        )

        # ── Level 5: Ideas (Fri 6PM) + Innovation (1st&15th) + Challenger (Mon 9AM) ──
        scheduler.add_job(
            lambda: _run_brain_task("tools.idea_engine", "run_idea_generator", self.db_path),
            CronTrigger(day_of_week="fri", hour=18, minute=0),
            id="idea_generator",
            name="Idea Generator (Friday 6:00 PM)",
        )
        scheduler.add_job(
            lambda: _run_brain_task("tools.idea_engine", "run_innovation_digest", self.db_path),
            CronTrigger(day="1,15", hour=10, minute=0),
            id="innovation_digest",
            name="Innovation Digest (1st & 15th 10:00 AM)",
        )
        scheduler.add_job(
            lambda: _run_brain_task("tools.idea_engine", "run_blind_spot_challenger", self.db_path),
            CronTrigger(day_of_week="mon", hour=9, minute=0),
            id="blind_spot_challenger",
            name="Blind Spot Challenger (Monday 9:00 AM)",
        )

        # ── Level 6: Brain Autonomy (every 6h) — self-tasking & self-learning ──
        scheduler.add_job(
            lambda: _run_brain_task("tools.brain_autonomy", "run_brain_autonomy", self.db_path),
            IntervalTrigger(hours=6),
            id="brain_autonomy",
            name="Brain Autonomy (every 6h)",
        )

        scheduler.start()
        LOG(f"APScheduler started with {len(scheduler.get_jobs())} jobs:")
        for job in scheduler.get_jobs():
            LOG(f"  - {job.name} (next: {job.next_run_time})")

        # Run full reflection immediately on startup
        LOG("Running initial full reflection on startup...")
        run_reflection("full", self.db_path)
        run_graph_enrichment(self.db_path)

        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            scheduler.shutdown()
            LOG("Scheduler stopped")

    def _run_simple_loop(self) -> None:
        """Fallback: simple loop with sleep. Always-on like a thinking brain."""
        QUICK_INTERVAL = 30 * 60   # 30 minutes
        FULL_INTERVAL = 2 * 3600   # 2 hours
        GRAPH_INTERVAL = 4 * 3600  # 4 hours
        RSS_INTERVAL = 2 * 3600    # 2 hours
        GITHUB_INTERVAL = 6 * 3600 # 6 hours
        TASK_INTERVAL = 10 * 60  # 10 minutes
        CHECK_INTERVAL = 60        # check every minute

        last_quick: float = 0
        last_full: float = 0
        last_graph: float = 0
        last_rss: float = 0
        last_github: float = 0
        last_task: float = 0
        last_tech_radar: float = 0
        last_pre_research: float = 0
        last_weekly_day = -1
        last_dream_day = -1
        last_telegram_digest_day = -1
        last_reminders_day = -1
        last_retrain_day = -1
        last_curiosity_day = -1
        last_advisor_day = -1
        last_dep_monitor_day = -1
        last_git_observer_day = -1
        last_error_miner_day = -1
        last_cross_project_day = -1
        last_briefing_day = -1
        last_ideas_day = -1
        last_innovation_day = -1
        last_challenger_day = -1

        # Run full reflection immediately on start
        run_reflection("full", self.db_path)
        run_graph_enrichment(self.db_path)
        last_full = time.time()
        last_graph = time.time()
        last_quick = time.time()

        try:
            while True:
                now = time.time()
                current_day = datetime.now().weekday()
                current_hour = datetime.now().hour
                today_ordinal = datetime.now().toordinal()

                # Quick reflection every 30 minutes
                if now - last_quick >= QUICK_INTERVAL:
                    run_reflection("quick", self.db_path)
                    last_quick = now

                # Full reflection every 2 hours
                if now - last_full >= FULL_INTERVAL:
                    run_reflection("full", self.db_path)
                    last_full = now

                # Graph enrichment every 4 hours
                if now - last_graph >= GRAPH_INTERVAL:
                    run_graph_enrichment(self.db_path)
                    last_graph = now

                # Weekly reflection: Sunday at midnight
                if current_day == 6 and current_hour == 0 and last_weekly_day != current_day:
                    run_reflection("weekly", self.db_path)
                    last_weekly_day = current_day

                # Dream mode: daily at 3:00 AM
                if current_hour == 3 and last_dream_day != today_ordinal:
                    run_dream_mode(self.db_path)
                    last_dream_day = today_ordinal

                # Weekly Telegram digest: Sunday at 10:00 AM
                if current_day == 6 and current_hour == 10 and last_telegram_digest_day != today_ordinal:
                    run_weekly_telegram_digest(self.db_path)
                    last_telegram_digest_day = today_ordinal

                # RSS feed polling every 2 hours
                if now - last_rss >= RSS_INTERVAL:
                    run_rss_poll(self.db_path)
                    last_rss = now

                # Inactive project reminders: daily at 9:00 AM
                if current_hour == 9 and last_reminders_day != today_ordinal:
                    run_reminders(self.db_path)
                    last_reminders_day = today_ordinal

                # GitHub repo monitor every 6 hours
                if now - last_github >= GITHUB_INTERVAL:
                    run_github_monitor(self.db_path)
                    last_github = now

                # Auto-retrain Ollama: 3x daily at 6:00, 14:00, 22:00
                if current_hour in (6, 14, 22) and last_retrain_day != f"{today_ordinal}_{current_hour}":
                    run_auto_retrain(self.db_path)
                    last_retrain_day = f"{today_ordinal}_{current_hour}"

                # Curiosity Engine: daily at 2:00 AM
                if current_hour == 2 and last_curiosity_day != today_ordinal:
                    run_curiosity(self.db_path)
                    last_curiosity_day = today_ordinal

                # Proactive Advisor: daily at 8:30 AM (check at 8)
                if current_hour == 8 and datetime.now().minute >= 30 and last_advisor_day != today_ordinal:
                    run_advisor(self.db_path)
                    last_advisor_day = today_ordinal

                # Task Processor: every 3 hours
                if now - last_task >= TASK_INTERVAL:
                    run_task_processor(self.db_path)
                    last_task = now

                # ── Level 1: Tech Radar every 12h ──
                if now - last_tech_radar >= 12 * 3600:
                    _run_brain_task("tools.tech_radar", "run_tech_radar", self.db_path)
                    last_tech_radar = now

                # ── Level 1: Dependency Monitor daily 7:00 AM ──
                if current_hour == 7 and last_dep_monitor_day != today_ordinal:
                    _run_brain_task("tools.dependency_monitor", "run_dependency_monitor", self.db_path)
                    last_dep_monitor_day = today_ordinal

                # ── Level 2: Git Observer daily 11:00 PM ──
                if current_hour == 23 and datetime.now().minute < 30 and last_git_observer_day != today_ordinal:
                    _run_brain_task("tools.git_observer", "run_git_observer", self.db_path)
                    last_git_observer_day = today_ordinal

                # ── Level 2: Error Pattern Miner daily 11:30 PM ──
                if current_hour == 23 and datetime.now().minute >= 30 and last_error_miner_day != today_ordinal:
                    _run_brain_task("tools.git_observer", "run_error_pattern_miner", self.db_path)
                    last_error_miner_day = today_ordinal

                # ── Level 3: Cross-Project Intelligence Sunday 2:00 AM ──
                if current_day == 6 and current_hour == 2 and last_cross_project_day != today_ordinal:
                    _run_brain_task("tools.cross_project", "run_cross_project_intelligence", self.db_path)
                    last_cross_project_day = today_ordinal

                # ── Level 4: Smart Briefing daily 8:00 AM ──
                if current_hour == 8 and last_briefing_day != today_ordinal:
                    _run_brain_task("tools.predictive", "run_smart_briefing", self.db_path)
                    last_briefing_day = today_ordinal

                # ── Level 4: Pre-Research every 4h ──
                if now - last_pre_research >= 4 * 3600:
                    _run_brain_task("tools.predictive", "run_pre_research", self.db_path)
                    last_pre_research = now

                # ── Level 5: Idea Generator Friday 6:00 PM ──
                if current_day == 4 and current_hour == 18 and last_ideas_day != today_ordinal:
                    _run_brain_task("tools.idea_engine", "run_idea_generator", self.db_path)
                    last_ideas_day = today_ordinal

                # ── Level 5: Innovation Digest 1st & 15th at 10:00 AM ──
                if datetime.now().day in (1, 15) and current_hour == 10 and last_innovation_day != today_ordinal:
                    _run_brain_task("tools.idea_engine", "run_innovation_digest", self.db_path)
                    last_innovation_day = today_ordinal

                # ── Level 5: Blind Spot Challenger Monday 9:00 AM ──
                if current_day == 0 and current_hour == 9 and last_challenger_day != today_ordinal:
                    _run_brain_task("tools.idea_engine", "run_blind_spot_challenger", self.db_path)
                    last_challenger_day = today_ordinal

                time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            LOG("Scheduler stopped")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Reflection scheduler")
    parser.add_argument("--db", default=str(MEMORY_DIR / "memory.db"))
    parser.add_argument("--run-now", choices=[
        "quick", "full", "weekly", "dream", "telegram-digest",
        "rss", "reminders", "github", "retrain", "curiosity", "advisor", "tasks",
        # Level 1-5 Autonomous Brain
        "tech-radar", "dep-monitor", "git-observer", "error-miner",
        "cross-project", "briefing", "pre-research",
        "ideas", "innovation", "challenge",
    ], help="Run once immediately and exit")
    args = parser.parse_args()

    if args.run_now == "dream":
        run_dream_mode(args.db)
    elif args.run_now == "telegram-digest":
        run_weekly_telegram_digest(args.db)
    elif args.run_now == "rss":
        run_rss_poll(args.db)
    elif args.run_now == "reminders":
        run_reminders(args.db)
    elif args.run_now == "github":
        run_github_monitor(args.db)
    elif args.run_now == "retrain":
        run_auto_retrain(args.db)
    elif args.run_now == "curiosity":
        run_curiosity(args.db)
    elif args.run_now == "advisor":
        run_advisor(args.db)
    elif args.run_now == "tasks":
        run_task_processor(args.db)
    elif args.run_now == "tech-radar":
        _run_brain_task("tools.tech_radar", "run_tech_radar", args.db)
    elif args.run_now == "dep-monitor":
        _run_brain_task("tools.dependency_monitor", "run_dependency_monitor", args.db)
    elif args.run_now == "git-observer":
        _run_brain_task("tools.git_observer", "run_git_observer", args.db)
    elif args.run_now == "error-miner":
        _run_brain_task("tools.git_observer", "run_error_pattern_miner", args.db)
    elif args.run_now == "cross-project":
        _run_brain_task("tools.cross_project", "run_cross_project_intelligence", args.db)
    elif args.run_now == "briefing":
        _run_brain_task("tools.predictive", "run_smart_briefing", args.db)
    elif args.run_now == "pre-research":
        _run_brain_task("tools.predictive", "run_pre_research", args.db)
    elif args.run_now == "ideas":
        _run_brain_task("tools.idea_engine", "run_idea_generator", args.db)
    elif args.run_now == "innovation":
        _run_brain_task("tools.idea_engine", "run_innovation_digest", args.db)
    elif args.run_now == "challenge":
        _run_brain_task("tools.idea_engine", "run_blind_spot_challenger", args.db)
    elif args.run_now:
        run_reflection(args.run_now, args.db)
    else:
        scheduler = ReflectionScheduler(args.db)
        scheduler.run()
