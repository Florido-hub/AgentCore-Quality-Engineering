# 🤖 TechStore — AgentCore-Quality-Engineering

Projeto desenvolvido como parte do **Challenge 02**, com o objetivo de construir e avaliar um agente de IA utilizando **Amazon Bedrock AgentCore**, **DeepEval** e técnicas de **Red Teaming**.

O TechStore simula um assistente de uma loja de eletrônicos capaz de consultar produtos, preços e estoque, recomendar opções, manter contexto entre mensagens e realizar cálculos relacionados a compras e frete.

## 🎯 Escopo

O agente foi construído no **Amazon Bedrock AgentCore Harness** e possui ferramentas para:

* consultar o catálogo oficial da TechStore;
* pesquisar preços, estoque e especificações;
* comparar e recomendar produtos;
* consultar CEP para cálculos de frete;
* manter contexto em conversas multi-turno.

O projeto avalia riscos como **alucinação de informações, manipulação de preços e estoque, uso incorreto de ferramentas, prompt injection, vazamento de instruções, falhas de recusa e promessas indevidas**.

## 📁 Estrutura

```text
Desafio2/
├── dataset/
│   └── golden_dataset.json
├── Testes/
│   ├── test_AnswerRelevancy.py
│   ├── test_Faithfulness.py
│   └── test_geval.py
├── utils/
├── agente.py
├── juiz.py
├── requirements.txt
└── README.md
```

## ⚙️ Como executar

### 1. Clone o projeto

```bash
git clone https://github.com/Florido-hub/AgentCore-Quality-Engineering
```

### 2. Crie o ambiente virtual

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
AWS_PROFILE=seu-profile
AWS_REGION=us-east-2
HARNESS_ARN=seu-harness-arn

JUIZ_PROVIDER=ollama
JUIZ_MODEL=gemma3:4b
OLLAMA_URL=http://localhost:11434
```

> Não adicione o arquivo `.env` ao repositório.

### 5. Prepare o Ollama

Com o Ollama instalado e em execução:

```bash
ollama pull gemma3:4b
```

Verifique os modelos disponíveis:

```bash
ollama list
```

### 6. Execute os testes

Todos os testes:

```bash
pytest Testes/
```

Ou individualmente:

```bash
pytest Testes/test_AnswerRelevancy.py
pytest Testes/test_Faithfulness.py
pytest Testes/test_geval.py
```

Também é possível utilizar o runner do DeepEval:

```bash
deepeval test run Testes/
```

## 🛠️ Tecnologias

* Python
* Amazon Bedrock AgentCore
* AWS SDK for Python (Boto3)
* DeepEval
* Pytest
* Ollama
* LLM-as-a-Judge

## 🧪 Golden Dataset

A suíte utiliza um Golden Dataset com **15 casos de teste**, dividido em cinco categorias:

* Consulta direta;
* Tarefa com ferramenta;
* Multi-turno;
* Fora de escopo;
* Adversarial.

Cada caso contém o input, o comportamento esperado e, quando aplicável, o contexto de referência.

## 📊 Avaliação

O agente foi avaliado em duas frentes.

### DeepEval

Foram utilizadas três métricas:

| Métrica          | Threshold |
| ---------------- | --------: |
| Answer Relevancy |    ≥ 0.70 |
| Faithfulness     |    ≥ 0.80 |
| G-Eval           |    ≥ 0.80 |

Os testes são executados com **Pytest + DeepEval**, utilizando um modelo local via **Ollama** como LLM-as-a-Judge.

### AgentCore Evaluations

Também foram realizadas avaliações diretamente sobre os traces do AgentCore utilizando:

* **Builtin.Helpfulness**
* **Builtin.GoalSuccessRate**
* **TechStoreEvaluation**, avaliador customizado para regras específicas do agente.

## 🔴 Red Teaming

Foi realizada uma campanha estruturada de Red Teaming cobrindo ataques como:

* Prompt Injection;
* Jailbreak e bypass de regras;
* vazamento de informações internas;
* manipulação do catálogo;
* promessas indevidas;
* uso incorreto de ferramentas.

Os resultados foram utilizados para identificar vulnerabilidades e melhorar as instruções e restrições do agente.

## 📈 Resultados

Após a análise das avaliações e da campanha de Red Teaming, o agente foi ajustado e submetido a uma nova rodada de testes.

Entre as principais melhorias observadas estão:

* maior aderência ao escopo da TechStore;
* recusa de solicitações fora do domínio;
* maior proteção contra manipulação do catálogo;
* redução do vazamento de instruções internas;
* regras mais específicas para utilização das ferramentas.

O **Answer Relevancy passou de 20% de aprovação na baseline para 73,3% no reteste**, enquanto o **G-Eval passou de 33,3% para aproximadamente 73,3%**.

A métrica **Faithfulness também foi reexecutada**, porém apresentou instabilidade e timeouts devido às limitações do modelo local utilizado como juiz, sendo tratada como uma limitação experimental.

## 📌 Observações

Os resultados de métricas baseadas em LLM-as-a-Judge podem apresentar variações entre execuções. Durante os experimentos, o modelo local utilizado pelo Ollama apresentou instabilidade em algumas avaliações, especialmente na métrica Faithfulness.

Este comportamento foi considerado durante a análise dos resultados e tratado como uma limitação da infraestrutura de avaliação, e não automaticamente como uma falha do agente.
