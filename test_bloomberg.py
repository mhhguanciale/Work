"""Test Bloomberg Terminal connection."""
import sys

print("Testing Bloomberg Terminal connection...\n")

# Test 1: Check if blpapi is installed
try:
    import blpapi
    print("✓ blpapi library is installed")
except ImportError:
    print("✗ blpapi library not found. Install with: pip install blpapi")
    sys.exit(1)

# Test 2: Try to connect to Bloomberg Terminal
try:
    from xbbg import blp
    print("✓ xbbg library is installed")

    # Try to fetch a simple data point (S&P 500 latest price)
    print("\nAttempting to fetch S&P 500 data from Bloomberg Terminal...")
    data = blp.bdp(tickers='SPX Index', flds='PX_LAST')

    if data is not None and not data.empty:
        print("✓ Successfully connected to Bloomberg Terminal!")
        print(f"\nSample data retrieved:")
        print(data)
        print("\n✓ Bloomberg API is ready to use!")
    else:
        print("✗ Connection failed - no data returned")

except ImportError:
    print("✗ xbbg library not found. Install with: pip install xbbg")
    print("   (Alternatively, you can use blpapi directly, but it's more complex)")
    sys.exit(1)
except Exception as e:
    print(f"\n✗ Connection to Bloomberg Terminal failed!")
    print(f"Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure Bloomberg Terminal is running and you're logged in")
    print("2. Bloomberg Terminal must be on the same machine as this script")
    print("3. Try restarting the Terminal if it's already running")
    print("4. Check if the Bloomberg API service is enabled in Terminal settings")
    sys.exit(1)
