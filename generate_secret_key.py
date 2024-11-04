from django.core.management.utils import get_random_secret_key

if __name__ == "__main__":
    secret_key = get_random_secret_key()
    print("\nGenerated Django Secret Key:")
    print("-" * 50)
    print(secret_key)
    print("-" * 50) 