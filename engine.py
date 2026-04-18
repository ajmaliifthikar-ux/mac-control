import json
import os
import objc
import sys
import argparse
from AppKit import NSWorkspace
from ApplicationServices import (
    AXUIElementCreateApplication,
    AXUIElementCopyAttributeValue,
    AXValueGetValue,
    kAXRoleAttribute,
    kAXTitleAttribute,
    kAXPositionAttribute,
    kAXSizeAttribute,
    kAXChildrenAttribute,
    kAXFocusedWindowAttribute,
    kAXDescriptionAttribute,
    kAXValueAttribute,
    kAXValueCGPointType,
    kAXValueCGSizeType,
)
import Vision
from Cocoa import NSURL, NSImage

# ============================================
# AX-API ENGINE (Structural Metadata)
# ============================================

def get_ax_attribute(element, attribute):
    res = AXUIElementCopyAttributeValue(element, attribute, None)
    if res[0] == 0:
        return res[1]
    return None

def _extract_point(ax_value):
    try:
        ok, pt = AXValueGetValue(ax_value, kAXValueCGPointType, None)
        if ok: return float(pt.x), float(pt.y)
    except: pass
    return None, None

def _extract_size(ax_value):
    try:
        ok, sz = AXValueGetValue(ax_value, kAXValueCGSizeType, None)
        if ok: return float(sz.width), float(sz.height)
    except: pass
    return None, None

def parse_element(element, depth=0, max_depth=4):
    if depth > max_depth: return None
    role = get_ax_attribute(element, kAXRoleAttribute)
    title = get_ax_attribute(element, kAXTitleAttribute)
    pos = get_ax_attribute(element, kAXPositionAttribute)
    size = get_ax_attribute(element, kAXSizeAttribute)
    x, y = _extract_point(pos) if pos is not None else (None, None)
    w, h = _extract_size(size) if size is not None else (None, None)

    data = {
        "role": str(role) if role else "Unknown",
        "name": str(title or ""),
        "x": x, "y": y, "w": w, "h": h,
    }
    children = get_ax_attribute(element, kAXChildrenAttribute)
    if children and depth < max_depth:
        child_list = [parse_element(c, depth + 1, max_depth) for c in children[:20]]
        data["children"] = [c for c in child_list if c]
    return data

# ============================================
# VISION ENGINE (Visual Metadata)
# ============================================

def run_native_ocr(image_path):
    input_url = NSURL.fileURLWithPath_(image_path)
    results = []
    def handler(request, error):
        if error: return
        for obs in request.results():
            candidate = obs.topCandidates_(1)[0]
            bbox = obs.boundingBox()
            results.append({"text": candidate.string(), "box": [bbox.origin.x, bbox.origin.y, bbox.size.width, bbox.size.height]})
    
    request = Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(handler)
    req_handler = Vision.VNImageRequestHandler.alloc().initWithURL_options_(input_url, None)
    req_handler.performRequests_error_([request], None)
    return results

# ============================================
# MAIN ORCHESTRATOR
# ============================================

def main():
    parser = argparse.ArgumentParser(description="mac-control. unified engine")
    parser.add_argument("--mode", choices=["ax", "vision", "both"], default="ax")
    parser.add_argument("--output", help="Path to save JSON output")
    args = parser.parse_args()

    active_app = NSWorkspace.sharedWorkspace().frontmostApplication()
    output_data = {"app": active_app.localizedName(), "pid": active_app.processIdentifier()}

    if args.mode in ["ax", "both"]:
        app_ref = AXUIElementCreateApplication(active_app.processIdentifier())
        window = get_ax_attribute(app_ref, kAXFocusedWindowAttribute)
        output_data["ax_tree"] = parse_element(window) if window else None

    if args.mode in ["vision", "both"]:
        temp_img = "/tmp/mc_vision.png"
        os.system(f"screencapture -x {temp_img}")
        output_data["ocr"] = run_native_ocr(temp_img)

    result_json = json.dumps(output_data, indent=2)
    if args.output:
        with open(args.output, "w") as f: f.write(result_json)
    else:
        print(result_json)

if __name__ == "__main__":
    main()
