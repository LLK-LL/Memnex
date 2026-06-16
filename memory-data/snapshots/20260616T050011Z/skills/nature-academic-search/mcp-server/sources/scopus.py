"""Scopus data source via pybliometrics."""

from __future__ import annotations

from typing import Any

from pybliometrics.scopus import (
    AbstractRetrieval,
    AffiliationRetrieval,
# REDACTED: sensitive-looking memory line
    CitationOverview,
    PlumXMetrics,
    SerialTitleISSN,
)
from pybliometrics.utils import URLS, get_content

from utils.errors import DataSourceError

from .elsevier_common import (
    ensure_pybliometrics_config,
    record_to_dict,
    safe_attr,
    year_from_date,
)


SOURCE_NAME = "scopus"


class ScopusSource:
    """pybliometrics-backed Scopus operations."""

    SOURCE_NAME = SOURCE_NAME

    def search(
        self,
        query: str,
        rows: int = 5,
        view: str | None = None,
        refresh: bool | int = False,
        subscriber: bool = True,
    ) -> dict[str, Any]:
        """Search Scopus documents and return only the requested first page."""
        if not query or not query.strip():
            raise DataSourceError(SOURCE_NAME, "Empty search query")

        rows = max(1, min(rows, 50))

        def run() -> dict[str, Any]:
            effective_view = view or ("COMPLETE" if subscriber else "STANDARD")
            data = self._search_api(
                "ScopusSearch",
                {"query": query.strip(), "count": rows, "start": 0, "view": effective_view},
            )
            records = _search_entries(data)
            return {
                "total": _total_results(data),
                "query": query,
                "source": SOURCE_NAME,
                "results": [self._normalize_search_entry(r) for r in records[:rows]],
            }

        return self._run("Scopus search", run)

    def get_abstract(
        self,
        identifier: str,
        id_type: str | None = None,
        view: str = "META_ABS",
        refresh: bool | int = False,
    ) -> dict[str, Any]:
        """Retrieve Scopus abstract metadata by EID, Scopus ID, DOI, PMID, or PII."""
        if not identifier or not identifier.strip():
            raise DataSourceError(SOURCE_NAME, "Empty identifier")

        def run() -> dict[str, Any]:
            paper = AbstractRetrieval(
                identifier.strip(),
                id_type=id_type,
                view=view,
                refresh=refresh,
            )
            return self._normalize_abstract(paper)

        return self._run("Scopus abstract retrieval", run)

    def get_citation_overview(
        self,
        identifiers: list[str],
        id_type: str = "scopus_id",
        date: str | None = None,
        citation: str | None = None,
        refresh: bool | int = False,
    ) -> dict[str, Any]:
        """Retrieve Scopus citation overview for one or more documents."""
        clean = [i.strip() for i in identifiers if i and i.strip()]
        if not clean:
            raise DataSourceError(SOURCE_NAME, "Empty identifier list")

        def run() -> dict[str, Any]:
            overview = CitationOverview(
                clean,
                date=date,
                id_type=id_type,
                citation=citation,
                refresh=refresh,
            )
            return self._normalize_citation_overview(overview)

        return self._run("Scopus citation overview", run)

# REDACTED: sensitive-looking memory line
        self,
        query: str,
        rows: int = 5,
        refresh: bool | int = False,
    ) -> dict[str, Any]:
# REDACTED: sensitive-looking memory line
        if not query or not query.strip():
# REDACTED: sensitive-looking memory line
        rows = max(1, min(rows, 50))

        def run() -> dict[str, Any]:
            data = self._search_api(
# REDACTED: sensitive-looking memory line
                {"query": query.strip(), "count": rows, "start": 0},
            )
            records = _search_entries(data)
            return {
                "total": _total_results(data),
                "query": query,
                "source": SOURCE_NAME,
# REDACTED: sensitive-looking memory line
            }

# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line
        self,
# REDACTED: sensitive-looking memory line
        view: str = "ENHANCED",
        refresh: bool | int = False,
    ) -> dict[str, Any]:
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

        def run() -> dict[str, Any]:
