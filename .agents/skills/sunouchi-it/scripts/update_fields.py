import os
import sys
import json
import time
import argparse

# Configure stdout and stderr to use UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
if sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Add venv site-packages to path
venv_site_packages = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "venv", "Lib", "site-packages")
)
if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)
    sys.path.insert(0, os.path.join(venv_site_packages, "win32"))
    sys.path.insert(0, os.path.join(venv_site_packages, "win32", "lib"))
    sys.path.insert(0, os.path.join(venv_site_packages, "Pythonwin"))
    
    pywin32_dll_dir = os.path.join(venv_site_packages, "pywin32_system32")
    if os.path.exists(pywin32_dll_dir) and hasattr(os, "add_dll_directory"):
        try:
            os.add_dll_directory(pywin32_dll_dir)
        except Exception:
            pass

# Switch thread desktop to "Default" before importing pywinauto
try:
    import win32service
    import win32con
    hdesk = win32service.OpenDesktop("Default", 0, False, win32con.GENERIC_ALL)
    hdesk.SetThreadDesktop()
    print("[*] Switched thread to 'Default' desktop.")
except Exception as e:
    print(f"[*] Warning: SetThreadDesktop failed: {e}")

try:
    import win32gui
    from pywinauto import Application, Desktop
    from pywinauto import keyboard
except ImportError as e:
    print(f"[-] Import error: {e}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Update specific ERP header fields on open screen")
    parser.add_argument("--fields", help="JSON string representing fields to update")
    parser.add_argument("--json_file", help="Path to JSON file containing fields to update")
    args = parser.parse_args()

    data = {}
    if args.fields:
        try:
            data = json.loads(args.fields)
        except Exception as e:
            print(f"[-] Error parsing fields JSON: {e}")
            sys.exit(1)
    elif args.json_file:
        try:
            with open(args.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"[-] Error reading JSON file: {e}")
            sys.exit(1)
    else:
        print("[-] Error: Either --fields or --json_file must be specified.")
        sys.exit(1)

    # Find the open ERP window
    hwnd = None
    def enum_win(h, ctx):
        nonlocal hwnd
        title = win32gui.GetWindowText(h)
        if "生産管理システム" in title and "受注入力" in title:
            hwnd = h

    win32gui.EnumWindows(enum_win, None)

    if not hwnd:
        print("[-] Error: Could not find open ERP '受注入力' window.")
        sys.exit(1)

    print(f"[+] Found window handle: {hwnd}")
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(1.0)
    else:
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

    try:
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
    except Exception as e:
        print(f"[*] Warning: SetForegroundWindow failed: {e}")

    try:
        app = Application(backend="uia").connect(handle=hwnd)
        dlg = app.window(handle=hwnd)
        print(f"[+] Connected to window: {dlg.window_text()}")
    except Exception as e:
        print(f"[-] pywinauto connection failed: {e}")
        sys.exit(1)

    # Class wrapper to perform fields filling
    class FieldFiller:
        def __init__(self, dlg):
            self.dlg = dlg

        def order_no(self, val):
            order_field = self.dlg.child_window(auto_id="txtOrderNo", control_type="Edit")
            order_field.set_focus()
            order_field.set_text(val)
            print(f"[+] Updated オーダーNo to: {val}")

        def work_name(self, val):
            kouji_pane = self.dlg.child_window(auto_id="ucKoujiName", control_type="Pane")
            kouji_edit = kouji_pane.child_window(control_type="Edit")
            kouji_edit.set_focus()
            kouji_edit.set_text(val)
            print(f"[+] Updated 工事名 to: {val}")

        def shipping_date(self, val):
            shipping_pane = self.dlg.child_window(auto_id="dtpSyukkaDate", control_type="Pane")
            date_edit = shipping_pane.child_window(auto_id="txtDate", control_type="Edit")
            date_edit.set_focus()
            date_edit.set_text(val)
            print(f"[+] Updated 出荷日 to: {val}")

        def delivery_date(self, val):
            delivery_pane = self.dlg.child_window(auto_id="dtpNoukiDate", control_type="Pane")
            date_edit = delivery_pane.child_window(auto_id="txtDate", control_type="Edit")
            date_edit.set_focus()
            date_edit.set_text(val)
            print(f"[+] Updated 納期 to: {val}")

        def customer_code(self, val):
            tokuisaki_pane = self.dlg.child_window(auto_id="ucTokuisaki", control_type="Pane")
            customer_input = tokuisaki_pane.child_window(auto_id="txtInput", control_type="Edit")
            customer_input.set_focus()
            customer_input.set_text(val)
            keyboard.send_keys('{ENTER}')
            print(f"[+] Updated 得意先 Code to: {val}")

        def supplier_code(self, val):
            nounyu_pane = self.dlg.child_window(auto_id="ucNounyu", control_type="Pane")
            supplier_input = nounyu_pane.child_window(auto_id="txtInput", control_type="Edit")
            supplier_input.set_focus()
            supplier_input.set_text(val)
            keyboard.send_keys('{ENTER}')
            print(f"[+] Updated 納入先 Code to: {val}")

        def agent(self, val):
            agent_pane = self.dlg.child_window(auto_id="ucDaiten", control_type="Pane")
            if not agent_pane.exists():
                agent_pane = self.dlg.child_window(title="代理店", control_type="Pane")
            agent_input = agent_pane.child_window(auto_id="txtInput", control_type="Edit")
            agent_input.set_focus()
            agent_input.set_text(val)
            keyboard.send_keys('{ENTER}')
            print(f"[+] Updated 代理店 to: {val}")

        def comment(self, val):
            system_biko_pane = self.dlg.child_window(auto_id="ucSystemBiko", control_type="Pane")
            comment_field = system_biko_pane.child_window(auto_id="txtName", control_type="Edit")
            comment_field.set_focus()
            comment_field.set_text(val)
            keyboard.send_keys('{ENTER}')
            print(f"[+] Updated 備考 to: {val}")

        def shipping_warehouse(self, val):
            combo_box = self.dlg.child_window(auto_id="cmbSyukkaSouko", control_type="ComboBox")
            combo_box.click_input()
            time.sleep(0.3)
            dropdown_items = self.dlg.descendants(control_type="ListItem")
            for item in dropdown_items:
                item_text = item.window_text() if item.window_text() else item.element_info.name
                if item_text == val:
                    item.click_input()
                    print(f"[+] Selected 出荷倉庫: {val}")
                    return
            print(f"[-] Warning: Shipping warehouse '{val}' not found in list.")

        def category(self, val):
            combo_box = self.dlg.child_window(auto_id="cmbJutyuType", control_type="ComboBox")
            combo_box.click_input()
            time.sleep(0.3)
            dropdown_items = self.dlg.descendants(control_type="ListItem")
            for item in dropdown_items:
                item_text = item.window_text() if item.window_text() else item.element_info.name
                if item_text == val:
                    item.click_input()
                    print(f"[+] Selected 受注区分: {val}")
                    return
            print(f"[-] Warning: Category '{val}' not found in list.")

    filler = FieldFiller(dlg)
    for field, val in data.items():
        if hasattr(filler, field):
            try:
                func = getattr(filler, field)
                func(val)
                time.sleep(0.5)
            except Exception as e:
                print(f"[-] Error updating field '{field}': {e}")
        else:
            print(f"[-] Warning: Unknown field '{field}'. Supported fields: order_no, work_name, shipping_date, delivery_date, customer_code, supplier_code, agent, comment, shipping_warehouse, category.")

if __name__ == "__main__":
    main()
