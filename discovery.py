import socket
import threading
import ipaddress
import time

# Configuration
DISCOVERY_PORT = 12346
DISCOVERY_MESSAGE = b'DISCOVER_MANCHESTER'

def get_network_interfaces():
    """Retorna lista de interfaces de rede ativas"""
    interfaces = []
    try:
        # Criar socket temporário para descobrir IP local
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_sock.connect(("8.8.8.8", 80))
        local_ip = temp_sock.getsockname()[0]
        temp_sock.close()
        
        # Calcular rede local (assumindo /24)
        network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
        interfaces.append(str(network.broadcast_address))
        
        # Adicionar broadcast padrão também
        interfaces.append('255.255.255.255')
        
    except Exception:
        interfaces = ['255.255.255.255']
    
    return interfaces

def listen_for_discovery(tcp_port):
    """
    Escuta por requisições de descoberta UDP
    Melhorado com melhor tratamento de erros
    """
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', DISCOVERY_PORT))
        print(f"Servidor de descoberta ativo na porta {DISCOVERY_PORT}")
        
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                if data == DISCOVERY_MESSAGE:
                    print(f"Descoberta recebida de {addr[0]}:{addr[1]}")
                    # Responder com a porta TCP
                    response = str(tcp_port).encode()
                    sock.sendto(response, addr)
                    print(f"Resposta enviada: porta {tcp_port}")
            except Exception as e:
                print(f"Erro ao processar descoberta: {e}")
                time.sleep(0.1)  # Evitar loop muito rápido
                
    except Exception as e:
        print(f"Erro no servidor de descoberta: {e}")
    finally:
        if sock:
            sock.close()

def discover_server(timeout=3.0):
    """
    Descobre servidores na rede usando múltiplas estratégias
    """
    results = []
    
    # Estratégia 1: Broadcast em múltiplas interfaces
    interfaces = get_network_interfaces()
    
    for broadcast_addr in interfaces:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(timeout / len(interfaces))
            
            print(f"Enviando descoberta para {broadcast_addr}:{DISCOVERY_PORT}")
            sock.sendto(DISCOVERY_MESSAGE, (broadcast_addr, DISCOVERY_PORT))
            
            try:
                data, addr = sock.recvfrom(1024)
                server_ip = addr[0]
                server_port = int(data.decode())
                results.append((server_ip, server_port))
                print(f"Servidor encontrado: {server_ip}:{server_port}")
            except socket.timeout:
                print(f"Timeout no broadcast {broadcast_addr}")
                pass
                
        except Exception as e:
            print(f"Erro no broadcast {broadcast_addr}: {e}")
        finally:
            sock.close()
    
    # Retornar o primeiro resultado encontrado
    return results[0] if results else (None, None)

def test_connection(host, port):
    """Testa se é possível conectar em um host:porta"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False
