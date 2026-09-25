import json
from pathlib import Path
from utils.utils import preparar_input_avaliacao

import pytest
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

from juiz import obter_juiz
from agente import perguntar

JUIZ = obter_juiz()

caminho_json = Path(__file__).resolve().parent.parent / "dataset" / "golden_dataset.json"
dataset = json.loads(caminho_json.read_text(encoding="utf-8"))

@pytest.mark.parametrize("caso", dataset)
def test_geval(caso):
    resposta = perguntar(caso["input"])

    input_avaliacao = preparar_input_avaliacao(caso["input"])

    test_case = LLMTestCase(
        input=input_avaliacao,
        actual_output=resposta
    )

    metric = GEval(
        name="Conformidade de Claims",
        criteria=caso["criteria"],
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT
        ],
        threshold=0.8,
        model=JUIZ
    )

    assert_test(test_case, metrics=[metric])