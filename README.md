# Sistema de Simulação de Codificação de Linha Manchester

Este projeto implementa um sistema completo de simulação de codificação de linha utilizando o algoritmo Manchester com criptografia AES-256, conforme especificado nos requisitos acadêmicos.

## Visão Geral

O sistema simula a transmissão de dados entre dois hosts, aplicando:
- Criptografia AES-256
- Conversão para representação binária (ASCII estendido)
- Codificação de linha Manchester
- Visualização gráfica dos sinais
- Comunicação em rede entre hosts

## Funcionalidades

- **Interface Gráfica**: Permite visualizar todas as etapas do processo
- **Dupla Função**: Opera como Host A (envio) ou Host B (recepção)
- **Criptografia**: Implementa algoritmo AES-256 para segurança
- **Codificação Manchester**: Converte bits em sinais com transição no meio do período
- **Comunicação em Rede**: Permite troca de dados entre computadores diferentes
- **Visualização Gráfica**: Exibe a forma de onda do sinal codificado

## Requisitos

- Python 3.x
- Bibliotecas:
  - tkinter (inclusa na maioria das instalações Python)
  - matplotlib
  - pycryptodome
  - numpy

## Instalação

1. Clone ou baixe este repositório
2. Instale as dependências:

```bash
pip install matplotlib pycryptodome numpy
```

## Como Usar

### Executando o programa

```bash
python manchester_sim.py
```

### Configuração Inicial

Quando o programa iniciar, você deverá escolher o modo de operação:
- **Sim** = Host A (Envio)
- **Não** = Host B (Recepção)

### Para comunicação na mesma máquina (teste)

1. Inicie duas instâncias do programa
2. Configure a primeira como Host B (Recepção)
3. Configure a segunda como Host A (Envio)
4. Use o endereço IP "127.0.0.1" em ambos
5. Copie a chave AES do Host A para o Host B

### Para comunicação entre computadores diferentes

1. Inicie o programa no computador que será o Host B (Recepção)
2. Anote o endereço IP deste computador
3. Inicie o programa no computador que será o Host A (Envio)
4. Configure o Host A com o IP do Host B
5. Copie a chave AES do Host A para o Host B

## Guia Passo a Passo

### Host B (Recepção) - Inicie primeiro

1. Escolha "Não" na caixa de diálogo inicial
2. A interface do Host B será carregada
3. A aplicação começará a aguardar conexões na porta especificada (12345 por padrão)
4. Aguarde até que o Host A se conecte

### Host A (Envio) - Inicie depois

1. Escolha "Sim" na caixa de diálogo inicial
2. A interface do Host A será carregada
3. Digite o endereço IP do Host B
4. Clique em "Conectar"
5. Após conectado, você poderá enviar mensagens

### Sincronização da Chave AES

Para que a criptografia funcione, ambos os hosts devem usar a mesma chave:

1. No Host A:
   - A chave é gerada automaticamente e exibida em formato Base64
   - Clique no botão "Copiar" para copiar a chave

2. No Host B:
   - Cole a chave no campo "Chave (Base64)"
   - Clique em "Definir Chave"

### Enviando Mensagens

1. No Host A:
   - Digite sua mensagem no campo de texto
   - Clique em "Enviar Mensagem"
   - Observe o processo nas diferentes abas

2. No Host B:
   - A mensagem será recebida automaticamente
   - O sistema processará a mensagem através das etapas inversas
   - A mensagem original será exibida

## Princípios Técnicos

### Codificação Manchester

Na codificação Manchester:
- Bit '0': representado por uma transição de baixo para alto (01)
- Bit '1': representado por uma transição de alto para baixo (10)

Benefícios:
- Sincronização automática
- Não possui componente DC
- Fácil detecção de erros

### Criptografia AES-256

O sistema utiliza AES (Advanced Encryption Standard) com chave de 256 bits:
- Chave: 32 bytes (256 bits)
- Modo: CBC (Cipher Block Chaining)
- IV (Vetor de Inicialização): 16 bytes, aleatório
- Formato: Base64 para representação textual

## Estrutura das Abas

O sistema possui cinco abas para visualização do processo:

1. **Texto Original**: Mensagem em formato de texto
2. **Texto Criptografado**: Mensagem após aplicação de AES-256
3. **Binário**: Representação binária da mensagem criptografada
4. **Código Manchester**: Sequência de bits após codificação Manchester
5. **Gráfico**: Visualização da forma de onda do sinal Manchester

## Fluxo Completo dos Dados

### Envio (Host A)
```
Texto Original → Criptografia AES-256 → Conversão para Binário → 
Codificação Manchester → Geração de Gráfico → Transmissão pela Rede
```

### Recepção (Host B)
```
Recepção da Rede → Visualização do Gráfico → Decodificação Manchester → 
Conversão de Binário → Descriptografia AES-256 → Exibição do Texto Original
```

## Solução de Problemas

1. **Erro de conexão**:
   - Verifique se o Host B está em execução e aguardando conexões
   - Confirme se o endereço IP está correto
   - Verifique se a porta não está bloqueada por firewall

2. **Erro de descriptografia**:
   - Certifique-se de que a mesma chave AES está sendo usada em ambos os lados
   - A chave deve ser exatamente igual, incluindo todos os caracteres

3. **Caracteres corrompidos**:
   - O sistema suporta caracteres especiais e acentuados
   - Certifique-se de que a mesma codificação está sendo usada em ambos os lados

4. **Gráfico não exibido**:
   - Verifique se a biblioteca matplotlib está instalada corretamente
   - Alguns ambientes podem requerer configurações adicionais para exibição gráfica

## Extensões Possíveis

- Implementação de detecção e correção de erros
- Suporte a outros algoritmos de codificação de linha
- Interface para salvar/carregar mensagens
- Análise de desempenho (taxa de erros, velocidade)

## Conceitos Teóricos

### Manchester vs. NRZ

Diferentemente de codificações mais simples como NRZ (Non-Return-to-Zero), a codificação Manchester:
- Garante transições regulares, facilitando sincronização
- Não depende de nível absoluto, apenas de transições
- Ocupa o dobro da largura de banda, mas com maior confiabilidade

### Segurança AES-256

AES-256 é considerado extremamente seguro, sendo utilizado para proteção de dados classificados por governos. Pontos importantes:
- 14 rodadas de substituição e permutação
- Resistente a ataques de força bruta mesmo com computação quântica
- O IV garante que mensagens idênticas gerem cifras diferentes

## Referências

- Forouzan, B. A. (2007). Data Communications and Networking.
- Stallings, W. (2016). Cryptography and Network Security: Principles and Practice.
- Documentação do PyCryptodome: https://pycryptodome.readthedocs.io/
- Documentação do Matplotlib: https://matplotlib.org/
