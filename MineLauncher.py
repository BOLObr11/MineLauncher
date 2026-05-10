import customtkinter as ctk
import minecraft_launcher_lib
import subprocess
import threading
import uuid
import os

# Configurações de Aparência
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MinecraftLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Custom Gaming Launcher")
        self.geometry("500x400")

        # Pasta padrão do Minecraft
        self.minecraft_dir = os.path.join(os.getenv('APPDATA'), ".meu_launcher_custom")

        # UI - Título
        self.label_title = ctk.CTkLabel(self, text="MINECRAFT LAUNCHER", font=("Orbitron", 24, "bold"))
        self.label_title.pack(pady=20)

        # UI - Nome de Usuário
        self.username_entry = ctk.CTkEntry(self, placeholder_text="Seu Nome de Usuário", width=300)
        self.username_entry.pack(pady=10)

        # UI - Seleção de Versão
        self.label_ver = ctk.CTkLabel(self, text="Selecione a Versão:")
        self.label_ver.pack()
        
        # Pegando lista de versões (filtrando apenas as releases)
        versions = [v['id'] for v in minecraft_launcher_lib.utils.get_version_list() if v['type'] == 'release']
        self.version_select = ctk.CTkComboBox(self, values=versions[:20], width=300) # Mostra as 20 mais recentes
        self.version_select.pack(pady=10)

        # UI - Botão Jogar
        self.btn_play = ctk.CTkButton(self, text="INSTALAR E JOGAR", command=self.start_launch_thread, 
                                      fg_color="#2ecc71", hover_color="#27ae60", font=("Arial", 14, "bold"))
        self.btn_play.pack(pady=20)

        # UI - Status e Progresso
        self.status_label = ctk.CTkLabel(self, text="Status: Pronto", text_color="gray")
        self.status_label.pack()

        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

    def update_status(self, text, color="white"):
        self.status_label.configure(text=f"Status: {text}", text_color=color)

    def start_launch_thread(self):
        # Desativa o botão para evitar múltiplos cliques
        self.btn_play.configure(state="disabled")
        thread = threading.Thread(target=self.launch_game)
        thread.start()

    def launch_game(self):
        username = self.username_entry.get()
        version = self.version_select.get()

        if not username:
            self.update_status("Erro: Digite um nome!", "red")
            self.btn_play.configure(state="normal")
            return

        try:
            # 1. Instalação
            self.update_status(f"Baixando arquivos da {version}...")
            self.progress_bar.set(0.2)
            
            minecraft_launcher_lib.install.install_minecraft_version(version, self.minecraft_dir)
            
            self.progress_bar.set(0.7)
            self.update_status("Gerando comando de inicialização...")

            # 2. Configuração
            options = {
                "username": username,
                "uuid": str(uuid.uuid4()),
                "token": "",
                "jvmArguments": ["-Xmx4G", "-Xms2G"] # 4GB de RAM para melhor performance
            }

            command = minecraft_launcher_lib.command.get_minecraft_command(version, self.minecraft_dir, options)

            # 3. Execução
            self.progress_bar.set(1.0)
            self.update_status("Jogo Iniciado! Pode fechar o launcher.", "#2ecc71")
            
            # Esconde a janela do launcher ao abrir o jogo
            self.withdraw() 
            subprocess.run(command)
            self.deiconify() # Mostra de novo quando o jogo fechar
            
        except Exception as e:
            self.update_status(f"Erro: {str(e)[:40]}...", "red")
        
        self.btn_play.configure(state="normal")
        self.progress_bar.set(0)

if __name__ == "__main__":
    app = MinecraftLauncher()
    app.mainloop()