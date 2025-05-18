"""
future todos:

- Identify long pauses in audio, this is likely a reasonable place to chunk the text
"""

import re

from .models import SpeechLine, TranscriptChunk


class TranscriptChunker:
    """Chunks a transcript into (Advisor, Client...) speech sequences."""

    def chunk(self, transcript: str, n_clients: int) -> list[TranscriptChunk]:
        """
        Chunks the transcript into segments starting with an advisor's speech,
        followed by subsequent client responses.

        Args:
            transcript: The transcript text.
            n_clients: the number of clients, used to route to the correct parser for the transcript

        Returns:
            A list of text chunks, where each chunk is a formatted string
            representing a speech sequence.  Returns an empty list if no chunks
            are found.
        """
        if n_clients == 1:
            structured = structured_transcript_single_speaker(transcript)
        else:
            structured = structured_transcript(transcript)

        # NOTE: needs more detection of when the advisor is speaking
        chunks: list[list[SpeechLine]] = []
        current_chunk: list[SpeechLine] = []
        for line in structured:
            if line.speaker.lower() == "advisor":
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = [line]
            elif current_chunk and current_chunk[0].speaker.lower() == "advisor":
                current_chunk.append(line)

        if current_chunk and current_chunk[0].speaker == "advisor":
            chunks.append(current_chunk)

        chunks_with_indices = [
            TranscriptChunk(lines=chunk, chunk_index=index)
            for index, chunk in enumerate(chunks)
        ]
        return chunks_with_indices


def structured_transcript(transcript: str) -> list[SpeechLine]:
    """
    Parses a transcript string into a list of SpeechLine objects.

    Args:
        transcript: The transcript text.

    Returns:
        A list of SpeechLine objects.  Returns an empty list on error.
    """

    speech_lines: list[SpeechLine] = []
    regex = r"^([A-Za-z0-9]+):\s*\[?(\d{2}:\d{2}:\d{2})?\]?\s*(.*)$"
    for line in transcript.strip().split("\n"):
        match = re.match(regex, line)
        if match:
            speaker = match.group(1)
            timestamp = match.group(2)
            dialogue = match.group(3).strip()
            speech_lines.append(
                SpeechLine(speaker=speaker, timestamp=timestamp, dialogue=dialogue)
            )
    return speech_lines


def structured_transcript_single_speaker(transcript: str) -> list[SpeechLine]:
    lines = transcript.strip().split("\n")
    speech_lines: list[SpeechLine] = []
    current_speaker = None
    current_dialogue_lines: list[str] = []
    current_timestamp = None

    for line in lines:
        if line.strip().endswith(":"):
            if current_speaker and current_dialogue_lines:
                speech_lines.append(
                    SpeechLine(
                        speaker=current_speaker,
                        timestamp=current_timestamp,
                        dialogue=" ".join(current_dialogue_lines).strip(),
                    )
                )
            current_speaker = line.strip().replace(":", "")
            current_dialogue_lines = []
            current_timestamp = None
        elif re.match(r"\d+:\d+:\d+", line.strip()):
            if current_dialogue_lines:
                speech_lines.append(
                    SpeechLine(
                        speaker=current_speaker,
                        timestamp=current_timestamp,
                        dialogue=" ".join(current_dialogue_lines).strip(),
                    )
                )
                current_dialogue_lines = []
            current_timestamp = line.strip()
        elif line.strip() == "":
            if current_speaker and current_dialogue_lines:
                speech_lines.append(
                    SpeechLine(
                        speaker=current_speaker,
                        timestamp=current_timestamp,
                        dialogue=" ".join(current_dialogue_lines).strip(),
                    )
                )
                current_dialogue_lines = []
                current_timestamp = None
        else:
            current_dialogue_lines.append(line.strip())

    if current_speaker and current_dialogue_lines:
        speech_lines.append(
            SpeechLine(
                speaker=current_speaker,
                timestamp=current_timestamp,
                dialogue=" ".join(current_dialogue_lines).strip(),
            )
        )

    return speech_lines
