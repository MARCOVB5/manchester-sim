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
from discovery import listen_for_discovery, discover_server


class ManchesterEncoder:
    """Classe para codificação Manchester baseada no manchester_test_v2.py"""
    
    @staticmethod
    def encode_binary_to_manchester(binary):
        """Codifica binário em Manchester - Padrão IEEE 802.3"""
        manchester = []
        for bit in binary:
            if bit == '0':
                # 0 é codificado como transição alto-baixo (1,0)
                manchester.extend([1, 0])
            elif bit == '1':
                # 1 é codificado como transição baixo-alto (0,1)
                manchester.extend([0, 1])
        return manchester
    
    @staticmethod
    def decode_manchester_to_binary(manchester):
        """Decodifica Manchester em binário"""
        binary = ''
        for i in range(0, len(manchester), 2):
            if i + 1 < len(manchester):
                if manchester[i] == 1 and manchester[i + 1] == 0:
                    binary += '0'  # Alto-baixo representa 0
                elif manchester[i] == 0 and manchester[i + 1] == 1:
                    binary += '1'  # Baixo-alto representa 1
        return binary
    
    @staticmethod
    def validate_encoding(binary, manchester):
        """Valida a codificação"""
        if len(manchester) != len(binary) * 2:
            return {'valid': False, 'error': 'Comprimento incorreto'}
        
        for i, bit in enumerate(binary):
            manchester_pair = [manchester[i * 2], manchester[i * 2 + 1]]
            
            if bit == '0' and not (manchester_pair[0] == 1 and manchester_pair[1] == 0):
                return {'valid': False, 'error': f"Erro no bit {i}: '0' deve ser codificado como '10'"}
            if bit == '1' and not (manchester_pair[0] == 0 and manchester_pair[1] == 1):
                return {'valid': False, 'error': f"Erro no bit {i}: '1' deve ser codificado como '01'"}
        
        return {'valid': True}

