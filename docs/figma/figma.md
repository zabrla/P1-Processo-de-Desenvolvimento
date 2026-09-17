1. Visão Geral

O sistema web fornece uma interface minimalista e intuitiva para troca de mensagens e gerenciamento seguro do histórico de conversas. A documentação mapeia as interações do usuário na interface desde o acesso inicial (Login/Cadastro) até a manipulação de ações de segurança (Criptografar/Descriptografar) e a consulta de registros (Histórico/Logs).

1.1 Objetivos da Documentação

- Mapear o ciclo de vida completo da sessão do usuário e o fluxo das telas projetadas no Figma.

- Especificar as regras de transição da interface de chat e as ações de importação/exportação de conversas.

- Formalizar o acesso à rastreabilidade visual (Histórico e Logs).

2. Atores e Responsabilidades

- Usuário (Humano / Cliente): Responsável por realizar autenticação/cadastro, interagir na interface de chat, solicitar o salvamento ou criptografia das mensagens, importar arquivos locais e navegar pelos menus de Histórico e Logs.

- Sistema (Aplicação Web): Responsável por gerenciar a sessão ativa, alternar os estados da interface de chat (botões de ação), processar as requisições de segurança (criptografia/descriptografia) e registrar/exibir as trilhas de auditoria.

3. Especificação dos Fluxos de Atividade

3.1 Autenticação e Cadastro Inicial

O fluxo de entrada no sistema é dividido em duas telas principais, permitindo o acesso de usuários existentes ou a criação de novas contas.

Fluxo de Login:

1. O Usuário acessa a primeira tela da aplicação.

2. Insere suas credenciais nos campos indicados por ícones (Usuário e Senha).

3. Clica no botão "Acessar" para entrar no sistema.

4. Caso não possua conta, o usuário pode clicar no link "Cadastre-se" para ser redirecionado.

Fluxo de Cadastro:

1. O Usuário é apresentado ao formulário "SIGN UP".

3. Preenche os campos obrigatórios representados visualmente: Nome de Usuário, Email (@), Senha (Cadeado) e Confirmação de Senha (Cadeado com +).

4. Clica no botão de ação para finalizar o registro.

5. Caso já tenha registro, o usuário pode clicar no link "Entrar" para ser redirecionado.

3.2 Processos Principais (Home & Chat)

Após a autenticação, o usuário é direcionado para a in terface principal. A tela é composta por uma barra lateral de navegação (identificando o usuário ativo, ex: "Usuário Y") e uma área central de chat.

Fluxo 1: Chat, Salvamento e Criptografia:

1. O sistema exibe o cabeçalho com o contato destinatário (ex: emailusuariox@email.com).

2. O usuário interage com o campo central "Escreva sua mensagem...".

3. Para gerenciar a conversa atual, o usuário dispõe de dois botões de ação primários na parte inferior: "Salvar" (para registrar o progresso) e "Criptografar" (para acionar o processo de segurança/exportação da conversa).

Fluxo 2: Importação e Descriptografia:

1. Na mesma estrutura da Home, caso o usuário precise recuperar um histórico protegido, a interface adapta seus botões de ação.

2. O usuário clica em "Importar" para buscar o arquivo criptografado no dispositivo local.

3. Com o arquivo carregado, o usuário clica no botão "Descriptografar" para revelar o conteúdo no bloco de texto central da interface.

3.3 Consulta de Dados e Auditoria

A barra lateral fornece acesso rápido às áreas de consulta do sistema, permitindo visualizar mensagens passadas e ações de sistema.

Fluxo 3: Visualização do Histórico:

1. O usuário clica no botão "Histórico" na barra lateral.

2. O menu lateral mantém o botão em destaque (estado ativo).

3. A área central exibe o registro da troca de mensagens com balões de diálogo diferenciados por cor (mensagens enviadas e recebidas).

4. O usuário pode retornar ao chat ativo clicando na ação superior "< Voltar".

Fluxo 4: Visualização de Logs:

1. O usuário clica no botão "Logs" na barra lateral.

2. O menu lateral mantém o botão em destaque.

3. O sistema exibe uma lista estruturada de balões sequenciais representando os registros técnicos, operacionais e de segurança realizados pelo usuário.

4. O usuário pode retornar à tela anterior clicando em "< Voltar".

3.4 Encerramento da Sessão

1. O Usuário localiza e clica no botão "Sair" posicionado ao final da barra lateral esquerda.

2. O Sistema encerra a sessão ativa de forma segura.

3. O Sistema redireciona a interface de volta para a tela inicial de Login.