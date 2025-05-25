from transcript_to_form.base_structured_extractor import StructuredExtractor


# NOTE: ran out of time, did not implement
class TranscriptCondense(StructuredExtractor):
    """Given a transcript, produce a list of client names, and short descriptions, present in the text."""

    def condense(
        self, transcript: str, chunk_size_chars: int = 10_000, overlap_chars: int = 500
    ):
        # keep the start of the transcript, since this will likely give context that is important

        transcript_intro = transcript[:2_000]  # arbitrary

        chunks: list[str] = []
        transcript_length = len(transcript)

        step_size = chunk_size_chars - overlap_chars
        start_index = 0

        while start_index < transcript_length:
            end_index = min(start_index + chunk_size_chars, transcript_length)
            chunks.append(transcript[start_index:end_index])
            if end_index == transcript_length:
                break
            start_index += step_size

        return chunks
