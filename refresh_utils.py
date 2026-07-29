import subprocess
from pathlib import Path

# ==========================================================
# CONFIG
# ==========================================================

APP_DIR = Path(__file__).resolve().parent
JAVA_PROJECT = APP_DIR
BASE_CSV_FOLDER = APP_DIR.parent / "smartgate-downloads"


# ==========================================================
# FIND MAVEN
# ==========================================================

def find_maven_cmd():
    candidates = [
        r"C:\Program Files\Apache\maven-mvnd-1.0.6-windows-amd64\bin\mvnd.cmd",
        r"C:\Program Files\Apache\apache-maven-3.9.12\bin\mvn.cmd",
        "mvnd.cmd",
        "mvnd",
        "mvn.cmd",
        "mvn",
        str(JAVA_PROJECT / "mvnw.cmd"),
    ]

    for cmd in candidates:
        try:
            subprocess.run(
                [cmd, "-v"],
                capture_output=True,
                timeout=5
            )
            return cmd
        except Exception:
            continue

    return None


MAVEN_CMD = find_maven_cmd()


# ==========================================================
# BUILD PROJECT
# ==========================================================

def build_project():

    if not MAVEN_CMD:
        print("❌ Maven not found.")
        return False

    print("🔨 Building Java project...")

    build = subprocess.run(
        [
            MAVEN_CMD,
            "clean",
            "dependency:copy-dependencies",
            "compile",
        ],
        cwd=str(JAVA_PROJECT),
        capture_output=True,
        text=True,
        timeout=300,
    )

    if build.returncode != 0:
        print("❌ Build failed.")
        print(build.stderr)
        return False

    print("✅ Build completed successfully.")
    return True


# ==========================================================
# DOWNLOAD SINGLE DASHBOARD
# ==========================================================

def download_latest_csv(dashboard_type):

    print(f"📥 Downloading {dashboard_type} dashboard...")

    java_arg = (
        "ZAPPING"
        if dashboard_type == "Zapping"
        else dashboard_type
    )

    run = subprocess.run(
        [
            "java",
            "-cp",
            "target/classes;target/dependency/*",
            "com.smartgate.automation.App",
            java_arg,
        ],
        cwd=str(JAVA_PROJECT),
        capture_output=True,
        text=True,
        timeout=600
    )

    if run.returncode != 0:
        print(f"❌ Failed to download {dashboard_type}")
        print(run.stderr)
        return False

    print(f"✅ {dashboard_type} downloaded successfully.")
    return True


# ==========================================================
# DOWNLOAD ALL DASHBOARDS
# ==========================================================

def download_all_dashboards():

    dashboards = [
        "CT",
        "LongPlayback",
        "Maintenance",
        "Devices Without Test Execution",
        "Zapping",
    ]

    print("======================================")
    print("SMARTGATE DASHBOARD REFRESH STARTED")
    print("======================================")

    if not build_project():
        return False

    failed = []

    for dashboard in dashboards:
        success = download_latest_csv(dashboard)

        if not success:
            failed.append(dashboard)

    print()

    if failed:
        print("⚠ Refresh completed with errors.")
        print("Failed dashboards:")
        for dashboard in failed:
            print(f" - {dashboard}")
        return False

    print("======================================")
    print("✅ ALL DASHBOARDS REFRESHED SUCCESSFULLY")
    print("======================================")

    return True
