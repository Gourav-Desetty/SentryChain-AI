import os, sys, json
from src.SentryChain.logging.logger import logging
from src.SentryChain.exception.exception import CustomException
from src.SentryChain.constants.prompts import VALIDATION_PROMPT
from src.SentryChain.entity.artifact_entity import InputGuardrailArtifact, OutputGuardrailArtifact

class Guardrails:
    def __init__(self, llm) -> None:
        self.llm = llm

    def input_guardrail(self, articles: list) -> InputGuardrailArtifact:
        try:
            KEYWORDS = ["outage", "breach", "status", "downtime", "incident", "sla", "penalty", "unavailable", "offline", "war"]

            def is_relevant(article):
                text = (article["title"] + article["content"]).lower()
                return any(kw in text for kw in KEYWORDS)

            filtered_articles = [a for a in articles if is_relevant(a)]

            input_guardrail_artifact = InputGuardrailArtifact(filtered_articles=filtered_articles)
            return input_guardrail_artifact
        except Exception as e:
            raise CustomException(e, sys)


    def output_guardrail(self, verdict: str, combined_contexts: list) -> OutputGuardrailArtifact:
        try:
            validation_input = VALIDATION_PROMPT.format(
                verdict=verdict,
                clauses = "\n".join(combined_contexts)
                )

            ## pass the prompt to llm
            validation_response = self.llm.invoke(validation_input) 

            validation_data = json.loads(validation_response.content)

            is_grounded = validation_data.get("is_grounded", False)
            hallucinations = validation_data.get("hallucinated_claims", [])

            if is_grounded:
                logging.info("Verdict grounded in SLA clauses.")
            else:
                logging.warning(f"Hallucinations detected: {hallucinations}")

            guardrailartifact = OutputGuardrailArtifact(is_verified=is_grounded,
                                                hallucinations=hallucinations)

            return guardrailartifact
        except Exception as e:
            logging.error(f"Guardrail validation failed: {e}")
            raise CustomException(e, sys)