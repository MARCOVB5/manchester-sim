import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import socket
import json
import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import numpy as np

class ManchesterCodingApp:
    def __init__(self, root, is_sender=True):
        self.root = root
        self.is_sender = is_sender
        
        if is_sender:
            self.root.title("Manchester Coding - Host A (Envio)")
        else:
            self.root.title("Manchester Coding - Host B (Recepção)")
        
        self.root.geometry("1200x900")
        
        # Socket configurations
        self.socket = None
        self.client_socket = None
        self.host = '127.0.0.1'  # Localhost por padrão (será substituído)
        self.port = 12345
        
        # For AES encryption
        self.key = get_random_bytes(32)  # 256 bits
        
        # Para armazenar dados de transmissão
        self.binary_data = ""
        self.manchester_data = []
        self.received_data = {}
        
        # Criar widgets após inicializar as variáveis
        self.create_widgets()
        
        if not is_sender:
            # Iniciar servidor se for o host de recepção
            self.start_server()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de configuração de rede
        net_frame = ttk.LabelFrame(main_frame, text="Configuração de Rede", padding=10)
        net_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(net_frame, text="IP:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.ip_entry = ttk.Entry(net_frame, width=15)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.ip_entry.insert(0, "127.0.0.1")
        
        ttk.Label(net_frame, text="Porta:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.port_entry = ttk.Entry(net_frame, width=6)
        self.port_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        self.port_entry.insert(0, "12345")
        
        if self.is_sender:
            # Host A (Envio)
            self.connect_btn = ttk.Button(net_frame, text="Conectar", command=self.connect_to_receiver)
            self.connect_btn.grid(row=0, column=4, padx=5, pady=5)
            
            # Frame de mensagem
            msg_frame = ttk.LabelFrame(main_frame, text="Mensagem", padding=10)
            msg_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(msg_frame, text="Digite sua mensagem:").pack(anchor=tk.W)
            self.message_text = scrolledtext.ScrolledText(msg_frame, width=80, height=3)
            self.message_text.pack(fill=tk.X, pady=5)
            
            # Botão de envio
            self.send_btn = ttk.Button(msg_frame, text="Enviar Mensagem", command=self.process_and_send)
            self.send_btn.pack(pady=5)
            
            # Chave de criptografia
            key_frame = ttk.LabelFrame(main_frame, text="Chave AES-256", padding=10)
            key_frame.pack(fill=tk.X, pady=5)
            
            self.key_var = tk.StringVar()
            self.key_var.set(base64.b64encode(self.key).decode())
            
            ttk.Label(key_frame, text="Chave (Base64):").pack(side=tk.LEFT)
            key_entry = ttk.Entry(key_frame, textvariable=self.key_var, width=50)
            key_entry.pack(side=tk.LEFT, padx=5)
            
            ttk.Button(key_frame, text="Gerar Nova", command=self.generate_new_key).pack(side=tk.LEFT)
            ttk.Button(key_frame, text="Copiar", command=lambda: self.root.clipboard_append(self.key_var.get())).pack(side=tk.LEFT, padx=5)
        else:
            # Host B (Recepção)
            self.status_var = tk.StringVar(value="Aguardando conexão na porta 12345...")
            ttk.Label(net_frame, textvariable=self.status_var).grid(row=0, column=4, padx=5, pady=5)
            
            # Chave de criptografia
            key_frame = ttk.LabelFrame(main_frame, text="Chave AES-256", padding=10)
            key_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(key_frame, text="Chave (Base64):").pack(side=tk.LEFT)
            self.key_entry = ttk.Entry(key_frame, width=50)
            self.key_entry.pack(side=tk.LEFT, padx=5)
            
            ttk.Button(key_frame, text="Definir Chave", command=self.set_key).pack(side=tk.LEFT)
        
        # Notebook para mostrar diferentes dados
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Abas
        self.create_tabs()
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Pronto", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_tabs(self):
        # Aba de texto original
        self.text_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.text_tab, text="Texto Original")
        
        self.text_display = scrolledtext.ScrolledText(self.text_tab, width=80, height=10)
        self.text_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Aba de texto criptografado
        self.encrypted_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.encrypted_tab, text="Texto Criptografado")
        
        self.encrypted_display = scrolledtext.ScrolledText(self.encrypted_tab, width=80, height=10)
        self.encrypted_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Aba de binário
        self.binary_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.binary_tab, text="Binário")
        
        self.binary_display = scrolledtext.ScrolledText(self.binary_tab, width=80, height=10)
        self.binary_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Aba de código Manchester
        self.manchester_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.manchester_tab, text="Código Manchester")
        
        self.manchester_display = scrolledtext.ScrolledText(self.manchester_tab, width=80, height=10)
        self.manchester_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Aba de gráfico
        self.graph_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.graph_tab, text="Gráfico")
        
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_tab)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def generate_new_key(self):
        self.key = get_random_bytes(32)  # Gera 32 bytes (256 bits)
        key_b64 = base64.b64encode(self.key).decode()
        self.key_var.set(key_b64)
    
        # Copiar automaticamente para a área de transferência
        self.root.clipboard_clear()
        self.root.clipboard_append(key_b64)
    
        messagebox.showinfo("Nova Chave", "Nova chave AES-256 gerada com sucesso e copiada para a área de transferência!")

    def set_key(self):
        try:
            key_b64 = self.key_entry.get().strip()
            if not key_b64:
                messagebox.showerror("Erro", "A chave não pode estar vazia")
                return
            
            # Decodificar a chave base64
            try:
                decoded_key = base64.b64decode(key_b64)
            except Exception:
                messagebox.showerror("Erro", "Formato de chave inválido. Certifique-se de que é um valor Base64 válido.")
                return
            
            # Verificar se tem o tamanho correto (256 bits = 32 bytes)
            if len(decoded_key) != 32:
                messagebox.showerror("Erro", f"Tamanho de chave inválido: {len(decoded_key)} bytes. A chave deve ter 32 bytes (256 bits)")
                return
            
            # Definir a chave
            self.key = decoded_key
            messagebox.showinfo("Chave Definida", "Chave AES-256 definida com sucesso!")
        
            # Atualizar a interface para mostrar que a chave está pronta
            self.status_bar.config(text="Chave AES definida e pronta para descriptografia")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao definir a chave: {str(e)}")

    def connect_to_receiver(self):
        try:
            host = self.ip_entry.get()
            port = int(self.port_entry.get())
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            
            messagebox.showinfo("Conexão", f"Conectado com sucesso ao receptor em {host}:{port}")
            self.status_bar.config(text=f"Conectado a {host}:{port}")
            self.connect_btn.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar: {str(e)}")

    def start_server(self):
        try:
            host = self.ip_entry.get()
            port = int(self.port_entry.get())
            
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((host, port))
            server_socket.listen(1)
            
            self.status_var.set(f"Aguardando conexão na porta {port}...")
            
            # Iniciar thread para aceitar conexões
            threading.Thread(target=self.accept_connections, args=(server_socket,), daemon=True).start()
        except Exception as e:
            messagebox.showerror("Erro no Servidor", f"Não foi possível iniciar o servidor: {str(e)}")

    def accept_connections(self, server_socket):
        try:
            while True:
                client_socket, addr = server_socket.accept()
                self.client_socket = client_socket
                
                # Atualizar UI na thread principal
                self.root.after(0, lambda: self.status_var.set(f"Conectado com {addr[0]}:{addr[1]}"))
                self.root.after(0, lambda: self.status_bar.config(text=f"Cliente conectado de {addr[0]}:{addr[1]}"))
                
                # Iniciar thread para receber dados
                threading.Thread(target=self.receive_data, args=(client_socket,), daemon=True).start()
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro de Conexão", f"Erro ao aceitar conexão: {str(e)}"))

    def encrypt_aes_256(self, data):
        try:
            # Gerar um IV aleatório
            iv = get_random_bytes(16)
            
            # Criar cifra
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            
            # Criptografar
            encrypted_data = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
            
            # Retornar IV + dados criptografados em base64
            return base64.b64encode(iv + encrypted_data).decode('utf-8')
        except Exception as e:
            messagebox.showerror("Erro de Criptografia", f"Erro ao criptografar: {str(e)}")
            return ""

    def decrypt_aes_256(self, encrypted_data):
        try:
            # Decodificar de base64
            raw_data = base64.b64decode(encrypted_data)
            
            # Extrair IV (primeiros 16 bytes)
            iv = raw_data[:16]
            encrypted_data = raw_data[16:]
            
            # Criar cifra
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            
            # Descriptografar
            decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            messagebox.showerror("Erro de Descriptografia", f"Erro ao descriptografar: {str(e)}")
            return ""

    def text_to_binary(self, text):
        # Converter texto para binário usando ASCII estendido
        binary = ""
        for char in text:
            # Pegar código ASCII do caractere e converter para binário (8 bits)
            binary += format(ord(char), '08b')
        return binary

    def binary_to_text(self, binary):
        # Converter binário para texto usando ASCII estendido
        text = ""
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) == 8:  # Verificar se é um byte completo
                text += chr(int(byte, 2))
        return text

    def binary_to_manchester(self, binary):
        # Codificação Manchester: 0 -> 01, 1 -> 10
        manchester = []
        for bit in binary:
            if bit == '0':
                manchester.extend([0, 1])  # 0 -> 01
            else:
                manchester.extend([1, 0])  # 1 -> 10
        return manchester

    def manchester_to_binary(self, manchester):
        # Decodificação Manchester: 01 -> 0, 10 -> 1
        binary = ""
        for i in range(0, len(manchester), 2):
            if i+1 < len(manchester):
                if manchester[i] == 0 and manchester[i+1] == 1:
                    binary += '0'
                elif manchester[i] == 1 and manchester[i+1] == 0:
                    binary += '1'
        return binary

    def plot_manchester(self, manchester_data, title="Codificação Manchester"):
        # Limpar gráfico anterior
        self.ax.clear()
        
        # Se não houver dados, não plotar
        if not manchester_data:
            self.ax.set_title("Sem dados para exibir")
            self.canvas.draw()
            return
        
        # Criar uma representação mais precisa do sinal para melhor visualização
        # Dobrar cada ponto para criar transições verticais claras
        x_values = []
        y_values = []
        
        # Iniciar com um tempo negativo pequeno para mostrar o início do sinal
        x_values.append(-0.5)
        y_values.append(manchester_data[0])
        
        for i, bit in enumerate(manchester_data):
            # Adicionar um ponto antes da transição (mesmo x, valor anterior)
            if i > 0:
                x_values.append(i - 0.001)
                y_values.append(manchester_data[i - 1])
            
            # Adicionar o ponto atual
            x_values.append(i)
            y_values.append(bit)
            
            # Adicionar outro ponto para manter o valor até a próxima transição
            x_values.append(i + 0.999)
            y_values.append(bit)
        
        # Adicionar um ponto extra no final para mostrar o final do sinal
        x_values.append(len(manchester_data) - 0.001)
        y_values.append(manchester_data[-1])
        x_values.append(len(manchester_data))
        y_values.append(manchester_data[-1])
        
        # Desenhar o sinal como uma linha contínua
        self.ax.plot(x_values, y_values, 'b-', linewidth=2)
        
        # Adicionar marcações para cada bit
        for i in range(0, len(manchester_data), 2):
            if i+1 < len(manchester_data):
                # Determinar qual bit original este par representa
                bit_value = '0' if manchester_data[i] == 0 and manchester_data[i+1] == 1 else '1'
                # Posicionar o texto no meio do par
                self.ax.text(i + 0.5, -0.2, bit_value, 
                            horizontalalignment='center', 
                            verticalalignment='center',
                            fontsize=9, color='red')
        
        # Adicionar linhas verticais para separar os pares de bits (bits originais)
        for i in range(0, len(manchester_data) + 1, 2):
            self.ax.axvline(x=i, color='lightgray', linestyle='--', alpha=0.7)
        
        # Adicionar uma linha horizontal no nível 0
        self.ax.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
        
        # Adicionar uma linha horizontal no nível 1
        self.ax.axhline(y=1, color='gray', linestyle='-', alpha=0.5)
        
        # Configurar o layout do gráfico
        self.ax.set_xlabel('Tempo (amostras)')
        self.ax.set_ylabel('Nível')
        self.ax.set_title(title)
        self.ax.set_ylim([-0.5, 1.5])
        
        # Ajustar os limites do eixo x para mostrar um pouco antes e depois do sinal
        self.ax.set_xlim([-1, len(manchester_data) + 1])
        
        # Adicionar legendas para explicar a codificação
        self.ax.text(len(manchester_data) + 0.5, 0.8, '01 → 0', color='blue', 
                    bbox=dict(facecolor='white', alpha=0.8))
        self.ax.text(len(manchester_data) + 0.5, 0.3, '10 → 1', color='blue',
                    bbox=dict(facecolor='white', alpha=0.8))
        
        # Adicionar grade
        self.ax.grid(True, which='both', linestyle=':', alpha=0.6)
        
        # Adicionar ticks para cada posição de bit
        self.ax.set_xticks(range(0, len(manchester_data)))
        
        # Anotações para indicar os pares de bits
        for i in range(0, len(manchester_data), 2):
            if i+1 < len(manchester_data):
                mid_point = i + 0.5
                self.ax.annotate(f'', xy=(i, 1.3), xytext=(i+2, 1.3),
                                arrowprops=dict(arrowstyle='<->',
                                            linestyle='-',
                                            color='green',
                                            alpha=0.7))
                if i % 4 == 0:  # Para não sobrecarregar o gráfico, só mostrar algumas anotações
                    self.ax.text(mid_point, 1.4, f'1 bit', 
                                horizontalalignment='center', 
                                color='green', fontsize=8)
        
        # Atualizar canvas
        self.canvas.draw()

    def process_and_send(self):
        try:
            # Pegar mensagem da UI
            message = self.message_text.get("1.0", tk.END).strip()
            if not message:
                messagebox.showwarning("Aviso", "Digite uma mensagem para enviar.")
                return
            
            # Exibir texto original
            self.text_display.delete("1.0", tk.END)
            self.text_display.insert(tk.END, message)
            
            # Criptografar
            encrypted = self.encrypt_aes_256(message)
            self.encrypted_display.delete("1.0", tk.END)
            self.encrypted_display.insert(tk.END, encrypted)
            
            # Converter para binário
            binary = self.text_to_binary(encrypted)
            self.binary_data = binary
            self.binary_display.delete("1.0", tk.END)
            self.binary_display.insert(tk.END, binary)
            
            # Aplicar codificação Manchester
            manchester = self.binary_to_manchester(binary)
            self.manchester_data = manchester
            
            # Mostrar codificação Manchester
            manchester_text = ''.join(map(str, manchester))
            self.manchester_display.delete("1.0", tk.END)
            self.manchester_display.insert(tk.END, manchester_text)
            
            # Desenhar o gráfico
            self.plot_manchester(manchester)
            
            # Preparar dados para envio
            data_to_send = {
                "text": message,
                "encrypted": encrypted,
                "binary": binary,
                "manchester": manchester
            }
            
            # Enviar para o receptor
            if self.socket:
                self.socket.sendall(json.dumps(data_to_send).encode())
                self.status_bar.config(text="Mensagem enviada com sucesso")
            else:
                messagebox.showwarning("Aviso", "Conecte-se a um receptor primeiro.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar e enviar: {str(e)}")

    def receive_data(self, client_socket):
        try:
            while True:
                # Receber dados
                data = client_socket.recv(65536)
                if not data:
                    break
                
                # Processar dados recebidos
                received_data = json.loads(data.decode())
                self.received_data = received_data
                
                # Atualizar UI na thread principal
                self.root.after(0, self.process_received_data)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro de Recepção", f"Erro ao receber dados: {str(e)}"))
        finally:
            client_socket.close()

    def process_received_data(self):
        try:
            # Pegar dados recebidos
            manchester = self.received_data.get("manchester", [])
            binary = self.received_data.get("binary", "")
            encrypted = self.received_data.get("encrypted", "")
            
            # Mostrar dados recebidos
            self.manchester_display.delete("1.0", tk.END)
            self.manchester_display.insert(tk.END, ''.join(map(str, manchester)))
            
            self.binary_display.delete("1.0", tk.END)
            self.binary_display.insert(tk.END, binary)
            
            self.encrypted_display.delete("1.0", tk.END)
            self.encrypted_display.insert(tk.END, encrypted)
            
            # Desenhar o gráfico
            self.plot_manchester(manchester, "Decodificação Manchester (Recebido)")
            
            # Decodificar e descriptografar
            if self.key:
                decrypted = self.decrypt_aes_256(encrypted)
                
                # Mostrar mensagem original
                self.text_display.delete("1.0", tk.END)
                self.text_display.insert(tk.END, decrypted)
                
                # Atualizar status
                self.status_bar.config(text="Mensagem recebida e decodificada com sucesso")
            else:
                messagebox.showwarning("Aviso", "Configure uma chave AES-256 para descriptografar.")
        except Exception as e:
            messagebox.showerror("Erro de Processamento", f"Erro ao processar dados recebidos: {str(e)}")

def main():
    root = tk.Tk()
    app_type = messagebox.askyesno("Tipo de Aplicação", "Executar como Host A (Envio)?\n\nSim - Host A (Envio)\nNão - Host B (Recepção)")
    app = ManchesterCodingApp(root, is_sender=app_type)
    root.mainloop()

if __name__ == "__main__":
    main()
