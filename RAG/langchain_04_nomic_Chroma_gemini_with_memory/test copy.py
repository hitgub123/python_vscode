from datasets import load_dataset
from ragas.metrics import context_precision, answer_relevancy, faithfulness
from ragas import evaluate
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_recall,
    context_precision,
)


test_dataset = load_dataset("JC-24/meta-record-ragas-synthetic-dataset")['train']
# print(test_dataset)
# features: ['user_input', 'reference_contexts', 'reference', 'synthesizer_name'],

test_dataset=test_dataset.add_column("answer", test_dataset['user_input'])


# Format dataset structure
formatted_dataset = []
for item in test_dataset:
    formatted_item = {
        "question": item["user_input"],
        "answer": item["answer"],
        "reference": item["answer"],
        "contexts": item["reference_contexts"],
        "retrieved_contexts": item["reference_contexts"],
    }
    formatted_dataset.append(formatted_item)

# Convert to RAGAS dataset
ragas_dataset = Dataset.from_list(formatted_dataset)

result = evaluate(
    dataset=ragas_dataset,
    llm=llm,
    embeddings=embeddings,
    metrics=[
        context_precision,
        faithfulness,
        answer_relevancy,
        context_recall,
    ],
)

print(result)
