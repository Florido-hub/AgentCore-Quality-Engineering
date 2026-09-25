import json
from pathlib import Path

import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

from juiz import obter_juiz

from agente import perguntar
from utils.utils import preparar_input_avaliacao

JUIZ = obter_juiz()

caminho_json = Path(__file__).resolve().parent.parent / "dataset" / "golden_dataset.json"
dataset = json.loads(caminho_json.read_text(encoding="utf-8"))

@pytest.mark.parametrize("caso", dataset)
def test_answer_relevancy(caso):
    resposta = perguntar(caso["input"])

    input_avaliacao = preparar_input_avaliacao(caso["input"])

    test_case = LLMTestCase(
        input=input_avaliacao,
        actual_output=resposta
    )

    metric = AnswerRelevancyMetric(
        threshold=0.7,
        model=JUIZ,
        verbose_mode=True
    )

    assert_test(test_case, metrics=[metric])