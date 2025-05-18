import asyncio
from pathlib import Path

import questionary
import typer
from rich.console import Console

from tests.data import SAMPLE_TRANSCRIPT_1, SAMPLE_TRANSCRIPT_2

from .extract import extract

app = typer.Typer(help="CLI tool to select and process transcripts.")
console = Console()

TRANSCRIPT_OPTIONS = {
    "Sample Transcript 1": SAMPLE_TRANSCRIPT_1,
    "Sample Transcript 2": SAMPLE_TRANSCRIPT_2,
}


@app.command()
def select_transcript(
    output_path: Path = typer.Option(
        ...,
        "--output_dir",
        "-o",
        help="Directory to save the extracted output.",
        dir_okay=True,
        writable=False,
    ),
):
    output_path.mkdir(exist_ok=True)
    console.print("[bold]Transcript Selection[/bold]")

    selected_transcript_name = questionary.select(
        "Please choose a transcript:", choices=list(TRANSCRIPT_OPTIONS.keys())
    ).ask()

    if selected_transcript_name is not None:
        transcript_content = TRANSCRIPT_OPTIONS[selected_transcript_name]
        console.print(
            f"\nYou selected: [bold green]{selected_transcript_name}[/bold green]. Starting processing..."
        )

        asyncio.run(extract(transcript=transcript_content, output_path=output_path))
    else:
        console.print("\nNo transcript selected.", style="bold red")
        exit()


if __name__ == "__main__":
    app()
