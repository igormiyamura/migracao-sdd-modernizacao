# Estado e retomada de execução

Referência consultada sempre que uma migração é criada, atualizada entre estágios, ou retomada.

## Por que UUID curto

Um analista costuma ter várias migrações em andamento ao mesmo tempo. O UUID isola cada execução (memória, artefatos, estado) da máquina do analista, sem depender de o analista lembrar em que estágio parou. 8 caracteres (os 8 primeiros de um UUID v4) bastam para não colidir dentro do volume de processos de uma mesa e ficam curtos o suficiente para aparecer no nome da pasta e serem digitados de cabeça.

## `estado.yaml`

Vive em `.sdd/estado.yaml` dentro da pasta da execução. É a fonte de verdade de onde a migração está — todo agente que conclui um estágio grava sua saída aqui antes de encerrar.

```yaml
uuid: "3f2b9a10"
processo:
  nome: "Consolidação de Carteira Equities"
  mesa: "Equities - Risco de Mercado"
  dono: "nome do dono do processo"
  frequencia: "diaria"
  criticidade: "alta"
origem:
  stack: alteryx              # excel | excel_vba | alteryx | csharp | python_legado
analista: "email do analista"
criado_em: "2026-08-19T10:00:00-03:00"
atualizado_em: "2026-08-19T14:32:00-03:00"
estagio_atual: especificacao

estagios:
  discovery:          {status: concluido,    artefato: "entrada/discovery.yaml"}
  doc_negocio:         {status: concluido,    artefato: "especificacao/doc_negocio.md"}
  doc_tecnico:         {status: concluido,    artefato: "especificacao/doc_tecnico.md"}
  grafo:               {status: em_andamento, artefato: "especificacao/grafo_processo.mmd"}
  plano:               {status: pendente}
  aprovacao_plano:     {status: pendente}
  implementacao:       {status: pendente}
  homologacao:         {status: pendente}
  revisao_tecnica:     {status: pendente}

revisao_tecnica:
  obrigatoria: true
  aprovado_por: null
  aprovado_em: null
```

`status` de cada estágio é um destes três: `pendente`, `em_andamento`, `concluido`. Um estágio só entra em `concluido` depois que seu artefato de saída existe no caminho declarado — nunca marque conclusão sem o arquivo correspondente no disco.

A ordem dos estágios é fixa: `discovery → doc_negocio → doc_tecnico → grafo → plano → aprovacao_plano → implementacao → homologacao → revisao_tecnica`. `aprovacao_plano` é um gate manual (ver `.claude/agents/planejador.md`) — não avance para `implementacao` sem ele estar `concluido`.

## `.sdd/memoria/`

Guarda snapshots de contexto que um agente de uma etapa posterior pode precisar sem reprocessar tudo desde o início: o resumo da entrevista de discovery, decisões tomadas com o analista durante o planejamento, divergências já resolvidas em rodadas anteriores de homologação. Cada agente decide o que vale a pena registrar aqui seguindo uma régua simples: "se eu (ou outro agente) reabrir essa execução daqui a duas semanas, o que preciso ler para não repetir uma pergunta já respondida?".

## Retomando uma execução

Ao ser acionado, o orquestrador (`SKILL.md`) sempre pergunta primeiro se é uma migração nova ou uma continuação. Para continuar:

1. Localizar a pasta pelo UUID informado ou, se o analista não lembra o UUID, pelo nome do processo em `migracoes/indice.yaml` (ver abaixo).
2. Ler `.sdd/estado.yaml` e `.sdd/memoria/`.
3. Anunciar ao analista em que estágio a execução parou e o que já foi produzido, antes de continuar — nunca retomar em silêncio.
4. Seguir a partir do primeiro estágio com `status: pendente` ou `em_andamento`.

## `migracoes/indice.yaml`

Vive na raiz do repositório, não dentro de uma execução específica. É o índice agregado de todas as migrações — o que dá visibilidade de progresso entre analistas e para a liderança da área, sem precisar abrir cada `estado.yaml` individualmente.

```yaml
- uuid: "3f2b9a10"
  processo: "Consolidação de Carteira Equities"
  slug: "consolidacao-carteira-equities"
  analista: "email do analista"
  estagio_atual: especificacao
  atualizado_em: "2026-08-19T14:32:00-03:00"
```

Todo agente que atualiza `estado.yaml` também atualiza (ou cria) a entrada correspondente aqui — é uma cópia derivada para leitura rápida, nunca a fonte de verdade de uma execução individual. Se os dois divergirem, `estado.yaml` da própria execução manda.

Este arquivo é o ponto de partida natural para sincronizar visibilidade entre analistas (ex: copiar para uma pasta compartilhada de rede ou SharePoint) — a sincronização em si ainda não está automatizada nesta fase, mas o formato já foi desenhado para isso.
