# core/yolo_worker.py
try:
    from PySide6.QtCore import QThread, Signal
    HAS_PYSIDE = True
except ImportError:
    # Fake classes so the script can import successfully without PySide6
    class QThread:
        def __init__(self, *args, **kwargs):
            pass
    class Signal:
        def __init__(self, *args, **kwargs):
            pass
        def emit(self, *args, **kwargs):
            pass
    HAS_PYSIDE = False
from pathlib import Path
import fitz
from PIL import Image
from ultralytics import YOLO
import tempfile
import os
import sys
import traceback 

import torch
# Tắt dynamo trước khi bất kỳ thứ gì dùng torch
torch._dynamo.disable() if hasattr(torch, '_dynamo') else None

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

# Check both script-relative model path (for skill) and package-relative model path (for app)
MODEL_PATH = Path(__file__).resolve().parent / "model" / "best.pt"
if not MODEL_PATH.exists():
    MODEL_PATH = BASE_DIR / "model" / "best.pt"

class YOLOWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)
    progress = Signal(int)

    def __init__(self, pdf_path, file_bytes=None, conf_threshold=0.5):
        super().__init__()
        self.pdf_path = pdf_path
        self.file_bytes = file_bytes
        self.conf_threshold = conf_threshold

    def run(self):
        tmp_path = None
        doc = None
        try:
            # Mapping cho warehouse
            warehouse_mapping = {
                'kho_a': '本社倉庫',
                'kho_b': '東広島倉庫',
                'kho_c': '綾瀬倉庫'
            }

            # Mapping cho category_file
            category_mapping = {
                'loai_a': '仮受注',
                'loai_b': '本受注',
                'loai_c': '内示'
            }

            if not MODEL_PATH.exists():
                print(f"❌ YOLO Model not found at: {MODEL_PATH}")
                self.finished.emit({
                    'success': False,
                    'warehouse_name': None,
                    'warehouse_code': None,
                    'category_file': None,
                    'category_code': None,
                    'message': f'Model not found at {MODEL_PATH}'
                })
                return

            print(f"✅ Loading YOLO model from: {MODEL_PATH}")
            # Load model riêng cho mỗi thread để tránh race condition
            model = YOLO(str(MODEL_PATH), verbose=False)

            if self.file_bytes:
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    tmp_file.write(self.file_bytes)
                    tmp_path = tmp_file.name
                doc = fitz.open(tmp_path)
                print(f"🔍 YOLO processing from bytes (temp file: {tmp_path})")
            else:
                doc = fitz.open(self.pdf_path)
                print(f"🔍 YOLO processing: {self.pdf_path}")

            total_pages = len(doc)
            all_detections = []
            warehouse_detections = []
            category_detections = []

            for page_num, page in enumerate(doc):
                pix = page.get_pixmap(dpi=150)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                results = model(img, conf=self.conf_threshold, verbose=False)

                for r in results:
                    if r.boxes is None:
                        continue

                    for box in r.boxes:
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])

                        # Kiểm tra an toàn: cls phải tồn tại trong model.names
                        if model.names is None or cls not in model.names:
                            print(f"⚠️ Page {page_num+1}: Unknown class index {cls}, skipping")
                            continue

                        class_name = model.names[cls]  # đổi tên biến tránh shadow

                        detection_info = {
                            'page': page_num + 1,
                            'detected_class': class_name,
                            'confidence': round(conf * 100, 1)
                        }

                        if class_name in warehouse_mapping:
                            detection_info['warehouse_code'] = class_name
                            detection_info['warehouse_name'] = warehouse_mapping[class_name]
                            warehouse_detections.append(detection_info)
                            print(f"  🏚️ Page {page_num+1}: Warehouse {class_name} -> {warehouse_mapping[class_name]} (conf: {conf*100:.1f}%)")

                        elif class_name in category_mapping:
                            detection_info['category_code'] = class_name
                            detection_info['category_file'] = category_mapping[class_name]
                            category_detections.append(detection_info)
                            print(f"  📋 Page {page_num+1}: Category {class_name} -> {category_mapping[class_name]} (conf: {conf*100:.1f}%)")

                        all_detections.append(detection_info)

                self.progress.emit(int((page_num + 1) / total_pages * 100))

            best_warehouse = None
            best_category = None

            if warehouse_detections:
                best_warehouse = max(warehouse_detections, key=lambda x: x['confidence'])
                print(f"✅ YOLO Best warehouse: {best_warehouse['warehouse_name']} (conf: {best_warehouse['confidence']}%)")

            if category_detections:
                best_category = max(category_detections, key=lambda x: x['confidence'])
                print(f"✅ YOLO Best category: {best_category['category_file']} (conf: {best_category['confidence']}%)")

            result = {
                'success': len(all_detections) > 0,
                'warehouse_code': best_warehouse['warehouse_code'] if best_warehouse else None,
                'warehouse_name': best_warehouse['warehouse_name'] if best_warehouse else None,
                'warehouse_confidence': best_warehouse['confidence'] if best_warehouse else 0,
                'category_code': best_category['category_code'] if best_category else None,
                'category_file': best_category['category_file'] if best_category else None,
                'category_confidence': best_category['confidence'] if best_category else 0,
                'all_detections': all_detections,
                'warehouse_detections': warehouse_detections,
                'category_detections': category_detections
            }

            if all_detections:
                print(f"✅ YOLO Result: warehouse={result['warehouse_name']}, category={result['category_file']}")
            else:
                result['message'] = 'Không tìm thấy ký hiệu kho hoặc loại tài liệu nào!'

            self.finished.emit(result)

        except Exception as e:
            print(f"❌ YOLO Error: {str(e)}")
            print(f"❌ Stack trace:\n{traceback.format_exc()}") 
            self.error.emit(str(e))

        finally:
            # Đảm bảo luôn đóng doc và xóa file tạm dù có lỗi hay không
            if doc is not None:
                try:
                    doc.close()
                except Exception:
                    pass
            if tmp_path is not None and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

