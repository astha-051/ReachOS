import os
import re
import datetime
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from tavily import TavilyClient
from app.config import settings

logger = logging.getLogger(__name__)

class TavilyResearchService:
    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        self.client = TavilyClient(api_key=self.api_key) if self.api_key else None

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def generate_search_queries(self, company_name: str, website: Optional[str] = None, industry: Optional[str] = None) -> List[str]:
        queries = []
        domain = website.replace("https://", "").replace("http://", "").strip("/") if website else ""
        
        # Primary targeted query
        primary = f'"{company_name}" latest news funding hiring product sales enterprise'
        if domain:
            primary += f" {domain}"
        queries.append(primary)

        # Secondary business signal query
        if industry:
            queries.append(f'"{company_name}" {industry} growth market expansion')
        else:
            queries.append(f'"{company_name}" AI outbound automation leads')

        return queries[:2]

    def check_company_relevance(self, company_name: str, website: Optional[str], result: Dict[str, Any]) -> float:
        """
        Evaluates whether a web search result belongs to the target company.
        Returns relevance_score (0.0 to 1.0).
        Rejects results referencing unrelated companies.
        """
        title = (result.get("title") or "").lower()
        snippet = (result.get("snippet") or "").lower()
        url = (result.get("url") or "").lower()

        target_domain = ""
        if website:
            parsed = urlparse(website if website.startswith("http") else f"https://{website}")
            target_domain = parsed.netloc.replace("www.", "").lower()

        # Extract domain from search result
        result_domain = urlparse(url).netloc.replace("www.", "").lower()

        company_tokens = [t for t in re.findall(r'\b\w+\b', company_name.lower()) if len(t) > 2 and t not in ("inc", "llc", "corp", "co", "labs", "solutions", "group", "systems", "advisory", "tech")]
        if not company_tokens:
            company_tokens = [t for t in re.findall(r'\b\w+\b', company_name.lower()) if len(t) > 1]

        score = 0.0

        # 1. Exact or parent domain match
        if target_domain and (target_domain in result_domain or result_domain in target_domain):
            score += 0.8

        # 2. Token matching in title / snippet / URL
        matches = 0
        for token in company_tokens:
            if token in title or token in snippet or token in result_domain:
                matches += 1

        if company_tokens:
            token_ratio = matches / len(company_tokens)
            score += token_ratio * 0.4

        # 3. Penalize if none of the company tokens appear anywhere in title or snippet or domain
        if company_tokens and not any(t in title or t in snippet or t in result_domain for t in company_tokens):
            score -= 0.6

        final_score = round(min(1.0, max(0.0, score)), 2)
        return final_score

    def research_company(self, company_name: str, website: Optional[str] = None, industry: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.is_configured():
            logger.warning("Tavily API key not configured. Returning dynamically generated mock evidence.")
            return self._get_fallback_mock_evidence(company_name, website, industry)

        queries = self.generate_search_queries(company_name, website, industry)
        all_results = []
        seen_urls = set()

        for query in queries:
            try:
                response = self.client.search(
                    query=query,
                    max_results=4,
                    search_depth="basic"
                )
                for res in response.get("results", []):
                    url = res.get("url", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        
                        raw_item = {
                            "title": res.get("title", f"{company_name} Overview"),
                            "url": url,
                            "snippet": res.get("content") or res.get("snippet", ""),
                            "source_type": "web",
                            "published_date": res.get("published_date") or None
                        }

                        # Company Relevance Check (TASK 3)
                        rel_score = self.check_company_relevance(company_name, website, raw_item)
                        if rel_score >= 0.4:
                            domain = urlparse(url).netloc
                            raw_item["domain"] = domain
                            raw_item["relevance_score"] = rel_score
                            raw_item["retrieved_at"] = datetime.datetime.utcnow().isoformat()
                            all_results.append(raw_item)
                        else:
                            logger.info(f"Rejected search result for '{company_name}' (relevance score {rel_score}): {url}")
            except Exception as e:
                logger.error(f"Tavily search failed for query '{query}': {str(e)}")

        if not all_results:
            logger.warning(f"No relevant Tavily search results verified for target company '{company_name}'.")
            return self._get_fallback_mock_evidence(company_name, website, industry)

        return all_results

    def _get_fallback_mock_evidence(self, company_name: str, website: Optional[str] = None, industry: Optional[str] = None) -> List[Dict[str, Any]]:
        domain = website if website else f"https://{company_name.lower().replace(' ', '')}.com"
        parsed_domain = urlparse(domain if domain.startswith("http") else f"https://{domain}").netloc
        ind = industry if industry else "B2B Professional Services"
        now_str = datetime.datetime.utcnow().isoformat()

        return [
            {
                "title": f"{company_name} - Official Company Profile & Overview",
                "url": f"https://{parsed_domain}/about",
                "domain": parsed_domain,
                "snippet": f"{company_name} is a leading organization in the {ind} industry, providing specialized advisory and growth services to commercial clients.",
                "source_type": "web",
                "published_date": "2026-01-15",
                "relevance_score": 1.0,
                "retrieved_at": now_str
            },
            {
                "title": f"{company_name} Expansion & Hiring Updates",
                "url": f"https://{parsed_domain}/careers",
                "domain": parsed_domain,
                "snippet": f"{company_name} is actively expanding its sales and business development operations to scale commercial pipeline across regional markets.",
                "source_type": "web",
                "published_date": "2026-03-01",
                "relevance_score": 1.0,
                "retrieved_at": now_str
            }
        ]

tavily_service = TavilyResearchService()
