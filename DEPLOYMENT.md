# Deployment Guide — Docker → Azure Container Registry → Azure Web App → CI/CD

This guide takes your Streamlit medical image app from **local Docker** to a
**public URL** with **automatic deploys on every git push**.

> Note: Your app uses **Streamlit**, not FastAPI. Everything below still applies —
> the only difference is the container listens on port **8501** (Streamlit's port).

---

## 0. Prerequisites (install once)

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- An Azure subscription
- Git + a GitHub repository for this project

Log in:

```powershell
az login
```

Set some names you'll reuse (pick your own unique values; ACR name must be
globally unique and lowercase):

```powershell
$RG        = "medical-rg"
$LOCATION  = "eastus"
$ACR       = "mymedicalacr"          # must be globally unique, lowercase
$WEBAPP    = "my-medical-webapp"     # must be globally unique
$PLAN      = "medical-plan"
$IMAGE     = "medical-image-analysis"
```

---

## 1. Develop & run locally with Docker

Build the image:

```powershell
docker build -t $IMAGE .
```

Run it locally (pass your OpenAI key as an env var):

```powershell
docker run -p 8501:8501 -e OPENAI_API_KEY="sk-..." $IMAGE
```

Open http://localhost:8501 — you should see the app.

---

## 2. Push the Docker image to Azure Container Registry (ACR)

Create the resource group and registry (one time):

```powershell
az group create --name $RG --location $LOCATION

az acr create --resource-group $RG --name $ACR --sku Basic --admin-enabled true
```

Log in and push:

```powershell
az acr login --name $ACR

$REGISTRY = "$ACR.azurecr.io"
docker tag $IMAGE "$REGISTRY/$IMAGE:latest"
docker push "$REGISTRY/$IMAGE:latest"
```

Verify:

```powershell
az acr repository list --name $ACR --output table
```

---

## 3. Run that image as a public Azure Web App

Create an App Service plan (Linux) and the Web App from your ACR image:

```powershell
az appservice plan create --name $PLAN --resource-group $RG --is-linux --sku B1

az webapp create `
  --resource-group $RG `
  --plan $PLAN `
  --name $WEBAPP `
  --deployment-container-image-name "$REGISTRY/$IMAGE:latest"
```

Tell the Web App which port the container listens on (Streamlit = 8501) and
give it the OpenAI key:

```powershell
az webapp config appsettings set `
  --resource-group $RG `
  --name $WEBAPP `
  --settings WEBSITES_PORT=8501 OPENAI_API_KEY="sk-..."
```

Let the Web App pull from ACR (grant it access):

```powershell
# Enable admin creds on ACR and wire them to the web app
$ACR_USER = az acr credential show -n $ACR --query username -o tsv
$ACR_PASS = az acr credential show -n $ACR --query "passwords[0].value" -o tsv

az webapp config container set `
  --name $WEBAPP `
  --resource-group $RG `
  --container-image-name "$REGISTRY/$IMAGE:latest" `
  --container-registry-url "https://$REGISTRY" `
  --container-registry-user $ACR_USER `
  --container-registry-password $ACR_PASS
```

Your public URL is now:

```
https://<WEBAPP>.azurewebsites.net
```

(First load can take a minute while it pulls the image.)

---

## 4. Do I need to store uploaded images? (No)

**No — this app does not store images anywhere.** Uploads are handled entirely
**in memory**:

- `st.image(uploaded, ...)` renders the preview directly from the in-memory
  bytes — no file is written to disk or blob.
- `analyze_image_bytes(uploaded.getvalue(), ...)` sends the same in-memory bytes
  straight to OpenAI.
- When the user's session ends, the bytes are discarded.

### What about multiple users at once?

You're safe out of the box. Streamlit gives **each browser connection its own
isolated session** and its own `st.session_state`, so two people uploading at
the same time never mix up their images or results. The `uploaded` variable
lives only inside that one user's session.

Collisions would only be a concern if you *saved* files with a shared name
(e.g. everyone writing `upload.jpg`). Since we don't save anything, there is
nothing to worry about.

---

## 5. Automatic deployment on every git push (CI/CD)

The workflow file lives at `.github/workflows/deploy.yml`. On every push to
`main` it will: build the image → push to ACR (tagged with the commit SHA and
`latest`) → point the Web App at the new image → restart.

### One-time setup: create a service principal for GitHub

```powershell
$SUB = az account show --query id -o tsv

az ad sp create-for-rbac `
  --name "gh-medical-deploy" `
  --role contributor `
  --scopes "/subscriptions/$SUB/resourceGroups/$RG" `
  --sdk-auth
```

Copy the **entire JSON output**.

### Add GitHub repository secrets

In GitHub: **Settings → Secrets and variables → Actions → New repository secret**

| Secret name             | Value                                             |
| ----------------------- | ------------------------------------------------- |
| `AZURE_CREDENTIALS`     | the full JSON from `create-for-rbac` above        |
| `AZURE_RESOURCE_GROUP`  | your resource group name (e.g. `medical-rg`)      |

Also make sure the Web App can pull from ACR (already done in step 3, or grant
the managed identity `AcrPull`).

### Edit the workflow env values

Open `.github/workflows/deploy.yml` and set:

- `ACR_NAME` → your ACR name (without `.azurecr.io`)
- `IMAGE_NAME` → `medical-image-analysis`
- `WEBAPP_NAME` → your Web App name

### Trigger it

```powershell
git add .
git commit -m "Add Docker + CI/CD"
git push origin main
```

Watch it run under the **Actions** tab in GitHub. When it finishes, refresh
your public URL — the new version is live.

---

## The full flow (recap)

```
git commit  →  git push  →  GitHub Actions
                                 │
                          docker build
                                 │
                     push image (SHA + latest) → ACR
                                 │
                     az webapp config container set
                                 │
                        az webapp restart
                                 │
              https://<WEBAPP>.azurewebsites.net  (new version live)
```
