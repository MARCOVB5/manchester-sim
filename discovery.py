import socket
import threading

# Configuration: UDP discovery port and magic string
DISCOVERY_PORT = 12346
DISCOVERY_MESSAGE = b'DISCOVER_MANCHESTER'


def listen_for_discovery(tcp_port):
    """
    Runs in a background thread on the server side.
    Listens for UDP discovery requests and replies with the TCP port.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # bind to all interfaces on the discovery port
    sock.bind(('0.0.0.0', DISCOVERY_PORT))
    while True:
        data, addr = sock.recvfrom(1024)
        if data == DISCOVERY_MESSAGE:
            # reply with our TCP port
            sock.sendto(str(tcp_port).encode(), addr)


def discover_server(timeout=1.0):
    """
    Sends a UDP broadcast to find any server instances.
    Returns a tuple (server_ip, server_tcp_port) or (None, None).
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)
    try:
        # broadcast discovery message
        sock.sendto(DISCOVERY_MESSAGE, ('255.255.255.255', DISCOVERY_PORT))
        data, addr = sock.recvfrom(1024)
        server_ip = addr[0]
        server_port = int(data.decode())
        return server_ip, server_port
    except socket.timeout:
        return None, None
    finally:
        sock.close()


# Example of starting discovery listener in your main GUI/server code:
#
# from discovery import listen_for_discovery
#
# def start_server(self):
#     tcp_port = int(self.port_entry.get())
#     threading.Thread(target=listen_for_discovery, args=(tcp_port,), daemon=True).start()
#     # ... continue binding TCP socket, accepting connections

# Example of using discovery in client code:
#
# from discovery import discover_server
#
# def connect_to_receiver(self):
#     server_ip, server_port = discover_server()
#     if server_ip is None:
#         print("No server found on LAN")
#     else:
#         # fill GUI fields or directly connect:
#         self.ip_entry.delete(0, 'end')
#         self.ip_entry.insert(0, server_ip)
#         self.port_entry.delete(0, 'end')
#         self.port_entry.insert(0, str(server_port))
#         # now proceed with your TCP connect logic

