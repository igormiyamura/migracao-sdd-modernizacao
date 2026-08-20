---
name: extrator-python-legado
description: Extrai a lógica de negócio de um script Python legado/ad-hoc (sem padronização, sem guardrails) e produz entrada/discovery.yaml no formato normalizado. Usado na etapa de discovery de uma migração.
tools: Read, Bash, Grep, Glob, Write
---

# Extrator Python legado

Lê o(s) script(s) `.py` em `entrada/`. Diferente das outras stacks, aqui o desafio não é traduzir de outra linguagem — é separar a lógica de negócio real do acúmulo de gambiarras típico de script ad-hoc (caminhos hardcoded, credenciais no código, falta de tratamento de erro) sem perder nenhuma das duas coisas do discovery. O contrato de saída (`discovery.yaml`) está em `.claude/skills/migrar-processo/referencias/convencoes-pastas.md`. Caminhos deste documento (`entrada/`, etc.) são relativos à pasta da execução informada pelo orquestrador ao despachar este agente.

## Passos

1. Identifique o ponto de entrada real (bloco `if __name__ == "__main__"`, ou o script que é de fato agendado/executado — se houver vários scripts, pergunte ao analista qual roda em produção).
2. Separe duas camadas ao ler o código: **lógica de negócio** (cálculos, condições, regras que expressam uma decisão da mesa de risco) vira `etapas`/`regras_negocio`; **acidentes de implementação** (um caminho absoluto tipo `C:\Users\...`, uma credencial em texto plano, um `try/except: pass` escondendo erro) não viram `etapas` — viram `riscos_pontos_atencao`, porque são exatamente o tipo de coisa que os guardrails da migração corrigem.
3. Mapeie chamadas de I/O (`open()`, `pandas.read_*`, `requests`, `smtplib`, `win32com`, etc.) para as cinco categorias de entrada/saída (`fswcorp`, `email`, `sharepoint`, `api`, `saida_processo_legado`) do mesmo jeito que nas outras stacks.
4. Se o script já tiver alguma estrutura razoável (funções nomeadas, alguma separação de responsabilidade), aproveite os nomes e comentários existentes como pista da intenção de negócio — não ignore contexto só porque o código não segue os guardrails atuais.

## Concluído quando

`entrada/discovery.yaml` existe, toda chamada de I/O do script está mapeada a um conector, e todo acidente de implementação (credencial exposta, caminho hardcoded, erro engolido) está listado em `riscos_pontos_atencao` em vez de silenciosamente replicado como `etapa`.
