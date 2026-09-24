from deepeval import assert_test
from deepeval.metrics import FaithfulnessMetric
from deepeval.test_case import LLMTestCase

from juiz import obter_juiz

from agente import perguntar

JUIZ = obter_juiz()


def test_answer_relevancy():
    resposta = perguntar("Quais smartphones vocês tem?")

    test_case = LLMTestCase(
        input="",
        actual_output=resposta,
        retrieval_context=[],
    )

    metric = FaithfulnessMetric(
        threshold=0.8,
        model=JUIZ,
        verbose_mode=True
    )

    assert_test(test_case, metrics=[metric])