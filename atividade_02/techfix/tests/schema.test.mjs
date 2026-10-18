import assert from 'node:assert/strict';
import fs from 'node:fs/promises';

// PGLITE_MODULE permite usar uma instalação temporária sem adicionar node_modules ao repo.
const { PGlite } = await import(process.env.PGLITE_MODULE || '@electric-sql/pglite');
const db = new PGlite();
let grupos = 0;
const ok = mensagem => { grupos++; console.log(`ok ${grupos} - ${mensagem}`); };
const valor = async sql => Object.values((await db.query(sql)).rows[0])[0];
async function falha(acao, codigo) {
  const codigos = Array.isArray(codigo) ? codigo : [codigo];
  await assert.rejects(acao, erro => codigos.includes(erro.code));
}
const registrar = async (email, modelo='Notebook Exemplo', nome='Ana Exemplo') => {
  const resposta = await db.query(
    'select public.registrar_atendimento($1,$2,$3,$4,$5,$6) as id',
    [nome,'Rua Fictícia, 100',email,'11900000001',modelo,'Não liga (teste fictício)'],
  );
  return Number(resposta.rows[0].id);
};

try {
  // Roles equivalentes às usadas pela API Supabase; nenhum dado remoto é acessado.
  await db.exec('create role anon; create role authenticated;');
  await db.exec(await fs.readFile(new URL('../sql/schema.sql', import.meta.url),'utf8'));
  assert.equal(await valor("select count(*)::int from pg_class where relname in ('clientes','ordens_servico') and relrowsecurity"),2);
  ok('schema executa em PostgreSQL e RLS está ativa nas duas tabelas');

  await db.exec('set role anon');
  for (const tabela of ['clientes','ordens_servico']) {
    await falha(()=>db.query(`select * from public.${tabela}`),'42501');
    await falha(()=>db.query(`delete from public.${tabela}`),'42501');
  }
  const primeira = await registrar('ANA@EXAMPLE.INVALID');
  const segunda = await registrar('ana@example.invalid','Outro equipamento','Nome que não deve substituir o original');
  assert.notEqual(primeira,segunda);
  ok('visitante cadastra via RPC, mas não consulta nem exclui tabelas');

  await db.exec('reset role');
  assert.equal(await valor('select count(*)::int from public.clientes'),1);
  assert.equal(await valor('select count(*)::int from public.ordens_servico'),2);
  assert.equal(await valor('select nome from public.clientes'),'Ana Exemplo');
  assert.equal(await valor('select email from public.clientes'),'ana@example.invalid');
  assert.equal(await valor("select count(*)::int from public.ordens_servico where status='Aberto'"),2);
  ok('e-mail normalizado reaproveita cliente e cada envio cria uma nova OS Aberto');

  await falha(()=>registrar('rollback@example.invalid',''),'23514');
  assert.equal(await valor("select count(*)::int from public.clientes where email='rollback@example.invalid'"),0);
  ok('falha ao criar OS desfaz também o cadastro do novo cliente');

  await db.exec('set role authenticated');
  assert.equal(await valor('select count(*)::int from public.clientes'),1);
  await falha(()=>db.query("insert into public.clientes(nome,endereco,email,celular_whatsapp) values ('Duplicado','Rua X','ana@example.invalid','11900000002')"),'23505');
  for (const [email, celular] of [['invalido','11900000001'],['valido@example.invalid','(11)900000001'],['MAIUSCULA@EXAMPLE.INVALID','11900000001']]) {
    await falha(()=>db.query('insert into public.clientes(nome,endereco,email,celular_whatsapp) values ($1,$2,$3,$4)', ['Teste','Rua X',email,celular]),'23514');
  }
  await falha(()=>db.query("insert into public.ordens_servico(cliente_id,modelo_computador,problema_relatado) values (999,'Notebook','Teste')"),'23503');
  await falha(()=>db.query("update public.ordens_servico set status='Inválido' where id=$1",[primeira]),'23514');
  ok('UNIQUE, e-mail, celular, FK e status inválido são rejeitados pelo banco');

  const antes = (await db.query('select data_atualizacao from public.ordens_servico where id=$1',[primeira])).rows[0].data_atualizacao;
  for (const status of ['Aberto','Em análise','Aguardando peça','Concluído','Entregue']) {
    await db.query('update public.ordens_servico set status=$1 where id=$2',[status,primeira]);
  }
  const depois = (await db.query('select status,data_atualizacao from public.ordens_servico where id=$1',[primeira])).rows[0];
  assert.equal(depois.status,'Entregue');
  assert.ok(new Date(depois.data_atualizacao)>=new Date(antes));
  await db.query("update public.clientes set endereco='Rua Atualizada, 20', email='atualizado@example.invalid', celular_whatsapp='11900000009' where email='ana@example.invalid'");
  assert.equal(await valor('select email from public.clientes'),'atualizado@example.invalid');
  ok('equipe consulta e edita dados; trigger atualiza data da OS');

  await falha(()=>db.query('delete from public.clientes'),['23503','23001']);
  assert.equal(await valor('select count(*)::int from public.clientes'),1);
  await db.query('delete from public.ordens_servico where id=$1',[primeira]);
  assert.equal(await valor('select count(*)::int from public.ordens_servico'),1);
  await db.query('delete from public.ordens_servico where id=$1',[segunda]);
  await db.query('delete from public.clientes');
  assert.equal(await valor('select count(*)::int from public.clientes'),0);
  ok('RESTRICT preserva cliente com OS; exclusão de OS e de cliente sem vínculos funciona');

  await db.exec('reset role');
  const seed = await fs.readFile(new URL('../sql/seed.sql', import.meta.url),'utf8');
  await db.exec(seed);
  assert.equal(await valor('select count(*)::int from public.clientes'),12);
  assert.equal(await valor('select count(*)::int from public.ordens_servico'),15);
  assert.equal(await valor('select count(distinct status)::int from public.ordens_servico'),5);
  await db.exec(seed);
  assert.equal(await valor('select count(*)::int from public.clientes'),12);
  assert.equal(await valor('select count(*)::int from public.ordens_servico'),15);
  ok('seed cria 12 clientes, 15 OS e cinco status sem duplicar na reexecução');
  console.log(`${grupos} grupos SQL aprovados (PostgreSQL/PGlite local).`);
} finally {
  await db.close();
}
