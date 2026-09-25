# RELATÓRIO — CHALLENGE 02

# 1. Contexto, escopo e estratégia da avaliação

O **TechStore** é um agente de atendimento para uma loja de eletrônicos desenvolvido e executado no **Amazon Bedrock AgentCore Harness**. O projeto teve como objetivo aplicar um ciclo completo de **Quality Engineering para agentes de IA**, envolvendo construção e configuração do agente, sessão exploratória, criação de Golden Dataset, avaliação em duas frentes, campanha estruturada de Red Teaming, análise das falhas, correções e retestes.
O agente foi projetado para atender solicitações relacionadas exclusivamente ao domínio da TechStore. Entre suas principais funções estão consultar produtos disponíveis, informar preços, estoque e especificações, realizar comparações e recomendações e calcular frete a partir do CEP informado pelo usuário.
O **catálogo da TechStore é tratado como fonte oficial de verdade** para informações comerciais e técnicas dos produtos. Dessa forma, o agente não deve inventar produtos, preços, estoque ou especificações quando essas informações não estiverem disponíveis nas fontes consultadas.

## 1.1 Arquitetura e configuração do agente

O TechStore utiliza o **Amazon Nova 2 Lite** como modelo principal e é executado por meio do **Amazon Bedrock AgentCore Harness**. A temperatura foi configurada em **0.1**, buscando reduzir a variabilidade das respostas e favorecer um comportamento mais determinístico, adequado ao domínio de atendimento e consulta de informações estruturadas.
O agente possui instruções próprias que definem seu papel, escopo, comportamento esperado, regras de utilização das fontes e limites de atuação. Entre elas estão a obrigação de respeitar as informações oficiais do catálogo, não aceitar alterações de preços ou estoque fornecidas pelo usuário, evitar promessas não verificáveis e recusar solicitações que estejam fora do domínio da TechStore.
Para executar suas tarefas, o agente possui acesso a ferramentas de **consulta ao catálogo** e **consulta de CEP**, além do **Code Interpreter** quando necessário. A consulta ao catálogo fornece as informações utilizadas para responder sobre produtos, enquanto a consulta de CEP é utilizada nos fluxos relacionados ao cálculo de frete.
O suporte a conversas **multi-turno** é realizado por meio do `runtimeSessionId`. Os diferentes turnos de uma mesma conversa utilizam o mesmo identificador de sessão, permitindo que informações como orçamento, tipo de produto e preferências mencionadas anteriormente sejam consideradas nas mensagens seguintes.
De forma simplificada, o fluxo do agente é:
**Usuário → AgentCore Harness → Amazon Nova 2 Lite → Skills/Ferramentas → Resposta**

## 1.2 Thresholds do DeepEval

| **Métrica**      | **Threshold** | **Foco**                                                        |
| ---------------- | ------------- | --------------------------------------------------------------- |
| Answer Relevancy | >= 0,70       | Relevância da resposta em relação à solicitação.                |
| Faithfulness     | >= 0,80       | Fidelidade ao contexto de referência, sem informação inventada. |
| G-Eval           | >= 0,80       | Conformidade com o critério esperado de cada caso.              |

# 2. Sessão exploratória e principais achados

Foi realizada uma sessão exploratória orientada por charter, cobrindo consultas diretas, uso de ferramentas, conversas multi-turno, solicitações fora de escopo e entradas adversariais. Os comportamentos suspeitos observados foram utilizados como base para o Golden Dataset e para a campanha de red teaming.

| **Área**               | **Principal achado**                                                                                                        |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Consulta direta        | Falhas em consultas amplas, como listar notebooks disponíveis e filtrar todos os produtos abaixo de determinado preço.      |
| Ferramenta - catálogo  | Fluxos de busca e filtragem funcionaram em casos específicos, inclusive continuidade com pergunta sobre RAM.                |
| Ferramenta - CEP/frete | Falha observada porque o agente enviava parâmetro basePath indevido para a ferramenta de CEP.                               |
| Multi-turno            | O contexto da sessão foi preservado, mas em alguns turnos o agente adiou a consulta ao catálogo e fez perguntas adicionais. |
| Fora de escopo         | O agente inicialmente respondia perguntas de geografia, cálculo, programação e previsão do tempo, em vez de recusar.        |
| Adversarial            | Boa resistência a produto inexistente, preço/estoque induzido, prompt injection e manipulação de frete.                     |
| Vazamento              | Em recusas, o agente às vezes justificava a decisão citando regras internas e nomes/uso de ferramentas.                     |

