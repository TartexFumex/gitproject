import os
import zipfile
from datetime import datetime

def zip_synthesis_files(start_date, end_date):
    """
    Zip all files in the fiches_de_synthese directory into a zip file named with the date range.
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        
    Returns:
        tuple: (success (bool), message (str))
    """
    try:
        # Create directory if it doesn't exist
        synthesis_dir = "./fiches_de_synthese"
        if not os.path.exists(synthesis_dir):
            return False, "Le dossier de synthèse est vide, rien à zipper."
        
        # Check if directory has files
        files = [f for f in os.listdir(synthesis_dir) if os.path.isfile(os.path.join(synthesis_dir, f))]
        if not files:
            return False, "Aucun fichier trouvé dans le dossier de synthèse."
        
        # Create zip filename with date range
        zip_filename = f"synthesis-{start_date}-{end_date}.zip"
        zip_path = os.path.join(".", zip_filename)
        
        # Create the zip file
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files:
                file_path = os.path.join(synthesis_dir, file)
                # Add file to zip with its name only (not the full path)
                zipf.write(file_path, arcname=file)
        
        return True, f"Fichiers de synthèse zippés avec succès dans {zip_filename}"
    
    except Exception as e:
        return False, f"Erreur lors de la création du fichier zip: {str(e)}"


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
