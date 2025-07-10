import fire
import subprocess


def main(app_path, port=51075):
    subprocess.run(["streamlit", "run", app_path, "--server.port", str(port)])


if __name__ == "__main__":
    fire.Fire(main)