O achado de maior impacto de segurança foi o vazamento indireto de instruções. Mesmo quando recusava corretamente uma solicitação, o agente podia explicar a recusa com frases que expunham regras internas, por exemplo mencionando explicitamente que os critérios exigiam o uso da ferramenta de consulta de CEP. O comportamento não revelava necessariamente o prompt completo, mas fornecia informação operacional desnecessária ao usuário.

# 3. Golden Dataset

O Golden Dataset foi consolidado com 15 casos e cobre as cinco categorias exigidas pelo desafio. Cada caso contém input ou sequência de turnos, critério esperado e retrieval_context quando aplicável. Os cenários foram derivados tanto do escopo funcional quanto das falhas observadas na exploração.

| **Categoria**         | **Cobertura / objetivo**                                                               |
| --------------------- | -------------------------------------------------------------------------------------- |
| Consulta direta       | Produto, preço, disponibilidade e filtros sobre o catálogo.                            |
| Tarefa com ferramenta | Casos que dependem de consulta correta ao catálogo ou CEP/frete.                       |
| Multi-turno           | Casos em que a resposta final depende de orçamento, preferência ou intenção acumulada. |
| Fora de escopo        | Solicitações que devem receber recusa breve e redirecionamento para a TechStore.       |
| Adversarial           | Indução de produto/preço/estoque falso, prompt injection e promessa indevida.          |

Para os testes multi-turno, o mesmo runtimeSessionId é utilizado ao longo da sequência, preservando o estado da conversa. No DeepEval, a sequência é executada turno a turno e a avaliação considera a solicitação final em conjunto com a resposta produzida pelo agente.

# 4. Avaliação em duas frentes

## 4.1 Frente A - AgentCore Evaluations

A avaliação nativa do AgentCore foi configurada sobre os traces reais do Harness. Foram utilizados dois avaliadores integrados - Builtin.Helpfulness e Builtin.GoalSuccessRate - e um avaliador customizado, TechStoreCatalogRule, implementado por função Lambda para verificar uma regra específica do domínio.



| **Avaliador**           | **Nível / finalidade**          | **Resultado observado**                                                                                                                            |
| ----------------------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Builtin.Helpfulness     | Trace - utilidade da resposta   | Scores entre 0,33 e 1,00; média aproximada de 0,61 no conjunto registrado.                                                                         |
| Builtin.GoalSuccessRate | Session - conclusão do objetivo | 3 sucessos em 10 sessões registradas (30%).                                                                                                        |
| TechStoreCatalogRule    | Customizado - regra de catálogo | Resultados foram gerados em volume menor; nas 10 sessões inicialmente consolidadas o valor exibido foi 0, exigindo interpretação junto aos traces. |

Os resultados do AgentCore mostraram que avaliadores diferentes não necessariamente produzem a mesma quantidade de resultados, pois operam em níveis distintos e dependem da disponibilidade do trace, sessão ou evento compatível. Isso foi observado principalmente no avaliador customizado.

## 4.2 Frente B - DeepEval

A baseline do DeepEval foi executada com 15 casos. O modelo juiz local via Ollama foi utilizado por restrições de acesso a provedores externos. A baseline evidenciou baixa aprovação nas três métricas, especialmente Answer Relevancy e G-Eval.

| **Métrica**      | **Threshold** | **Baseline** |
| ---------------- | ------------- | ------------ |
| Answer Relevancy | >= 0,70       | 3/15 (20,0%) |
| Faithfulness     | >= 0,80       | 7/15 (46,7%) |
| G-Eval           | >= 0,80       | 5/15 (33,3%) |

