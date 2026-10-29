#!/usr/bin/env python3
"""Editorial SEO quality report for the generated AutoCalc España site.

This is deliberately diagnostic: short or similar pages are reported for review,
not automatically removed from the sitemap or marked noindex. Those decisions
require editorial judgement and Search Console evidence.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SKIP_TAGS = {"script", "style", "noscript", "svg", "nav", "footer", "header"}
WORD_RE = re.compile(r"[\wáéíóúüñ]+", re.IGNORECASE)


class EditorialParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.in_title = False
        self.title_parts: list[str] = []
        self.description = ""
        self._description_seen = False
        self.text_parts: list[str] = []
        self.h1_count = 0
        self.h2_count = 0
        self.in_h1 = False
        self.in_h2 = False
        self.h1_parts: list[str] = []
        self.h2_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs = {k.lower(): (v or "") for k, v in attrs}
        if tag in SKIP_TAGS:
            self.skip_depth += 1
        if self.skip_depth:
            return
        if tag == "title":
            self.in_title = True
        if tag == "meta" and attrs.get("name", "").lower() == "description":
            self.description = attrs.get("content", "").strip()
            self._description_seen = True
        if tag == "h1":
            self.h1_count += 1
            self.in_h1 = True
        if tag == "h2":
            self.h2_count += 1
            self.in_h2 = True

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
        if self.skip_depth:
            return
        if tag == "title":
            self.in_title = False
        if tag == "h1":
            self.in_h1 = False
        if tag == "h2":
            self.in_h2 = False

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        text = " ".join(data.split())
        if not text:
            return
        self.text_parts.append(text)
        if self.in_title:
            self.title_parts.append(text)
        if self.in_h1:
            self.h1_parts.append(text)
        if self.in_h2:
            self.h2_parts.append(text)

    @property
    def title(self) -> str:
        return " ".join(self.title_parts).strip()

    @property
    def h1(self) -> str:
        return " ".join(self.h1_parts).strip()

    @property
    def text(self) -> str:
        return " ".join(self.text_parts).strip()


def normalized(value: str) -> str:
    return " ".join(WORD_RE.findall(value.lower()))


def main() -> int:
    if not PUBLIC.is_dir():
        print("No existe public/. Ejecuta primero python src/build.py y los generadores de contenido.")
        return 2

    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    base = ("https://" + cfg["custom_domain"].strip().lower()) if cfg.get("use_custom_domain") else str(cfg.get("github_pages_url") or cfg.get("domain", "")).rstrip("/")
    pages = sorted(p for p in PUBLIC.rglob("*.html") if p.name != "404.html")
    if not pages:
        print("No se encontraron páginas HTML generadas.")
        return 2

    title_pages: dict[str, list[str]] = defaultdict(list)
    h1_pages: dict[str, list[str]] = defaultdict(list)
    content_pages: dict[str, list[str]] = defaultdict(list)
    low_content: list[tuple[str, int, str]] = []
    missing_h1: list[str] = []
    weak_meta: list[str] = []
    rows = []

    for page in pages:
        rel = page.relative_to(PUBLIC).as_posix()
        parser = EditorialParser()
        parser.feed(page.read_text(encoding="utf-8"))
        title_key = normalized(parser.title)
        h1_key = normalized(parser.h1)
        body_key = normalized(parser.text)
        words = WORD_RE.findall(body_key)
        title_pages[title_key].append(rel) if title_key else None
        h1_pages[h1_key].append(rel) if h1_key else None
        content_pages[body_key].append(rel) if body_key else None

        if not parser.h1:
            missing_h1.append(rel)
        if len(words) < 180:
            low_content.append((rel, len(words), parser.title))
        if len(parser.description) < 70:
            weak_meta.append(rel)

        rows.append({
            "path": rel,
            "url": base + ("/" if rel == "index.html" else "/" + rel),
            "title": parser.title,
            "description_length": len(parser.description),
            "h1": parser.h1,
            "h2_count": parser.h2_count,
            "visible_word_count_approx": len(words),
        })

    duplicate_titles = {k: v for k, v in title_pages.items() if k and len(v) > 1}
    duplicate_h1 = {k: v for k, v in h1_pages.items() if k and len(v) > 1}
    duplicate_content = {k: v for k, v in content_pages.items() if k and len(v) > 1}

    report = {
        "generated_by": "scripts/audit_seo_content_quality.py",
        "page_count": len(rows),
        "thresholds": {
            "short_page_words": 180,
            "short_description_characters": 70,
            "note": "Diagnostic thresholds only; not Google ranking requirements.",
        },
        "summary": {
            "short_pages": len(low_content),
            "pages_without_h1": len(missing_h1),
            "short_or_missing_descriptions": len(weak_meta),
            "duplicate_titles_groups": len(duplicate_titles),
            "duplicate_h1_groups": len(duplicate_h1),
            "exact_duplicate_body_groups": len(duplicate_content),
        },
        "short_pages": [{"path": p, "words": n, "title": t} for p, n, t in low_content],
        "pages_without_h1": missing_h1,
        "short_or_missing_descriptions": weak_meta,
        "duplicate_titles": [{"title": k, "pages": v} for k, v in duplicate_titles.items()],
        "duplicate_h1": [{"h1": k, "pages": v} for k, v in duplicate_h1.items()],
        "exact_duplicate_body": [{"word_count": len(k.split()), "pages": v} for k, v in duplicate_content.items()],
        "pages": rows,
    }
    report_path = ROOT / "build" / "seo-content-quality-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Informe editorial SEO: {len(rows)} páginas HTML.")
    print(f"- Páginas con menos de 180 palabras visibles aprox.: {len(low_content)}")
    print(f"- Páginas sin H1: {len(missing_h1)}")
    print(f"- Descripciones ausentes/cortas (<70 caracteres): {len(weak_meta)}")
    print(f"- Grupos con title repetido: {len(duplicate_titles)}")
    print(f"- Grupos con H1 repetido: {len(duplicate_h1)}")
    print(f"- Grupos con cuerpo textual exactamente repetido: {len(duplicate_content)}")
    print(f"Informe completo: {report_path.relative_to(ROOT).as_posix()}")
    print("AVISO: estos indicadores priorizan revisiones humanas; no justifican por sí solos noindex ni eliminar URLs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
