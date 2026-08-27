# 🩺 Medical Image Analysis

A **Streamlit** web application that performs automated analysis of medical
images — **Brain MRI**, **Chest X-ray**, and **Retina Fundus** — using an
OpenAI vision models. The user selects an image type, uploads an
image, and receives a structured analysis with a classification, confidence,
reasoning, key observations.


---

## 🌐 Live application (primary)

**Public URL:**
👉 https://medical-image-analysis-6502it-fwaggzbggtfcaydd.southindia-01.azurewebsites.net

The app is deployed on **Azure Web App for Containers** using **GitHub Actions**.


---

## 🚀 Usage walkthrough

Once the app is open (public URL **or** `http://localhost:8501`):

1. **Select an image type** from the dropdown — Brain MRI, Chest X-ray, or
   Retina Fundus.
2. **Upload an image.** You can use one of the provided samples
3. **Preview** — the uploaded image appears.
4. Click **Analyze**
5. **Result** — the app returns a structured analysis: a classification, confidence,
   reasoning, key visual observations.


---

## �🐳 Run locally with Docker (fallback)

If the public URL is unavailable for any reason (e.g. credits exhausted), the
application can be run locally from the **public Docker image on Docker Hub**.

**Docker Hub image:** [`pramodi/medical-image-analysis`](https://hub.docker.com/r/pramodi/medical-image-analysis)

### Option A — Pull the ready-made image (fastest)

```bash
# 1. Pull the image from Docker Hub
docker pull pramodi/medical-image-analysis:latest

# 2. Run it (replace with a valid OpenAI API key)
docker run -p 8501:8501 -e OPENAI_API_KEY="sk-your-key-here" pramodi/medical-image-analysis:latest
```

Then open **http://localhost:8501** in your browser.

### Option B — Build from source

```bash
# From the project root (where the Dockerfile is)
docker build -t medical-image-analysis .

docker run -p 8501:8501 -e OPENAI_API_KEY="sk-your-key-here" medical-image-analysis
```

Then open **http://localhost:8501** in your browser.

> 💡 You can also place the key in a `.env` file and run with
> `--env-file .env` instead of `-e OPENAI_API_KEY=...`.

---

## Configuration

The application requires a single environment variable:

| Variable         | Description                          |
| ---------------- | ------------------------------------ |
| `OPENAI_API_KEY` | Your OpenAI API key (`sk-...`)       |

Locally this is provided via `-e` or `--env-file`. In Azure it is stored as a
Web App **application setting**, injected securely from a GitHub Actions secret
(see the CI/CD section).

---

## 🧩 Application development

### Tech stack

| Layer         | Technology                     |
| ------------- | ------------------------------ |
| UI / frontend | Streamlit                      |
| AI model      | OpenAI `gpt-4.1-mini` (vision) |
| Language      | Python 3.11                    |
| Packaging     | Docker                         |

### How it works

1. The user selects one of three image types (Brain MRI / Chest X-ray / Retina
   Fundus).
2. The user uploads an image (`jpg`, `jpeg`, `png`, `webp`).
3. Streamlit holds the uploaded image **in memory** and renders a preview.
4. On **Analyze**, the raw image bytes are base64-encoded and sent to the
   OpenAI vision model together with a modality-specific prompt from
   `prompts.py`.
5. The structured result is rendered back in the UI.



### Project structure

```
app.py                        # Streamlit application
prompts.py                    # Per-modality prompts and icons
requirements.txt              # Python dependencies
Dockerfile                    # Container definition (Streamlit on port 8501)
.dockerignore                 # Files excluded from the image
README.md                     # Project documentation
screenshot_UI.png             # Screenshot of the live application
.github/
  └── workflows/
      └── deploy.yml           # CI/CD pipeline (build → ACR → Web App)
sample_images/                # Example images for testing
  ├── brain_mri/
  ├── chest_xray/
  └── retina_fundus/
```

### Run without Docker 

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

# Provide your key (PowerShell shown; or use a .env file)
$env:OPENAI_API_KEY="sk-your-key-here"

streamlit run app.py
```

---

## ☁️ Deployment on Azure

The application is containerized and deployed to **Azure Web App for
Containers**, pulling its image from **Azure Container Registry (ACR)**.

### Azure resources used

| Resource                     | Name / Value                     | Purpose                                   |
| ---------------------------- | -------------------------------- | ----------------------------------------- |
| Resource Group               | `medical-rg`                     | Logical container for all resources       |
| Azure Container Registry     | `pramodimedicalacr`              | Stores the Docker images                  |
| App Service Plan (Linux)     | `medical-plan` (B1)              | Compute host for the Web App              |
| Azure Web App for Containers | `medical-image-analysis-6502it`  | Runs the container, serves the public URL |

### Architecture

```
Developer
   │  git push (main)
   ▼
GitHub Actions
   │  docker build
   ▼
Azure Container Registry (pramodimedicalacr.azurecr.io)
   │  az webapp config container set
   ▼
Azure Web App for Containers (medical-image-analysis-6502it)
   │
   ▼
https://medical-image-analysis-6502it-....azurewebsites.net
   │  user uploads image
   ▼
Streamlit (port 8501) ──► OpenAI Vision ──► Analysis result
```

---

## 🔄 CI/CD — automatic deployment

Whenever the code is updated and pushed to the `main` branch, a **GitHub
Actions CI/CD pipeline** automatically rebuilds the Docker image, pushes it to
Azure Container Registry, and redeploys the Web App — so the live URL always
reflects the latest code.

The pipeline is defined in `.github/workflows/deploy.yml`. On every push to
`main` (or manual trigger) it:

1. **Checks out** the code.
2. **Logs in to Azure** using the service principal / OIDC credentials.
3. **Sets a unique image tag** based on a UTC timestamp + run number, e.g.
   `20260827.1345.42`.
4. **Logs in to ACR** and **builds** the Docker image.
5. **Pushes** the image (unique tag + `latest`) to ACR.
6. **Configures Web App settings** — injects `OPENAI_API_KEY` (from a GitHub
   secret) and `WEBSITES_PORT=8501`.
7. **Deploys** by pointing the Web App at the freshly built image and
   restarting it — so each run always goes live with the newest image.

```
git commit → git push → GitHub Actions
                              │
                        docker build
                              │
                push (timestamp tag + latest) → ACR
                              │
                  az webapp config container set
                              │
                     az webapp restart
                              │
        https://medical-image-analysis-6502it-....azurewebsites.net  (live)
```

### Required GitHub secrets

Authentication to Azure uses **GitHub OIDC** (`azure/login` with a federated
credential — no stored password). Set the following under
**Settings → Secrets and variables → Actions**:

| Secret name             | Purpose                                                    |
| ----------------------- | ---------------------------------------------------------- |
| `AZURE_CLIENT_ID`       | App registration (client) ID for OIDC login               |
| `AZURE_TENANT_ID`       | Azure AD tenant ID for OIDC login                          |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID for OIDC login                       |
| `AZURE_RESOURCE_GROUP`  | Target resource group (`medical-rg`)                       |
| `OPENAI_API_KEY`        | OpenAI API key injected into the Web App settings          |

---

## 🖼️ Screenshot

A screenshot of the live application is available in the repository:
[`screenshot_UI.png`](screenshot_UI.png).