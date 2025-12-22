from extract import run_full_ingestion
from ingest import run_chunking

def main() -> None:
    # ingest all markdown files under data/*/*.md
    run_full_ingestion()
    # chunk them and save in chromadb
    run_chunking()

if __name__ == "__main__":
    main()