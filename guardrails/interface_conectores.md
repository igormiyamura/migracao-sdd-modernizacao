# Interface de conectores

Referência consultada pelo `implementador-python` sempre que uma etapa lê uma entrada ou escreve uma saída, e pelo `planejador` ao mapear `entradas`/`saidas` do `discovery.yaml` para tarefas de implementação.

## Por que existe

O time já tem um toolkit de conectores para essas cinco fontes, hoje embutido dentro de outra biblioteca maior — nesta fase ele não está acessível para inspeção. Em vez de cada processo migrado escrever seu próprio acesso a fswcorp/e-mail/SharePoint/API (código duplicado cinco vezes por processo, e outra vez por analista), esta interface define o contrato estável que o código de negócio depende. Hoje ela é implementada com bibliotecas diretas em `conectores/`; quando o toolkit real for refatorado (etapa 1.5), a implementação por trás da interface é trocada — o código de cada processo migrado não muda uma linha. O mesmo vale para a Fase 2: trocar a implementação por uma versão AWS (S3, SES, etc.) fica atrás da mesma interface.

**Regra de guardrail**: código de negócio (`logica.py`, `fluxo.py`) nunca importa `pywin32`, `smbclient`, `O365`, `msal` ou `requests` diretamente — sempre importa de `conectores`.

## As cinco interfaces

Cada uma tem uma função `ler(...)` e/ou `escrever(...)` — a assinatura exata vive em `conectores/base.py`, este documento descreve o contrato em prosa:

- **`conectores.fswcorp`**: lê/escreve arquivo em caminho de rede local (`\\fswcorp\...`). `ler_arquivo(caminho) -> DataFrame | bytes`, `escrever_arquivo(caminho, conteudo)`.
- **`conectores.email`**: envia e-mail com anexo opcional; lê anexos de uma caixa/pasta específica por assunto ou remetente. `enviar(destinatarios, assunto, corpo, anexos=[])`, `ler_anexos(pasta, filtro)`.
- **`conectores.sharepoint`**: lê/escreve arquivo numa biblioteca de documentos do SharePoint. `ler_arquivo(site, biblioteca, caminho)`, `escrever_arquivo(site, biblioteca, caminho, conteudo)`.
- **`conectores.api`**: chamada HTTP autenticada a uma API interna, com retry e timeout padronizados. `chamar(endpoint, metodo, payload=None) -> dict`.
- **`conectores.processo_legado`**: lê o output de outro processo (planilha, CSV, parquet) como entrada — trata o caso comum de um processo consumir a saída de outro. `ler_saida(caminho, formato) -> DataFrame`.

Toda função de leitura retorna um `pandas.DataFrame` quando o dado é tabular, ou o tipo nativo (bytes, dict) quando não é — nunca um objeto específico da biblioteca por trás (ex: nunca vaza um objeto do `O365` para o código de negócio).

## Autenticação e segredos

Toda credencial (usuário/senha, client secret, token de API) é resolvida dentro do conector via `keyring`, nunca passada como argumento em texto plano pelo código de negócio. O código de negócio só informa qual credencial usar por um nome lógico (ex: `conectores.email.enviar(..., credencial="mesa_equities")`), nunca o segredo em si.

## Como o pacote chega ao projeto migrado

`conectores/` vive na raiz deste repositório, não dentro de cada execução. O `implementador-python` adiciona `conectores` como dependência editável do `pyproject.toml` do processo (`uv add --editable <caminho-para-conectores>`), nunca copiando os arquivos para dentro de `src/`. Isso mantém uma única cópia — corrigir um conector corrige todos os processos migrados de uma vez, sem precisar tocar em cada um.

## Quando a etapa não se encaixa em nenhuma das cinco

Registrar em `riscos_pontos_atencao` no `discovery.yaml` e tratar como decisão manual no `plano_implementacao.md` — não inventar uma sexta categoria de conector sem alinhar com o dono da iniciativa.
