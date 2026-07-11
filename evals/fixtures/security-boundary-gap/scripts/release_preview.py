import os


def main():
    if not os.environ.get("DEPLOY_CREDENTIAL"):
        raise SystemExit("deployment credential is required")
    print("preview release prepared")


if __name__ == "__main__":
    main()
