# ==============================================================================
# SCRIPT: WinReg_USB_Auditor_Final.py
# DESCRIÇÃO: Ferramenta forense para extração de artefatos USB da hive SYSTEM.
#            Coleta histórico de conexão em: HKLM\SYSTEM\CurrentControlSet\Enum\USBSTOR
# FUNCIONALIDADES:
#   1. Auto-elevação de privilégios (UAC Bypass request).
#   2. Extração de timestamps de última escrita (Last Write Time).
#   3. Geração de relatório automático na Área de Trabalho.
# PLATAFORMA: Windows 10/11
# AUTOR: Cláudio Francisco (CFSJ TECH)
# REVISÃO TÉCNICA: Gemini (AI)
# DATA: 2026
# ==============================================================================

import winreg
import datetime
import ctypes
import os
import sys
from typing import List, Dict, Optional, Any

# ==============================================================================
# SEÇÃO 1: GERENCIAMENTO DE PRIVILÉGIOS E SISTEMA
# ==============================================================================

def is_admin() -> bool:
    """Verifica se o processo atual possui token de Administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    """
    Reinicia o script solicitando elevação de privilégios via ShellExecute 'runas'.
    Necessário para leitura da hive HKLM.
    """
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([script] + sys.argv[1:])
    
    # Executa novamente o script, mas agora invocando o prompt UAC
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)

def get_registry_key_timestamp(hKey_handle: int) -> Optional[datetime.datetime]:
    """
    Utiliza a Windows API (advapi32) para extrair o 'Last Write Time' de uma chave.
    Isso indica a última vez que o Windows interagiu com este dispositivo.
    """
    class FILETIME(ctypes.Structure):
        _fields_ = [("dwLowDateTime", ctypes.c_ulong),
                    ("dwHighDateTime", ctypes.c_ulong)]

    ft = FILETIME()
    
    # RegQueryInfoKeyW recupera metadados da chave aberta
    ret = ctypes.windll.advapi32.RegQueryInfoKeyW(
        hKey_handle,
        None, None, None, # lpClass, lpcchClass, lpReserved
        None, None, None, # lpcSubKeys, lpcbMaxSubKeyLen, lpcbMaxClassLen
        None, None, None, # lpcValues, lpcbMaxValueNameLen, lpcbMaxValueLen
        None,             # lpcbSecurityDescriptor
        ctypes.byref(ft)  # lpftLastWriteTime
    )
    
    if ret == 0:
        # O Windows conta intervalos de 100ns desde 01/01/1601
        timestamp = (ft.dwHighDateTime << 32) + ft.dwLowDateTime
        return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=timestamp // 10)
    
    return None

# ==============================================================================
# SEÇÃO 2: LÓGICA DE FORENSE DIGITAL (EXTRAÇÃO)
# ==============================================================================

def analyze_usb_storage() -> List[Dict[str, Any]]:
    """
    Itera recursivamente sobre a chave USBSTOR para mapear dispositivos conectados.
    """
    registry_path = r"SYSTEM\CurrentControlSet\Enum\USBSTOR"
    devices_found = []

    print(f"[INFO] Iniciando varredura forense em: HKLM\\{registry_path}...")

    try:
        # Acesso ao Registro usando Context Manager (with) para segurança de memória
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as reg_key:
            
            # Nível 1: Identificação do Hardware (Vendor/Product ID)
            i = 0
            while True:
                try:
                    device_name = winreg.EnumKey(reg_key, i)
                    device_full_path = f"{registry_path}\\{device_name}"
                    
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, device_full_path) as device_key:
                        
                        # Nível 2: Instâncias Únicas (Serial Number / Instance ID)
                        j = 0
                        while True:
                            try:
                                instance_name = winreg.EnumKey(device_key, j)
                                instance_path = f"{device_full_path}\\{instance_name}"
                                
                                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, instance_path) as instance_key:
                                    
                                    # Tentativa de obter o nome amigável
                                    friendly_name = "Desconhecido (Driver Genérico)"
                                    try:
                                        friendly_name, _ = winreg.QueryValueEx(instance_key, "FriendlyName")
                                    except FileNotFoundError:
                                        pass 
                                    
                                    # Extração do Timestamp via API
                                    last_write = get_registry_key_timestamp(instance_key.handle)
                                    
                                    # Compilação do Artefato
                                    device_info = {
                                        "Device ID": device_name,
                                        "Serial Number": instance_name,
                                        "Friendly Name": friendly_name,
                                        "Last Connection (Reg Update)": last_write
                                    }
                                    devices_found.append(device_info)
                                    
                                j += 1
                            except OSError:
                                break # Fim das instâncias deste dispositivo
                    i += 1
                except OSError:
                    break # Fim da lista de dispositivos

        return devices_found

    except PermissionError:
        print("[ERRO CRÍTICO] Acesso negado. O script não tem permissão de Admin.")
        return []
    except Exception as e:
        print(f"[ERRO] Falha sistêmica durante a varredura: {str(e)}")
        return []

# ==============================================================================
# SEÇÃO 3: RELATÓRIOS E SAÍDA (I/O)
# ==============================================================================

def generate_report(devices: List[Dict[str, Any]]):
    """
    Gera relatório na Área de Trabalho e o executa.
    """
    # Define caminho agnóstico para o Desktop do usuário atual
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    filename = "Relatorio_Forense_USB.txt"
    filepath = os.path.join(desktop_path, filename)
    
    print(f"[INFO] Compilando dados para relatório...")

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("="*80 + "\n")
            f.write(f"RELATÓRIO TÉCNICO - AUDITORIA DE ARTEFATOS USB\n")
            f.write(f"Organização: CFSJ TECH\n")
            f.write(f"Responsável Técnico: Cláudio Francisco\n")
            f.write(f"Data da Análise: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Hostname Alvo: {os.environ.get('COMPUTERNAME', 'Unknown')}\n")
            f.write("="*80 + "\n\n")
            
            if not devices:
                f.write("[!] Nenhum artefato USBSTOR encontrado ou erro de leitura.\n")
                f.write("    Verifique se dispositivos USB de armazenamento já foram conectados a esta máquina.\n")
            else:
                f.write(f"TOTAL DE DISPOSITIVOS CATALOGADOS: {len(devices)}\n")
                f.write("Nota: 'Última Atividade' refere-se à última atualização da chave de registro.\n\n")
                
                # Ordena por data de conexão (mais recente primeiro)
                devices.sort(key=lambda x: x['Last Connection (Reg Update)'] or datetime.datetime.min, reverse=True)

                for idx, dev in enumerate(devices, 1):
                    ts = dev['Last Connection (Reg Update)']
                    ts_str = ts.strftime('%d/%m/%Y %H:%M:%S') if ts else "N/A"
                    
                    f.write(f"REGISTRO #{idx:03d}\n")
                    f.write(f"  [-] Nome Amigável:    {dev['Friendly Name']}\n")
                    f.write(f"  [-] Hardware ID:      {dev['Device ID']}\n")
                    f.write(f"  [-] Serial Number:    {dev['Serial Number']}\n")
                    f.write(f"  [-] Última Atividade: {ts_str}\n")
                    f.write("-" * 80 + "\n")
                    
            f.write("\n" + "="*80 + "\n")
            f.write("FIM DO RELATÓRIO\n")

        print(f"[SUCESSO] Relatório salvo em: {filepath}")
        
        # Abre o relatório automaticamente com o programa padrão (ex: Notepad)
        os.startfile(filepath)

    except IOError as e:
        print(f"[ERRO] Falha de I/O ao gravar no disco: {e}")

# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    # Verifica se já somos admin. Se não, solicita elevação e encerra esta instância.
    if is_admin():
        os.system('cls' if os.name == 'nt' else 'clear')
        print("="*60)
        print("  CFSJ TECH - WinReg USB Auditor (vFinal)")
        print("  Modo: Administrador [ATIVO]")
        print("="*60 + "\n")
        
        artifacts = analyze_usb_storage()
        generate_report(artifacts)
        
        print("\nProcesso concluído.")
        print("Pressione ENTER para fechar o console...")
        input()
    else:
        print("[SISTEMA] Solicitando elevação de privilégios via UAC...")
        run_as_admin()