import win32com.client
import pythoncom

# Initialize COM library
pythoncom.CoInitialize()

# Try to list all registered COM objects and their ProgIDs
try:
    # Use win32com.client.gencache to try loading available libraries
    gencache = win32com.client.gencache
    for progid in gencache.GetClassIDs():
        print(progid)
except Exception as e:
    print(f"Error: {e}")
finally:
    pythoncom.CoUninitialize()
