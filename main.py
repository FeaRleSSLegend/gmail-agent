from gmail_auth import get_gmail_service
def main():
    service = get_gmail_service()
    print("Authentication Complete!")

if __name__ == "__main__":
    main()
