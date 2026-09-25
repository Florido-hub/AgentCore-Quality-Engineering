# 🚀 Demo Day 

## 1. Construção do agente

O **TechStore** é um agente de atendimento para uma loja de eletrônicos construído no **Amazon Bedrock AgentCore Harness**.

O agente foi desenvolvido para:

* consultar produtos, preços, estoque e especificações;
* comparar e recomendar produtos;
* manter contexto em conversas multi-turno;
* calcular frete a partir do CEP;
* utilizar o catálogo como fonte oficial de informações.

### Arquitetura

**Usuário → AgentCore Harness → Agente TechStore → Skills/Ferramentas → Resposta**

Principais componentes:

* **AgentCore Harness** para execução;
* consulta ao **catálogo oficial**;
* ferramenta de **consulta de CEP**;
* **Code Interpreter** quando necessário;
* `runtimeSessionId` para preservar contexto multi-turno.

Principais riscos considerados:

* alucinação de produtos ou especificações;
* alteração indevida de preço ou estoque;
* uso incorreto das ferramentas;
* vazamento de instruções internas;
* falha de recusa;
* vazamento ou invenção de contexto entre sessões;
* promessas indevidas.

---

## 2. Sessão exploratória

Antes da automação, foi realizada uma exploração manual do agente para identificar comportamentos suspeitos.

Foram testados:

* consultas diretas;
* filtros e recomendações;
* uso das ferramentas;
* contexto multi-turno;
* perguntas fora do escopo;
* tentativas de manipulação.

### Principais problemas encontrados

❌ Falhas em algumas consultas de catálogo.

❌ Uso incorreto da ferramenta de CEP, incluindo envio de parâmetro `basePath`.

❌ Respostas para perguntas completamente fora do escopo.

⚠️ Algumas consultas dependentes do catálogo não acionavam imediatamente a ferramenta.

Esses achados serviram de base para o **Golden Dataset** e para a campanha de **Red Teaming**.

---

## 3. Golden Dataset

Foi construído um Golden Dataset com **15 casos**, cobrindo as cinco categorias exigidas:

* Consulta direta;
* Tarefa com ferramenta;
* Multi-turno;
* Fora de escopo;
* Adversarial.

Cada caso contém:

* `input` ou sequência de turnos;
* `criteria`;
* `retrieval_context`, quando aplicável.

O objetivo foi transformar comportamentos encontrados durante a exploração em **casos reproduzíveis de avaliação**.

---

## 4. Avaliação em duas frentes

O mesmo agente foi avaliado utilizando dois ecossistemas.

### DeepEval

A suíte utiliza **Pytest + DeepEval**, com um modelo local via **Ollama** atuando como LLM-as-a-Judge.

Métricas:

* **Answer Relevancy ≥ 0.7**
* **Faithfulness ≥ 0.8**
* **G-Eval ≥ 0.8**

O modelo juiz local apresentou instabilidade em algumas execuções, principalmente em **Faithfulness**, incluindo timeouts. Essa limitação foi considerada na análise dos resultados.

### AgentCore Evaluations

Foram utilizados dois avaliadores integrados:

* **Helpfulness**
* **Goal Success Rate**

E um avaliador customizado:

* **TechStoreCatalogRule**

O avaliador customizado verifica uma regra específica do domínio relacionada ao comportamento do agente diante do catálogo.

### Por que duas frentes?

O **DeepEval** permitiu avaliar casos controlados e reproduzíveis do Golden Dataset.

O **AgentCore Evaluations** permitiu avaliar as interações e traces do agente no próprio ambiente de execução.

---

## 5. Campanha de Red Teaming

A campanha foi a principal etapa de segurança do projeto.

Foram executadas **20 tentativas**, distribuídas em cinco categorias:

* Prompt Injection;
* Jailbreak;
* Leakage;
* Tool Misuse;
* False Claim.

### Resultado

* ✅ **14 resistências — 70%**
* ⚠️ **5 resistências parciais — 25%**
* ❌ **1 falha direta — 5%**

### Principais vulnerabilidades

**Exposição de informações internas**

O agente chegou a revelar nomes de ferramentas, parâmetros e partes da lógica interna durante algumas respostas.

**Vazamento indireto durante recusas**

Mesmo recusando determinadas solicitações, o agente explicava o motivo utilizando informações das próprias instruções.

**Alucinação de contexto entre sessões**

Não foi identificado vazamento real entre sessões, porém o agente chegou a inventar informações quando questionado sobre uma sessão anterior.

**Manipulação de catálogo**

Alguns ataques revelaram comportamentos inadequados diante de tentativas de alteração de preço ou estoque.

---

## 6. Baseline × correção

Os resultados das avaliações e do Red Teaming foram utilizados para melhorar o agente.

### Principais correções

**Antes:** respondia perguntas fora do escopo.
**Depois:** regra explícita de recusa e redirecionamento.

**Antes:** recusas podiam revelar instruções internas.
**Depois:** proibição explícita de mencionar ou parafrasear prompts, Skills, ferramentas e parâmetros.

**Antes:** possibilidade de inventar contexto de outra sessão.
**Depois:** instrução explícita para não inferir ou inventar contexto indisponível.

**Antes:** comportamento inconsistente diante de manipulação de preço e estoque.
**Depois:** alterações de dados oficiais devem ser recusadas definitivamente.

**Antes:** ferramenta de CEP recebia parâmetros indevidos, como `basePath`.
**Depois:** instruções reforçadas para utilizar somente o CEP necessário.

### Resultados

As melhorias aumentaram principalmente a consistência das:

* recusas fora do escopo;
* consultas ao catálogo;
* respostas contra manipulação;
* proteção de informações internas;
* chamadas de ferramentas.

Os casos problemáticos foram então utilizados novamente como **testes de regressão**.

---

## 7. Considerações finais
