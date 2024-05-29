import requests
from github import Github
import trimesh
import numpy as np
import os

# Get the environment variables
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# Initialize GitHub object
g = Github(GITHUB_TOKEN)


def fetch_contributions(username):
    query = """
    query ($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """
    variables = {
        "login": username,
        "from": "2023-01-01T00:00:00Z",  # Adjust the start date if needed
        "to": "2023-12-31T23:59:59Z"  # Adjust the end date if needed
    }
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables},
                             headers=headers)
    data = response.json()
    return data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']


def create_3d_calendar(contributions):
    vertices = []
    faces = []
    colors = []

    size = 1.0
    for i, week in enumerate(contributions):
        for j, day in enumerate(week['contributionDays']):
            count = day['contributionCount']
            height = count / 10.0
            x = i * size
            y = j * size
            vertices.extend([
                [x, y, 0],
                [x + size, y, 0],
                [x + size, y + size, 0],
                [x, y + size, 0],
                [x, y, height],
                [x + size, y, height],
                [x + size, y + size, height],
                [x, y + size, height],
            ])
            base_index = (i * 7 + j) * 8
            faces.extend([
                [base_index, base_index + 1, base_index + 5],
                [base_index, base_index + 5, base_index + 4],
                [base_index + 1, base_index + 2, base_index + 6],
                [base_index + 1, base_index + 6, base_index + 5],
                [base_index + 2, base_index + 3, base_index + 7],
                [base_index + 2, base_index + 7, base_index + 6],
                [base_index + 3, base_index, base_index + 4],
                [base_index + 3, base_index + 4, base_index + 7],
                [base_index + 4, base_index + 5, base_index + 6],
                [base_index + 4, base_index + 6, base_index + 7],
            ])
            color = [count / 10.0, 0, 1 - count / 10.0, 1]  # Example color scaling
            colors.extend([color] * 8)

    vertices = np.array(vertices)
    faces = np.array(faces)
    colors = np.array(colors)

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, vertex_colors=colors)
    mesh.export('commit_calendar.glb')


# Fetch contributions and generate the calendar
username = 'your-username'
contributions = fetch_contributions(username)
create_3d_calendar(contributions)

# Upload to GitHub Gist
gist_url = "https://api.github.com/gists"
headers = {'Authorization': f'token {GITHUB_TOKEN}'}

with open('commit_calendar.glb', 'rb') as f:
    content = f.read()

data = {
    "description": "GitHub Commit Calendar",
    "public": True,
    "files": {
        "commit_calendar.glb": {
            "content": content.decode('latin1')
        }
    }
}

response = requests.post(gist_url, headers=headers, json=data)

if response.status_code == 201:
    print(f"Gist created: {response.json()['html_url']}")
else:
    print(f"Error creating gist: {response.status_code}")
