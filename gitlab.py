import urllib3, datetime, requests
from synthesis import export_synthesis
from dotenv import load_dotenv
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

class Gitlab:
    GITLAB_URL = os.getenv("GITLAB_URL")
    GRAPHQL_TOKEN = os.getenv("GRAPHQL_TOKEN")
    EXCLUDE_LABEL = os.getenv("EXCLUDE_LABEL").split(",") if os.getenv("EXCLUDE_LABEL") else []

    def __init__(self, start_date:str, end_date:str, project:str):
        self.start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        self.project_path = project

        self.board_list = self.get_issues_board_list()

    def get_issues_board_list(self):
        """
        Récupère la liste des boards d'un projet
        """
        headers = {
            "Authorization": f"Bearer {self.GRAPHQL_TOKEN}",
            "Content-Type": "application/json"
        }

        query = {
            "query": "query project_boards($fullPath: ID!) {  project(fullPath: $fullPath) {    id    boards {      nodes {        id        name }}}}",
            "variables": {
                "fullPath": self.project_path
            }
        }

        response = requests.post(f"{self.GITLAB_URL}/api/graphql", headers=headers, json=query, verify=False)
    
        if response.status_code != 200:
            return "Error"
                
        return response.json()["data"]["project"]["boards"]["nodes"]
    
    def get_label_list(self, board_id):
        """
        Récupère la liste des issues d'un board
        """
        headers = {
            "Authorization": f"Bearer {self.GRAPHQL_TOKEN}",
            "Content-Type": "application/json"
        }

        query = {
            "query": """
            query BoardLists($fullPath: ID!, $boardId: BoardID!) {
              project(fullPath: $fullPath) {
            id
            board(id: $boardId) {
              id
              lists {
                nodes {
                  label {
                id
                title
                color
                  }
                }
              }
            }
              }
            }
            """,
            "variables": {
            "boardId": board_id,
            "fullPath": self.project_path,
            }
        }

        response = requests.post(f"{self.GITLAB_URL}/api/graphql", headers=headers, json=query, verify=False)
        

        if response.status_code != 200:
            return "Error"
        
        labels = []

        for l in response.json()["data"]["project"]["board"]["lists"]["nodes"]:
            labels.append(l["label"])

        return labels

    def fetch_timelogs_from_api(self, user):
        headers = {
            "Authorization": f"Bearer {self.GRAPHQL_TOKEN}",
            "Content-Type": "application/json"
        }

        delta = self.end_date - self.start_date

        timelog = {}

        for i in range(delta.days//7+1):
            start = self.start_date + datetime.timedelta(days=i*7)
            end = self.start_date + datetime.timedelta(days=(i+1)*7-1)
            if end > self.end_date:
                end = self.end_date

            start_str = start.strftime("%Y-%m-%d")
            end_str = end.strftime("%Y-%m-%d")

            query = {
            "query": f"""
                query {{
                    timelogs(startDate: "{start_str}", endDate: "{end_str}", username: "{user}") {{
                        edges {{
                            node {{
                                issue {{
                                    iid
                                    title
                                    labels {{ edges {{ node {{ title }} }} }}
                                }}
                                timeSpent
                            }}
                        }}
                    }}
                }}
                """
            }
            
            response = requests.post(f"{self.GITLAB_URL}/api/graphql", headers=headers, json=query, verify=False)
            if response.status_code != 200:
                return "Error"

            for r in response.json()["data"]["timelogs"]["edges"]:
                issue_id = r["node"]["issue"]["iid"]

                if issue_id not in timelog.keys():
                    timelog[issue_id] = {
                        "issue_name": r["node"]["issue"]["title"],
                        "time_spend": r["node"]["timeSpent"],
                        "labels": []
                    }

                    # récupération des labels
                    for label in r["node"]["issue"]["labels"]["edges"]:
                        timelog[issue_id]["labels"].append(label["node"]["title"])
                
                else:
                    timelog[issue_id]["time_spend"] += r["node"]["timeSpent"]

        return timelog
    
    def ordonner(self, timelogs):
        ordinate_timelog = {}

        for board in self.board_list:
            ordinate_timelog[board["name"]] = {}

            for label in self.get_label_list(board["id"]):
                if label:
                    ordinate_timelog[board["name"]][label["title"]] = {
                        "time_spend": 0,
                        "issues": []
                    }
        
        for timelog in timelogs.values():
            for board in self.board_list:
                board_name = board["name"]
                for label in timelog["labels"]:
                    if (label in list(ordinate_timelog[board_name].keys())) and (label not in self.EXCLUDE_LABEL) and (label != board_name):
                        ordinate_timelog[board_name][label]["time_spend"] += timelog["time_spend"]
                        ordinate_timelog[board_name][label]["issues"].append(timelog["issue_name"])
                        break
        
        return ordinate_timelog

    def export_synthesis(self, user):
        timelog = self.fetch_timelogs_from_api(user)
        ordinate_timelog = self.ordonner(timelog)
        
        return export_synthesis(
            user=user,
            start_date=self.start_date,
            end_date=self.end_date,
            ordinate_timelog=ordinate_timelog
        )

if __name__ == "__main__":
    gitlab = Gitlab("2025-01-01", "2025-03-12")
    import json
    open("test.json", "w").write(json.dumps(gitlab.fetch_timelogs_from_api("bonhomki"), indent=4))
