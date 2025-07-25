QA = [
    {
        "question": "What is the name of the ship owner's daughter?",
        "answer": "Europa",
        "reference": "who bore the surprising name of Europa, was the daughter of a wealthy shipowner",
    },
    {
        "question": "what did john do when he was 23?",
        "answer": "he outwitted the six warships that six Great Powers had sent to seize him.",
        "reference": "and that at twenty-three, in appearance but little altered, he outwitted the six warships that six Great Powers had sent to seize him"
    },
    # {
    #     "question": "船主的女儿的名字是什么",
    #     "answer": "Europa",
    # },
    # {
    #     "question": "who is the child of the ship owner?",
    #     "answer": "Europa",
    # },
    # {
    #     "question": "who is pandora",
    #     "answer": "her name is pandora day",
    # },
    # {
    #     "question": "does she has sister or brothers",
    #     "answer": "Yes,a sister and a brother",
    # },
    # {
    #     "question": "is she married",
    #     "answer": "yes",
    # },
]

import raga_util
import ragas


def test_llm(rag_chain):
    data_map_list = []
    for qa in QA:
        q = qa["question"]
        a = qa["answer"]
        r = qa["reference"]
        response = rag_chain.invoke(f"search_query: {q}")
        data_map = {
            "question": q,
            "answer": response["answer"],
            "contexts": response["context"],
            "ground_truths": a,
            "reference": r,
        }
        data_map_list.append(data_map)

    raga_util.evaluate_ragas(data_map_list=data_map_list)
