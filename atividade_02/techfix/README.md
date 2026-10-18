# TechFix Informática · Atividade Aula 2

Autora: Naomi Pomella. Sistema acadêmico para uma loja de informática, com duas interfaces que compartilham o mesmo banco Supabase. Use apenas dados fictícios.

Integração verificada em 18/10/2026 com 13 clientes e 17 OS no Supabase. Consulte os [testes e prints da entrega](evidencias/entrega.md). O [Gradio público temporário](https://537b9615f8c8c1d969.gradio.live/) depende do processo local em execução; o [painel Streamlit local](http://127.0.0.1:8502/) exige a conta Auth da equipe.

## O que está implementado

- Cadastro Gradio em `gr.Blocks`, com nome, endereço, e-mail, celular/WhatsApp, modelo do computador e problema apresentado; botões Cadastrar e Limpar.
- Cliente reaproveitado pelo e-mail normalizado e uma nova OS com status `Aberto` a cada envio válido.
- Criação do cliente e da OS na mesma transação: se uma etapa falhar, a outra não fica gravada pela metade.
- Painel com login da equipe, abas Consultar, Cadastrar, Editar / Excluir e Indicadores.
- Filtros literais por nome e e-mail e seleção de status na barra lateral.
- Edição do status e dos dados do cliente, exclusão com confirmação e proteção de clientes com OS vinculadas.
- Métricas para os cinco status, gráfico de barras e exportação do resultado filtrado em CSV.
- Validações no Python e no PostgreSQL, tratamento de falhas e credenciais fora do código.

## Estrutura

```text
atividade_02/
  techfix/
    sql/schema.sql          Tabelas, restrições, índices, trigger, RLS e RPC
    sql/seed.sql            12 clientes fictícios e 15 ordens de serviço
    app_gradio.py           Cadastro de atendimento
    app_streamlit.py        Painel administrativo
    config.py               .env, variáveis de ambiente e secrets
    servicos.py             Validação, acesso ao Supabase, filtros e exportação
    requirements.txt        Dependências Python
    .env.example            Variáveis sem valores reais
    README.md               Instalação, banco e execução
    evidencias/             Estado da entrega e capturas verificadas
    tests/                  Testes Python, Streamlit e PostgreSQL/PGlite
```

## Instalar

Python 3.12. Execute os comandos a partir da raiz `pos_unicamp/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r atividade_02/techfix/requirements.txt
```

As dependências desta atividade ficam em sua própria pasta. O app e os atalhos da raiz continuam apontando para a atividade 01.

## Configurar o Supabase

1. Crie um projeto gratuito dedicado à atividade no [painel Supabase](https://supabase.com/dashboard). Guarde a senha do banco em local seguro.
2. No SQL Editor desse projeto, execute [`sql/schema.sql`](sql/schema.sql) uma vez. O script não apaga tabelas existentes e aborta caso seus nomes já existam; não o execute sobre um projeto de produção.
3. Execute [`sql/seed.sql`](sql/seed.sql) para carregar 12 clientes e 15 OS fictícios. O seed pode ser reexecutado sem duplicar seus exemplos.
4. Em **Authentication → Sign In / Providers**, desative novos cadastros públicos e mantenha login anônimo desativado. Somente a equipe deve ter contas Auth neste projeto.
5. Em **Authentication → Users → Add user**, crie manualmente uma conta da equipe com e-mail e senha e confirmação automática. A conta é usada no login do painel; não grave sua senha no repositório.
6. Em **Project Settings → Data API / API Keys** (ou **Connect**), copie a URL do projeto e a chave pública **anon/publishable**. A aplicação não precisa de `service_role` ou chave secreta.
7. Copie o exemplo e preencha os valores localmente. Não sobrescreva um `.env` que já tenha preenchido:

```bash
cp atividade_02/techfix/.env.example atividade_02/techfix/.env
```

```dotenv
SUPABASE_URL=https://SEU-PROJETO.supabase.co
SUPABASE_PUBLIC_KEY=SUA-CHAVE-PUBLICA-ANON-OU-PUBLISHABLE
```

O `.env` é carregado com python-dotenv, sem substituir variáveis já definidas no ambiente. O Streamlit também aceita as mesmas duas entradas em `.streamlit/secrets.toml`. As interfaces priorizam `SUPABASE_PUBLIC_KEY`; por compatibilidade, aceitam uma chave pública em `SUPABASE_KEY`. Chaves secretas/service_role são recusadas nas interfaces. Se você mantiver uma chave administrativa em `SUPABASE_KEY` para manutenção local, preencha também `SUPABASE_PUBLIC_KEY`. Todos os `.env` e `secrets.toml` estão no `.gitignore`. Nunca faça commit desses arquivos.

### Acesso ao banco

As tabelas têm RLS habilitada. Visitantes sem login não podem listar, editar ou excluir registros. O cadastro público do Gradio usa apenas a função `registrar_atendimento`, que retorna o número da nova OS e não divulga cadastros existentes. A função tem `search_path` vazio, nomes qualificados e não sobrescreve os dados do cliente reaproveitado.

Usuários autenticados da equipe podem gerenciar clientes e OS. Por isso, o projeto deve ter criação pública de contas desativada e somente usuários de equipe criados manualmente. As sessões do painel são separadas por visitante.

O cadastro público é destinado aos testes da atividade. Compartilhe o link temporário apenas para esses testes e encerre o Gradio depois. Para uso real seriam necessários controles adicionais de acesso no atendimento e proteção contra abuso.

## Executar o Gradio

```bash
python -m atividade_02.techfix.app_gradio
```

Abra <http://127.0.0.1:7861>. Por padrão o lançamento usa `share=True`, exibindo também um link temporário `gradio.live` no terminal para abrir pelo celular. Esse endereço só funciona enquanto o processo estiver em execução. O endereço muda ao reiniciar e o túnel pode expirar.

Para conferir apenas localmente:

```bash
TECHFIX_SHARE=false python -m atividade_02.techfix.app_gradio
```

O botão **Limpar** esvazia os seis campos e o resultado. Cada clique válido em **Cadastrar** cria outra OS, inclusive para um cliente existente; só clique novamente se quiser abrir um novo atendimento.

## Executar o painel Streamlit

```bash
python -m streamlit run atividade_02/techfix/app_streamlit.py --server.port 8502
```

Abra <http://localhost:8502> e entre com a conta da equipe criada no Supabase Auth.

As abas de edição mostram todos os registros. Os filtros da barra lateral afetam a consulta, o CSV e os indicadores. A seleção vazia de status significa que nenhum status foi selecionado e retorna uma consulta vazia. **Atualizar dados** recarrega as informações do Supabase.

Para excluir, selecione a OS ou o cliente e marque a confirmação que identifica o registro. O botão permanece desabilitado até a confirmação. A FK usa `ON DELETE RESTRICT`: exclua primeiro as OS de um cliente para depois poder removê-lo. Isso evita apagar seu histórico acidentalmente.

O CSV usa UTF-8 com BOM para preservar acentos em planilhas. Textos que começam com caracteres de fórmula recebem um apóstrofo no arquivo exportado; o conteúdo original no banco permanece igual.

## Testes

Testes Python, com transporte HTTP simulado para a biblioteca oficial e `AppTest` para o painel:

```bash
python -m unittest discover -s atividade_02/techfix/tests -v
```

Teste do SQL em PostgreSQL embarcado, sem Docker (Node.js 20 ou superior):

```bash
npm install --prefix atividade_02/techfix/tests
npm test --prefix atividade_02/techfix/tests
```

O teste SQL usa PGlite para executar o mesmo `schema.sql`, incluindo PL/pgSQL, restrições, trigger, grants e políticas RLS. Verifica reuso de cliente, atomicidade, criação das OS, acesso anônimo restrito, CRUD da equipe, exclusão protegida e seed sem duplicação. O ambiente é local e descartável; esses testes não substituem a verificação do projeto Supabase remoto e de seu login Auth.

Para verificar a integração real depois de configurar o projeto:

1. Cadastre uma OS no Gradio com `ana@example.invalid` e confira o número retornado.
2. Cadastre outro equipamento com o mesmo e-mail e confira no Table Editor: um cliente, duas OS vinculadas. Se usar o seed, Ana já existe e terá atendimentos anteriores.
3. Entre no painel, confira a consulta e teste os filtros de nome, e-mail e status.
4. Altere o status, edite endereço/e-mail/celular e confira a mudança no Table Editor.
5. Marque a confirmação e exclua uma OS fictícia. Tente excluir um cliente com OS e confira a recusa amigável; remova suas OS antes de excluir esse cliente.
6. Confira as métricas, o gráfico e o CSV filtrado.
7. Abra o link temporário do Gradio no celular, faça um cadastro e capture a confirmação.

## Referências

- [Supabase Python](https://supabase.com/docs/reference/python/introduction), [funções PostgreSQL via RPC](https://supabase.com/docs/reference/python/rpc) e [autenticação por senha](https://supabase.com/docs/reference/python/auth-signinwithpassword).
- [Supabase Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security).
- [PGlite](https://github.com/electric-sql/pglite) para os testes SQL locais.

O estado da entrega e as evidências ficam em [`evidencias/entrega.md`](evidencias/entrega.md).
