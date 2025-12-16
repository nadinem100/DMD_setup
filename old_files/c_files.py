# include <stdio.h>
# include <windows.h>

# define DLL_PATH "C:\\Windows\\SysWOW64\\D4100_usb.dll"
# define DEVICE_NUMBER 0
# define ROW_WIDTH 1024
# define NUM_ROWS 768

typedef
short(__stdcall * GetCOMPDATA)(short);
typedef
int(__stdcall * GetDLLRev)(void);

typedef
struct
{
    HINSTANCE
dll;
GetCOMPDATA
getCOMPDATA;
GetDLLRev
getDLLRev;
} DMD;

DMD
load_dmd(const
char * dll_path) {
    DMD
dmd;
dmd.dll = LoadLibrary(dll_path);
if (!dmd.dll)
{
    printf("Failed to load DLL: %s\n", dll_path);
exit(1);
}
dmd.getCOMPDATA = (GetCOMPDATA)
GetProcAddress(dmd.dll, "GetCOMPDATA");
dmd.getDLLRev = (GetDLLRev)
GetProcAddress(dmd.dll, "GetDLLRev");
return dmd;
}

int
main()
{
DMD
dmd = load_dmd(DLL_PATH);

short
comp_data = dmd.getCOMPDATA(DEVICE_NUMBER);
printf("COMPLEMENT DATA (Expected 1 or 0): %d\n", comp_data);
printf("DLL REV: %d\n", dmd.getDLLRev());

FreeLibrary(dmd.dll);
return 0;
}
