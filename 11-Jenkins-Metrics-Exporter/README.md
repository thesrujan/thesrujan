# Jenkins Pipeline for a Python Metrics Exporter

This project demonstrates a Jenkins CI/CD pipeline for a small Python metrics exporter. The exporter provides a Prometheus-compatible `/metrics` endpoint and a `/health` endpoint. Jenkins checks out the source, installs dependencies, compiles and tests the project, packages deployment files, and verifies the package.

## Project structure

```text
11-Jenkins-Metrics-Exporter/
├── Jenkinsfile
├── README.md
├── requirements.txt
├── metrics_exporter.py
├── config/
│   └── exporter.env.example
├── tests/
│   ├── test_metrics_exporter.py
│   └── test_controlled_failure.py
├── scripts/
│   └── package.py
└── .gitignore
```

## Prerequisites

- Git installed on the computer and on the Jenkins build agent.
- Python 3.10 or newer installed on the Jenkins build agent and available on `PATH`.
- Jenkins with the Pipeline and Git plugins installed.
- For this public repository, no Git credentials are needed. For a private repository, configure Jenkins credentials and select them in the job.

The Python exporter itself uses only the standard library. `requirements.txt` installs pytest for automated tests.

## A. Add this folder to your existing GitHub repository

The repository already contains other exercises. Extract this folder into the root of your existing local clone so that it sits beside the other numbered exercise folders. Do not run `git init` inside this new folder.

From the root of your local `thesrujan` clone, run:

```bash
git status
git add 11-Jenkins-Metrics-Exporter
git commit -m "Add Jenkins Python metrics exporter pipeline"
git push origin main
```

If you do not have the repository locally yet:

```bash
git clone https://github.com/thesrujan/thesrujan.git
cd thesrujan
```

Then extract this project folder into the `thesrujan` directory and run the three `git add`, `git commit`, and `git push` commands above.

## B. Run and test locally on Windows PowerShell

Open PowerShell in the `11-Jenkins-Metrics-Exporter` folder:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m compileall -q metrics_exporter.py scripts tests
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\package.py --output deployment
```

Run the exporter:

```powershell
$env:PORT = "8000"
python metrics_exporter.py
```

Open these URLs in a browser:

- `http://localhost:8000/health` — expected response: `{"status":"ok"}`
- `http://localhost:8000/metrics` — Prometheus text metrics

Press `Ctrl+C` in PowerShell to stop the exporter.

## C. Run and test locally on Linux

```bash
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m compileall -q metrics_exporter.py scripts tests
.venv/bin/python -m pytest -q
.venv/bin/python scripts/package.py --output deployment
```

Start the exporter with `PORT=8000 .venv/bin/python metrics_exporter.py`.

## D. Configure the Jenkins Pipeline job

1. Open Jenkins in your browser and sign in.
2. Select **New Item**.
3. Enter the item name `Metrics-Exporter-Pipeline`.
4. Select **Pipeline**, then select **OK**.
5. Under **General**, optionally add a description such as `CI pipeline for the Python metrics exporter`.
6. Find the **Pipeline** section at the bottom.
7. Set **Definition** to **Pipeline script from SCM**.
8. Set **SCM** to **Git**.
9. Set **Repository URL** to `https://github.com/thesrujan/thesrujan.git`.
10. Set **Branch Specifier** to `*/main`.
11. Leave **Credentials** empty for the public repository.
12. Set **Script Path** to `11-Jenkins-Metrics-Exporter/Jenkinsfile`.
13. Select **Save**.

Make sure Git and Python are installed on the machine that runs the Jenkins build executor (agent), not merely on your browser computer. On a Windows agent, the `python` command must work for the Jenkins service account. On a Linux agent, `python3` must work.

## E. Run the successful pipeline

1. Open `Metrics-Exporter-Pipeline` in Jenkins.
2. Select **Build with Parameters** if that option is shown. Otherwise select **Build Now**; the default failure parameter is false.
3. Keep `INJECT_TEST_FAILURE` unchecked.
4. Open the build number and select **Console Output**.
5. Confirm that the five stages complete successfully and that the result is `SUCCESS`.
6. Open **Test Result** (or the published test report) and confirm the tests passed.
7. Open **Build Artifacts** and download `deployment/metrics-exporter.zip`.

The package stage creates:

```text
deployment/
├── metrics-exporter/
│   ├── README.md
│   ├── requirements.txt
│   ├── metrics_exporter.py
│   └── config/
│       └── exporter.env.example
└── metrics-exporter.zip
```

## F. Demonstrate a controlled test failure

1. Open the Jenkins job and select **Build with Parameters**.
2. Check `INJECT_TEST_FAILURE`.
3. Start the build.
4. Open **Console Output**. The test named `test_controlled_failure_switch` should fail with the message `Intentional controlled failure`.
5. Confirm that Jenkins marks the build as `FAILURE` and skips deployment packaging because the test stage failed.
6. Run **Build with Parameters** again with `INJECT_TEST_FAILURE` unchecked. The pipeline should return to `SUCCESS`.

This switch is only a demonstration mechanism. It does not change or damage the application source code.

## G. What to show in your assignment demonstration

Capture screenshots of:

1. The GitHub folder and its files.
2. Jenkins job configuration showing `Pipeline script from SCM` and the Script Path.
3. A successful build showing all five stages green.
4. Console Output showing tests passed and deployment files packaged.
5. Build Artifacts showing `metrics-exporter.zip`.
6. A second build with `INJECT_TEST_FAILURE` enabled and Jenkins result `FAILURE`.
7. A final successful rerun with the parameter unchecked.

## Troubleshooting

- **`python` or `python3` not found:** Install Python 3.10+ on the build agent, add it to `PATH`, and restart the Jenkins agent/service so it receives the updated environment.
- **Git checkout fails:** Verify the repository URL, branch name (`main`), Git installation, and credentials if the repository is private.
- **Jenkins cannot find the Jenkinsfile:** Verify the Script Path is exactly `11-Jenkins-Metrics-Exporter/Jenkinsfile`.
- **Build cannot find `requirements.txt`:** Keep the project folder in the repository root and do not change the `dir('11-Jenkins-Metrics-Exporter')` blocks in the Jenkinsfile.
- **Tests fail unexpectedly:** Inspect the test report and ensure `INJECT_TEST_FAILURE` is unchecked for a normal successful build.
- **Port 8000 is already in use:** Start the exporter with another port, for example `$env:PORT = "8001"` in PowerShell or `PORT=8001` in Linux.

## Cleanup

Generated local files can be removed after the demonstration:

- Windows PowerShell: `Remove-Item -Recurse -Force .venv, deployment -ErrorAction SilentlyContinue`
- Linux: `rm -rf .venv deployment`
