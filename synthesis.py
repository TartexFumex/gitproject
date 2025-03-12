import datetime
import os

def export_synthesis(user, start_date, end_date, ordinate_timelog):
    """
    Generate and export a synthesis report based on GitLab time logs.
    
    Args:
        user: The GitLab username
        start_date: The start date for the report period
        end_date: The end date for the report period
        ordinate_timelog: Organized time log data by board and label
        
    Returns:
        str: Path to the generated file
    """
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    # Create the directory if it doesn't exist
    os.makedirs("fiches_de_synthese", exist_ok=True)
    
    # Format the current date for the filename
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    filename = f"fiches_de_synthese/{user}_synthese_label_{current_date}.md"
    
    # Calculate overall total time spent across all boards
    total_time_seconds = 0
    all_labels_time = {}
    
    # First pass to collect all time data
    for board_name, labels in ordinate_timelog.items():
        for label_name, label_data in labels.items():
            time_spend = label_data["time_spend"]
            if time_spend > 0:
                total_time_seconds += time_spend
                if label_name in all_labels_time:
                    all_labels_time[label_name] += time_spend
                else:
                    all_labels_time[label_name] = time_spend
    
    with open(filename, "w") as f:
        # Write the header
        f.write(f"# Fiche de Synthèse - Période du {start_date_str} au {end_date_str}\n\n")
        
        # Write the time per label section
        f.write("## 🏷️ Temps total\n\n")
        
        # Calculate and write total
        total_hours = total_time_seconds // 3600
        total_minutes = (total_time_seconds % 3600) // 60
        total_time_str = f"{total_hours}.0h {total_minutes}.0m"
        
        f.write(f"> **TOTAL:** **{total_time_str}**\n\n")
        
        # Optional: Add board-specific sections if requested
        for board_name, labels in ordinate_timelog.items():
            # Calculate total time for this board
            board_total_time = sum(label_data["time_spend"] for label_data in labels.values())
            
            # Skip board if no time was spent
            if board_total_time == 0:
                continue
            
            # Write board section header
            f.write(f"## {board_name}\n\n")
            
            # Create table for this board
            f.write("| Label | Temps | Issues |\n")
            f.write("|-------|-------|---------|\n")
            
            # Sort labels by time spent (descending)
            sorted_board_labels = sorted(
                [(name, data) for name, data in labels.items() if data["time_spend"] > 0],
                key=lambda x: x[1]["time_spend"], 
                reverse=True
            )
            
            # Write each label's data
            for label_name, label_data in sorted_board_labels:
                time_spend = label_data["time_spend"]
                hours = time_spend // 3600
                minutes = (time_spend % 3600) // 60
                time_str = f"{hours}.0h {minutes}.0m"
                
                # Format issues list
                issues_str = ", ".join(sorted(set(label_data["issues"])))
                if len(issues_str) > 40:
                    issues_str = issues_str[:37] + "..."
                
                f.write(f"| {label_name} | {time_str} | {issues_str} |\n")
            
            # Write board total
            hours_total = board_total_time // 3600
            minutes_total = (board_total_time % 3600) // 60
            time_str_total = f"{hours_total}.0h {minutes_total}.0m"
            percentage = (board_total_time / total_time_seconds * 100) if total_time_seconds > 0 else 0
            
            f.write("|-------|-------|---------|\n")
            f.write(f"| **TOTAL {board_name}** | **{time_str_total}** | **{percentage:.1f}% du temps total** |\n\n")

    return filename

