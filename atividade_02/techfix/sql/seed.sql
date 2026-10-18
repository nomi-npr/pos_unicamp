-- Dados inteiramente fictícios: 12 clientes e 15 OS distribuídas nos 5 status.
-- Execute após schema.sql, no projeto dedicado da atividade.
-- Reexecutar não duplica as OS de exemplo (cliente + equipamento + problema).
begin;
do $$
declare
    item record;
    v_os bigint;
begin
    for item in
        select * from (values
            ('Ana Exemplo','ana@example.invalid','11900000001','Notebook Modelo A','Não liga','Aberto'),
            ('Bruno Exemplo','bruno@example.invalid','11900000002','Desktop Modelo B','Reinicia sozinho','Em análise'),
            ('Carla Exemplo','carla@example.invalid','11900000003','Notebook Modelo C','Tela com falha','Aguardando peça'),
            ('Diego Exemplo','diego@example.invalid','11900000004','Desktop Modelo D','Limpeza preventiva','Concluído'),
            ('Eva Exemplo','eva@example.invalid','11900000005','Notebook Modelo E','Troca de teclado','Entregue'),
            ('Fábio Exemplo','fabio@example.invalid','11900000006','Desktop Modelo F','Sem conexão de rede','Aberto'),
            ('Gabriela Exemplo','gabriela@example.invalid','11900000007','Notebook Modelo G','Bateria não carrega','Em análise'),
            ('Henrique Exemplo','henrique@example.invalid','11900000008','Desktop Modelo H','Fonte com defeito','Aguardando peça'),
            ('Isabela Exemplo','isabela@example.invalid','11900000009','Notebook Modelo I','Atualização do sistema','Concluído'),
            ('João Exemplo','joao@example.invalid','11900000010','Desktop Modelo J','Instalação de memória','Entregue'),
            ('Karina Exemplo','karina@example.invalid','11900000011','Notebook Modelo K','Lentidão no sistema','Aberto'),
            ('Larissa Exemplo','larissa@example.invalid','11900000012','Desktop Modelo L','Saída de vídeo sem sinal','Em análise'),
            ('Ana Exemplo','ana@example.invalid','11900000001','Impressora Modelo A','Não imprime','Aberto'),
            ('Bruno Exemplo','bruno@example.invalid','11900000002','Notebook Modelo B2','Dobradiça quebrada','Aguardando peça'),
            ('Carla Exemplo','carla@example.invalid','11900000003','Monitor Modelo C2','Falha na iluminação','Concluído')
        ) as dados(nome,email,celular,modelo,problema,status)
    loop
        if not exists (
            select 1 from public.ordens_servico os
            join public.clientes c on c.id=os.cliente_id
            where c.email=item.email and os.modelo_computador=item.modelo
                and os.problema_relatado=item.problema
        ) then
            v_os := public.registrar_atendimento(
                item.nome, 'Rua Fictícia, 100, Bairro Exemplo', item.email,
                item.celular, item.modelo, item.problema
            );
            update public.ordens_servico set status=item.status where id=v_os;
        end if;
    end loop;
end;
$$;
commit;