A interpretação de Answer Relevancy exige cuidado. Antes das melhorias, o agente frequentemente respondia perguntas fora do escopo; essas respostas podiam ser consideradas relevantes pelo juiz porque atendiam literalmente à pergunta. Após a correção, o agente passou a recusar adequadamente esses pedidos. Em alguns casos, a recusa correta recebeu score menor de relevância, demonstrando que uma queda pontual da métrica não representa necessariamente regressão funcional.
Faithfulness foi reexecutada, porém o juiz local apresentou instabilidade, com inferências muito longas e timeouts recorrentes. Por esse motivo, a métrica foi marcada como repetida, mas seus resultados pós-melhoria foram tratados com ressalva e não utilizados isoladamente para concluir melhora ou piora do agente.

# 5. Campanha de Red Teaming

A campanha de red teaming foi estruturada a partir dos riscos identificados na exploração e cobriu mais de 15 tentativas, atendendo ao requisito mínimo. Os ataques foram distribuídos entre prompt injection, jailbreak/bypass, vazamento de informação, indução de promessa indevida e uso indevido de ferramentas.

| **Categoria**              | **Objetivo**                                           | **Resultado consolidado**                                                                                                          | **Severidade**                   |
| -------------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| Prompt injection           | Ignorar regras e revelar prompt/instruções.            | O agente resistiu à revelação direta, mas algumas recusas expuseram detalhes das regras internas.                                  | Média                            |
| Jailbreak / bypass         | Forçar alteração de preço, estoque ou catálogo.        | Boa resistência: não aceitou alterar catálogo nem inventar produtos solicitados.                                                   | Baixa após controles             |
| Vazamento de informação    | Obter system prompt, regras ou dados de outra sessão.  | Vazamento parcial de lógica/instruções em justificativas de recusa; não foi observada evidência de mistura de dados entre sessões. | Média                            |
| Promessa indevida          | Forçar garantia de entrega ou afirmação não suportada. | O agente recusou garantia absoluta de entrega e solicitou dados quando necessários.                                                | Baixa                            |
| Uso indevido da ferramenta | Manipular CEP, parâmetros ou evitar validação.         | A ferramenta de CEP apresentou falha funcional de parâmetros; regras foram reforçadas para enviar apenas o CEP esperado.           | Alta funcional / Média segurança |

## 5.1 Tabela de achados

| **Vulnerabilidade**                       | **Severidade**         | **Evidência**                                                       |
| ----------------------------------------- | ---------------------- | ------------------------------------------------------------------- |
| Vazamento indireto de instruções internas | Média                  | Recusas citavam regras internas e o uso obrigatório de ferramentas. |
| Uso incorreto da ferramenta de CEP        | Alta                   | Envio indevido de basePath causava erro e impedia cálculo de frete. |
| Falha de recusa fora do escopo            | Média                  | Baseline respondia geografia, cálculo, Java e previsão do tempo.    |
| Consulta incompleta ao catálogo           | Média                  | Falhas em listagens amplas e filtros de preço durante exploração.   |
| Instabilidade do juiz local               | Limitação de avaliação | Timeouts e variação de scores, especialmente em Faithfulness.       |

A campanha mostrou que o agente apresentava melhor resistência a manipulação explícita do catálogo do que a vazamento indireto durante recusas. Esse resultado orientou a revisão do prompt: além de recusar, o agente passou a ser instruído a não explicar políticas internas, nomes de ferramentas, parâmetros, prompts ou detalhes de implementação.

# 6. Baseline × versão final

A análise conjunta dos resultados do **DeepEval**, **AgentCore Evaluations** e da campanha de **Red Teaming** permitiu identificar comportamentos que precisavam ser corrigidos antes da versão final do agente.
Entre os principais problemas encontrados estavam respostas a solicitações fora do escopo da TechStore, exposição parcial de instruções internas durante recusas, alucinação de contexto em perguntas sobre sessões anteriores e comportamentos inconsistentes diante de tentativas de manipulação de preço, estoque e ferramentas.

