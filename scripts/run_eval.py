#!/usr/bin/env python3
"""CLI runner for RAGAS evaluation.

Usage:
  python scripts/run_eval.py \\
    --document_id <uuid> \\
    --eval_file tests/eval_dataset.json \\
    --output eval_results.json \\
    --base_url http://localhost:8000
"""

import argparse
import json
import sys

import httpx


def main():
    parser = argparse.ArgumentParser(description="Run RAGAS evaluation against the Document Intelligence API")
    parser.add_argument("--document_id", required=True, help="UUID of the ingested document")
    parser.add_argument("--eval_file", default="tests/eval_dataset.json", help="Path to eval dataset JSON")
    parser.add_argument("--output", default="eval_results.json", help="Output file for results")
    parser.add_argument("--base_url", default="http://localhost:8000", help="API base URL")
    args = parser.parse_args()

    with open(args.eval_file, "r") as f:
        eval_dataset = json.load(f)

    print(f"Loaded {len(eval_dataset)} eval samples from {args.eval_file}")

    payload = {"document_id": args.document_id, "eval_dataset": eval_dataset}
    url = f"{args.base_url}/api/v1/eval"

    print(f"Calling POST {url} ...")
    with httpx.Client(timeout=300.0) as client:
        response = client.post(url, json=payload)

    if response.status_code != 200:
        print(f"ERROR {response.status_code}: {response.text}", file=sys.stderr)
        sys.exit(1)

    result = response.json()
    if result.get("status") != "success":
        print(f"API error: {result.get('error')}", file=sys.stderr)
        sys.exit(1)

    data = result["data"]
    print("\n─── RAGAS Evaluation Results ───")
    print(f"  Faithfulness:      {data['faithfulness']:.3f}")
    print(f"  Answer Relevancy:  {data['answer_relevancy']:.3f}")
    print(f"  Context Precision: {data['context_precision']:.3f}")
    print(f"  Context Recall:    {data['context_recall']:.3f}")
    print(f"  Samples:           {data['num_samples']}")
    print(f"  Model:             {data['eval_model']}")
    print(f"  Evaluated at:      {data['evaluated_at']}")

    with open(args.output, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
