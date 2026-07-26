# 3D Commit Calendar

A Python script that generates a 3D visualization of your GitHub contribution calendar, where each day's contributions are represented as columns with heights proportional to the number of contributions made.

## Overview

This project creates a 3D model (GLB format) of your GitHub contribution calendar, which is automatically updated every 8 hours and hosted on GitHub Gists. The model is currently being displayed at [ethanhao.org](https://ethanhao.org).

## Features

- Converts GitHub contribution data into a 3D mesh
- Color-coded contribution levels (from light grey to dark green)
- Automatic updates via GitHub Actions
- Exports in GLB format for web compatibility
- Centered and properly oriented 3D model

## How it Works

1. Fetches contribution data using GitHub's GraphQL API
2. Generates a 3D mesh where:
   - Each column represents one day
   - Column height is proportional to contribution count
   - Colors vary based on contribution intensity
3. Exports the model in GLB format
4. Automatically uploads to GitHub Gists
5. Updates every 8 hours via GitHub Actions

## Setup

1. Create a GitHub personal access token with appropriate permissions
2. Create a new GitHub Gist to host the GLB file
3. Set up the following repository secrets:
   - `ACCESS_TOKEN`: Your GitHub personal access token
   - `GIST_ID`: The ID of your created Gist
4. Optionally set the `GH_USERNAME` environment variable to the account whose
   contributions should be rendered (defaults to `ethan-yz-hao`)

`index.html` is a standalone three.js viewer for the generated model, useful for
checking the output locally before it goes live.

## Dependencies

- Python 3.9-3.12 (the pinned numpy 1.26.4 has no support for 3.13+)
- Required packages (install via `pip install -r requirements.txt`):
  - requests
  - trimesh
  - numpy
  - scipy (required by trimesh's GLB export path)
  - python-dotenv

## Usage

To run locally:

```bash
python main.py
```

The script will automatically:
1. Fetch your GitHub contribution data
2. Generate the 3D model
3. Upload it to your specified Gist

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

[Ethan Hao](https://ethanhao.org)