def run_yolo_detection_sync(pdf_path, conf_threshold=0.5):
    """
    Hàm đồng bộ để phát hiện kho (warehouse) và loại tài liệu (category_file) bằng YOLO.
    Trả về dict chứa kết quả hoặc None nếu lỗi.
    """
    doc = None
    try:
        warehouse_mapping = {
            'kho_a': '本社倉庫',
            'kho_b': '東広島倉庫',
            'kho_c': '綾瀬倉庫'
        }
        category_mapping = {
            'loai_a': '仮受注',
            'loai_b': '本受注',
            'loai_c': '内示'
        }

        if not MODEL_PATH.exists():
            print(f"❌ YOLO Model not found at: {MODEL_PATH}")
            return None

        # Tắt dynamo trước khi dùng torch
        import torch
        torch._dynamo.disable() if hasattr(torch, '_dynamo') else None

        from ultralytics import YOLO
        import fitz
        from PIL import Image

        model = YOLO(str(MODEL_PATH), verbose=False)
        doc = fitz.open(pdf_path)

        all_detections = []
        warehouse_detections = []
        category_detections = []

        for page_num, page in enumerate(doc):
            pix = page.get_pixmap(dpi=150)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            results = model(img, conf=conf_threshold, verbose=False)

            for r in results:
                if r.boxes is None:
                    continue
                for box in r.boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])

                    if model.names is None or cls not in model.names:
                        continue

                    class_name = model.names[cls]

                    detection_info = {
                        'page': page_num + 1,
                        'detected_class': class_name,
                        'confidence': round(conf * 100, 1)
                    }

                    if class_name in warehouse_mapping:
                        detection_info['warehouse_code'] = class_name
                        detection_info['warehouse_name'] = warehouse_mapping[class_name]
                        warehouse_detections.append(detection_info)
                    elif class_name in category_mapping:
                        detection_info['category_code'] = class_name
                        detection_info['category_file'] = category_mapping[class_name]
                        category_detections.append(detection_info)
                    all_detections.append(detection_info)

        best_warehouse = None
        best_category = None

        if warehouse_detections:
            best_warehouse = max(warehouse_detections, key=lambda x: x['confidence'])
        if category_detections:
            best_category = max(category_detections, key=lambda x: x['confidence'])

        return {
            'success': len(all_detections) > 0,
            'warehouse_code': best_warehouse['warehouse_code'] if best_warehouse else None,
            'warehouse_name': best_warehouse['warehouse_name'] if best_warehouse else None,
            'warehouse_confidence': best_warehouse['confidence'] if best_warehouse else 0.0,
            'category_code': best_category['category_code'] if best_category else None,
            'category_file': best_category['category_file'] if best_category else None,
            'category_confidence': best_category['confidence'] if best_category else 0.0,
        }

    except Exception as e:
        print(f"❌ YOLO sync error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass