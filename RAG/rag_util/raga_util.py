from datasets import load_dataset
from ragas.metrics import (
    context_precision,
    answer_relevancy,
    faithfulness,
    LLMContextPrecisionWithoutReference,
)
from ragas import evaluate
from datasets import Dataset
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_recall,
    context_precision
)
import gemini_api_util, huggingface_dataset_util

"""
data_map_list = [{
    "question": XXX,
    "answer": XXX,
    "contexts": XXX,
    "ground_truth": XXX,
    "reference": XXX,
}]
"""


def evaluate_ragas(
    data_map_list,
    llm=gemini_api_util.get_llm(),
    embeddings=gemini_api_util.get_embeddings(),
    metrics=[
        # context_precision,
        # LLMContextPrecisionWithoutReference(),
        faithfulness,
        answer_relevancy,
        context_recall,
    ],
):
    dataset = Dataset.from_list(data_map_list)
    result = evaluate(
        dataset=dataset,
        llm=llm,
        embeddings=embeddings,
        metrics=metrics,
    )

    print(">" * 40, f"\nresult:\n{result}")
    return result


if __name__ == "__main__":
    dataset = huggingface_dataset_util.get_dataset(
        "JC-24/meta-record-ragas-synthetic-dataset"
    )
    test_dataset = dataset["train"]
    # print(test_dataset)
    # features: ['user_input', 'reference_contexts', 'reference', 'synthesizer_name'],

    test_dataset = test_dataset.add_column("answer", test_dataset["user_input"])

    # Format dataset structure
    formatted_dataset = []
    for item in test_dataset:
        formatted_item = {
            "question": item["user_input"],
            "answer": item["answer"],
            "contexts": item["reference_contexts"],
            "ground_truth": item["answer"],
            "reference": item["answer"],
        }
        formatted_dataset.append(formatted_item)

    # Convert to RAGAS dataset
    ragas_dataset = Dataset.from_list(formatted_dataset)

    result = evaluate_ragas(
        dataset=ragas_dataset,
        metrics=[
            context_precision,
            faithfulness,
            answer_relevancy,
            context_recall,
        ],
    )

    print(result)
