import React, { useState, useRef, useEffect } from 'react';
import { Play, RotateCcw, Download, Upload, CheckCircle, XCircle } from 'lucide-react';

const ManchesterApp = () => {
  const [binaryInput, setBinaryInput] = useState('0110110');
  const [manchesterData, setManchesterData] = useState([]);
  const [isEncoded, setIsEncoded] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const canvasRef = useRef(null);

  // Função para codificar binário em Manchester
  const encodeBinaryToManchester = (binary) => {
    const manchester = [];
    for (let bit of binary) {
      if (bit === '0') {
        // 0 é codificado como transição alto-baixo (1,0)
        manchester.push(1, 0);
      } else if (bit === '1') {
        // 1 é codificado como transição baixo-alto (0,1)
        manchester.push(0, 1);
      }
    }
    return manchester;
  };

  // Função para decodificar Manchester em binário
  const decodeManchesterToBinary = (manchester) => {
    let binary = '';
    for (let i = 0; i < manchester.length; i += 2) {
      if (i + 1 < manchester.length) {
        if (manchester[i] === 1 && manchester[i + 1] === 0) {
          binary += '0'; // Alto-baixo representa 0
        } else if (manchester[i] === 0 && manchester[i + 1] === 1) {
          binary += '1'; // Baixo-alto representa 1
        }
      }
    }
    return binary;
  };

  // Função para validar a codificação
  const validateEncoding = (binary, manchester) => {
    if (manchester.length !== binary.length * 2) {
      return { valid: false, error: 'Comprimento incorreto' };
    }

    for (let i = 0; i < binary.length; i++) {
      const bit = binary[i];
      const manchesterPair = [manchester[i * 2], manchester[i * 2 + 1]];
      
      if (bit === '0' && !(manchesterPair[0] === 1 && manchesterPair[1] === 0)) {
        return { valid: false, error: `Erro no bit ${i}: '0' deve ser codificado como '10'` };
      }
      if (bit === '1' && !(manchesterPair[0] === 0 && manchesterPair[1] === 1)) {
        return { valid: false, error: `Erro no bit ${i}: '1' deve ser codificado como '01'` };
      }
    }
    
    return { valid: true };
  };

  // Função para desenhar o gráfico Manchester
  const drawManchesterChart = () => {
    const canvas = canvasRef.current;
    if (!canvas || manchesterData.length === 0) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Limpar canvas
    ctx.clearRect(0, 0, width, height);
    
    // Configurações do gráfico
    const padding = 60;
    const chartWidth = width - 2 * padding;
    const chartHeight = height - 2 * padding;
    const bitWidth = chartWidth / binaryInput.length;
    const halfBitWidth = bitWidth / 2;
    
    // Níveis de voltagem
    const highLevel = padding + chartHeight * 0.2;
    const lowLevel = padding + chartHeight * 0.8;
    
    // Desenhar eixos
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;
    ctx.beginPath();
    // Eixo Y
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    // Eixo X
    ctx.moveTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();
    
    // Rótulos dos eixos
    ctx.fillStyle = '#333';
    ctx.font = '14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Tempo (unidades de amostra)', width / 2, height - 20);
    
    ctx.save();
    ctx.translate(20, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Nível Manchester', 0, 0);
    ctx.restore();
    
    // Desenhar linhas de referência
    ctx.strokeStyle = '#ff4444';
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(padding, lowLevel);
    ctx.lineTo(width - padding, lowLevel);
    ctx.stroke();
    
    ctx.strokeStyle = '#44ff44';
    ctx.beginPath();
    ctx.moveTo(padding, highLevel);
    ctx.lineTo(width - padding, highLevel);
    ctx.stroke();
    ctx.setLineDash([]);
    
    // Rótulos dos níveis
    ctx.fillStyle = '#ff4444';
    ctx.textAlign = 'right';
    ctx.fillText('0 (Low)', padding - 10, lowLevel + 5);
    ctx.fillStyle = '#44ff44';
    ctx.fillText('1 (High)', padding - 10, highLevel + 5);
    
    // Desenhar sinal Manchester
    ctx.strokeStyle = '#2563eb';
    ctx.lineWidth = 3;
    ctx.beginPath();
    
    let currentX = padding;
    let currentY = manchesterData[0] === 1 ? highLevel : lowLevel;
    ctx.moveTo(currentX, currentY);
    
    for (let i = 0; i < manchesterData.length; i++) {
      const nextX = padding + ((i + 1) / manchesterData.length) * chartWidth;
      const nextY = manchesterData[i] === 1 ? highLevel : lowLevel;
      
      // Linha horizontal
      ctx.lineTo(nextX, currentY);
      // Transição vertical
      if (i < manchesterData.length - 1) {
        const futureY = manchesterData[i + 1] === 1 ? highLevel : lowLevel;
        if (futureY !== currentY) {
          ctx.lineTo(nextX, futureY);
        }
        currentY = futureY;
      }
    }
    ctx.stroke();
    
    // Desenhar separadores de bits
    ctx.strokeStyle = '#999';
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 3]);
    for (let i = 1; i < binaryInput.length; i++) {
      const x = padding + (i / binaryInput.length) * chartWidth;
      ctx.beginPath();
      ctx.moveTo(x, padding);
      ctx.lineTo(x, height - padding);
      ctx.stroke();
    }
    ctx.setLineDash([]);
    
    // Rótulos dos bits originais
    ctx.fillStyle = '#2563eb';
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'center';
    for (let i = 0; i < binaryInput.length; i++) {
      const x = padding + (i + 0.5) * bitWidth;
      const y = height - padding + 25;
      ctx.fillText(binaryInput[i], x, y);
      
      // Rótulo da posição do bit
      ctx.fillStyle = '#666';
      ctx.font = '12px Arial';
      ctx.fillText(`bit ${i}`, x, y + 20);
      ctx.fillStyle = '#2563eb';
      ctx.font = 'bold 16px Arial';
    }
    
    // Legendas das regras de codificação
    const legendX = width - padding - 120;
    const legendY = padding + 30;
    
    ctx.fillStyle = '#ff6b6b';
    ctx.fillRect(legendX, legendY, 100, 25);
    ctx.fillStyle = 'white';
    ctx.font = 'bold 12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('0 → 10 (↓)', legendX + 50, legendY + 17);
    
    ctx.fillStyle = '#51cf66';
    ctx.fillRect(legendX, legendY + 35, 100, 25);
    ctx.fillStyle = 'white';
    ctx.fillText('1 → 01 (↑)', legendX + 50, legendY + 52);
    
    // Título
    ctx.fillStyle = '#333';
    ctx.font = 'bold 18px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Codificação Manchester – Sinal Bifásico', width / 2, 30);
    
    // Mostrar dados binários originais
    ctx.fillStyle = '#2563eb';
    ctx.font = '14px Arial';
    ctx.textAlign = 'left';
    ctx.fillText(`Dados binários: ${binaryInput}`, padding, padding + 20);
    ctx.fillText(`Manchester: ${manchesterData.join('')}`, padding, padding + 40);
  };

  // Executar codificação
  const handleEncode = () => {
    if (!/^[01]+$/.test(binaryInput)) {
      alert('Por favor, insira apenas 0s e 1s');
      return;
    }
    
    const encoded = encodeBinaryToManchester(binaryInput);
    setManchesterData(encoded);
    setIsEncoded(true);
    
    const validation = validateEncoding(binaryInput, encoded);
    setValidationResult(validation);
  };

  // Limpar dados
  const handleClear = () => {
    setBinaryInput('');
    setManchesterData([]);
    setIsEncoded(false);
    setValidationResult(null);
  };

  // Teste de decodificação
  const handleTestDecode = () => {
    if (manchesterData.length === 0) {
      alert('Primeiro codifique alguns dados');
      return;
    }
    
    const decoded = decodeManchesterToBinary(manchesterData);
    const isCorrect = decoded === binaryInput;
    
    alert(`Teste de decodificação:\nOriginal: ${binaryInput}\nDecodificado: ${decoded}\nResultado: ${isCorrect ? '✅ Correto' : '❌ Erro'}`);
  };

  // Redimensionar canvas e redesenhar quando necessário
  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      canvas.width = 800;
      canvas.height = 400;
      drawManchesterChart();
    }
  }, [manchesterData, binaryInput]);

  return (
    <div className="max-w-6xl mx-auto p-6 bg-white">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          Codificação de Linha Manchester
        </h1>
        <p className="text-gray-600">
          Implementação da codificação Manchester conforme método bifásico polar
        </p>
      </div>

      {/* Seção de entrada */}
      <div className="bg-blue-50 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Entrada de Dados</h2>
        
        <div className="flex flex-wrap items-center gap-4 mb-4">
          <div className="flex-1 min-w-64">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Dados Binários:
            </label>
            <input
              type="text"
              value={binaryInput}
              onChange={(e) => setBinaryInput(e.target.value)}
              placeholder="Ex: 0110110"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={handleEncode}
              disabled={!binaryInput}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              <Play size={16} />
              Codificar
            </button>
            
            <button
              onClick={handleClear}
              className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
            >
              <RotateCcw size={16} />
              Limpar
            </button>
          </div>
        </div>

        {/* Regras de codificação */}
        <div className="bg-white rounded-lg p-4 border border-blue-200">
          <h3 className="font-semibold text-gray-800 mb-2">Regras de Codificação Manchester:</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <span className="w-8 h-6 bg-red-400 text-white text-center font-bold rounded">0</span>
              <span>→ Alto-Baixo (10) - Transição descendente ↓</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-8 h-6 bg-green-400 text-white text-center font-bold rounded">1</span>
              <span>→ Baixo-Alto (01) - Transição ascendente ↑</span>
            </div>
          </div>
        </div>
      </div>

      {/* Resultados */}
      {isEncoded && (
        <div className="bg-green-50 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Resultados da Codificação</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-sm font-medium text-gray-700">Dados Originais:</p>
              <p className="font-mono text-lg text-blue-600">{binaryInput}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">Manchester Codificado:</p>
              <p className="font-mono text-lg text-green-600">{manchesterData.join('')}</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-4">
            {validationResult && (
              <div className={`flex items-center gap-2 ${validationResult.valid ? 'text-green-600' : 'text-red-600'}`}>
                {validationResult.valid ? <CheckCircle size={20} /> : <XCircle size={20} />}
                <span className="font-medium">
                  {validationResult.valid ? 'Codificação válida' : 'Erro: ' + validationResult.error}
                </span>
              </div>
            )}
            
            <button
              onClick={handleTestDecode}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            >
              Testar Decodificação
            </button>
          </div>
        </div>
      )}

      {/* Visualização */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Visualização do Sinal</h2>
        <div className="bg-white rounded-lg p-4 border border-gray-200 overflow-auto">
          <canvas
            ref={canvasRef}
            className="w-full max-w-full"
            style={{ maxWidth: '100%', height: 'auto' }}
          />
        </div>
        
        {manchesterData.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            Insira dados binários e clique em "Codificar" para visualizar o sinal Manchester
          </div>
        )}
      </div>

      {/* Informações técnicas */}
      <div className="mt-6 bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Sobre a Codificação Manchester</h3>
        <div className="text-sm text-gray-700 space-y-2">
          <p>
            <strong>Método Bifásico:</strong> A codificação Manchester combina os conceitos dos métodos RZ e NRZ-L.
          </p>
          <p>
            <strong>Sincronismo:</strong> A transição no meio de cada bit fornece sincronismo automático.
          </p>
          <p>
            <strong>Características:</strong> Cada bit tem duração dividida em duas metades com transição obrigatória.
          </p>
          <p>
            <strong>Vantagens:</strong> Autossincronização, detecção de erros, sem componente DC.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ManchesterApp;
