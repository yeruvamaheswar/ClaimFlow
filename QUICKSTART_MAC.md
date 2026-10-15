# ClaimFlow — quick start on a Mac

This workspace is a downloadable project folder, **not a folder automatically created on your Mac or in the ChatGPT Projects sidebar**.

1. Unzip `ClaimFlow_Starter.zip`.
2. Move the resulting `ClaimFlow` directory to your normal Git repositories folder, for example `~/Code-Git-Repos/ClaimFlow`.
3. Open the folder in Cursor, VS Code, Codex, or Claude Code.
4. Open two terminal tabs and run the commands below.

**Tab 1 — backend**

```bash
cd ~/Code-Git-Repos/ClaimFlow/backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
uvicorn app.main:app --reload --port 8000
```

**Tab 2 — frontend**

```bash
cd ~/Code-Git-Repos/ClaimFlow/frontend
npm install
npm run dev
```

Then visit **http://localhost:3000** and choose **Load example claim**. The API docs are at **http://localhost:8000/docs**.

To initialize this as a local Git repo after reviewing the contents:

```bash
cd ~/Code-Git-Repos/ClaimFlow
git init
git add .
git commit -m "Initialize ClaimFlow synthetic evidence prototype"
```

This does not publish to GitHub; GitHub publication can be a separate deliberate action. **Do not upload real claims data.**
