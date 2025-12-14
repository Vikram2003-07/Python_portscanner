import socket
import sys
from datetime import datetime
import threading

class PortScanner:
    def __init__(self, host, start_port=1, end_port=1024, timeout=1):
        """
        Initialize the port scanner.
        
        Args:
            host: Target IP address or hostname
            start_port: Starting port number (default: 1)
            end_port: Ending port number (default: 1024)
            timeout: Timeout for each connection attempt in seconds (default: 1)
        """
        self.host = host
        self.start_port = start_port
        self.end_port = end_port
        self.timeout = timeout
        self.open_ports = []
        self.lock = threading.Lock()
        
    def scan_port(self, port):
        """
        Scan a single port to check if it's open.
        
        Args:
            port: Port number to scan
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.host, port))
            sock.close()
            
            if result == 0:
                with self.lock:
                    self.open_ports.append(port)
                    print(f"[+] Port {port} is OPEN")
        except socket.gaierror:
            print(f"\n[-] Hostname {self.host} could not be resolved")
            sys.exit()
        except socket.error:
            print(f"\n[-] Could not connect to {self.host}")
            sys.exit()
    
    def scan(self, num_threads=100):
        """
        Scan all ports in the specified range using threading for faster scanning.
        
        Args:
            num_threads: Number of threads to use for scanning (default: 100)
        """
        print(f"\n[*] Starting scan on {self.host}")
        print(f"[*] Scanning ports {self.start_port} to {self.end_port}")
        print(f"[*] Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        start_time = datetime.now()
        
        # Create and start threads
        threads = []
        port_range = range(self.start_port, self.end_port + 1)
        
        for port in port_range:
            thread = threading.Thread(target=self.scan_port, args=(port,))
            threads.append(thread)
            thread.start()
            
            # Limit the number of active threads
            if len(threads) >= num_threads:
                for t in threads:
                    t.join()
                threads = []
        
        # Wait for remaining threads to complete
        for thread in threads:
            thread.join()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n[*] End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[*] Scan completed in {duration.total_seconds():.2f} seconds")
        
        if self.open_ports:
            print(f"\n[+] Open ports found: {len(self.open_ports)}")
            print(f"[+] Open ports: {sorted(self.open_ports)}")
        else:
            print("\n[-] No open ports found")
        
        return sorted(self.open_ports)


def get_common_ports():
    """Return a list of commonly used ports"""
    return [20, 21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 465, 587, 993, 995, 
            1433, 3306, 3389, 5432, 5984, 6379, 8080, 8443, 27017, 50070]


def main():
    """Main function to run the port scanner"""
    print("=" * 60)
    print("         Python Port Scanner")
    print("=" * 60)
    
    # Get IP address from user
    host = input("\nEnter the IP address or hostname to scan: ").strip()
    
    if not host:
        print("[-] Please provide a valid IP address or hostname")
        sys.exit()
    
    # Resolve hostname to IP if necessary
    try:
        resolved_ip = socket.gethostbyname(host)
        print(f"[+] Resolved {host} to {resolved_ip}")
        host = resolved_ip
    except socket.gaierror:
        print(f"[-] Could not resolve hostname: {host}")
        sys.exit()
    
    # Ask user for scanning mode
    print("\nScanning modes:")
    print("1. Quick scan (common ports)")
    print("2. Custom range (specify start and end port)")
    print("3. Full scan (ports 1-65535) - WARNING: This may take a long time!")
    
    choice = input("\nSelect mode (1-3): ").strip()
    
    if choice == "1":
        common_ports = get_common_ports()
        # We'll scan individual ports from the common list
        print(f"\n[*] Scanning {len(common_ports)} common ports...")
        open_ports = []
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    open_ports.append(port)
                    print(f"[+] Port {port} is OPEN")
            except Exception as e:
                continue
        
        if open_ports:
            print(f"\n[+] Open ports: {sorted(open_ports)}")
        else:
            print("\n[-] No common ports are open")
    
    elif choice == "2":
        try:
            start_port = int(input("Enter start port (1-65535): ").strip())
            end_port = int(input("Enter end port (1-65535): ").strip())
            
            if start_port < 1 or end_port > 65535 or start_port > end_port:
                print("[-] Invalid port range")
                sys.exit()
            
            scanner = PortScanner(host, start_port, end_port, timeout=1)
            scanner.scan(num_threads=100)
        except ValueError:
            print("[-] Please enter valid port numbers")
            sys.exit()
    
    elif choice == "3":
        print("\n[!] Full scan will scan all 65535 ports. This may take 10-30 minutes.")
        confirm = input("Continue? (y/n): ").strip().lower()
        
        if confirm == "y":
            scanner = PortScanner(host, 1, 65535, timeout=0.5)
            scanner.scan(num_threads=200)
        else:
            print("[-] Scan cancelled")
    
    else:
        print("[-] Invalid choice")
        sys.exit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[-] Scan interrupted by user")
        sys.exit()
