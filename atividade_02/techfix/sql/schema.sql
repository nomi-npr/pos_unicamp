-- TechFix Informática: executar uma vez no SQL Editor de um projeto dedicado.
-- Todo o script é uma transação: uma falha não deixa o esquema pela metade.
begin;

-- Um cliente pode ter várias ordens. E-mail normalizado é a chave de reuso.
create table public.clientes (
    id bigint generated always as identity primary key,
    nome text not null check (length(btrim(nome)) between 1 and 120),
    endereco text not null check (length(btrim(endereco)) between 1 and 250),
    email text not null unique check (
        length(email) <= 254 and email = lower(btrim(email))
        and email ~ '^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$'
    ),
    celular_whatsapp text not null check (celular_whatsapp ~ '^[0-9]{10,13}$'),
    data_cadastro timestamptz not null default now()
);

-- RESTRICT protege o histórico: um cliente só pode ser excluído sem OS vinculadas.
create table public.ordens_servico (
    id bigint generated always as identity primary key,
    cliente_id bigint not null references public.clientes(id) on delete restrict,
    modelo_computador text not null check (length(btrim(modelo_computador)) between 1 and 150),
    problema_relatado text not null check (length(btrim(problema_relatado)) between 1 and 4000),
    status text not null default 'Aberto' check (
        status in ('Aberto', 'Em análise', 'Aguardando peça', 'Concluído', 'Entregue')
    ),
    data_abertura timestamptz not null default now(),
    data_atualizacao timestamptz not null default now()
);

-- Índices para relacionamento, consultas por status e ordenação por data.
create index ordens_cliente_idx on public.ordens_servico(cliente_id);
create index ordens_status_idx on public.ordens_servico(status);
create index ordens_abertura_idx on public.ordens_servico(data_abertura desc);

-- A data de atualização é mantida no banco, inclusive em alterações externas.
create function public.techfix_atualizar_data()
returns trigger language plpgsql set search_path = '' as $$
begin
    new.data_atualizacao := clock_timestamp();
    return new;
end;
$$;
create trigger ordens_atualizar_data
before update on public.ordens_servico
for each row execute function public.techfix_atualizar_data();
revoke all on function public.techfix_atualizar_data() from public;

-- RLS: visitantes não consultam nem alteram tabelas. A equipe entra pelo Auth.
-- No painel Supabase, desative novos cadastros públicos de usuários Auth e
-- crie manualmente apenas as contas da equipe (README, configuração do banco).
alter table public.clientes enable row level security;
alter table public.ordens_servico enable row level security;
revoke all on public.clientes, public.ordens_servico from anon, authenticated;
grant usage on schema public to anon, authenticated;
grant select, insert, update, delete on public.clientes, public.ordens_servico to authenticated;
grant usage, select on sequence public.clientes_id_seq, public.ordens_servico_id_seq to authenticated;
create policy clientes_equipe on public.clientes
    for all to authenticated using (true) with check (true);
create policy ordens_equipe on public.ordens_servico
    for all to authenticated using (true) with check (true);

-- Única operação pública: cadastrar um atendimento, sem expor dados existentes.
-- SECURITY DEFINER usa nomes qualificados e search_path vazio.
-- O UPSERT bloqueia o cliente em conflito e devolve seu id sem sobrescrever
-- nome/endereço/telefone. Cadastro do cliente + OS é atômico (uma transação).
create function public.registrar_atendimento(
    p_nome text, p_endereco text, p_email text, p_celular_whatsapp text,
    p_modelo_computador text, p_problema_relatado text
)
returns bigint language plpgsql security definer set search_path = '' as $$
declare
    v_cliente_id bigint;
    v_os_id bigint;
begin
    insert into public.clientes (nome, endereco, email, celular_whatsapp)
    values (btrim(p_nome), btrim(p_endereco), lower(btrim(p_email)), btrim(p_celular_whatsapp))
    on conflict (email) do update set email = excluded.email
    returning id into v_cliente_id;

    insert into public.ordens_servico (cliente_id, modelo_computador, problema_relatado, status)
    values (v_cliente_id, btrim(p_modelo_computador), btrim(p_problema_relatado), 'Aberto')
    returning id into v_os_id;
    return v_os_id;
end;
$$;
revoke all on function public.registrar_atendimento(text,text,text,text,text,text) from public;
grant execute on function public.registrar_atendimento(text,text,text,text,text,text) to anon, authenticated;

-- Atualiza o catálogo da API REST após a criação das tabelas e da função.
notify pgrst, 'reload schema';
commit;