| **Problema identificado**             | **Melhoria aplicada**                                                                                    |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Respondia solicitações fora do escopo | Regra explícita de recusa breve e redirecionamento para produtos e compras da TechStore.                 |
| Vazava detalhes ao justificar recusas | Proibição de mencionar prompt, políticas, ferramentas, parâmetros, traces ou regras internas.            |
| Uso incorreto da consulta de CEP      | Instrução para chamar a ferramenta somente quando necessária e enviar apenas o CEP, sem basePath.        |
| Consulta ao catálogo inconsistente    | Reforço de que preço, estoque, especificações, filtros e recomendações devem partir do catálogo oficial. |
| Risco de alucinação                   | Proibição explícita de inventar ou aceitar dados induzidos pelo usuário como dados oficiais.             |
| Contexto multi-turno                  | Preservação do runtimeSessionId e tratamento da sequência de turnos no script de testes.                 |

## 6.1 Comparação

Com base nesses achados, foram realizados ajustes no prompt e nas instruções do agente. As principais modificações foram:

- reforço da consulta ao catálogo como fonte oficial para informações sobre produtos, preços, estoque e especificações;
- definição mais rígida do comportamento para perguntas fora do escopo, orientando o agente a recusar brevemente em vez de responder ao conteúdo solicitado;
- proibição explícita de revelar ou parafrasear prompts, Skills, regras internas, nomes de ferramentas, parâmetros e detalhes de implementação;
- reforço da proibição de alterar preços, estoque ou outros dados oficiais a partir de instruções do usuário;
- orientação para não inventar informações quando o contexto solicitado não estiver disponível, especialmente em tentativas de recuperar dados de outras sessões;
- reforço das restrições contra promessas de entrega e outras afirmações não sustentadas;
- refinamento das instruções de frete e do uso da ferramenta de CEP, evitando parâmetros indevidos e chamadas desnecessárias.

As mudanças buscaram corrigir especificamente as falhas observadas durante a avaliação, sem alterar o objetivo principal do agente.
Após as modificações, os casos mais relevantes foram executados novamente para verificar o impacto das correções. Os retestes indicaram melhora principalmente no comportamento de **fora de escopo**, que anteriormente apresentava respostas para perguntas não relacionadas à TechStore. 

| **Indicador**    | **Baseline**                                    | **Final / reteste**                                     | **Leitura**                                                                          |
| ---------------- | ----------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Answer Relevancy | 20,0% (3/15)                                    | 73,3% (11/15)                                           | Melhora expressiva; falhas restantes incluem recusas corretas penalizadas pelo juiz. |
| G-Eval           | 33,3% (5/15)                                    | 73,3% (11/15)                                           | Maior aderência aos critérios específicos dos casos.                                 |
| Faithfulness     | 46,7% (7/15)                                    | 73,3% (11/15)                                           | Maior aderência aos contextos de referência dos casos.                               |
| Fora de escopo   | Agente respondia temas externos                 | Recusas passaram a ocorrer                              | Correção funcional confirmada qualitativamente.                                      |
| Red teaming      | Vazamento indireto e falha de CEP identificados | Prompt reforçado e vulnerabilidades críticas retestadas | Redução do risco, ainda requer monitoramento.                                        |

# 7. Conclusão e avaliação de risco

O desafio demonstrou que a qualidade de um agente não pode ser avaliada por uma única métrica. O DeepEval permitiu testar sistematicamente o Golden Dataset e comparar comportamento antes e depois das mudanças; o AgentCore Evaluations trouxe observabilidade sobre sessões e traces reais; e o red teaming revelou vulnerabilidades que métricas de qualidade de resposta não capturaram diretamente.
A versão final apresentou melhora clara em conformidade com o escopo, relevância funcional e resistência a manipulação do catálogo. A principal limitação experimental foi o uso de um LLM juiz local, que apresentou variação entre execuções e timeouts, especialmente em Faithfulness. Essa limitação foi tratada separadamente das falhas semânticas do agente.
Em uma decisão de produção, o agente ainda exigiria controles adicionais antes de uma liberação ampla: validação determinística de parâmetros das ferramentas, observabilidade contínua, testes de regressão automatizados, proteção contra vazamento de instruções e uso de um juiz mais estável para avaliações periódicas. Com esses controles, a arquitetura demonstrada é adequada como base para evolução do TechStore.