class ManchesterCodingApp:
    def __init__(self, root, is_sender=True):
        self.root = root
        self.is_sender = is_sender
        
        if is_sender:
            self.root.title("Manchester Coding - Host A (Envio)")
        else:
            self.root.title("Manchester Coding - Host B (Recepção)")
        
        self.root.geometry("1400x1000")
        
        # Socket configurations
        self.socket = None
        self.client_socket = None
        self.host = '192.168.100.1'
        self.port = 12349
        
        # For AES encryption
        self.key = get_random_bytes(32)  # 256 bits
        
        # Para armazenar dados de transmissão
        self.binary_data = ""
        self.manchester_data = []
        self.received_data = {}
        
        # Instância do encoder Manchester
        self.manchester_encoder = ManchesterEncoder()
        
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
        self.ip_entry.insert(0, "192.168.100.1")
        
        ttk.Label(net_frame, text="Porta:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.port_entry = ttk.Entry(net_frame, width=6)
        self.port_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        self.port_entry.insert(0, "12349")
        
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
            self.status_var = tk.StringVar(value="Aguardando conexão na porta 12349...")
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
        
        # Aba de gráfico - MELHORADA
        self.graph_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.graph_tab, text="Forma de Onda")
        
        # Frame para controles do gráfico
        controls_frame = ttk.Frame(self.graph_tab)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Testar Decodificação", command=self.test_decode).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Validar Codificação", command=self.validate_manchester).pack(side=tk.LEFT, padx=5)
        
        # Criar figura matplotlib com tamanho maior
        self.figure, self.ax = plt.subplots(figsize=(12, 8))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_tab)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Inicializar gráfico vazio
        self.draw_empty_graph()

    def draw_empty_graph(self):
        """Desenha um gráfico vazio com instruções"""
        self.ax.clear()
        self.ax.text(0.5, 0.5, 'Digite uma mensagem e clique em "Enviar Mensagem"\npara visualizar a forma de onda Manchester', 
                    ha='center', va='center', transform=self.ax.transAxes, fontsize=12, color='gray')
        self.ax.set_title('Forma de Onda Manchester - Aguardando dados')
        self.canvas.draw()

    def draw_manchester_waveform(self, binary_data, manchester_data, title="Codificação Manchester"):
        """Desenha a forma de onda Manchester corretamente - baseado no manchester_test_v2.py"""
        if not manchester_data:
            self.draw_empty_graph()
            return
        
        # Limpar gráfico anterior
        self.ax.clear()
        
        # Criar eixo de tempo para forma de onda contínua
        time_points = []
        signal_values = []
        
        # Criar pontos para forma de onda escalonada
        for i, value in enumerate(manchester_data):
            time_points.extend([i, i + 1])
            signal_values.extend([value, value])
        
        # Plotar sinal Manchester
        self.ax.plot(time_points, signal_values, 'b-', linewidth=3, label='Sinal Manchester')
        
        # Configurar eixos
        self.ax.set_ylim(-0.5, 1.5)
        self.ax.set_xlim(0, len(manchester_data))
        self.ax.set_ylabel('Amplitude (V)', fontsize=12)
        self.ax.set_xlabel('Tempo (unidades de amostra)', fontsize=12)
        self.ax.set_title(f'{title} – Sinal Bifásico', fontsize=14, fontweight='bold')
        
        # Adicionar linhas de referência
        self.ax.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='Nível Baixo (0V)')
        self.ax.axhline(y=1, color='green', linestyle='--', alpha=0.7, label='Nível Alto (1V)')
        
        # Adicionar separadores de bits originais
        for i in range(1, len(binary_data)):
            x_pos = i * 2
            self.ax.axvline(x=x_pos, color='gray', linestyle=':', alpha=0.8, linewidth=1)
        
        # Adicionar rótulos dos bits originais
        for i, bit in enumerate(binary_data):
            x_pos = i * 2 + 1
            # Rótulo do bit
            self.ax.text(x_pos, -0.3, f'Bit {i}\n{bit}', 
                        ha='center', va='top', fontsize=10, 
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.8))
            
            # Mostrar a codificação Manchester correspondente
            manchester_pair = manchester_data[i*2:i*2+2]
            manchester_str = ''.join(map(str, manchester_pair))
            self.ax.text(x_pos, 1.3, f'→ {manchester_str}', 
                        ha='center', va='bottom', fontsize=9, color='blue',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='lightyellow', alpha=0.8))
        
        # Adicionar informações dos dados
        info_text = f'Dados binários: {binary_data}\nManchester: {"".join(map(str, manchester_data))}\nComprimento: {len(binary_data)} bits → {len(manchester_data)} símbolos'
        self.ax.text(0.02, 0.98, info_text, transform=self.ax.transAxes, 
                    verticalalignment='top', fontsize=10,
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9))
        
        # Legenda das regras de codificação
        legend_text = 'Regras Manchester:\n0 → 10 (Alto→Baixo) ↓\n1 → 01 (Baixo→Alto) ↑'
        self.ax.text(0.98, 0.98, legend_text, transform=self.ax.transAxes, 
                    verticalalignment='top', horizontalalignment='right', fontsize=10,
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.9))
        
        # Configurar legenda
        self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)
        
        # Adicionar grade
        self.ax.grid(True, alpha=0.3)
        
        # Ajustar layout
        self.figure.tight_layout()
        
        # Atualizar canvas
        self.canvas.draw()

    def test_decode(self):
        """Testa a decodificação Manchester"""
        if not self.manchester_data or not self.binary_data:
            messagebox.showwarning("Aviso", "Primeiro envie uma mensagem para ter dados Manchester")
            return
        
        # Decodificar
        decoded_binary = self.manchester_encoder.decode_manchester_to_binary(self.manchester_data)
        is_correct = decoded_binary == self.binary_data
        
        result_text = f"""Teste de Decodificação Manchester:

Original (binário): {self.binary_data[:50]}{'...' if len(self.binary_data) > 50 else ''}
Decodificado:      {decoded_binary[:50]}{'...' if len(decoded_binary) > 50 else ''}

Resultado: {'✅ Decodificação CORRETA' if is_correct else '❌ ERRO na decodificação'}

Comprimentos:
- Binário original: {len(self.binary_data)} bits
- Manchester: {len(self.manchester_data)} símbolos ({len(self.manchester_data)//2} bits esperados)
- Decodificado: {len(decoded_binary)} bits"""
        
        messagebox.showinfo("Teste de Decodificação", result_text)

    def validate_manchester(self):
        """Valida a codificação Manchester"""
        if not self.manchester_data or not self.binary_data:
            messagebox.showwarning("Aviso", "Primeiro envie uma mensagem para ter dados Manchester")
            return
            
        validation = self.manchester_encoder.validate_encoding(self.binary_data, self.manchester_data)
        
        if validation['valid']:
            messagebox.showinfo("Validação", "✅ Codificação Manchester VÁLIDA!\n\nTodos os bits estão codificados corretamente.")
        else:
            messagebox.showerror("Validação", f"❌ Codificação Manchester INVÁLIDA!\n\n{validation['error']}")

    def generate_new_key(self):
        self.key = get_random_bytes(32)
        key_b64 = base64.b64encode(self.key).decode()
        self.key_var.set(key_b64)
        
        self.root.clipboard_clear()
        self.root.clipboard_append(key_b64)
        
        messagebox.showinfo("Nova Chave", "Nova chave AES-256 gerada com sucesso e copiada para a área de transferência!")

    def set_key(self):
        try:
            key_b64 = self.key_entry.get().strip()
            if not key_b64:
                messagebox.showerror("Erro", "A chave não pode estar vazia")
                return
            
            try:
                decoded_key = base64.b64decode(key_b64)
            except Exception:
                messagebox.showerror("Erro", "Formato de chave inválido. Certifique-se de que é um valor Base64 válido.")
                return
            
            if len(decoded_key) != 32:
                messagebox.showerror("Erro", f"Tamanho de chave inválido: {len(decoded_key)} bytes. A chave deve ter 32 bytes (256 bits)")
                return
            
            self.key = decoded_key
            messagebox.showinfo("Chave Definida", "Chave AES-256 definida com sucesso!")
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
            #host = self.ip_entry.get()
            host = self.ip_entry.get().strip() or '0.0.0.0'
            port = int(self.port_entry.get())
            
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((host, port))
            server_socket.listen(1)
            
            self.status_var.set(f"Aguardando conexão na porta {port}...")
            
            threading.Thread(target=self.accept_connections, args=(server_socket,), daemon=True).start()
        except Exception as e:
            messagebox.showerror("Erro no Servidor", f"Não foi possível iniciar o servidor: {str(e)}")

    def accept_connections(self, server_socket):
        try:
            while True:
                client_socket, addr = server_socket.accept()
                self.client_socket = client_socket
                
                self.root.after(0, lambda: self.status_var.set(f"Conectado com {addr[0]}:{addr[1]}"))
                self.root.after(0, lambda: self.status_bar.config(text=f"Cliente conectado de {addr[0]}:{addr[1]}"))
                
                threading.Thread(target=self.receive_data, args=(client_socket,), daemon=True).start()
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro de Conexão", f"Erro ao aceitar conexão: {str(e)}"))

    def encrypt_aes_256(self, data):
        try:
            iv = get_random_bytes(16)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            encrypted_data = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
            return base64.b64encode(iv + encrypted_data).decode('utf-8')
        except Exception as e:
            messagebox.showerror("Erro de Criptografia", f"Erro ao criptografar: {str(e)}")
            return ""

    def decrypt_aes_256(self, encrypted_data):
        try:
            raw_data = base64.b64decode(encrypted_data)
            iv = raw_data[:16]
            encrypted_data = raw_data[16:]
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            messagebox.showerror("Erro de Descriptografia", f"Erro ao descriptografar: {str(e)}")
            return ""

    def text_to_binary(self, text):
        binary = ""
        for char in text:
            binary += format(ord(char), '08b')
        return binary

    def binary_to_text(self, binary):
        text = ""
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) == 8:
                text += chr(int(byte, 2))
        return text

    def process_and_send(self):
        try:
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
            
            # Aplicar codificação Manchester CORRETA
            manchester = self.manchester_encoder.encode_binary_to_manchester(binary)
            self.manchester_data = manchester
            
            # Mostrar codificação Manchester
            manchester_text = ''.join(map(str, manchester))
            self.manchester_display.delete("1.0", tk.END)
            self.manchester_display.insert(tk.END, manchester_text)
            
            # Desenhar a forma de onda CORRETA
            self.draw_manchester_waveform(binary[:32], manchester[:64], "Codificação Manchester - Enviado")  # Limitar para visualização
            
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
                data = client_socket.recv(65536)
                if not data:
                    break
                
                received_data = json.loads(data.decode())
                self.received_data = received_data
                
                self.root.after(0, self.process_received_data)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro de Recepção", f"Erro ao receber dados: {str(e)}"))
        finally:
            client_socket.close()

    def process_received_data(self):
        try:
            manchester = self.received_data.get("manchester", [])
            binary = self.received_data.get("binary", "")
            encrypted = self.received_data.get("encrypted", "")
            
            # Armazenar dados recebidos
            self.manchester_data = manchester
            self.binary_data = binary
            
            # Mostrar dados recebidos
            self.manchester_display.delete("1.0", tk.END)
            self.manchester_display.insert(tk.END, ''.join(map(str, manchester)))
            
            self.binary_display.delete("1.0", tk.END)
            self.binary_display.insert(tk.END, binary)
            
            self.encrypted_display.delete("1.0", tk.END)
            self.encrypted_display.insert(tk.END, encrypted)
            
            # Desenhar a forma de onda dos dados recebidos
            self.draw_manchester_waveform(binary[:32], manchester[:64], "Decodificação Manchester - Recebido")
            
            # Decodificar e descriptografar
            if self.key:
                decrypted = self.decrypt_aes_256(encrypted)
                
                self.text_display.delete("1.0", tk.END)
                self.text_display.insert(tk.END, decrypted)
                
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
