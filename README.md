# Manchester Coding Simulator

Esta é uma aplicação gráfica interativa para codificação e decodificação de mensagens utilizando o código Manchester (padrão IEEE 802.3).  
O sistema implementa criptografia AES-256, exibição gráfica dos sinais e comunicação entre dois computadores por meio de sockets TCP.

O projeto foi desenvolvido com fins didáticos, principalmente para o estudo de redes digitais, criptografia simétrica e transmissão de dados binários.

## Funcionalidades

- Criptografia e descriptografia AES-256 com chave personalizável
- Codificação Manchester com validação e decodificação
- Visualização gráfica dos sinais codificados com Matplotlib
- Interface gráfica com Tkinter
- Comunicação entre dois hosts pela rede via TCP
- Interface separada para envio (Host A) e recepção (Host B)

## Requisitos

- Python 3.8 ou superior
- Bibliotecas:
  - tkinter
  - matplotlib
  - numpy
  - pycryptodome

## Instalação

1. Clone este repositório:

```bash
git clone https://github.com/seu-usuario/manchester-sim.git
cd manchester-sim
