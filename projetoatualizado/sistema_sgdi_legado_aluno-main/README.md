# SGDI - Sistema de Gerenciamento de Demandas

## 1. Sobre o projeto

O SGDI (Sistema de Gerenciamento de Demandas) foi desenvolvido para facilitar o cadastro e o acompanhamento de demandas dentro de uma equipe.

A ideia principal é centralizar as demandas em um único sistema, permitindo visualizar o que precisa ser feito, qual é a prioridade e quem é o responsável por cada atividade.

## 2. Objetivo

O objetivo do sistema é permitir que uma equipe consiga:

- cadastrar novas demandas;
- definir a prioridade de cada demanda;
- informar o responsável no momento do cadastro;
- visualizar as demandas cadastradas;
- editar informações de uma demanda;
- alterar o responsável por uma demanda quando necessário;
- organizar as demandas de acordo com sua prioridade.

Neste momento, o sistema não possui categorias, prazo de resolução ou alertas de vencimento, pois esses recursos não fazem parte dos requisitos atuais.

## 3. Regras definidas para as demandas

### Prioridade

Foram definidas três opções de prioridade:

- **ALTA:** utilizada para demandas urgentes ou que possuem maior impacto.
- **MÉDIA:** utilizada para demandas importantes, mas que não precisam ser tratadas imediatamente.
- **BAIXA:** utilizada para demandas que podem ser resolvidas posteriormente.

As demandas são apresentadas considerando a prioridade, facilitando a identificação das atividades mais importantes.

### Responsável

O responsável é informado no momento em que a demanda é criada.

Depois do cadastro, qualquer pessoa que tenha acesso ao sistema pode editar a demanda e alterar o responsável. Essa regra foi adotada para permitir que a equipe redistribua as atividades conforme a necessidade.

### Categorias

Não foi implementada separação por categorias, pois esse recurso não é necessário para a versão atual do sistema.

### Prazo e alertas

Não foi implementado prazo para resolução das demandas e, consequentemente, também não existem alertas de vencimento nesta versão.

## 4. Funcionamento

O fluxo básico do sistema é:

1. Acessar o sistema.
2. Criar uma nova demanda.
3. Informar os dados solicitados.
4. Selecionar a prioridade.
5. Informar o responsável.
6. Salvar a demanda.
7. Visualizar a demanda na lista.
8. Editar a demanda quando for necessário alterar alguma informação, inclusive o responsável.

## 5. Estrutura do projeto

A aplicação possui a estrutura necessária para executar o sistema web e armazenar as informações das demandas.

Os principais elementos do projeto são:

- aplicação responsável pelas rotas e regras do sistema;
- banco de dados utilizado para armazenar as demandas;
- arquivos de configuração e dependências;
- arquivos da interface;
- arquivos de inicialização do banco de dados.

## 6. Banco de dados

O banco de dados armazena as informações das demandas cadastradas.

Entre os dados utilizados estão as informações da demanda, sua prioridade e o responsável definido.

A estrutura foi ajustada para suportar os novos requisitos de prioridade e responsável.

## 7. Como executar

Primeiro, é necessário ter o Python instalado.

Com o projeto aberto no VS Code, abrir o terminal na pasta do projeto e executar:

```bash
python init_db.py
```

Depois, iniciar a aplicação:

```bash
python app.py
```

Após iniciar o servidor, acessar o endereço informado pelo Flask no terminal, normalmente:

```text
http://127.0.0.1:5000
```

## 8. Alterações realizadas nesta versão

Nesta versão foram realizadas as seguintes alterações:

- criação do campo de prioridade;
- criação das opções BAIXA, MÉDIA e ALTA;
- inclusão do responsável no cadastro da demanda;
- obrigatoriedade de informar o responsável ao criar uma demanda;
- possibilidade de alterar o responsável posteriormente;
- organização da visualização das demandas por prioridade;
- atualização do banco de dados para armazenar os novos campos;
- ajustes na interface para apresentar essas informações.

## 9. Testes realizados

Foram realizados testes para verificar:

- criação de uma demanda;
- cadastro da prioridade;
- cadastro do responsável;
- visualização da prioridade e do responsável;
- edição de uma demanda;
- alteração do responsável;
- funcionamento das diferentes prioridades;
- inicialização do banco de dados;
- execução da aplicação.

Os testes foram feitos para verificar se as novas regras estavam funcionando corretamente no fluxo de cadastro e edição.

## 10. Conclusão

Com as alterações realizadas, o sistema passou a atender aos requisitos definidos para o gerenciamento das demandas.

A utilização das prioridades permite identificar mais facilmente o que deve ser tratado primeiro, enquanto a definição do responsável no cadastro deixa claro quem ficou encarregado pela demanda.

A possibilidade de alterar o responsável posteriormente também permite que a equipe faça ajustes na distribuição das atividades conforme necessário.

Os recursos de categorias, prazos e alertas não foram adicionados nesta versão porque não fazem parte dos requisitos atuais do sistema.
