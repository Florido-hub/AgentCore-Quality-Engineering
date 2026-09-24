from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

from juiz import obter_juiz

from agente import perguntar

JUIZ = obter_juiz()


def test_answer_relevancy():
    resposta = perguntar("Quais smartphones vocês tem?")

    test_case = LLMTestCase(
        input="",
        actual_output=resposta
    )

    metric = GEval(
        name="Conformidade de Claims",
        criteria="",
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT
        ],
        threshold=0.8,
        model=JUIZ
    )

    assert_test(test_case, metrics=[metric])