# REDACTED: sensitive-looking memory line
            return {
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
                "source": SOURCE_NAME,
            }

# REDACTED: sensitive-looking memory line

    def search_affiliations(
        self,
        query: str,
        rows: int = 5,
        refresh: bool | int = False,
    ) -> dict[str, Any]:
        """Search Scopus affiliations and return only the requested first page."""
        if not query or not query.strip():
            raise DataSourceError(SOURCE_NAME, "Empty affiliation search query")
        rows = max(1, min(rows, 50))

        def run() -> dict[str, Any]:
            data = self._search_api(
                "AffiliationSearch",
                {"query": query.strip(), "count": rows, "start": 0},
            )
            records = _search_entries(data)
            return {
                "total": _total_results(data),
                "query": query,
                "source": SOURCE_NAME,
                "results": [self._normalize_affiliation_entry(r) for r in records[:rows]],
            }

        return self._run("Scopus affiliation search", run)

    def get_affiliation(
        self,
        affiliation_id: str,
        view: str = "STANDARD",
        refresh: bool | int = False,
    ) -> dict[str, Any]:
        """Retrieve a Scopus affiliation profile."""
        if not affiliation_id or not affiliation_id.strip():
            raise DataSourceError(SOURCE_NAME, "Empty affiliation ID")

        def run() -> dict[str, Any]:
            affiliation = AffiliationRetrieval(
                affiliation_id.strip(),
                view=view,
                refresh=refresh,
            )
            return {
                "affiliation_id": safe_attr(affiliation, "identifier"),
                "eid": safe_attr(affiliation, "eid"),
                "name": safe_attr(affiliation, "affiliation_name"),
                "sort_name": safe_attr(affiliation, "sort_name"),
                "documents": safe_attr(affiliation, "document_count"),
# REDACTED: sensitive-looking memory line
                "address": safe_attr(affiliation, "address"),
                "city": safe_attr(affiliation, "city"),
                "state": safe_attr(affiliation, "state"),
                "country": safe_attr(affiliation, "country"),
                "postal_code": safe_attr(affiliation, "postal_code"),
                "org_domain": safe_attr(affiliation, "org_domain"),
                "org_url": safe_attr(affiliation, "org_URL"),
                "variants": record_to_dict(safe_attr(affiliation, "name_variants")),
                "scopus_affiliation_link": safe_attr(affiliation, "scopus_affiliation_link"),
                "url": safe_attr(affiliation, "url"),
                "source": SOURCE_NAME,
            }

        return self._run("Scopus affiliation retrieval", run)

    def search_serial_titles(
        self,
        query: dict[str, str],
        rows: int = 5,
        view: str = "ENHANCED",
        refresh: bool | int = False,
    ) -> dict[str, Any]:
        """Search Scopus serial titles and return only the requested first page."""
        clean = {k: v for k, v in query.items() if v}
        if not clean:
            raise DataSourceError(SOURCE_NAME, "Empty serial title query")
        rows = max(1, min(rows, 50))

        def run() -> dict[str, Any]:
            data = self._search_api(
                "SerialTitleSearch",
                {**clean, "count": rows, "start": 0, "view": view},
            )
            records = data.get("serial-metadata-response", {}).get("entry", [])
            records = _as_list(records)
            return {
                "total": len(records),
                "query": clean,
                "source": SOURCE_NAME,
                "results": [record_to_dict(r) for r in records[:rows]],
            }

        return self._run("Scopus serial title search", run)

    def get_serial_title(
        self,
        issn: str,
        view: str = "ENHANCED",
        years: str | None = None,
        refresh: bool | int = False,
    ) -> dict[str, Any]:
        """Retrieve a Scopus serial title by ISSN."""
        if not issn or not issn.strip():
            raise DataSourceError(SOURCE_NAME, "Empty ISSN")

        def run() -> dict[str, Any]:
            title = SerialTitleISSN(
                issn.strip(),
                view=view,
                years=years,
                refresh=refresh,
            )
            return {
                "title": safe_attr(title, "title"),
                "source_id": safe_attr(title, "source_id"),
                "issn": safe_attr(title, "issn"),
                "eissn": safe_attr(title, "eissn"),
                "publisher": safe_attr(title, "publisher"),
                "aggregation_type": safe_attr(title, "aggregation_type"),
                "openaccess": safe_attr(title, "openaccess"),
                "subject_areas": record_to_dict(safe_attr(title, "subject_area")),
                "citescore_year_info": record_to_dict(
                    safe_attr(title, "citescoreyearinfolist")
                ),
                "scopus_source_link": safe_attr(title, "scopus_source_link"),
                "source": SOURCE_NAME,
            }

        return self._run("Scopus serial title retrieval", run)

    def get_plumx_metrics(
        self,
        identifier: str,
        id_type: str,
        refresh: bool | int = False,
    ) -> dict[str, Any]:
        """Retrieve PlumX metrics for a document."""
        if not identifier or not identifier.strip():
            raise DataSourceError(SOURCE_NAME, "Empty PlumX identifier")
        if not id_type or not id_type.strip():
            raise DataSourceError(SOURCE_NAME, "Empty PlumX id_type")

        def run() -> dict[str, Any]:
            metrics = PlumXMetrics(
                identifier.strip(),
                id_type.strip(),
                refresh=refresh,
            )
            return {
                "identifier": identifier,
                "id_type": id_type,
                "category_totals": record_to_dict(safe_attr(metrics, "category_totals")),
                "capture": record_to_dict(safe_attr(metrics, "capture")),
                "citation": record_to_dict(safe_attr(metrics, "citation")),
                "mention": record_to_dict(safe_attr(metrics, "mention")),
                "social_media": record_to_dict(safe_attr(metrics, "social_media")),
                "usage": record_to_dict(safe_attr(metrics, "usage")),
                "source": SOURCE_NAME,
            }

        return self._run("Scopus PlumX metrics", run)

    def _run(self, operation: str, callback):
        ensure_pybliometrics_config(SOURCE_NAME)
        try:
            return callback()
        except DataSourceError:
            raise
        except Exception as exc:
            raise DataSourceError(
                SOURCE_NAME,
                f"{operation} failed: {exc}",
                original_error=exc,
            ) from exc

    @staticmethod
    def _search_api(api: str, params: dict[str, Any]) -> dict[str, Any]:
        response = get_content(URLS[api], api, params=params)
        return response.json()

    @staticmethod
    def _normalize_search_entry(data: dict[str, Any]) -> dict[str, Any]:
        return {
            "title": data.get("dc:title"),
# REDACTED: sensitive-looking memory line
            "year": year_from_date(data.get("prism:coverDate")),
            "doi": data.get("prism:doi"),
            "eid": data.get("eid"),
            "pii": data.get("pii"),
            "pmid": data.get("pubmed-id"),
            "journal": data.get("prism:publicationName"),
            "volume": data.get("prism:volume"),
            "issue": data.get("prism:issueIdentifier"),
            "pages": data.get("prism:pageRange"),
            "subtype": data.get("subtype"),
            "subtype_description": data.get("subtypeDescription"),
            "citation_count": _int_or_none(data.get("citedby-count")),
            "openaccess": data.get("openaccess"),
            "source": SOURCE_NAME,
        }

    @staticmethod
# REDACTED: sensitive-looking memory line
        preferred = data.get("preferred-name", {})
        affiliation = data.get("affiliation-current", {})
        areas = _as_list(data.get("subject-area"))
        return {
            "eid": data.get("eid"),
            "orcid": data.get("orcid"),
            "surname": preferred.get("surname"),
            "initials": preferred.get("initials"),
            "givenname": preferred.get("given-name"),
            "affiliation": affiliation.get("affiliation-name"),
            "documents": _int_or_none(data.get("document-count")),
            "affiliation_id": affiliation.get("affiliation-id"),
            "city": affiliation.get("affiliation-city"),
            "country": affiliation.get("affiliation-country"),
            "areas": [
                {
                    "abbreviation": area.get("@abbrev"),
                    "frequency": _int_or_none(area.get("@frequency")),
                    "name": area.get("$"),
                }
                for area in areas
            ],
            "source": SOURCE_NAME,
        }

    @staticmethod
    def _normalize_affiliation_entry(data: dict[str, Any]) -> dict[str, Any]:
        variants = [
            item.get("$")
            for item in _as_list(data.get("name-variant"))
            if item.get("$") and item.get("$") != data.get("affiliation-name")
        ]
        return {
            "eid": data.get("eid"),
            "name": data.get("affiliation-name"),
            "variant": ";".join(variants),
            "documents": _int_or_none(data.get("document-count")),
            "city": data.get("city"),
            "country": data.get("country"),
            "source": SOURCE_NAME,
        }

    @staticmethod
    def _normalize_abstract(paper: Any) -> dict[str, Any]:
        return {
            "title": safe_attr(paper, "title"),
# REDACTED: sensitive-looking memory line
            "year": year_from_date(safe_attr(paper, "coverDate")),
            "doi": safe_attr(paper, "doi"),
            "eid": safe_attr(paper, "eid"),
            "scopus_id": safe_attr(paper, "identifier"),
            "pii": safe_attr(paper, "pii"),
            "abstract": safe_attr(paper, "abstract") or safe_attr(paper, "description"),
            "journal": safe_attr(paper, "publicationName"),
            "volume": safe_attr(paper, "volume"),
            "issue": safe_attr(paper, "issueIdentifier"),
            "pages": safe_attr(paper, "pageRange"),
            "publisher": safe_attr(paper, "publisher"),
            "citation_count": safe_attr(paper, "citedby_count"),
            "reference_count": safe_attr(paper, "refcount"),
            "affiliations": record_to_dict(safe_attr(paper, "affiliation")),
# REDACTED: sensitive-looking memory line
            "subject_areas": record_to_dict(safe_attr(paper, "subject_areas")),
            "url": safe_attr(paper, "url"),
            "source": SOURCE_NAME,
        }

    @staticmethod
    def _normalize_citation_overview(overview: Any) -> dict[str, Any]:
        titles = safe_attr(overview, "title") or []
        documents = []
        parallel_fields = {
            "scopus_id": safe_attr(overview, "scopus_id"),
            "doi": safe_attr(overview, "doi"),
            "title": titles,
            "publication_name": safe_attr(overview, "publicationName"),
            "row_total": safe_attr(overview, "rowTotal"),
            "range_count": safe_attr(overview, "rangeCount"),
            "citation_type": safe_attr(overview, "citationType_long"),
            "yearly_citations": safe_attr(overview, "cc"),
        }
        for idx in range(len(titles)):
            doc = {}
            for key, values in parallel_fields.items():
                if values is not None and idx < len(values):
                    doc[key] = record_to_dict(values[idx])
            documents.append(doc)

        return {
            "grand_total": safe_attr(overview, "grandTotal"),
            "h_index": safe_attr(overview, "h_index"),
            "column_total": safe_attr(overview, "columnTotal"),
            "previous_column_total": safe_attr(overview, "prevColumnTotal"),
            "range_column_total": safe_attr(overview, "rangeColumnTotal"),
            "later_column_total": safe_attr(overview, "laterColumnTotal"),
            "documents": documents,
            "source": SOURCE_NAME,
        }


def _search_entries(data: dict[str, Any]) -> list[dict[str, Any]]:
    entries = data.get("search-results", {}).get("entry", [])
    return _as_list(entries)


def _total_results(data: dict[str, Any]) -> int:
    total = data.get("search-results", {}).get("opensearch:totalResults", 0)
    return _int_or_none(total) or 0


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
        if name:
# REDACTED: sensitive-looking memory line
    creator = data.get("dc:creator")
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
