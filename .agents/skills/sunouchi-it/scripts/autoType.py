import os
import sys

# Configure stdout and stderr to use UTF-8 encoding to avoid Windows UnicodeEncodeErrors
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

import json
import time
import argparse

# Thêm đường dẫn dự phòng đến thư viện của venv cục bộ trong .agent để chạy được bằng Python toàn cục
venv_site_packages = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "venv", "Lib", "site-packages")
)
if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)
    sys.path.insert(0, os.path.join(venv_site_packages, "win32"))
    sys.path.insert(0, os.path.join(venv_site_packages, "win32", "lib"))
    sys.path.insert(0, os.path.join(venv_site_packages, "Pythonwin"))
    
    # Thêm thư mục DLLs của pywin32 vào DLL search path cho Python 3.8+ trên Windows
    pywin32_dll_dir = os.path.join(venv_site_packages, "pywin32_system32")
    if os.path.exists(pywin32_dll_dir) and hasattr(os, "add_dll_directory"):
        try:
            os.add_dll_directory(pywin32_dll_dir)
        except Exception:
            pass

try:
    from pywinauto import Application, Desktop
    from pywinauto import keyboard
    import win32gui
    import win32con
except ImportError as e:
    print("❌ Lỗi import các thư viện tự động hóa!")
    print("Vui lòng cài đặt trước bằng lệnh: pip install pywinauto pywin32")
    sys.exit(1)


# ============================================================================
# CẤU HÌNH & HÀM LOGGING
# ============================================================================
class Logger:
    @staticmethod
    def info(msg):
        print(f"[*] {msg}", flush=True)

    @staticmethod
    def success(msg):
        print(f"[+] {msg}", flush=True)

    @staticmethod
    def warning(msg):
        print(f"[!] {msg}", flush=True)

    @staticmethod
    def error(msg):
        print(f"[-] {msg}", flush=True)


