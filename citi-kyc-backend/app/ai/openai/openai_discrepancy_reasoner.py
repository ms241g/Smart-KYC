from app.ai.gemini.schemas import GeminiReasoningOutput
from app.ai.contracts.outputs import DiscrepancyItem


class OpenAIDiscrepancyReasoner:
    def __init__(self, client):
        self.client = client

    async def reason(self, ctx):
        prompt = f"""You are a compliance-grade KYC discrepancy reasoner for Citi Bank.

        Your task is to identify KYC-relevant discrepancies by comparing:
        1. Authoritative Customer Profile
        2. User-Provided Payload
        3. Evidence / Extracted Fields

        ### Normalization Rules (MANDATORY)
        Before any comparison, you MUST normalize ALL text inputs as follows:
        - Convert all characters to UPPERCASE
        - REMOVE all whitespace characters (spaces, tabs, newlines)
        - REMOVE punctuation, symbols, and special characters
        - REMOVE common prefixes and honorifics from names, including but not limited to:
        ["MR", "MRS", "MS", "MISS", "DR", "SHRI", "SHREE", "SMT", "KUMARI"]
        - TRIM leading and trailing non-alphanumeric characters
        - Normalize multiple representations of the same value (e.g., "INDIA" vs "REPUBLICOFINDIA")

        ⚠️ After normalization, comparisons must be STRICT and EXACT.

        ### Comparison Logic
        - Compare normalized fields across all three sources
        - Apply special handling of state and city. If document mentions only city or state, allow match if other source has both but one matches
        - Prioritize authoritative customer profile over user payload when conflicts arise
        - Identify discrepancies ONLY if:
        - The authoritative profile conflicts with payload or evidence
        - The mismatch is relevant to regulatory KYC requirements
        - Ignore discrepancies that are:
        - Formatting-only
        - Caused solely by prefixes, whitespace, punctuation, or casing

        ### Discrepancy Classification
        For each valid discrepancy:
        - Clearly identify the field name
        - Specify mismatching sources
        - Assign a severity level:
        - LOW: Minor but acceptable variance
        - MEDIUM: Requires clarification or supporting documents
        - HIGH: Regulatory or compliance risk
        - Provide concise, actionable resolution guidance suitable for KYC operations teams

        ### Safety & Compliance Constraints
        - DO NOT hallucinate, infer, or fabricate missing values
        - If a field is missing in any source, explicitly mark it as "NOT_AVAILABLE"
        - If no discrepancies exist, return an empty discrepancies array

        ### Output Requirements
        - Return ONLY valid JSON
        - JSON MUST strictly conform to the provided response schema
        :\n{ctx.model_dump_json(indent=2)}"""

        out: GeminiReasoningOutput = self.client.generate_structured(
            prompt=prompt,
            schema_model=GeminiReasoningOutput,
        )

        return ReasoningOutput(
            discrepancies=[
                DiscrepancyItem(
                    field=d.field,
                    expected=d.expected,
                    received=d.received,
                    severity=d.severity,
                    resolution_required=d.resolution_required,
                    explanation=d.explanation,
                )
                for d in out.discrepancies
            ],
            overall_confidence=out.overall_confidence,
        )
