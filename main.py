import requests
from github import Github
import trimesh
import numpy as np
import os
import datetime
from dotenv import load_dotenv
import base64

# Get the environment variables
load_dotenv()
GITHUB_TOKEN = os.getenv('ACCESS_TOKEN')
GIST_ID = os.getenv('GIST_ID')

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
        "from": (datetime.datetime.now() - datetime.timedelta(weeks=53)).isoformat() + "Z",
        "to": datetime.datetime.now().isoformat() + "Z"
    }
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables},
                             headers=headers)
    data = response.json()
    return data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']


PALETTE = [
    (0.9, 0.9, 0.9),  # Light grey for no contributions
    (0.7, 0.9, 0.7),  # Light green
    (0.4, 0.8, 0.4),  # Medium green
    (0.2, 0.6, 0.2),  # Darker green
    (0.1, 0.4, 0.1),  # Dark green
]


def srgb_to_linear(c):
    """Convert one sRGB channel to linear."""
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def get_color(count):
    """Get color based on contribution count.

    glTF stores COLOR_0 in linear space, so the sRGB palette above is converted
    before export. Without this, renderers treat the sRGB values as linear and
    the columns come out noticeably lighter and washed out than intended.
    """
    if count == 0:
        index = 0
    elif count < 5:
        index = 1
    elif count < 10:
        index = 2
    elif count < 20:
        index = 3
    else:
        index = 4
    return [srgb_to_linear(c) for c in PALETTE[index]] + [1]


def create_3d_calendar(contributions):
    vertices = []
    faces = []
    face_colors = []

    size = 1.0
    for i, week in enumerate(contributions):
        for j, day in enumerate(week['contributionDays']):
            count = day['contributionCount']
            height = count / 10.0
            x = i * size
            y = j * size * -1
            base_index = len(vertices)
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
            faces.extend([
                # front
                [base_index, base_index + 1, base_index + 5],
                [base_index, base_index + 5, base_index + 4],
                # right
                [base_index + 1, base_index + 2, base_index + 6],
                [base_index + 1, base_index + 6, base_index + 5],
                # back
                [base_index + 2, base_index + 3, base_index + 7],
                [base_index + 2, base_index + 7, base_index + 6],
                # left
                [base_index + 3, base_index, base_index + 4],
                [base_index + 3, base_index + 4, base_index + 7],
                # top
                [base_index + 4, base_index + 5, base_index + 6],
                [base_index + 4, base_index + 6, base_index + 7],
                # bottom
                [base_index + 3, base_index + 2, base_index + 1],
                [base_index + 3, base_index + 1, base_index],
            ])
            color = get_color(count)
            face_colors.extend([color] * 12)

    vertices = np.array(vertices)
    faces = np.array(faces)
    face_colors = np.array(face_colors)

    # process=False keeps every day's box as its own 8 vertices. With the default
    # process=True trimesh welds the duplicate vertices that neighbouring cells share,
    # and because glTF has no face colours the exporter averages the colours of all
    # faces touching a vertex - bleeding the grey of empty days into the green columns.
    mesh = trimesh.Trimesh(
        vertices=vertices, faces=faces, face_colors=face_colors, process=False
    )

    # Apply rotation to align columns pointing upwards
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle= - np.pi / 2,  # minus 90 degrees
        direction=[1, 0, 0],  # Rotate around the x-axis
        point=mesh.centroid  # Rotate around the centroid
    )
    mesh.apply_transform(rotation_matrix)
    # Apply translation to center the calendar
    mesh.apply_translation([-size * 53 / 2, size * 7 / 2, 0])

    mesh.export('commit_calendar.glb')


def upload_to_gist(path='commit_calendar.glb'):
    """Upload the generated model to the GitHub Gist."""
    gist_url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {'Authorization': f'Bearer {GITHUB_TOKEN}'}

    with open(path, 'rb') as f:
        content = f.read()

    # Encode the binary content to base64
    encoded_content = base64.b64encode(content).decode('utf-8')

    data = {
        "description": "GitHub Commit Calendar",
        "public": True,
        "files": {
            "commit_calendar.glb": {
                "content": encoded_content
            }
        }
    }

    response = requests.patch(gist_url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"Gist updated: {response.json()['html_url']}")
    else:
        print(f"Error updating gist: {response.status_code}")


if __name__ == '__main__':
    # Fetch contributions and generate the calendar
    username = 'ethan-yz-hao'
    contributions = fetch_contributions(username)
    create_3d_calendar(contributions)
    upload_to_gist()