# ============================================================================
# CLASS CHÍNH THỰC HIỆN NHẬP LIỆU ERP TỰ ĐỘNG
# ============================================================================
class ERPAutotyper:
    def __init__(self, open_new_form=True):
        self.open_new_form = open_new_form
        self.app = None
        self.dlg = None

    def ensure_order_form_open(self):
        """Đảm bảo form nhập đơn hàng đang mở và sẵn sàng để nhập"""
        # ====================== BƯỚC 1: TÌM FORM ĐANG MỞ ======================
        if not self.open_new_form:
            Logger.info("🔍 Đang kiểm tra form nhập đơn hàng hiện có...")
            try:
                # Sử dụng win32gui để tìm cửa sổ 受注入力 kể cả khi đang bị thu nhỏ (minimize)
                hwnd = None
                def enum_win(h, ctx):
                    nonlocal hwnd
                    title = win32gui.GetWindowText(h)
                    if "生産管理システム" in title and "受注入力" in title:
                        hwnd = h
                win32gui.EnumWindows(enum_win, None)

                if hwnd:
                    Logger.info(f"✅ Đã tìm thấy handle form 受注入力: {hwnd}")
                    if win32gui.IsIconic(hwnd):
                        Logger.info("🔄 Form đang bị thu nhỏ, đang khôi phục...")
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        time.sleep(1.0)
                    try:
                        win32gui.SetForegroundWindow(hwnd)
                        time.sleep(0.5)
                    except Exception:
                        pass
                    
                    self.app = Application(backend="uia").connect(handle=hwnd)
                    self.dlg = self.app.window(handle=hwnd)
                    Logger.success("✅ Đã kết nối và kích hoạt form hiện có")
                    return self._activate_form_for_input()
            except Exception as e:
                Logger.info(f"🔄 Không tìm thấy hoặc lỗi kết nối form hiện có ({e}), sẽ mở form mới từ menu...")

        # ====================== BƯỚC 2: MỞ FORM MỚI TỪ MENU ======================
        Logger.info("🔍 Đang tìm cửa sổ menu chính...")
        try:
            # Sử dụng win32gui để tìm cửa sổ Menu kể cả khi đang bị thu nhỏ
            hwnd = None
            def enum_win(h, ctx):
                nonlocal hwnd
                title = win32gui.GetWindowText(h)
                if "生産管理システム" in title and "メニュー" in title:
                    hwnd = h
            win32gui.EnumWindows(enum_win, None)

            if not hwnd:
                Logger.error("❌ Không tìm thấy cửa sổ menu chính của hệ thống (kể cả khi tìm bằng Win32)")
                return False

            Logger.info(f"✅ Đã tìm thấy handle Menu chính: {hwnd}")
            if win32gui.IsIconic(hwnd):
                Logger.info("🔄 Menu chính đang bị thu nhỏ, đang khôi phục...")
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(1.0)
            try:
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.5)
            except Exception:
                pass

            menu_app = Application(backend="uia").connect(handle=hwnd)
            menu_window = menu_app.window(handle=hwnd)
            
            menu_window.set_focus()

            # Ghi lại danh sách các handle đang mở trước khi bấm
            existing_handles = set()
            try:
                all_existing = Desktop(backend="uia").windows(title_re=r"生産管理システム.*受注入力")
                for f in all_existing:
                    existing_handles.add(f.handle)
            except Exception:
                pass

            # Tìm nút 受注入力
            receive_btn = menu_window.child_window(title="受注入力", control_type="Button")
            if not receive_btn or not receive_btn.exists():
                receive_btn = menu_window.child_window(title_re=".*受注入力.*", control_type="Button")
            
            if not receive_btn or not receive_btn.exists():
                Logger.error("❌ Không tìm thấy nút 受注入力 trên Menu")
                return False

            Logger.info("📝 Đang click nút 受注入力 để mở form mới...")
            receive_btn.click_input()

            # Chờ cửa sổ mới mở ra
            max_wait = 20
            for i in range(max_wait):
                try:
                    all_forms = Desktop(backend="uia").windows(title_re=r"生産管理システム.*受注入力")
                    new_form = None
                    for form in all_forms:
                        if form.handle not in existing_handles:
                            new_form = form
                            break
                    
                    if new_form:
                        self.app = Application(backend="uia").connect(handle=new_form.handle)
                        self.dlg = self.app.window(handle=new_form.handle)

                        if not self.dlg.is_visible():
                            win32gui.ShowWindow(self.dlg.handle, win32con.SW_RESTORE)

                        if self.dlg.is_visible():
                            Logger.success(f"✅ Đã mở form MỚI thành công sau {i+1} giây")
                            time.sleep(3)
                            return self._activate_form_for_input()
                except Exception:
                    continue
                time.sleep(0.5)

            Logger.error("❌ Không thể mở form nhập đơn hàng mới sau 20 giây")
            return False

        except Exception as e:
            Logger.error(f"❌ Lỗi khi mở form: {str(e)}")
            return False

    def _activate_form_for_input(self):
        """Click nút Enter (⏎) để kích hoạt form nhập"""
        try:
            Logger.info("🔍 Đang tìm nút Enter (⏎) để kích hoạt form...")
            self.dlg.set_focus()
            
            enter_btn = self.dlg.child_window(auto_id="btnEnter", control_type="Button")
            if not enter_btn or not enter_btn.exists():
                enter_btn = self.dlg.child_window(title="⏎", control_type="Button")
            
            if enter_btn and enter_btn.exists():
                Logger.info("✅ Đã tìm thấy nút Enter, đang click...")
                enter_btn.click_input()
                Logger.success("✅ Form đã sẵn sàng để nhập dữ liệu")
                return True
            else:
                Logger.warning("⚠ Không tìm thấy nút Enter, vẫn tiếp tục...")
                return True
        except Exception as e:
            Logger.warning(f"⚠ Lỗi khi click nút Enter: {str(e)}")
            return True

    # ============================================================================
    # CÁC HÀM ĐIỀN THÔNG TIN CHI TIẾT
    # ============================================================================
    def fill_order_no(self, order_no_text):
        try:
            order_field = self.dlg.child_window(auto_id="txtOrderNo", control_type="Edit")
            if order_field and order_field.exists():
                order_field.set_focus()
                order_field.set_text(order_no_text)
                Logger.success(f"  -> Đã điền オーダーNo: {order_no_text}")
                return True
        except Exception as e:
            Logger.error(f"  -> Lỗi điền オーダーNo: {str(e)}")
        return False

    def fill_work_name(self, workname_text):
        try:
            kouji_pane = self.dlg.child_window(auto_id="ucKoujiName", control_type="Pane")
            if kouji_pane and kouji_pane.exists():
                kouji_edit = kouji_pane.child_window(control_type="Edit")
                if kouji_edit and kouji_edit.exists():
                    kouji_edit.set_focus()
                    kouji_edit.set_text(workname_text)
                    Logger.success(f"  -> Đã điền 工事名: {workname_text}")
                    return True
        except Exception as e:
            Logger.error(f"  -> Lỗi điền 工事名: {str(e)}")
        return False

    def fill_shipping_date(self, date_str):
        try:
            shipping_pane = self.dlg.child_window(auto_id="dtpSyukkaDate", control_type="Pane")
            if shipping_pane and shipping_pane.exists():
                date_edit = shipping_pane.child_window(auto_id="txtDate", control_type="Edit")
                if date_edit and date_edit.exists():
                    date_edit.set_focus()
                    date_edit.set_text(date_str)
                    Logger.success(f"  -> Đã điền 出荷日: {date_str}")
                    return True
        except Exception as e:
            Logger.error(f"  -> Lỗi điền 出荷日: {str(e)}")
        return False

    def fill_delivery_date(self, date_str):
        try:
            delivery_pane = self.dlg.child_window(auto_id="dtpNoukiDate", control_type="Pane")
            if delivery_pane and delivery_pane.exists():
                date_edit = delivery_pane.child_window(auto_id="txtDate", control_type="Edit")
                if date_edit and date_edit.exists():
                    date_edit.set_focus()
                    date_edit.set_text(date_str)
                    Logger.success(f"  -> Đã điền 納期: {date_str}")
                    return True
        except Exception as e:
            Logger.error(f"  -> Lỗi điền 納期: {str(e)}")
        return False

    def fill_customer_direct(self, customer_code):
        try:
            tokuisaki_pane = self.dlg.child_window(auto_id="ucTokuisaki", control_type="Pane")
            if tokuisaki_pane and tokuisaki_pane.exists():
                customer_input = tokuisaki_pane.child_window(auto_id="txtInput", control_type="Edit")
                if customer_input and customer_input.exists():
                    customer_input.set_focus()
                    customer_input.set_text(customer_code)
                    Logger.success(f"  -> Đã điền 得意先 Code: {customer_code}")
                    keyboard.send_keys('{ENTER}')
                    return True
        except Exception as e:
            Logger.error(f"  -> Lỗi điền 得意先: {str(e)}")
        return False

    def fill_supplier_direct(self, supplier_code):
        try:
            nounyu_pane = self.dlg.child_window(auto_id="ucNounyu", control_type="Pane")
            if nounyu_pane and nounyu_pane.exists():
                supplier_input = nounyu_pane.child_window(auto_id="txtInput", control_type="Edit")
                if supplier_input and supplier_input.exists():
                    supplier_input.set_focus()
                    supplier_input.set_text(supplier_code)
                    Logger.success(f"  -> Đã điền 納入先 Code: {supplier_code}")
                    keyboard.send_keys('{ENTER}')
                    return True
        except Exception as e:
            Logger.error(f"  -> Lỗi điền 納入先: {str(e)}")
        return False

    def fill_agent(self, agent_name):
        try:
            agent_pane = self.dlg.child_window(auto_id="ucDaiten", control_type="Pane")
            if not agent_pane.exists():
                agent_pane = self.dlg.child_window(title="代理店", control_type="Pane")
            
            if agent_pane and agent_pane.exists():
                agent_input = agent_pane.child_window(auto_id="txtInput", control_type="Edit")
                if agent_input and agent_input.exists():
                    agent_input.set_focus()
                    agent_input.set_text(agent_name)
                    Logger.success(f"  -> Đã điền 代理店: {agent_name}")
                    keyboard.send_keys('{ENTER}')
                    return True
        except Exception as e:
            Logger.error(f"  -> Lỗi điền 代理店: {str(e)}")
        return False

    def fill_comment(self, comment_text):
        try:
            system_biko_pane = self.dlg.child_window(auto_id="ucSystemBiko", control_type="Pane")
            if system_biko_pane and system_biko_pane.exists():
                comment_field = system_biko_pane.child_window(auto_id="txtName", control_type="Edit")
                if comment_field and comment_field.exists():
                    comment_field.set_focus()
                    comment_field.set_text(comment_text)
                    Logger.success(f"  -> Đã điền 備考: {comment_text}")
                    keyboard.send_keys('{ENTER}')
                    return True
        except Exception as e:
            Logger.error(f"  -> Lỗi điền 備考: {str(e)}")
        return False

    def select_shipping_warehouse(self, warehouse_name):
        try:
            combo_box = self.dlg.child_window(auto_id="cmbSyukkaSouko", control_type="ComboBox")
            if combo_box and combo_box.exists():
                combo_box.click_input()
                time.sleep(0.3)
                dropdown_items = self.dlg.descendants(control_type="ListItem")
                for item in dropdown_items:
                    item_text = item.window_text() if item.window_text() else item.element_info.name
                    if item_text == warehouse_name:
                        item.click_input()
                        Logger.success(f"  -> Đã chọn 出荷倉庫: {warehouse_name}")
                        return True
                Logger.warning(f"  -> Không tìm thấy kho '{warehouse_name}' trong danh sách")
        except Exception as e:
            Logger.error(f"  -> Lỗi chọn 出荷倉庫: {str(e)}")
        return False

    def select_category_file(self, category_name):
        try:
            combo_box = self.dlg.child_window(auto_id="cmbJutyuType", control_type="ComboBox")
            if combo_box and combo_box.exists():
                combo_box.click_input()
                time.sleep(0.3)
                dropdown_items = self.dlg.descendants(control_type="ListItem")
                for item in dropdown_items:
                    item_text = item.window_text() if item.window_text() else item.element_info.name
                    if item_text == category_name:
                        item.click_input()
                        Logger.success(f"  -> Đã chọn 受注区分: {category_name}")
                        return True
                Logger.warning(f"  -> Không tìm thấy loại đơn hàng '{category_name}'")
        except Exception as e:
            Logger.error(f"  -> Lỗi chọn 受注区分: {str(e)}")
        return False

    # ============================================================================
    # HÀM NHẬP DANH SÁCH SẢN PHẨM (MR LIST)
    # ============================================================================
    def fill_mr_list(self, products, default_order_no="", default_work_name=""):
        if not products:
            Logger.warning("  -> Không có sản phẩm nào để nhập")
            return

        Logger.info(f"📦 Đang bắt đầu nhập {len(products)} sản phẩm vào bảng MR List...")
        try:
            mr_list_pane = self.dlg.child_window(auto_id="mrList", control_type="Pane")
            if not mr_list_pane.exists():
                Logger.error("❌ Không tìm thấy bảng MR List trong form")
                return

            mr_list_pane.click_input()
            time.sleep(0.5)

            for idx, product in enumerate(products):
                product_code = product.get('商品コード', product.get('product_code', ''))
                length_value = product.get('長さ', product.get('length', ''))
                inzu_value = product.get('員数', product.get('inzu', ''))
                order_no = product.get('オーダーNo', product.get('order_no', default_order_no))
                work_name = product.get('工事名', product.get('work_name', default_work_name))
                is_processing = product.get('is_processing', False)

                # Tìm ô đang được Focus
                edit_cells = mr_list_pane.descendants(control_type="Edit")
                current_edit = None
                for edit in edit_cells:
                    if edit.has_keyboard_focus():
                        current_edit = edit
                        break
                
                if not current_edit and edit_cells:
                    current_edit = edit_cells[0]
                    current_edit.click_input()

                if not current_edit:
                    Logger.error(f"❌ Không tìm thấy ô nhập dữ liệu cho dòng số {idx+1}")
                    continue

                # Trường hợp đặc biệt: Không có mã sản phẩm -> nhập mặc định là '3'
                if not product_code:
                    Logger.warning(f"  📍 Dòng {idx+1}: Không có mã SP, điền '3' mặc định...")
                    current_edit.set_focus()
                    current_edit.set_text('3')
                    keyboard.send_keys('{TAB}')
                    time.sleep(0.2)
                    
                    # Kiểm tra focus và click nếu cần thiết
                    edit_cells = mr_list_pane.descendants(control_type="Edit")
                    focused_found = False
                    for edit in edit_cells:
                        if edit.has_keyboard_focus():
                            focused_found = True
                            break
                    if not focused_found and edit_cells:
                        edit_cells[0].click_input()
                        
                    continue

                Logger.info(f"  📍 Dòng {idx+1}: Nhập sản phẩm {product_code}...")
                
                # Nhập Mã sản phẩm
                current_edit.set_focus()
                current_edit.set_text(product_code)
                
                # Nhập Chiều dài
                if length_value:
                    keyboard.send_keys('{ENTER}')
                    time.sleep(0.2)
                    
                    current_edit = None
                    edit_cells = mr_list_pane.descendants(control_type="Edit")
                    for edit in edit_cells:
                        if edit.has_keyboard_focus():
                            current_edit = edit
                            break
                    if current_edit:
                        current_edit.type_keys(str(length_value))
                        
                        # Điều hướng Tab đến ô số lượng (員数)
                        if is_processing:
                            keyboard.send_keys('{TAB}')
                        else:
                            for _ in range(2):
                                keyboard.send_keys('{TAB}')
                else:
                    if is_processing:
                        for _ in range(2):
                            keyboard.send_keys('{TAB}')
                    else:
                        keyboard.send_keys('{TAB}')
                
                time.sleep(0.1)

                # Nhập Số lượng (員数)
                if inzu_value:
                    current_edit = None
                    edit_cells = mr_list_pane.descendants(control_type="Edit")
                    for edit in edit_cells:
                        if edit.has_keyboard_focus():
                            current_edit = edit
                            break
                    if current_edit:
                        current_edit.type_keys(str(inzu_value))
                        
                        # Tab 6 lần để nhảy qua các cột phụ đến cột オーダーNo
                        for _ in range(6):
                            keyboard.send_keys('{TAB}')
                else:
                    for _ in range(6):
                        keyboard.send_keys('{TAB}')
                
                time.sleep(0.1)

                # Nhập オーダーNo
                if order_no:
                    current_edit = None
                    edit_cells = mr_list_pane.descendants(control_type="Edit")
                    for edit in edit_cells:
                        if edit.has_keyboard_focus():
                            current_edit = edit
                            break
                    if current_edit:
                        current_edit.type_keys(str(order_no))
                
                keyboard.send_keys('{TAB}')
                time.sleep(0.1)

                # Nhập 工事名
                if work_name:
                    current_edit = None
                    edit_cells = mr_list_pane.descendants(control_type="Edit")
                    for edit in edit_cells:
                        if edit.has_keyboard_focus():
                            current_edit = edit
                            break
                    if current_edit:
                        current_edit.set_focus()
                        current_edit.set_text(str(work_name))
                
                # Nhảy sang dòng mới
                for _ in range(2):
                    keyboard.send_keys('{TAB}')
                time.sleep(0.3)

                # Sửa lỗi mất focus dòng mới nếu xảy ra
                edit_cells = mr_list_pane.descendants(control_type="Edit")
                focused_found = False
                for edit in edit_cells:
                    if edit.has_keyboard_focus():
                        focused_found = True
                        break
                if not focused_found and edit_cells:
                    edit_cells[0].click_input()

                Logger.success(f"  -> Hoàn thành dòng {idx+1}")

            Logger.success(f"✅ Đã nhập xong toàn bộ {len(products)} sản phẩm")

        except Exception as e:
            Logger.error(f"❌ Lỗi khi nhập danh sách sản phẩm: {str(e)}")


    # ============================================================================
    # HÀM KHỞI CHẠY QUY TRÌNH TOÀN BỘ
    # ============================================================================
    def fill_all_from_json(self, json_data):
        """Đọc và tự động điền toàn bộ dữ liệu từ cấu trúc JSON"""
        try:
            header = json_data.get("header", {})
            tables = json_data.get("tables", {})
            items = tables.get("items", [])

            # 1. 得意先 (Mã khách hàng)
            customer_code = header.get("customer_code", "")
            if customer_code:
                self.fill_customer_direct(customer_code)
                time.sleep(0.5)

            # 2. 納入先 (Mã nhà cung cấp)
            supplier_code = header.get("supplier_code", "")
            if supplier_code:
                self.fill_supplier_direct(supplier_code)
                time.sleep(0.5)

            # 3. 出荷日 (Ngày xuất)
            shipping_date = header.get("出荷日", "")
            if shipping_date:
                self.fill_shipping_date(shipping_date)
                time.sleep(0.3)

            # 4. 納期 (Hạn giao)
            delivery_date = header.get("納期", "")
            if delivery_date:
                self.fill_delivery_date(delivery_date)
                time.sleep(0.3)

            # 5. オーダーNo
            order_no = header.get("オーダーNo", "")
            if order_no:
                self.fill_order_no(order_no)
                time.sleep(0.3)

            # 6. 工事名
            work_name = header.get("工事名", "")
            if work_name:
                self.fill_work_name(work_name)
                time.sleep(0.3)

            # 7. 出荷倉庫 (Chọn combobox kho)
            warehouse = header.get("warehouse", "")
            if warehouse:
                self.select_shipping_warehouse(warehouse)
                time.sleep(0.5)

            # 8. 受注区分 (Chọn combobox loại đơn hàng)
            category_file = header.get("category_file", "")
            if category_file:
                self.select_category_file(category_file)
                time.sleep(0.3)

            # 9. 代理店
            agent = header.get("agent", "")
            if agent:
                self.fill_agent(agent)
                time.sleep(0.3)

            # 10. 備考 (Comment)
            comment = header.get("comment", "")
            if comment:
                self.fill_comment(comment)
                time.sleep(0.3)

            # 11. Nhập danh sách sản phẩm
            if items:
                self.fill_mr_list(items, default_order_no=order_no, default_work_name=work_name)
            else:
                Logger.warning("⚠ Không tìm thấy danh sách sản phẩm trong dữ liệu JSON")

            Logger.success("🎉 Quy trình tự động điền dữ liệu hoàn tất!")
            return True

        except Exception as e:
            Logger.error(f"❌ Lỗi trong quá trình tự động điền: {str(e)}")
            return False


