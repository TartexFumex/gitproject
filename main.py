import gitlab
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import threading
import zipper

names = ["bonhomki", "bournyma", "cantinto", "digoutan", "alonsoma", "bricauma", "besseama", "tremblma"]

class GitlabSynthesisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Générateur de synthèse GitLab")
        self.root.geometry("590x520")
        self.root.resizable(False, False)
        
        # Variables
        self.date_start_var = tk.StringVar()
        self.date_end_var = tk.StringVar()
        self.project_var = tk.StringVar(value="e4e-fise/s8-se-prose/2025/fortil/common")
        self.user_vars = {name: tk.BooleanVar(value=True) for name in names}
 
        # Création des frames
        self.create_date_frame()
        self.create_project_frame()
        self.create_users_frame()
        self.create_progress_frame()
        self.create_action_frame()
    
    def create_date_frame(self):
        date_frame = ttk.LabelFrame(self.root, text="Sélection des dates")
        date_frame.pack(fill="x", padx=10, pady=5)
        
        # Date de début
        ttk.Label(date_frame, text="Date de début:").grid(row=0, column=0, padx=5, pady=5)
        start_date = DateEntry(date_frame, width=12, background='darkblue',
                            foreground='white', date_pattern='yyyy-mm-dd')
        start_date.grid(row=0, column=1, padx=5, pady=5)
        start_date.bind("<<DateEntrySelected>>", 
                    lambda e: self.date_start_var.set(start_date.get_date().strftime('%Y-%m-%d')))
        
        # Date de fin
        ttk.Label(date_frame, text="Date de fin:").grid(row=0, column=2, padx=5, pady=5)
        end_date = DateEntry(date_frame, width=12, background='darkblue',
                        foreground='white', date_pattern='yyyy-mm-dd')
        end_date.grid(row=0, column=3, padx=5, pady=5)
        end_date.bind("<<DateEntrySelected>>", 
                    lambda e: self.date_end_var.set(end_date.get_date().strftime('%Y-%m-%d')))
        
        # Initialisation des dates
        today = datetime.now()
        seven_days_ago = today.replace(day=today.day-7)  # Soustrait 7 jours
        start_date.set_date(seven_days_ago)
        end_date.set_date(today)
        self.date_start_var.set(seven_days_ago.strftime('%Y-%m-%d'))
        self.date_end_var.set(today.strftime('%Y-%m-%d'))
    
    def create_project_frame(self):
        project_frame = ttk.LabelFrame(self.root, text="Projet GitLab")
        project_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(project_frame, text="Chemin du projet:").grid(row=0, column=0, padx=5, pady=5)
        project_entry = ttk.Entry(project_frame, textvariable=self.project_var, width=50)
        project_entry.grid(row=0, column=1, padx=5, pady=5)
    
    def create_users_frame(self):
        users_frame = ttk.LabelFrame(self.root, text="Sélection des utilisateurs")
        users_frame.pack(fill="x", padx=10, pady=5)  # Changed from fill="both", expand=True to fill="x"
        
        # Boutons pour tout sélectionner/désélectionner
        btn_frame = ttk.Frame(users_frame)
        btn_frame.pack(fill="x", pady=5)
        
        select_all_btn = ttk.Button(btn_frame, text="Tout sélectionner", command=self.select_all_users)
        select_all_btn.pack(side="left", padx=5)
        
        deselect_all_btn = ttk.Button(btn_frame, text="Tout désélectionner", command=self.deselect_all_users)
        deselect_all_btn.pack(side="left", padx=5)
        
        # Frame pour la liste des utilisateurs avec scrollbar
        list_frame = ttk.Frame(users_frame)
        list_frame.pack(fill="x", padx=5, pady=5)  # Changed from fill="both", expand=True to fill="x"
        
        self.users_canvas = tk.Canvas(list_frame, height=150)  # Added fixed height
        self.users_canvas.pack(side="left", fill="x", expand=True)  # Changed fill="both" to fill="x"
        
        self.users_inner_frame = ttk.Frame(self.users_canvas)
        self.users_canvas.create_window((0, 0), window=self.users_inner_frame, anchor="nw")
        
        # Ajout des cases à cocher pour chaque utilisateur
        for i, name in enumerate(names):
            check = ttk.Checkbutton(self.users_inner_frame, text=name, variable=self.user_vars[name])
            check.grid(row=i//2, column=i%2, sticky="w", padx=10, pady=2)
        
    def create_progress_frame(self):
        progress_frame = ttk.LabelFrame(self.root, text="Progression")
        progress_frame.pack(fill="x", padx=10, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", padx=5, pady=5)
        
        self.status_var = tk.StringVar(value="Prêt")
        status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        status_label.pack(pady=5)
    
    def create_action_frame(self):
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        # Add a clean button to remove all files from the synthesis folder
        clean_btn = ttk.Button(action_frame, text="Nettoyer dossier", command=self.clean_synthesis_folder)
        clean_btn.pack(side="left", padx=5)
        
        generate_btn = ttk.Button(action_frame, text="Générer les synthèses", command=self.start_generation)
        generate_btn.pack(side="right", padx=5)
    
    def select_all_users(self):
        for var in self.user_vars.values():
            var.set(True)
    
    def deselect_all_users(self):
        for var in self.user_vars.values():
            var.set(False)
    
    def start_generation(self):
        # Vérification des champs
        start_date = self.date_start_var.get()
        end_date = self.date_end_var.get()
        project = self.project_var.get()
        selected_users = [name for name, var in self.user_vars.items() if var.get()]
        
        if not start_date or not end_date:
            messagebox.showerror("Erreur", "Veuillez sélectionner les dates de début et de fin")
            return
        
        if not project:
            messagebox.showerror("Erreur", "Veuillez entrer un chemin de projet")
            return
        
        if not selected_users:
            messagebox.showerror("Erreur", "Veuillez sélectionner au moins un utilisateur")
            return
        
        # Démarrer la génération dans un thread séparé
        thread = threading.Thread(target=self.generate_synthesis, 
                                 args=(start_date, end_date, project, selected_users))
        thread.daemon = True
        thread.start()
    
    def clean_synthesis_folder(self):
        """Clean all files from the synthesis folder"""
        success, message = zipper.clean_synthesis_folder()
        if success:
            messagebox.showinfo("Information", message)
        else:
            messagebox.showerror("Erreur", message)
    
    def generate_synthesis(self, start_date, end_date, project, selected_users):
        self.status_var.set("Génération en cours...")
        self.progress_var.set(0)
        
        try:
            git = gitlab.Gitlab(start_date, end_date, project)
            
            total_users = len(selected_users)
            for i, user in enumerate(selected_users):
                user_progress = (i / total_users) * 100
                self.progress_var.set(user_progress)
                self.status_var.set(f"Génération pour {user}...")
                self.root.update_idletasks()
                
                git.export_synthesis(user)
            
            self.progress_var.set(90)
            self.status_var.set("Compression des fichiers...")
            self.root.update_idletasks()
            
            # Zip all the synthesis files with date range in filename
            success, message = zipper.zip_synthesis_files(start_date, end_date)
            
            self.progress_var.set(100)
            
            if success:
                self.status_var.set("Génération et compression terminées avec succès!")
                messagebox.showinfo("Succès", f"Toutes les synthèses ont été générées avec succès et compressées.\n\n{message}")
            else:
                self.status_var.set("Génération terminée, mais erreur de compression.")
                messagebox.showwarning("Attention", f"Synthèses générées mais erreur lors de la compression : {message}")
            
        except Exception as e:
            self.status_var.set(f"Erreur: {str(e)}")
            messagebox.showerror("Erreur", f"Une erreur s'est produite: {str(e)}")

def main():
    root = tk.Tk()
    app = GitlabSynthesisApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()