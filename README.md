# WinReg USB Auditor (CFSJ TECH)

> **Ferramenta de Forense Digital para Auditoria de Artefatos USB no Registro do Windows.**

**Autor:** Cláudio Francisco (CFSJ TECH)  
**Ano:** 2026  
**Plataforma:** Windows (Requer Privilégios de Administrador)

---

## 📋 Sobre o Projeto

O **WinReg USB Auditor** é uma solução automatizada desenvolvida em Python para auditar a hive do Registro do Windows, especificamente em:
`HKLM\SYSTEM\CurrentControlSet\Enum\USBSTOR`

O objetivo principal desta ferramenta é **automatizar, escalar e facilitar** o trabalho de peritos forenses, auditores e profissionais de cibersegurança. Ela elimina a necessidade de navegação manual propensa a erros pelo `regedit` e realiza a conversão complexa de timestamps binários automaticamente.

### 🔍 Funcionalidades Principais

* 🛡️ **Auto-Elevação de Privilégios:** O script identifica se não é administrador e solicita automaticamente a elevação (UAC Bypass) para garantir acesso à hive `HKLM`.
* 🕵️ **Análise Profunda:** Extrai metadados cruciais como ID do Fabricante (Vendor ID), ID do Produto (Product ID), Número de Série e "Friendly Name".
* d **Timestamp Precision:** Converte os valores binários de *Last Write Time* do registro para um formato de data/hora legível para humanos.
* 📄 **Relatório Automático:** Gera e abre instantaneamente um relatório `.txt` detalhado diretamente na **Área de Trabalho** do usuário.

---

## 🔗 Origem e Inspiração

Este projeto nasceu da necessidade de otimizar processos de investigação digital em campo. A metodologia técnica baseia-se nos conceitos de *Live Forensics* discutidos por **Miguel Dantas**, visando transformar a análise manual de registros em uma solução executável de clique único ("One-Click Solution").

* **Referência Original:** [Post no LinkedIn - Digital Forensics & USB Registry Activity](https://www.linkedin.com/posts/miguel-dantas-b1467a1a2_digitalforensics-usbforensics-windowsregistry-activity-7426603709016641537-3Q2b?utm_source=share&utm_medium=member_desktop&rcm=ACoAADxZPvUBkBfLM6lIezga91bMQj_1J8O4JiQ)

---

## ⚙️ Pré-requisitos

Para executar o código fonte ou compilar o executável, você precisará de:

1.  **Python 3.x** instalado no Windows.
2.  Biblioteca **PyInstaller** (para gerar o executável standalone).

### Instalação das Dependências

Abra o terminal (CMD ou PowerShell) e execute:

```bash
pip install pyinstaller
Caso o comando pip não seja reconhecido pelo seu sistema, utilize o módulo do Python:

Bash
py -m pip install pyinstaller
🚀 Como Executar (Script Python)
Se você deseja apenas testar o código em sua máquina de desenvolvimento sem gerar o executável final:

Certifique-se de que o arquivo WinReg_USB_Auditor.py está na pasta atual.

Abra o terminal nesta pasta.

Execute:

Bash
python WinReg_USB_Auditor.py
📦 Como Compilar para Executável (.exe)
Esta etapa é crucial para transformar o script Python em um software autônomo (.exe) que pode ser executado em qualquer computador Windows (Pen drive, Live System), mesmo que a máquina alvo não tenha Python instalado.

⚠️ Importante: Localização
Certifique-se de que o seu terminal (CMD/PowerShell) esteja aberto EXATAMENTE na mesma pasta onde o arquivo WinReg_USB_Auditor.py está salvo.

Comando de Compilação
Copie e cole o comando abaixo no seu terminal para gerar o binário:

Bash
py -m PyInstaller --noconfirm --onefile --console --uac-admin --name "WinReg_USB_Auditor_CFSJ.exe" "WinReg_USB_Auditor.py"
Entendendo os Parâmetros:
--onefile: Empacota o Python, as bibliotecas e seu script em um único arquivo .exe.

--console: Mantém a janela de comando visível para exibir logs de progresso e erros.

--uac-admin: Crítico. Força o executável a pedir permissão de Administrador ao iniciar (adiciona o ícone de escudo do Windows).

--noconfirm: Substitui arquivos de compilação antigos sem perguntar.

📂 Onde está o meu executável?
Após a execução do comando de compilação, o PyInstaller criará uma pasta chamada dist no mesmo diretório.

O seu arquivo final estará em: \dist\WinReg_USB_Auditor_CFSJ.exe

Instrução de Uso: Basta copiar este arquivo .exe para um pen drive e executá-lo na máquina alvo. O relatório será gerado automaticamente na Área de Trabalho daquela máquina.

⚖️ Aviso Legal
Esta ferramenta destina-se estritamente ao uso ético por profissionais autorizados em auditorias de segurança, resposta a incidentes (IR) e perícia forense computacional.

O autor e a CFSJ TECH não se responsabilizam pelo uso indevido, malicioso ou ilegal deste software.

Desenvolvido por Cláudio Francisco (CFSJ TECH) - 2026
