from refresh_utils import download_all_dashboards

if __name__ == "__main__":
    print("Starting scheduled Smartgate refresh...")

    success = download_all_dashboards()

    if success:
        print("Scheduled refresh completed successfully.")
    else:
        print("Scheduled refresh completed with errors.")