# Consolidação de VaR - Mesa Equities

**Mesa/área**: Equities - Risco de Mercado
**Dono do processo**: ana.risco@banco.com.br
**Frequência**: diária
**Criticidade**: alta

## Objetivo

Consolidar diariamente a exposição e o VaR (Value at Risk) individual de cada ativo da carteira de equities, comparar o VaR total contra o limite definido pela área, e alertar a mesa quando o limite é ultrapassado.

## O que o processo recebe

- **Carteira de equities** (manual): posições da carteira (ativo, quantidade, preço unitário, volatilidade). Hoje colada manualmente pelo analista — **[a confirmar com o dono do processo: existe uma fonte automatizada para esses dados?]**. Atualizada diariamente.
- **Parâmetros de risco** (manual): fator de confiança do VaR e limite de VaR total da mesa. Raramente alterados.

## O que o processo faz

1. **Calcula a exposição de cada ativo** da carteira: quantidade multiplicada pelo preço unitário.
2. **Calcula o VaR individual de cada ativo**: a exposição multiplicada pela volatilidade do ativo e pelo fator de confiança definido pela área.
3. **Consolida o VaR total** somando o VaR individual de todos os ativos, e **verifica se ultrapassa o limite** definido pela mesa.
4. **Exporta o relatório consolidado** com o detalhe por ativo, o VaR total e o resultado da verificação do limite.
5. **Alerta a mesa por e-mail** sempre que o VaR total ultrapassar o limite.

## O que o processo entrega

- **Relatório de VaR consolidado**: arquivo com o detalhe por ativo, formato CSV.
- **E-mail de alerta**: enviado para a mesa de Equities somente quando o limite de VaR é ultrapassado.

## Pontos de atenção

- Não foi identificada uma fonte automatizada para os dados de carteira — hoje são colados manualmente. Antes de migrar, é preciso confirmar com o dono do processo se existe um sistema (gestão de carteira, custódia) de onde isso possa ser extraído automaticamente.
- O fator de confiança (1,65) e o limite de VaR estão fixos na planilha, sem registro de quem os definiu ou com que frequência mudam — confirmar se devem virar parâmetros configuráveis (recomendado) ou se há uma fonte oficial para eles.
- O caminho de saída do relatório e o endereço de e-mail de alerta estão fixos na macro — na versão migrada, devem virar configuração.
- Não há um agendamento explícito visível: o processo roda quando a planilha é aberta. Confirmar com o dono do processo o horário/gatilho real de execução em produção.
- O relatório de saída é sobrescrito a cada execução, sem manter histórico de versões anteriores — avaliar se a migração deve manter esse histórico.

## Glossário

- **VaR**: Value at Risk — perda máxima esperada de uma posição ou carteira, para um dado nível de confiança e horizonte de tempo.
- **Exposição**: valor financeiro de uma posição (quantidade × preço unitário).
- **Fator de confiança**: multiplicador do VaR paramétrico associado ao nível de confiança estatística adotado pela área (1,65 ≈ 95% em uma distribuição normal).
