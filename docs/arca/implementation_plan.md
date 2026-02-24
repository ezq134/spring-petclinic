# Add GitHub Actions Build Workflow

This plan outlines the creation of a GitHub Actions workflow to automatically build the Spring Petclinic Maven project.

## Proposed Changes

### GitHub Actions

#### [MODIFY] [build.yaml](file:///c:/vpoptani/Personal/antigravity/spring-petclinic/.github/workflows/build.yaml)
- Add `SONAR_TOKEN` to `env` or `secrets`.
- Add a step to set the version before building:
    - `mvn -B versions:set -DnewVersion=1.0.${{ github.run_number }}`
- Update build step to use the new version.
- Add a step to run Sonar analysis.
- [NEW] Add deployment to GitHub Packages
    - Add `distributionManagement` to `pom.xml` pointing to `maven.pkg.github.com`.
    - Update `build.yaml` to run `mvn deploy`.
    - Configure `GITHUB_TOKEN` for package permissions.

#### [MODIFY] [pom.xml](file:///c:/vpoptani/Personal/antigravity/spring-petclinic/pom.xml)
- Add `<distributionManagement>` section:
    - ArtifactId: `petclinic-service`
- [NEW] Docker Integration
    - Create `Dockerfile`:
        - Base Image: `eclipse-temurin:17-jre` (Lightweight, contains Java runtime).
        - Copy compiled JAR from build step.
        - Entrypoint: `java -jar application.jar`
    - Update `build.yaml`:
        - Login to GitHub Container Registry (`ghcr.io`).
        - Build and Push Docker image.

#### [NEW] [Dockerfile](file:///c:/vpoptani/Personal/antigravity/spring-petclinic/Dockerfile)
- Simple Dockerfile to containerize the Spring Boot application.

### Local Kubernetes Deployment & CD
#### Architecture: Self-Hosted Runner
- Setting up a GitHub Self-Hosted Runner on the local machine allows the GHA workflow to access Rancher Desktop directly.
- The `deploy` job will run on `self-hosted`.

#### [NEW] [k8s/deployment.yaml](file:///c:/vpoptani/Personal/antigravity/spring-petclinic/k8s/deployment.yaml)
- Kubernetes Deployment for the Petclinic app.
- Uses `imagePullPolicy: Always` to ensure the latest image is pulled.

#### [NEW] [k8s/service.yaml](file:///c:/vpoptani/Personal/antigravity/spring-petclinic/k8s/service.yaml)
- Exposes the application (port 8080) via a `NodePort` (30080) accessible to localhost.

### Email Notification Integration
- Use `dawidd6/action-send-mail` to send notifications on failure.
- Requires SMTP server configuration (can use Gmail or SendGrid).
- Add `MAIL_USERNAME` and `MAIL_PASSWORD` (App Password) to GitHub Secrets.

## Verification Plan
...
### AI DevOps: Automated Root Cause Analysis (ARCA)
#### Goal
Transition from simple failure emails to a **Generic AI Agent** capable of analyzing any GHA failure.

#### Architecture: The Generic Python Agent
- **Reusability**: By passing `--repo`, `--run-id`, `--token`, and `--gemini-key` as arguments, the same script can be used for any GitHub repository.
- **Trigger**: GitHub Action `if: failure()` hook passes the context variables.
- **Enhanced Log Extraction**: 
    - **Chronological Sorting**: Logs are sorted (1_step, 2_step) to ensure the AI follows the pipeline's natural progression.
    - **Expanded Keywords**: Searches for `ERROR`, `FAIL`, `REFUSED`, `UNABLE`, `TIMEOUT`, `EXCEPTION`, `EXIT CODE`, and `UNABLE TO CONNECT`.
    - **Context Window**: Captures 5 lines *before* and 10 lines *after* any match.
    - **Git Noise Filtering**: Explicitly skips git checkout/commit messages to avoid false positives.
- **LLM Reasoning (Gemini)**: 
    - **Prompt**: Uses a Senior DevOps Persona with strict instructions to prioritize **Hard Failures** (Connectivity/Crashes) over **Soft Warnings** (Style/Lints).
- **Delivery**: Agent uses `smtplib` to email results directly via Gmail SMTP.
- **Portability (Phase 5)**: Containerized using `Dockerfile.arca` and `requirements.txt` for consistent execution on any runner.

#### Implementation Roadmap
1. **Generic Python Script (`scripts/failure_agent.py`)**: Designed to accept CLI arguments.
2. **Library Selection**: Use `requests` for API, `zipfile` for logs, and `google-generativeai` for LLM (Gemini).
3. **Portability**: 
    - Use `requirements.txt` to track all installed libraries (`requests`, etc.).
    - Use environment variables (like `GEMINI_API_KEY`) instead of hardcoding tokens.
    - Create a `Dockerfile` so the agent can run anywhere (Local, Kubernetes Pod, or GHA Runner).

### Automated Tests
- The workflow itself runs the build and tests (`mvn package` runs tests by default).
- After committing the file, I will verify the workflow syntax if possible (though real execution requires pushing to GitHub).
- I will run `./mvnw package` locally to ensure the build command is valid before finalizing the workflow file.
- **SonarCloud**: Verify that the workflow logs show successful submission to SonarCloud (requires valid secrets `SONAR_TOKEN` to be set in the repo settings).
