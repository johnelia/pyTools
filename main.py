import winreg as reg
import pandas as pd
from datetime import datetime


def get_installed_software():
    software_list = []

    def get_software_from_registry(hive, subkey, view):
        try:
            registry = reg.ConnectRegistry(None, hive)
            registry_key = reg.OpenKey(registry, subkey, 0, reg.KEY_READ | view)
            for i in range(0, reg.QueryInfoKey(registry_key)[0]):
                subkey_name = reg.EnumKey(registry_key, i)
                subkey_path = subkey + "\\" + subkey_name
                try:
                    subkey_registry = reg.OpenKey(registry, subkey_path)
                    software = {
                        "Name": reg.QueryValueEx(subkey_registry, "DisplayName")[0] if "DisplayName" in [
                            reg.EnumValue(subkey_registry, j)[0] for j in
                            range(reg.QueryInfoKey(subkey_registry)[1])] else None,
                        "Version": reg.QueryValueEx(subkey_registry, "DisplayVersion")[0] if "DisplayVersion" in [
                            reg.EnumValue(subkey_registry, j)[0] for j in
                            range(reg.QueryInfoKey(subkey_registry)[1])] else None,
                        "Publisher": reg.QueryValueEx(subkey_registry, "Publisher")[0] if "Publisher" in [
                            reg.EnumValue(subkey_registry, j)[0] for j in
                            range(reg.QueryInfoKey(subkey_registry)[1])] else None,
                        "InstallDate": reg.QueryValueEx(subkey_registry, "InstallDate")[0] if "InstallDate" in [
                            reg.EnumValue(subkey_registry, j)[0] for j in
                            range(reg.QueryInfoKey(subkey_registry)[1])] else None
                    }
                    if software["Name"]:
                        software_list.append(software)
                except EnvironmentError:
                    continue
        except EnvironmentError:
            pass

    get_software_from_registry(reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                               reg.KEY_WOW64_32KEY)
    get_software_from_registry(reg.HKEY_LOCAL_MACHINE,
                               r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall", reg.KEY_WOW64_64KEY)

    return software_list


def save_to_html(dataframe):
    # Get current date and time for the filename
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"System_Inventory_Installed_apps_{current_datetime}.html"

    # Convert DataFrame to HTML and save it
    with open(filename, 'w') as f:
        f.write(dataframe.to_html(index=False))

    print(f"Data saved to {filename}")


software = get_installed_software()

df = pd.DataFrame(software)
df = df.dropna(subset=['Name']).sort_values(by='Name')

# Save the DataFrame to an HTML file
save_to_html(df)
