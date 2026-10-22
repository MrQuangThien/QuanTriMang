import requests

from config.settings import GNS3_HOST, GNS3_PORT


class GNS3Manager:
    def __init__(self):
        self.base_url = f"http://{GNS3_HOST}:{GNS3_PORT}/v2"

    def test_connection(self):
        try:
            response = requests.get(
                f"{self.base_url}/version",
                timeout=5,
            )
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json(),
            }
        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
            }

    def get_projects(self):
        response = requests.get(
            f"{self.base_url}/projects",
            timeout=5,
        )
        response.raise_for_status()
        return response.json()

    def get_project_nodes(self, project_id: str):
        response = requests.get(
            f"{self.base_url}/projects/{project_id}/nodes",
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
