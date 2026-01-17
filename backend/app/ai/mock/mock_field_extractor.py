from app.ai.contracts.outputs import ExtractedFields, FieldValue, ConfidenceScore


class MockFieldExtractor:
    async def extract(self, text: str) -> ExtractedFields:
        # Very basic stub
        return ExtractedFields(
            fields={
                "full_name": FieldValue(value="Manoj Sharma", confidence=ConfidenceScore(value=0.7)),
                "dob": FieldValue(value="1990-01-10", confidence=ConfidenceScore(value=0.65)),
                "address.city": FieldValue(value="mumbai", confidence=ConfidenceScore(value=0.6)),
            },
            meta={"extractor": "mock"}
        )