# ============================================================================
# ĐIỂM KHỞI CHẠY (MAIN ENTRY POINT)
# ============================================================================
def main():
    # Bật nhận mã màu terminal
    os.system("")

    parser = argparse.ArgumentParser(description="ERP Auto-Typer - CLI Tool")
    parser.add_argument("-f", "--file", help="Đường dẫn tới file JSON chứa dữ liệu đơn hàng")
    parser.add_argument("-j", "--json", help="Chuỗi dữ liệu JSON trực tiếp")
    parser.add_argument("--open-new-form", action="store_true", default=True, help="Bắt buộc mở form nhập đơn hàng mới từ menu (mặc định là True)")
    
    args = parser.parse_args()
    data = None

    # Đọc dữ liệu dựa trên đầu vào
    if args.json:
        try:
            data = json.loads(args.json)
            Logger.success("✅ Đã parse thành công chuỗi JSON từ tham số dòng lệnh.")
        except Exception as e:
            Logger.error(f"❌ Lỗi parse chuỗi JSON: {str(e)}")
            sys.exit(1)
    elif args.file:
        if not os.path.exists(args.file):
            Logger.error(f"❌ Không tìm thấy file JSON: {args.file}")
            sys.exit(1)
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            Logger.success(f"✅ Đọc thành công file dữ liệu: {args.file}")
        except Exception as e:
            Logger.error(f"❌ Lỗi đọc file JSON: {str(e)}")
            sys.exit(1)
    else:
        # Đọc từ stdin
        Logger.info("📥 Đang chờ đọc dữ liệu JSON từ standard input (stdin)...")
        try:
            # Thiết lập non-blocking hoặc kiểm tra stdin có dữ liệu không
            # Trong Windows/Python, sys.stdin.read() sẽ block cho đến khi EOF (Ctrl+Z hoặc Ctrl+D)
            # Thích hợp cho việc pipe dữ liệu sang: cat data.json | python erp_autotype.py
            stdin_data = sys.stdin.read().strip()
            if stdin_data:
                data = json.loads(stdin_data)
                Logger.success("✅ Đã nhận và parse thành công dữ liệu JSON từ stdin.")
            else:
                Logger.error("❌ Không nhận được dữ liệu từ standard input (stdin)!")
                parser.print_help()
                sys.exit(1)
        except Exception as e:
            Logger.error(f"❌ Lỗi đọc dữ liệu từ stdin hoặc parse JSON: {str(e)}")
            sys.exit(1)

    if not data:
        Logger.error("❌ Không có dữ liệu đơn hàng để nhập!")
        sys.exit(1)

    # 4. Thực hiện Auto-Type
    autotyper = ERPAutotyper(open_new_form=args.open_new_form)
    
    Logger.info("🚀 Bắt đầu quá trình tự động nhập đơn hàng...")
    Logger.warning("[⚠️ CHÚ Ý] Không di chuyển chuột hay gõ phím trong quá trình chạy tự động.")
    
    if autotyper.ensure_order_form_open():
        success = autotyper.fill_all_from_json(data)
        if success:
            Logger.success("🎉 Hoàn thành nhập liệu thành công!")
            sys.exit(0)
        else:
            Logger.error("❌ Gặp lỗi trong quá trình tự động điền dữ liệu.")
            sys.exit(1)
    else:
        Logger.error("❌ Không thể kết nối hoặc mở form nhập liệu trên ERP Nhật.")
        sys.exit(1)


if __name__ == "__main__":
    main()
