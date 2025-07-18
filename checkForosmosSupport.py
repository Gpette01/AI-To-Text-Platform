import osmosdr

def check_rtl_support():
    source_types = osmosdr.source().device_names()
    if 'rtl' in source_types:
        print("RTL-SDR support is available.")
    else:
        print("RTL-SDR support is not available.")

if __name__ == "__main__":
    check_rtl_support()