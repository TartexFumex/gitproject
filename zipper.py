import os

def clean_synthesis_folder():
    """
    Remove all files from the synthesis folder.
    
    Returns:
        tuple: (success (bool), message (str))
    """
    try:
        synthesis_dir = "./fiches_de_synthese"
        if not os.path.exists(synthesis_dir):
            os.makedirs(synthesis_dir)
            return True, "Le dossier de synthèse était déjà vide."
        
        count = 0
        for file in os.listdir(synthesis_dir):
            file_path = os.path.join(synthesis_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                count += 1
        
        return True, f"{count} fichiers supprimés du dossier de synthèse."
    
    except Exception as e:
        return False, f"Erreur lors du nettoyage du dossier: {str(e)}"