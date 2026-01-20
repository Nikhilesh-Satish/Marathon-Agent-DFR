
from pipeline import BuildPipeline

if __name__ == "__main__":
    pipeline = BuildPipeline(
        architecture_contract_path="architecture_contract.json",
        output_dir="generated_code",
        ledger_path="ledger.json"
    )

    pipeline.run()
