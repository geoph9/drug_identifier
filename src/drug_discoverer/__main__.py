"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Drug Discoverer."""


if __name__ == "__main__":
    main(prog_name="drug_discoverer")  # pragma: no cover
