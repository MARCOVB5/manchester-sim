import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class ManchesterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Codificação de Linha Manchester")
        self.root.geometry("1000x800")
        
        # Variáveis
        self.binary_input = tk.StringVar(value="0110110")
        self.manchester_data = []
        self.is_encoded = False
        self.validation_result = None
        
        self.setup_ui()
    
    def encode_binary_to_manchester(self, binary):
        """Codifica binário em Manchester"""
        manchester = []
        for bit in binary:
            if bit == '0':
                # 0 é codificado como transição alto-baixo (1,0)
                manchester.extend([1, 0])
            elif bit == '1':
                # 1 é codificado como transição baixo-alto (0,1)
                manchester.extend([0, 1])
        return manchester
    
    def decode_manchester_to_binary(self, manchester):
        """Decodifica Manchester em binário"""
        binary = ''
        for i in range(0, len(manchester), 2):
            if i + 1 < len(manchester):
                if manchester[i] == 1 and manchester[i + 1] == 0:
                    binary += '0'  # Alto-baixo representa 0
                elif manchester[i] == 0 and manchester[i + 1] == 1:
                    binary += '1'  # Baixo-alto representa 1
        return binary
    
    def validate_encoding(self, binary, manchester):
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
    
    def draw_manchester_chart(self):
        """Desenha o gráfico Manchester"""
        if not self.manchester_data:
            return
        
        # Limpar gráfico anterior
        self.ax.clear()
        
        binary = self.binary_input.get()
        
        # Criar eixo de tempo
        samples_per_bit = 2
        time_points = []
        signal_values = []
        
        for i, value in enumerate(self.manchester_data):
            time_points.extend([i, i + 1])
            signal_values.extend([value, value])
        
        # Plotar sinal
        self.ax.plot(time_points, signal_values, 'b-', linewidth=2, label='Sinal Manchester')
        
        # Configurar eixos
        self.ax.set_ylim(-0.5, 1.5)
        self.ax.set_xlim(0, len(self.manchester_data))
        self.ax.set_ylabel('Níveis Manchester')
        self.ax.set_xlabel('Tempo (unidades de amostra)')
        self.ax.set_title('Codificação Manchester – Sinal Bifásico')
        
        # Adicionar linhas de referência
        self.ax.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='0 (Low)')
        self.ax.axhline(y=1, color='green', linestyle='--', alpha=0.7, label='1 (High)')
        
        # Adicionar separadores de bits
        for i in range(1, len(binary)):
            x_pos = i * 2
            self.ax.axvline(x=x_pos, color='gray', linestyle=':', alpha=0.5)
        
        # Adicionar rótulos dos bits originais
        for i, bit in enumerate(binary):
            x_pos = i * 2 + 1
            self.ax.text(x_pos, -0.3, f'bit {i}\n{bit}', 
                        ha='center', va='top', fontsize=10, 
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7))
        
        # Adicionar informações
        info_text = f'Dados binários: {binary}\nManchester: {"".join(map(str, self.manchester_data))}'
        self.ax.text(0.02, 0.98, info_text, transform=self.ax.transAxes, 
                    verticalalignment='top', fontsize=10,
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
        
        # Legenda das regras
        legend_text = '0 → 10 (↓)\n1 → 01 (↑)'
        self.ax.text(0.98, 0.98, legend_text, transform=self.ax.transAxes, 
                    verticalalignment='top', horizontalalignment='right', fontsize=10,
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8))
        
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        
        # Atualizar canvas
        self.canvas.draw()
    
    def handle_encode(self):
        """Executa a codificação"""
        binary = self.binary_input.get().strip()
        
        # Validar entrada
        if not binary:
            messagebox.showerror("Erro", "Por favor, insira dados binários")
            return
        
        if not all(bit in '01' for bit in binary):
            messagebox.showerror("Erro", "Por favor, insira apenas 0s e 1s")
            return
        
        # Codificar
        self.manchester_data = self.encode_binary_to_manchester(binary)
        self.is_encoded = True
        
        # Validar
        self.validation_result = self.validate_encoding(binary, self.manchester_data)
        
        # Atualizar interface
        self.update_results()
        self.draw_manchester_chart()
    
    def handle_clear(self):
        """Limpa os dados"""
        self.binary_input.set("")
        self.manchester_data = []
        self.is_encoded = False
        self.validation_result = None
        
        # Limpar resultados
        self.result_frame.pack_forget()
        
        # Limpar gráfico
        self.ax.clear()
        self.ax.text(0.5, 0.5, 'Insira dados binários e clique em "Codificar"\npara visualizar o sinal Manchester', 
                    ha='center', va='center', transform=self.ax.transAxes, fontsize=12, color='gray')
        self.canvas.draw()
    
    def handle_test_decode(self):
        """Testa a decodificação"""
        if not self.manchester_data:
            messagebox.showwarning("Aviso", "Primeiro codifique alguns dados")
            return
        
        original = self.binary_input.get()
        decoded = self.decode_manchester_to_binary(self.manchester_data)
        is_correct = decoded == original
        
        result_text = f"""Teste de decodificação:
Original: {original}
Decodificado: {decoded}
Resultado: {'✅ Correto' if is_correct else '❌ Erro'}"""
        
        messagebox.showinfo("Teste de Decodificação", result_text)
    
    def update_results(self):
        """Atualiza a seção de resultados"""
        if not self.is_encoded:
            return
        
        # Mostrar frame de resultados
        self.result_frame.pack(fill='x', padx=10, pady=5)
        
        # Atualizar dados
        binary = self.binary_input.get()
        manchester_str = "".join(map(str, self.manchester_data))
        
        self.original_label.config(text=f"Dados Originais: {binary}")
        self.manchester_label.config(text=f"Manchester Codificado: {manchester_str}")
        
        # Atualizar validação
        if self.validation_result:
            if self.validation_result['valid']:
                self.validation_label.config(
                    text="✅ Codificação válida", 
                    foreground='green'
                )
            else:
                self.validation_label.config(
                    text=f"❌ Erro: {self.validation_result['error']}", 
                    foreground='red'
                )
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Título principal
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(title_frame, text="Codificação de Linha Manchester", 
                 font=('Arial', 16, 'bold')).pack()
        ttk.Label(title_frame, text="Implementação da codificação Manchester conforme método bifásico polar", 
                 font=('Arial', 10)).pack()
        
        # Seção de entrada
        input_frame = ttk.LabelFrame(self.root, text="Entrada de Dados", padding=10)
        input_frame.pack(fill='x', padx=10, pady=5)
        
        # Campo de entrada
        entry_frame = ttk.Frame(input_frame)
        entry_frame.pack(fill='x', pady=5)
        
        ttk.Label(entry_frame, text="Dados Binários:").pack(anchor='w')
        entry_widget = ttk.Entry(entry_frame, textvariable=self.binary_input, font=('Courier', 12))
        entry_widget.pack(fill='x', pady=2)
        
        # Botões
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill='x', pady=5)
        
        ttk.Button(button_frame, text="Codificar", command=self.handle_encode).pack(side='left', padx=2)
        ttk.Button(button_frame, text="Limpar", command=self.handle_clear).pack(side='left', padx=2)
        
        # Regras de codificação
        rules_frame = ttk.Frame(input_frame)
        rules_frame.pack(fill='x', pady=5)
        
        ttk.Label(rules_frame, text="Regras de Codificação Manchester:", 
                 font=('Arial', 10, 'bold')).pack(anchor='w')
        ttk.Label(rules_frame, text="0 → Alto-Baixo (10) - Transição descendente ↓").pack(anchor='w')
        ttk.Label(rules_frame, text="1 → Baixo-Alto (01) - Transição ascendente ↑").pack(anchor='w')
        
        # Seção de resultados (inicialmente oculta)
        self.result_frame = ttk.LabelFrame(self.root, text="Resultados da Codificação", padding=10)
        
        self.original_label = ttk.Label(self.result_frame, font=('Courier', 10))
        self.original_label.pack(anchor='w')
        
        self.manchester_label = ttk.Label(self.result_frame, font=('Courier', 10))
        self.manchester_label.pack(anchor='w')
        
        self.validation_label = ttk.Label(self.result_frame, font=('Arial', 10, 'bold'))
        self.validation_label.pack(anchor='w', pady=5)
        
        ttk.Button(self.result_frame, text="Testar Decodificação", 
                  command=self.handle_test_decode).pack(anchor='w')
        
        # Seção de visualização
        viz_frame = ttk.LabelFrame(self.root, text="Visualização do Sinal", padding=10)
        viz_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Criar figura matplotlib
        self.fig, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, viz_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Gráfico inicial vazio
        self.ax.text(0.5, 0.5, 'Insira dados binários e clique em "Codificar"\npara visualizar o sinal Manchester', 
                    ha='center', va='center', transform=self.ax.transAxes, fontsize=12, color='gray')
        self.canvas.draw()
        
        # Informações técnicas
        info_frame = ttk.LabelFrame(self.root, text="Sobre a Codificação Manchester", padding=10)
        info_frame.pack(fill='x', padx=10, pady=5)
        
        info_text = """• Método Bifásico: A codificação Manchester combina os conceitos dos métodos RZ e NRZ-L.
• Sincronismo: A transição no meio de cada bit fornece sincronismo automático.
• Características: Cada bit tem duração dividida em duas metades com transição obrigatória.
• Vantagens: Autossincronização, detecção de erros, sem componente DC."""
        
        ttk.Label(info_frame, text=info_text, justify='left').pack(anchor='w')

def main():
    root = tk.Tk()
    app = ManchesterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
