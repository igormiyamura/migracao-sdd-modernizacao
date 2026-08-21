# Apuração de Enquadramento de Limites - Mesa de Renda Fixa

**Mesa/área**: Renda Fixa - Risco de Mercado
**Dono do processo**: carlos.risco@banco.com.br
**Frequência**: diária
**Criticidade**: alta

## Objetivo

Consolidar diariamente a exposição de risco de taxa (DV01) da carteira de Renda Fixa por book, comparar contra os limites de negociação definidos pela área, e notificar a mesa (alerta) ou o head de risco (excesso) conforme a gravidade do desenquadramento.

## O que o processo recebe

- **Posições da carteira de Renda Fixa** (manual): ativo, book, quantidade, PU e DV01 unitário de cada posição. Hoje colada manualmente pelo analista — **[a confirmar com o dono do processo: existe um sistema de origem que poderia alimentar isso automaticamente?]**. Atualizada diariamente.
- **Limites de negociação** (manual): limite de DV01 por book, definido pela área. Raramente alterado.

## O que o processo faz

1. **Consolida a exposição de risco (DV01) de cada book**, somando o DV01 de todas as posições que pertencem a ele.
2. **Avalia o enquadramento de cada book**: compara a exposição consolidada contra o limite definido para aquele book.
3. **Classifica cada book em três níveis de severidade** conforme o quanto do limite já foi utilizado: dentro do normal, em alerta, ou excedido.
4. **Registra um log consolidado** com o resultado de todos os books.
5. **Notifica a pessoa certa conforme a gravidade**: quando um book excede o limite, o head de risco é avisado; quando um book está próximo do limite (mas ainda dentro), quem é avisado é o head da mesa de Renda Fixa — dois públicos diferentes para dois níveis de urgência diferentes.

## Onde o processo agrega valor

- **Consolidação de DV01 por book**: transforma uma lista de posições individuais num único número por book — é esse número, não a lista de posições, que a mesa e o head de risco realmente usam para decidir se precisa reduzir exposição.
- **Classificação de severidade (OK / alerta / excedido)**: não é só comparar dois números — é a decisão de negócio que determina se ninguém precisa agir, se a mesa deve ficar atenta, ou se o head de risco precisa agir agora. É o coração do processo: sem essa classificação, o processo seria só um relatório de números, não uma ferramenta de controle de risco.
- **Roteamento de notificação por severidade**: a escolha de avisar o head da mesa (alerta, ainda há tempo de ajustar) em vez do head de risco (excedido, já é uma quebra de limite) evita tanto alarme desnecessário no nível errado quanto demora em escalar um problema real.

## Regras e decisões de negócio

| Regra/parâmetro | Valor atual | O que controla | Origem |
|---|---|---|---|
| Limiar de alerta | 80% do limite (inclusive) | A partir daqui, o head da mesa é notificado | Não identificada na fonte — confirmar com o dono do processo quem definiu esse percentual e quando |
| Limiar de excesso | acima de 100% do limite | A partir daqui, o head de risco é notificado | Não identificada na fonte — mesma observação acima |
| Limite de DV01 por book | um valor por book, ver aba "Limites" da planilha original | Referência contra a qual a exposição de cada book é comparada | Definido pela área; não há registro de revisão periódica visível no processo |
| Book sem posição no dia | tratado como 0% de utilização (status OK) | Um book configurado em "Limites" mas sem nenhuma posição naquele dia não gera alerta | Comportamento implícito do código, não uma decisão documentada — confirmar se é o esperado |

## O que o processo entrega

- **Log de enquadramento**: arquivo com o resultado (limite, utilizado, percentual, status) de cada book, formato CSV.
- **E-mail de excesso de limite**: enviado ao head de risco sempre que um book ultrapassa 100% do limite.
- **E-mail de alerta de proximidade do limite**: enviado ao head da mesa de Renda Fixa quando um book está entre 80% e 100% do limite.

## Pontos de atenção

- Não foi identificada uma fonte automatizada para as posições — hoje são coladas manualmente, mesma situação de outros processos já migrados nesta mesa.
- Os limiares de alerta (80%) e excesso (100%) estão fixos no código, sem registro de quem os definiu — vale confirmar se são os valores corretos hoje ou se já mudaram informalmente sem atualizar o processo.
- A planilha original tem uma conferência manual paralela (fórmula numa aba separada) que recalcula o mesmo número de exposição por book, mas essa conferência **não é usada pelo processo automatizado** — é mantida à parte pelo analista. Vale confirmar com o dono do processo se essa conferência deve ser preservada na versão migrada (como uma checagem adicional) ou se pode ser descartada, já que os dois cálculos podem divergir sem ninguém perceber hoje.
- O caminho do log e os dois e-mails de destino estão fixos no processo original — na versão migrada, devem virar configuração, não texto fixo no código.
- O log é sobrescrito a cada execução — não existe hoje um histórico das apurações anteriores.

## Glossário

- **DV01**: variação no valor de uma posição de renda fixa para uma mudança de 1 ponto-base na taxa de juros; medida padrão de risco de taxa.
- **Book**: agrupamento de posições por estratégia/mesa dentro da carteira de Renda Fixa, usado como unidade de limite de risco.
- **Enquadramento**: verificação de que a exposição de um book está dentro do limite de risco definido pela área.
