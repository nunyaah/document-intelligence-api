from datetime import datetime, timezone
from fastapi import Depends

from app.dependencies import get_vector_store
from app.pipeline.embedder import embed_query
from app.pipeline.llm_engine import generate_answer
from app.vectorstore.base import VectorStoreAdapter
from app.utils.exceptions import DocumentNotFoundError
from app.config import get_settings
from app.utils.logging import get_logger
from app.services.document_service import _document_store

logger = get_logger(__name__)


class EvalService:
    def __init__(self, vector_store: VectorStoreAdapter):
        self._vs = vector_store

    async def run_eval(self, document_id: str, eval_dataset: list[dict], request_id: str = "") -> dict:
        if document_id not in _document_store:
            raise DocumentNotFoundError(document_id)

        doc_meta = _document_store[document_id]
        settings = get_settings()

        questions, answers, contexts, ground_truths = [], [], [], []

        for item in eval_dataset:
            question = item["question"]
            ground_truth = item["ground_truth"]

            query_vector = embed_query(question)
            results = self._vs.search(query_vector, document_id=document_id, top_k=settings.retrieval_top_k)
            results_sorted = sorted(results, key=lambda r: r.payload.get("chunk_index", 0))

            answer, _ = await generate_answer(
                question=question,
                chunks=results_sorted,
                filename=doc_meta["filename"],
            )

            chunk_texts = [r.payload.get("text", "") for r in results_sorted]

            questions.append(question)
            answers.append(answer)
            contexts.append(chunk_texts)
            ground_truths.append(ground_truth)

        scores = await self._compute_ragas(questions, answers, contexts, ground_truths)

        result = {
            "faithfulness": scores.get("faithfulness", 0.0),
            "answer_relevancy": scores.get("answer_relevancy", 0.0),
            "context_precision": scores.get("context_precision", 0.0),
            "context_recall": scores.get("context_recall", 0.0),
            "num_samples": len(eval_dataset),
            "eval_model": settings.groq_model,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }

        # Optionally save results
        import json
        import os
        os.makedirs(settings.eval_output_dir, exist_ok=True)
        output_path = os.path.join(settings.eval_output_dir, f"eval_{document_id}.json")
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        logger.info("Evaluation complete", extra={"request_id": request_id, "scores": scores})

        return result

    async def _compute_ragas(
        self,
        questions: list[str],
        answers: list[str],
        contexts: list[list[str]],
        ground_truths: list[str],
    ) -> dict:
        try:
            from datasets import Dataset
            from ragas import evaluate
            from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

            data = {
                "question": questions,
                "answer": answers,
                "contexts": contexts,
                "ground_truth": ground_truths,
            }
            dataset = Dataset.from_dict(data)
            result = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])
            return dict(result)
        except Exception as exc:
            logger.warning("RAGAS evaluation failed, returning zeros", extra={"error": str(exc)})
            return {
                "faithfulness": 0.0,
                "answer_relevancy": 0.0,
                "context_precision": 0.0,
                "context_recall": 0.0,
            }


def get_eval_service(vs: VectorStoreAdapter = Depends(get_vector_store)) -> EvalService:
    return EvalService(vs)
