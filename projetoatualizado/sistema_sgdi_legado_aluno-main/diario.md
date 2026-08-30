# Diário de Desenvolvimento - SGDI

## Etapa 1 - Análise do sistema

Primeiramente, foi analisado o sistema existente para entender como as demandas eram cadastradas, armazenadas e apresentadas.

Também verifiquei a estrutura do projeto e os arquivos envolvidos no cadastro e na edição das demandas.

## Etapa 2 - Definição dos requisitos

A partir dos requisitos definidos para a nova versão, foi estabelecido que cada demanda deveria possuir uma prioridade e um responsável.

Para a prioridade, foram escolhidas três opções:

- BAIXA
- MÉDIA
- ALTA

Também foi definido que o responsável deveria ser informado já no momento da criação da demanda.

## Etapa 3 - Alteração do banco de dados

Foi necessário alterar a estrutura utilizada para armazenar as demandas para incluir os novos dados.

Foram adicionados os campos necessários para armazenar a prioridade e o responsável.

Também foi ajustado o processo de inicialização do banco para criar a estrutura atualizada.

## Etapa 4 - Alteração do cadastro

No formulário de criação da demanda, foi incluido os campos de prioridade e responsável.

O responsável passou a ser obrigatório no cadastro, evitando que uma demanda seja criada sem uma pessoa definida para realizá-la.

## Etapa 5 - Alteração da edição

Na edição da demanda, mantive a possibilidade de modificar as informações cadastradas.

Também foi implementada a alteração do responsável. A regra definida para o projeto permite que qualquer pessoa com acesso ao sistema possa fazer essa alteração a qualquer momento.

## Etapa 6 - Organização das demandas

A visualização das demandas foi ajustada para considerar a prioridade.

Dessa forma, as demandas de maior prioridade ficam mais fáceis de identificar na utilização do sistema.

## Etapa 7 - Validação

Depois das alterações, realizei testes no cadastro e na edição das demandas.

Foi verificado principalmente:

- se era possível criar uma demanda;
- se a prioridade era salva corretamente;
- se o responsável era salvo;
- se o responsável aparecia na visualização;
- se era possível alterar o responsável;
- se as prioridades funcionavam corretamente.

## Etapa 8 - Recursos que ficaram fora desta versão

Durante a definição dos requisitos, também foi analisada a possibilidade de utilizar categorias, prazo para solução e alertas.

Esses recursos não foram implementados nesta versão, pois foi definido que não seriam necessários no momento.

## Resultado

Após as alterações, o sistema passou a permitir um controle mais organizado das demandas, principalmente em relação à prioridade e à definição dos responsáveis.

As funcionalidades implementadas foram testadas no fluxo de criação, visualização e edição das demandas.
