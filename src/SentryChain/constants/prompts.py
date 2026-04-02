SUPPLIER_RISK_SEARCH_QUERY = """{supplier_name} supply chain disruption OR outage OR compliance risk OR SLA breach {current_year}"""

RISK_ANALYSIS_PROMPT = """You are a contract risk analyst. 
            NEWS EVENTS:
            {news_content}
            SLA CLAUSES:
            {combined_contexts}

            Based on the news events above, analyze:
            1. Has an SLA violation likely occurred? (Yes/No/Unclear)
            2. Which specific clauses are triggered?
            3. What penalties or remedies apply?
            4. Overall risk severity? (Low/Medium/High/Critical)

            Be specific and cite clause numbers where possible."""

VALIDATION_PROMPT = """
    You are a fact checker for legal verdicts.
    
    VERDICT:
    {verdict}
    
    SLA CLAUSES (source of truth):
    {clauses}
    
    Check every specific number, clauses, percentage, amount, or timeframe mentioned in the verdict.
    Does each one actually appear in the SLA clauses above?

    Reply ONLY in this JSON format with no extra text:
    {{"is_grounded": true, "hallucinated_claims": []}}
    """