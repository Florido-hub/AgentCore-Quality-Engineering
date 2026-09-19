---
name: catalogo-techstore
description: Catálogo de produtos eletrônicos da TechStore. Use esta skill sempre que o usuário perguntar sobre produtos, preços, estoque, especificações, filtros, comparações ou recomendações.
---

# Catálogo TechStore

O arquivo `catalogo.json` contém o catálogo oficial da TechStore.

Quando o usuário perguntar sobre produtos, consulte o arquivo `catalogo.json`.

REGRAS:

- O catálogo é a única fonte de verdade sobre produtos.
- Nunca invente produtos.
- Nunca invente preços.
- Nunca invente estoque.
- Nunca invente especificações.
- Quando o usuário perguntar sobre produtos, consulte o arquivo `references/catalogo.json`.
- Quando o usuário solicitar filtros, aplique os filtros aos dados do catálogo.
- Quando o usuário solicitar uma comparação, utilize somente os dados presentes no catálogo.
- Quando o usuário pedir recomendação, recomende somente produtos presentes no catálogo.
- Se nenhum produto atender aos critérios, informe que nenhum produto do catálogo atende aos critérios.
- Se um produto não estiver no catálogo, informe que ele não foi encontrado.
- Produto com estoque igual a 0 deve ser informado como indisponível.
